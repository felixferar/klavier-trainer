"""Diagnose-Datei vom Handy auswerten und durch die aktuelle Erkennung schicken.

usage: python3 tools/bench/diag.py DATEI [--out DIR] [--replay]

- Zusammenfassung: Bildrate, Lücken, Zeitstempel (native vs. YouTube), Videoqualität, Tastatur
- schreibt DIR/still.jpg, DIR/rec.json (Format von replay.js), DIR/meta.json
- --replay: spielt die Aufnahme durch scanCore/finishScan aus web/index.html und vergleicht
  mit den Noten, die das Handy erkannt hat
"""
import base64, gzip, json, math, os, struct, sys, statistics as stt

def load(path):
    raw = open(path, 'rb').read()
    if raw.startswith(b'KTDIAG1'):
        raw = base64.b64decode(raw.split(b'\n', 1)[1].strip())
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    assert raw[:4] == b'KTD1', 'keine Diagnose-Datei'
    hl = struct.unpack_from('<I', raw, 4)[0]
    meta = json.loads(raw[8:8 + hl])
    frames = []
    if meta.get('w'):
        fs = 32 + meta['w'] * meta['n'] * 3
        p = 8 + hl
        while p + fs <= len(raw):
            t, vt, f, st = struct.unpack_from('<dddd', raw, p)
            frames.append((t, vt, f, st, raw[p + 32:p + fs]))
            p += fs
    return meta, frames

def summary(meta, frames):
    print('Grund:', meta.get('reason'), '| App:', meta.get('app'), '| Gerät:', meta.get('ua', '')[:90])
    print('Bildschirm', meta.get('screen'), 'dpr', meta.get('dpr'), '| Videobox', meta.get('box'))
    print('Qualität Start/Ende:', meta.get('quality'), '/', meta.get('qualityEnd'), '| Video', meta.get('videoId'))
    if meta.get('scanDet'):
        k = meta.get('keys') or []
        print('Tastatur:', len(k), 'Tasten', k and (k[0]['m'], k[-1]['m']), '| Zeilenbreite', meta.get('w'), 'px | kw', meta.get('kw'))
    if not frames:
        print('keine Frames (', meta.get('frameCount'), ')'); return
    used = [x for x in frames if not math.isnan(x[2])]
    t = [x[0] for x in frames]
    dt = [b - a for a, b in zip(t, t[1:])]
    dur = (t[-1] - t[0]) / 1000
    print(f'Frames: {len(frames)} ({len(used)} ausgewertet) in {dur:.1f} s → {len(frames)/max(dur,1e-9):.1f} Bilder/s'
          + (' | ABGESCHNITTEN' if meta.get('truncated') else ''))
    if dt:
        q = sorted(dt)
        print(f'Abstand ms: median {stt.median(dt):.0f}  p90 {q[int(len(q)*.9)]:.0f}  max {q[-1]:.0f}  | >80 ms: {sum(d>80 for d in dt)}  >200 ms: {sum(d>200 for d in dt)}')
    # YouTube-Zeit: wie oft ändert sie sich, Drift gegen native Zeit
    vt = [x[1] for x in used]
    ch = sum(1 for a, b in zip(vt, vt[1:]) if b != a)
    print(f'YouTube-Zeit ändert sich bei {ch}/{max(1,len(vt)-1)} Frames', '(gestuft → Zeitstempel ungenau)' if ch < 0.5 * len(vt) else '')
    if len(used) > 10:
        r = [(x[1] - x[0] / 1000) for x in used]
        print(f'Versatz YouTube−native: Spannweite {max(r)-min(r):.3f} s | f−vt median {stt.median([x[2]-x[1] for x in used]):+.3f} s')
    sts = {}
    for x in frames: sts[x[3]] = sts.get(x[3], 0) + 1
    print('Player-Zustände:', sts)
    n = meta.get('notes')
    if n is not None: print('Handy-Ergebnis:', len(n), 'Noten')

def write(meta, frames, out):
    os.makedirs(out, exist_ok=True)
    for i, s in enumerate([meta.get('still')] + list(meta.get('stills') or [])):
        if s and s.startswith('data:image'):
            open(os.path.join(out, f'still{i or ""}.jpg'), 'wb').write(base64.b64decode(s.split(',', 1)[1]))
    m = {k: v for k, v in meta.items() if k not in ('still', 'stills')}
    json.dump(m, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
    if frames and meta.get('keys'):
        rec = {'meta': {'keys': meta['keys'], 'kw': meta['kw'], 'w': meta['w'], 'n': meta['n'], 'start': meta.get('start', 0)},
               'frames': [[x[2], base64.b64encode(x[4]).decode()] for x in frames if not math.isnan(x[2])]}
        json.dump(rec, open(os.path.join(out, 'rec.json'), 'w'))
    print('geschrieben nach', out)

def replay(out):
    import asyncio
    from playwright.async_api import async_playwright
    here = os.path.dirname(os.path.abspath(__file__))
    app = 'file://' + os.path.abspath(os.path.join(here, '..', '..', 'web', 'index.html'))
    js = open(os.path.join(here, 'replay.js')).read()
    rec = json.load(open(os.path.join(out, 'rec.json')))
    meta = json.load(open(os.path.join(out, 'meta.json')))
    still = os.path.join(out, 'still.jpg')
    # Tastatur mit der AKTUELLEN Erkennung neu aus dem Standbild bestimmen (sonst würden die alten Tastenpositionen nachgespielt)
    relayout = None
    if os.path.exists(still) and meta.get('scanRows'):
        relayout = {'img': 'data:image/jpeg;base64,' + base64.b64encode(open(still, 'rb').read()).decode(), 'rows': meta['scanRows']}
    async def go():
        async with async_playwright() as p:
            br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
            pg = await br.new_page(); await pg.goto(app); await pg.wait_for_timeout(300)
            if relayout:
                info = await pg.evaluate("""async (o)=>{const img=await new Promise(r=>{const i=new Image();i.onload=()=>{const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);r(x.getImageData(0,0,i.width,i.height))};i.src=o.img});
                  const det=detectKeys(img,o.rows.yA);if(!det)return null;const keys=keyLayout(det,0);restColors(keys,[img],o.rows);return {keys,kw:det.w/det.W}}""", relayout)
                if info:
                    old = {k['m']: k['x'] for k in rec['meta']['keys']}
                    moved = [(k['m'], round((k['x'] - old.get(k['m'], k['x'])) * rec['meta']['w'], 1)) for k in info['keys'] if abs(k['x'] - old.get(k['m'], k['x'])) * rec['meta']['w'] > 0.5]
                    print('Tastatur neu bestimmt:', len(info['keys']), 'Tasten; verschoben (px):', moved)
                    rec['meta']['keys'] = info['keys']; rec['meta']['kw'] = info['kw']
            got = await pg.evaluate(js, rec); await br.close(); return got
    got = asyncio.run(go())
    json.dump(got, open(os.path.join(out, 'replay-notes.json'), 'w'))
    print('Nachgespielt:', len(got), 'Noten | Handy:', len(meta.get('notes') or []))

if __name__ == '__main__':
    a = sys.argv[1:]
    out = a[a.index('--out') + 1] if '--out' in a else '/tmp/diag'
    meta, frames = load(a[0])
    summary(meta, frames)
    write(meta, frames, out)
    if '--replay' in a: replay(out)
