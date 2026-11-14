"""Verdachtssuche in echten Handy-Aufnahmen – ohne MIDI-Sollwert.

usage: python3 tools/bench/verdacht.py DIAGDIR [DIAGDIR …] [--app web/index.html] [--top 25] [--json OUT.json]
  DIAGDIR = Ordner aus `diag.py AUFNAHME --out DIR` (enthält rec.json + meta.json); ein Elternordner wird nach */rec.json durchsucht.

Ablauf je Aufnahme:
  1. Die Aufnahme wird mit der App (Standard: web/index.html) nachgespielt → Notenliste + Zeitbezug (SCAN.start, Verschiebung).
  2. Aus den gespeicherten Pixelzeilen wird je Taste der Verlauf gelesen (Mitte der Taste, Median aus 5 Pixeln wie in der App):
     Abstand zur Ruhefarbe (Ruhefarbe = Median über ≤ 400 Bilder, wie gegenprobe.py) und Buntheit S·V.
     Aus den Balken-Zeilen (oberhalb der Tastatur) je Taste: Balken ja/nein (bunt oder deutlich anders als der Zeilen-Hintergrund).
  3. Drei Verdachtsarten, jede mit einer Punktzahl 0…1 (höher = verdächtiger):
     ZERSCHNITTEN  gleiche Taste, zwei Noten, Lücke < 70 ms, und die Taste leuchtet in der Lücke durchgehend weiter
                   (kein Bild nahe der Ruhefarbe). Abzug, wenn die Balken-Zeilen in dieser Zeit einen echten Spalt zeigen.
     VERSCHMOLZEN  Note > 0,5 s, und mitten in der Note fällt das Leuchten deutlich ab und steigt wieder (zweiter Anschlag).
                   Bonus, wenn die Balken-Zeilen in der Note einen neuen Balkenanfang zeigen (ehrlichster Beweis).
     STÖRUNG       > 10 Töne gleichzeitig, oder > 3 s ohne Note, obwohl in den Balken-Zeilen viel Farbe war.
Ausgabe: Zahl der Fälle je Aufnahme und Art, Rangliste der verdächtigsten Stellen (mit Video-ID und Zeit im Video und in der App),
optional alles als JSON. Die Zeiten 'video' sind Sekunden im YouTube-Video, 'app' die Songzeit in der App.
Hinweis: Das ist ein Verdachts-Finder, kein Sollwert. Jeder Treffer muss am Video angesehen werden.
GEPRÜFT 14.11.2026 an den 10 YouTube-Testvideos mit Sollwert (refs/yt-test): „zerschnitten“ 8 Treffer, davon 2 echte Fehler
(6 waren echte schnelle Wiederholungen – bei 24 Bildern/s leuchtet die Taste zwischen zwei Anschlägen oft durch);
„verschmolzen“ 53 Treffer, davon 5 echt (findet 5 von 6 echten, aber 48 Fehlalarme). → Zum Zählen ungeeignet, nur als Suchhilfe.
Genaue Zahlen gibt es nur mit Sollwert: score.py zählt 'zerschnitten' / 'verschmolzen'.
"""
import sys, os, json, glob, base64, asyncio, threading, functools, http.server, socketserver
import numpy as np
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
APP = os.path.abspath(opt('--app', os.path.join(HERE, '..', '..', 'web', 'index.html')))
TOP = int(opt('--top', '25')); OUT = opt('--json', None)
dirs = []
for a in args:
    if os.path.exists(os.path.join(a, 'rec.json')): dirs.append(a)
    else: dirs += sorted(os.path.dirname(p) for p in glob.glob(os.path.join(a, '*', 'rec.json')))
if not dirs: sys.exit(__doc__)

GAP_MAX = 0.07        # Lücke für „zerschnitten“
LONG_MIN = 0.5        # Mindestlänge für „verschmolzen“
MANY = 10             # gleichzeitige Töne für „Störung“
SILENT = 3.0          # Pause ohne Note für „Störung“
REST_LIT = 45         # Abstand zur Ruhefarbe: ab hier leuchtet die Taste (wie gegenprobe --rel)
REST_OFF = 25         # darunter: Taste in Ruhe

# --- kleiner Webserver, damit die App die großen rec.json selbst per fetch laden kann (schneller als über Playwright übergeben)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory='/')); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
H = f'http://127.0.0.1:{PORT}'
JS = open(os.path.join(HERE, 'replay.js')).read()
RUN = "async (u)=>{const rec=await (await fetch(u)).json();const f=" + JS + ";const n=f(rec);return {notes:n,start:SCAN.start,off:SCAN.firstNote-SCAN.start-1,kx:SCAN.keys.map(k=>k.x),km:SCAN.keys.map(k=>k.m),black:SCAN.keys.map(k=>k.black),kw:SCAN.kw,bd:SCAN.barDelay}}"


def hsv_sv(rgb):
    mx = rgb.max(-1); mn = rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0); v = mx / 255.0
    return s * v, s, v


def analyse(d, rep):
    rec = json.load(open(os.path.join(d, 'rec.json'))); M = rec['meta']; w, n = M['w'], M['n']
    meta = json.load(open(os.path.join(d, 'meta.json'))) if os.path.exists(os.path.join(d, 'meta.json')) else {}
    vid = meta.get('videoId') or os.path.basename(d)
    kx = np.round(np.array(rep['kx']) * (w - 1)).astype(int); km = rep['km']; blk = np.array(rep['black'])
    K = len(km); kw = (rep['kw'] or 0.02) * (w - 1)
    offs = np.array([-2, -1, 0, 1, 2]) * max(1, int(round(kw * 0.08)))
    cols = np.clip(kx[:, None] + offs[None, :], 0, w - 1)             # K × 5
    T = []; key = []; lane = []
    for f, b in rec['frames']:
        a = np.frombuffer(base64.b64decode(b), np.uint8).reshape(n, w, 3).astype(np.int16)
        rows = np.where(blk, 0, 1)
        px = a[rows[:, None], cols]                                    # K × 5 × 3
        lum = px @ np.array([3, 6, 1]); idx = np.argsort(lum, 1)[:, 2]   # Median nach Helligkeit (wie scanCore)
        key.append(px[np.arange(K), idx])
        if n >= 7:
            L = a[3:7]                                                  # 4 Balken-Zeilen
            bg = np.median(L, axis=1)                                   # Zeilen-Hintergrund (die meisten Pixel sind Hintergrund)
            p = L[:, kx]                                                # 4 × K × 3
            sv, s, v = hsv_sv(p.astype(float))
            diff = np.abs(p - bg[:, None, :]).sum(-1)
            lane.append((s > 0.3) & (v > 0.3) & (diff > 45))                # 4 × K: Balken je Zeile
        T.append(f)
    T = np.array(T) - rep['start'] - rep['off']                        # Bildzeit → App-Zeit
    key = np.array(key).astype(float)                                   # F × K × 3
    idx = np.linspace(0, len(key) - 1, min(400, len(key))).astype(int)
    rest = np.median(key[idx], 0)                                      # Ruhefarbe je Taste
    dist = np.linalg.norm(key - rest[None], axis=-1)                    # F × K
    chroma = hsv_sv(key)[0]                                             # F × K
    lane = np.array(lane) if lane else None
    lane_act = lane.any(1).mean(1) if lane is not None else None       # Anteil der Tasten mit Balken je Bild
    D = rep.get('bd') or 0.0                                           # Zeit vom Balken in den Lesezeilen bis zur Taste

    def bar_gap(k, t0, t1):
        # echter Spalt zwischen zwei Balken in mindestens einer Zeile: Balken → Hintergrund (≥ 1 Bild) → Balken, Zeit auf die Taste umgerechnet
        if lane is None: return None
        f_ = fr(t0 - D, t1 - D)
        for r in range(lane.shape[1]):
            seq = lane[f_, r, k]; seen = gap = False
            for x in seq:
                if x and gap: return True
                if x: seen = True
                elif seen: gap = True
        return False
    kidx = {m: i for i, m in enumerate(km)}
    notes = sorted(rep['notes'], key=lambda x: (x[0], x[1]))
    vt = lambda t: round(t + rep['off'] + rep['start'], 2)             # App-Zeit → Videozeit
    fr = lambda t0, t1: np.where((T >= t0) & (T <= t1))[0]
    cases = []

    # 1) zerschnitten
    for a_, b_ in zip(notes, notes[1:]):
        if a_[0] != b_[0] or a_[0] not in kidx: continue
        e1 = a_[1] + a_[2]; gap = b_[1] - e1
        if not (-0.01 <= gap < GAP_MAX): continue
        k = kidx[a_[0]]; f_ = fr(e1 - 0.045, b_[1] + 0.045)           # Bilder rund um die Lücke
        if not len(f_): continue
        dmin = dist[f_, k].min(); lit = (dist[f_, k] >= REST_LIT).mean()
        lane_gap = bar_gap(k, e1 - 0.15, b_[1] + 0.15)
        score = (0.4 + 0.6 * lit) * (0.15 if lane_gap else 1.0)       # ein Balkenspalt erklärt die Wiederholung → kaum verdächtig
        if dmin > REST_OFF:
            cases.append(dict(art='zerschnitten', video=vid, m=a_[0], app=round(e1, 2), vid_t=vt(e1), score=round(score, 3),
                              info=f'Lücke {gap*1000:.0f} ms, Taste min. {dmin:.0f} von Ruhe entfernt, Balkenspalt: {"ja" if lane_gap else "nein"}'))

    # 2) verschmolzen: in der Note beginnt ein neuer Balken (Spalt in den Balken-Zeilen), die Taste leuchtet aber durch
    #    (bei 24 Bildern/s ist die Ruhe zwischen zwei schnellen Anschlägen oft kürzer als ein Bild – die Taste allein zeigt es nicht)
    for m, s0, du, *_ in notes:
        if du <= 0.3 or m not in kidx: continue
        k = kidx[m]; g = bar_gap(k, s0 + 0.12, s0 + du - 0.06)
        f_ = fr(s0 + 0.12, s0 + du - 0.08); dip = 0.0
        if len(f_) >= 4:
            c = chroma[f_, k]; pk = np.maximum.accumulate(c); dip = float(np.max(1 - c / np.maximum(pk, 1e-6)))
        if not g and not (du > LONG_MIN and dip >= 0.35): continue
        score = (0.7 if g else 0.0) + 0.3 * min(1.0, dip / 0.5)
        cases.append(dict(art='verschmolzen', video=vid, m=m, app=round(s0, 2), vid_t=vt(s0), score=round(score, 3),
                          info=f'Note {s0:.2f}+{du:.2f} s, neuer Balken in der Note: {"ja" if g else "nein"}, Leuchten fällt zwischendurch um {dip*100:.0f} %'))

    # 3) Störungen
    ev = sorted([(x[1], 1) for x in notes] + [(x[1] + x[2], -1) for x in notes])
    cur = 0; run0 = None
    for t, dlt in ev:
        cur += dlt
        if cur > MANY and run0 is None: run0 = t
        if cur <= MANY and run0 is not None:
            cases.append(dict(art='störung', video=vid, m=None, app=round(run0, 2), vid_t=vt(run0), score=round(min(1, 0.5 + (t - run0) / 4), 3),
                              info=f'mehr als {MANY} Töne gleichzeitig für {t - run0:.2f} s')); run0 = None
    on = sorted(notes, key=lambda x: x[1]); last_end = on[0][1] if on else 0
    for x in on:
        if x[1] - last_end > SILENT and lane_act is not None:
            f_ = fr(last_end + 0.5, x[1] - 0.5); act = float(lane_act[f_].mean()) if len(f_) else 0
            typ = float(np.median(lane_act[lane_act > 0])) if np.any(lane_act > 0) else 0
            if act > 0.02 and act >= 0.5 * typ:
                cases.append(dict(art='störung', video=vid, m=None, app=round(last_end, 2), vid_t=vt(last_end), score=round(min(1, act / max(typ, 1e-6) / 2), 3),
                                  info=f'{x[1] - last_end:.1f} s ohne Note, aber Balken-Zeilen aktiv ({act*100:.0f} % der Tasten, sonst {typ*100:.0f} %)'))
        last_end = max(last_end, x[1] + x[2])
    return vid, len(rep['notes']), cases


async def main():
    allc = []; per = []
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--js-flags=--max-old-space-size=6000'])
        for d in dirs:
            pg = await br.new_page(); await pg.goto(H + APP); await pg.wait_for_timeout(300)
            try: rep = await pg.evaluate(RUN, H + os.path.abspath(os.path.join(d, 'rec.json')))
            except Exception as e: print('FEHLER Nachspielen', d, str(e)[:120]); await pg.close(); continue
            await pg.close()
            try: vid, nn, cs = analyse(d, rep)
            except Exception as e: print('FEHLER Analyse', d, str(e)[:120]); continue
            c = {a: sum(1 for x in cs if x['art'] == a) for a in ('zerschnitten', 'verschmolzen', 'störung')}
            top = sum(x['score'] for x in sorted(cs, key=lambda x: -x['score'])[:10])
            per.append(dict(video=vid, dir=os.path.basename(d), noten=nn, **c, top10=round(top, 2)))
            print(f"{vid:<14} {nn:>5} Noten | zerschnitten {c['zerschnitten']:>3} | verschmolzen {c['verschmolzen']:>3} | Störung {c['störung']:>3}", flush=True)
            allc += cs
        await br.close()
    print('\nSUMME', {a: sum(x[a] for x in per) for a in ('zerschnitten', 'verschmolzen', 'störung')}, 'in', len(per), 'Aufnahmen')
    print(f'\nRANGLISTE (Top {TOP})')
    for c in sorted(allc, key=lambda x: -x['score'])[:TOP]:
        print(f"{c['score']:.2f} {c['art']:<12} {c['video']:<13} Taste {str(c['m']):>4}  Video {c['vid_t']:>7.2f} s  App {c['app']:>7.2f} s  {c['info']}")
    print('\nBESTE TEST-VIDEOS (je Art die Aufnahme mit den meisten starken Fällen ≥ 0,6)')
    for a in ('zerschnitten', 'verschmolzen', 'störung'):
        cnt = {}
        for c in allc:
            if c['art'] == a and c['score'] >= 0.6: cnt[c['video']] = cnt.get(c['video'], 0) + 1
        best = sorted(cnt.items(), key=lambda x: -x[1])[:3]
        print(f'  {a:<12}', ', '.join(f'{v} ({k})' for v, k in best) or '—')
    if OUT: json.dump(dict(aufnahmen=per, faelle=allc), open(OUT, 'w'), ensure_ascii=False, indent=1)

asyncio.run(main())
