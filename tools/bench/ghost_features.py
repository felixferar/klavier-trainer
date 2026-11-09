"""Merkmale der vom Geisterfilter gelöschten Ereignisse + Wahrheit.
usage: ana.py MEAS.json phone DIAGDIR | ana.py MEAS.json bench TRUTH.json"""
import json, sys, base64, colorsys, collections
import numpy as np
R = json.load(open(sys.argv[1])); mode, src = sys.argv[2], sys.argv[3]
pre, flog, keys = R['pre'], R['flog'], R['keys']
kidx = {k['m']: i for i, k in enumerate(keys)}
nm = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'H']
name = lambda m: nm[m % 12] + str(m // 12 - 1)

# --- Wahrheit: Liste (m, s) in Scan-Zeit
if mode == 'phone':
    rec = json.load(open(src + '/rec.json')); M = rec['meta']; w, n = M['w'], M['n']
    on = {}; T = []
    for f, b in rec['frames']:
        a = np.frombuffer(base64.b64decode(b), np.uint8).reshape(n, w, 3).astype(int)
        st = []
        for k in keys:
            x = round(k['x'] * (w - 1)); p = a[0 if k['black'] else 1, x]
            h, s, v = colorsys.rgb_to_hsv(*(p / 255.0)); st.append((k['m'], s > 0.35 and v > 0.3))
        tt = f - R['start']
        for m, lit in st:
            if lit and m not in on: on[m] = tt
            elif not lit and m in on:
                if tt - on[m] > 0.06: T.append((m, on[m]))
                del on[m]
    tol = 0.1
else:
    tr = json.load(open(src)); notes = tr['notes']
    # Versatz (und Oktave) aus den behaltenen Ereignissen schätzen
    kept = [e for e in pre if e['kept']]
    best = None
    for o in (-24, -12, 0, 12, 24):
        c = collections.Counter(round(e['s'] - x['s'], 2) for e in kept for x in notes if e['m'] - o == x['m'])
        for d, _ in c.most_common(5):
            sc = sum(any(e['m'] - o == x['m'] and abs(e['s'] - d - x['s']) < 0.07 for e in kept) for x in notes)
            if best is None or sc > best[0]: best = (sc, o, d)
    _, o, d = best
    T = [(x['m'] + o, x['s'] + d) for x in notes]; tol = 0.07

def feat(e):
    L = flog[kidx[e['m']]]
    rows = [r for r in L if e['s'] - 0.001 <= r[0] <= e['e'] + 0.001 and r[6]]
    if not rows: return None
    a = np.array(rows)
    return dict(c=a[:, 1].mean(), cmin=a[:, 2].mean(), cmax=a[:, 3].mean(), dist=a[:, 4].mean(), n=len(rows))

def cause(e):
    fs = [f for f in pre if f is not e and f['bar'] and abs(f['m'] - e['m']) <= 2 and abs(f['s'] - e['s']) < 0.15]
    return min(fs, key=lambda f: abs(f['s'] - e['s'])) if fs else None

usedT = set()
for e in pre:  # behaltene Ereignisse verbrauchen Wahrheit zuerst
    if e['kept']:
        j = [i for i, (m, s) in enumerate(T) if i not in usedT and m == e['m'] and abs(s - e['s']) < tol]
        if j: usedT.add(min(j, key=lambda i: abs(T[i][1] - e['s'])))
rows = []
for e in pre:
    f = feat(e)
    if f is None: continue
    j = [i for i, (m, s) in enumerate(T) if m == e['m'] and abs(s - e['s']) < tol]
    real = any(i not in usedT for i in j)
    lab = ('KEPT' if e['kept'] else ('ECHT' if real else 'GEIST'))
    c = cause(e) if not e['kept'] else None
    fc = feat(c) if c else None
    rows.append(dict(lab=lab, m=e['m'], black=keys[kidx[e['m']]]['black'], s=round(e['s'], 2), dur=round(e['e'] - e['s'], 2), bar=e['bar'], **{k: round(v, 3) for k, v in f.items()},
                     cm=c and c['m'], rel=round(f['c'] / fc['c'], 2) if fc and fc['c'] else None))
for r in rows:
    if r['lab'] != 'KEPT': print(r)
k = [r for r in rows if r['lab'] == 'KEPT' and not r['bar']]
kb = [r for r in rows if r['lab'] == 'KEPT' and r['bar']]
for nmz, grp in (('behalten mit Balken', kb), ('behalten ohne Balken', k)):
    for bl in (False, True):
        g = [r for r in grp if r['black'] == bl]
        if g: print(nmz, 'schwarz' if bl else 'weiß', len(g), 'c p5/p50', np.percentile([r['c'] for r in g], 5).round(3), np.percentile([r['c'] for r in g], 50).round(3), 'cmin p5/p50', np.percentile([r['cmin'] for r in g], 5).round(3), np.percentile([r['cmin'] for r in g], 50).round(3))
json.dump(rows, open(sys.argv[1].replace('.json', '.feat.json'), 'w'))
