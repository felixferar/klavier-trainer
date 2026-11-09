"""Klassifiziert Abweichungen App-Noten vs. Gegenprobe.
usage: ana2.py DIAGDIR NOTES.json"""
import json, sys, base64, colorsys, collections
import numpy as np
D, notesf = sys.argv[1], sys.argv[2]
rec = json.load(open(D + '/rec.json')); M = rec['meta']; w, n = M['w'], M['n']
meta = json.load(open(D + '/meta.json')); keys = meta['keys']
on = {}; ev = []
for f, b in rec['frames']:
    a = np.frombuffer(base64.b64decode(b), np.uint8).reshape(n, w, 3).astype(int)
    for k in keys:
        x = round(k['x'] * (w - 1)); p = a[0 if k['black'] else 1, x]
        h, s, v = colorsys.rgb_to_hsv(*(p / 255.0)); lit = s > 0.35 and v > 0.3; m = k['m']
        if lit and m not in on: on[m] = f
        elif not lit and m in on:
            if f - on[m] > 0.06: ev.append((m, on[m], f))
            del on[m]
N = json.load(open(notesf)); nm = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'H']
name = lambda m: nm[m % 12] + str(m // 12 - 1)
c = collections.Counter(round(s - x[1], 2) for m, s, e in ev for x in N if x[0] == m)
best = max([k for k, _ in c.most_common(20)], key=lambda d: sum(1 for m, s, e in ev if any(x[0] == m and abs(x[1] + d - s) < 0.12 for x in N)))
T = [(m, s - best, e - best) for m, s, e in ev]  # in App-Zeit
used = set(); miss = []
for m, s, e in T:
    j = [i for i, x in enumerate(N) if i not in used and x[0] == m and abs(x[1] - s) < 0.2]
    if j: used.add(min(j, key=lambda i: abs(N[i][1] - s)))
    else: miss.append((m, s, e))
extra = [i for i in range(len(N)) if i not in used]
print(f'Noten {len(N)}  Gegenprobe {len(T)}  Treffer {len(used)}  fehlend {len(miss)}  zusätzlich {len(extra)}  (Versatz {best})')
print('\n-- FEHLEND (Gegenprobe-Anschlag ohne App-Note)')
for m, s, e in miss:
    cover = [x for x in N if x[0] == m and x[1] < s - 0.2 and x[1] + x[2] > s - 0.05]
    kind = 'VERSCHLUCKT (App-Note davor läuft darüber)' if cover else 'KEINE App-Note'
    print(f'  {name(m):4} t={s:7.2f} Dauer {e-s:4.2f}  {kind}' + (f' [Note {cover[0][1]:.2f}+{cover[0][2]:.2f}]' if cover else ''))
print('\n-- ZUSÄTZLICH (App-Note ohne Gegenprobe-Anschlag)')
for i in extra:
    m, s, d = N[i][0], N[i][1], N[i][2]
    inside = [t for t in T if t[0] == m and t[1] < s - 0.05 and t[2] > s + 0.05]
    near = [t for t in T if t[0] == m and abs(t[1] - s) < 0.5]
    kind = 'GESPLITTET (Anschlag läuft durch)' if inside else ('versetzt zu Anschlag' if near else 'ERFUNDEN (kein Anschlag dieser Taste)')
    print(f'  {name(m):4} t={s:7.2f} Dauer {d:4.2f}  {kind}')
