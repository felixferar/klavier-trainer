"""Gegenprobe: einfacher, unabhängiger Zähler leuchtender Tasten auf einer Diagnose-Aufnahme.
usage: python3 tools/bench/gegenprobe.py DIAG_DIR NOTES.json
Zählt nur Bilder, in denen die Tastatur sichtbar ist (≥ 60 % der weißen UND ≥ 60 % der schwarzen Tasten wie in Ruhe oder farbig leuchtend) –
sonst würden Abspann-/Intro-Grafiken an Tastenpositionen als Töne gezählt (Fehlalarm 09.11.: 'fehlender Schlussakkord')."""
import json, base64, colorsys, collections, sys
import numpy as np
D, notesf = sys.argv[1], sys.argv[2]
rec = json.load(open(D + '/rec.json')); M = rec['meta']; w, n = M['w'], M['n']
meta = json.load(open(D + '/meta.json')); keys = meta['keys']
on = {}; ev = []; skipped = 0
for f, b in rec['frames']:
    a = np.frombuffer(base64.b64decode(b), np.uint8).reshape(n, w, 3).astype(int)
    st = []
    for k in keys:
        x = round(k['x'] * (w - 1)); p = a[0 if k['black'] else 1, x]
        h, s, v = colorsys.rgb_to_hsv(*(p / 255.0)); lit = s > 0.35 and v > 0.3
        rest = np.linalg.norm(p - np.array(k['rest'])) < 50
        st.append((k['m'], lit, rest, k['black']))
    okw = [l or r for _, l, r, bl in st if not bl]; okb = [l or r for _, l, r, bl in st if bl]
    if sum(okw) < 0.6 * len(okw) or sum(okb) < 0.6 * len(okb):  # keine Tastatur im Bild (weiße UND schwarze Tasten getrennt prüfen)
        skipped += 1
        for m in list(on):
            if f - on[m] > 0.06: ev.append((m, on[m], f))
            del on[m]
        continue
    for m, lit, _, _ in st:
        if lit and m not in on: on[m] = f
        elif not lit and m in on:
            if f - on[m] > 0.06: ev.append((m, on[m], f))
            del on[m]
N = json.load(open(notesf)); nm = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'H']
name = lambda m: nm[m % 12] + str(m // 12 - 1)
c = collections.Counter(round(s - x[1], 2) for m, s, e in ev for x in N if x[0] == m)
best = max([k for k, _ in c.most_common(20)], key=lambda d: sum(1 for m, s, e in ev if any(x[0] == m and abs(x[1] + d - s) < 0.12 for x in N)))
used = set(); hit = 0; miss = []
for m, s, e in ev:
    j = [i for i, x in enumerate(N) if i not in used and x[0] == m and abs(x[1] + best - s) < 0.2]
    if j: used.add(j[0]); hit += 1
    else: miss.append((name(m), round(s, 2)))
extra = [(name(N[i][0]), round(N[i][1] + best, 2), round(N[i][2], 2)) for i in range(len(N)) if i not in used]
print(f'{len(N)} Noten | Gegenprobe {len(ev)} Anschläge ({skipped} Bilder ohne Tastatur ignoriert) | gefunden {hit/len(ev):.1%} | richtig {hit/len(N):.1%} | zusätzlich {extra[:10]} | fehlend {miss[:10]}')
