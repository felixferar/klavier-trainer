"""Gegenprobe: einfacher, unabhängiger Zähler leuchtender Tasten auf einer Diagnose-Aufnahme.
usage: python3 tools/bench/gegenprobe.py DIAG_DIR NOTES.json [--rel] [--dump REF.json]  (--rel: Abstand zur Ruhefarbe statt Sättigung – auch für blasse Leuchtfarben)  (--dump friert die gezählten Anschläge als Referenzliste ein, siehe refs/README.md)
Zählt nur Bilder, in denen die Tastatur sichtbar ist (≥ 60 % der weißen UND ≥ 60 % der schwarzen Tasten wie in Ruhe oder farbig leuchtend) –
sonst würden Abspann-/Intro-Grafiken an Tastenpositionen als Töne gezählt (Fehlalarm 09.11.: 'fehlender Schlussakkord')."""
import json, base64, colorsys, collections, sys
import numpy as np
D, notesf = sys.argv[1], sys.argv[2]
rec = json.load(open(D + '/rec.json')); M = rec['meta']; w, n = M['w'], M['n']
meta = json.load(open(D + '/meta.json')); keys = meta['keys']
N = json.load(open(notesf))
def eigene_ruhe():  # Ruhefarbe je Taste = Median über (bis zu 400 gleichmäßig gewählte) Bilder; meta.rest war z.B. bei Kkd7 falsch (154 statt 249)
    fr = rec['frames']; idx = np.linspace(0, len(fr) - 1, min(400, len(fr))).astype(int); acc = []
    for i in idx:
        a = np.frombuffer(base64.b64decode(fr[i][1]), np.uint8).reshape(n, w, 3).astype(int)
        acc.append([a[0 if k['black'] else 1, round(k['x'] * (w - 1))] for k in keys])
    return np.median(np.array(acc), axis=0)
RUHE = None
def scan(REL):
    global RUHE
    if REL and RUHE is None: RUHE = eigene_ruhe()
    skipset = set()
    on = {}; ev = []; skipped = 0
    for f, b in rec['frames']:
        a = np.frombuffer(base64.b64decode(b), np.uint8).reshape(n, w, 3).astype(int)
        st = []
        for ki, k in enumerate(keys):
            x = round(k['x'] * (w - 1)); p = a[0 if k['black'] else 1, x]
            h, s, v = colorsys.rgb_to_hsv(*(p / 255.0)); dist = np.linalg.norm(p - (RUHE[ki] if REL else np.array(k['rest'])))
            if REL:  # blasse Leuchtfarben: Abstand zur Ruhefarbe statt Sättigung (Hysterese 25/45, dazwischen bleibt der Zustand)
                lit = dist >= 45 or (dist > 25 and k['m'] in on and k['m'] not in skipset)
                rest = dist < 25
            else:
                lit = s > 0.35 and v > 0.3; rest = dist < 50
            st.append((k['m'], lit, rest, k['black']))
        okw = [l or r for _, l, r, bl in st if not bl]; okb = [l or r for _, l, r, bl in st if bl]
        rw = [r for _, l, r, bl in st if not bl]; rb = [r for _, l, r, bl in st if bl]
        if sum(okw) < 0.6 * len(okw) or sum(okb) < 0.6 * len(okb) or sum(rw) < 0.4 * len(rw) or sum(rb) < 0.4 * len(rb):  # zusätzlich: ≥ 40 % in Ruhefarbe, sonst Abspann-/Vollbildgrafik (WAk/XQla 10.11.: roter Hintergrund zählte als 'leuchtend')  # keine Tastatur im Bild (weiße UND schwarze Tasten getrennt prüfen)
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
    return ev, skipped, len(rec['frames'])
FORCE = '--rel' in sys.argv; CLASSIC = '--klassisch' in sys.argv
def passung(ev):  # Güte = gefunden × richtig, mit bestem Zeitversatz (nur zur Moduswahl)
    if not ev: return 0
    c = collections.Counter(round(s - x[1], 2) for m, s, e in ev for x in N if x[0] == m)
    if not c: return 0
    bd = max([k for k, _ in c.most_common(20)], key=lambda d: sum(1 for m, s, e in ev if any(x[0] == m and abs(x[1] + d - s) < 0.12 for x in N)))
    us = set(); h = 0
    for m, s, e in ev:
        j = [i for i, x in enumerate(N) if i not in us and x[0] == m and abs(x[1] + bd - s) < 0.2]
        if j: us.add(j[0]); h += 1
    return (h / len(ev)) * (h / len(N))
if FORCE: ev, skipped, nf = scan(True); mode = 'relativ'
elif CLASSIC: ev, skipped, nf = scan(False); mode = 'klassisch'
else:  # beide Modi rechnen, besseren nehmen (klassisch ist bei blassen Farben zu streng, relativ bei Effekten zu empfindlich)
    e1, s1, nf = scan(False); e2, s2, _ = scan(True); p1, p2 = passung(e1), passung(e2)
    if p2 > p1 + 0.02: ev, skipped, mode = e2, s2, 'relativ (automatisch, %.2f vs %.2f)' % (p2, p1)
    else: ev, skipped, mode = e1, s1, 'klassisch (%.2f vs relativ %.2f)' % (p1, p2)
if '--dump' in sys.argv: json.dump({'review': 'unreviewed', 'source': D.rstrip('/').split('/')[-1], 'events': [[m, round(s, 3), round(e, 3)] for m, s, e in ev]}, open(sys.argv[sys.argv.index('--dump') + 1], 'w'))
nm = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'H']
name = lambda m: nm[m % 12] + str(m // 12 - 1)
c = collections.Counter(round(s - x[1], 2) for m, s, e in ev for x in N if x[0] == m)
best = max([k for k, _ in c.most_common(20)], key=lambda d: sum(1 for m, s, e in ev if any(x[0] == m and abs(x[1] + d - s) < 0.12 for x in N)))
used = set(); hit = 0; miss = []
for m, s, e in ev:
    j = [i for i, x in enumerate(N) if i not in used and x[0] == m and abs(x[1] + best - s) < 0.2]
    if j: used.add(j[0]); hit += 1
    else: miss.append((name(m), round(s, 2)))
extra = [(name(N[i][0]), round(N[i][1] + best, 2), round(N[i][2], 2)) for i in range(len(N)) if i not in used]
print(f'[{mode}] {len(N)} Noten | Gegenprobe {len(ev)} Anschläge ({skipped} Bilder ohne Tastatur ignoriert) | gefunden {hit/len(ev):.1%} | richtig {hit/len(N):.1%} | zusätzlich {extra[:10]} | fehlend {miss[:10]}')
if '--verteilung' in sys.argv:  # wo fehlen Anschläge? (Zeit in 20-s-Blöcken, häufigste Tasten, Dauer)
    used2 = set(); fehl = []
    for m, s, e in ev:
        j = [i for i, x in enumerate(N) if i not in used2 and x[0] == m and abs(x[1] + best - s) < 0.2]
        if j: used2.add(j[0])
        else: fehl.append((m, s, e - s))
    cc = collections.Counter(int(s // 20) * 20 for m, s, d in fehl)
    print('Fehlende', len(fehl), '| je 20 s:', sorted(cc.items()))
    print('Tasten:', collections.Counter(name(m) for m, s, d in fehl).most_common(6))
    dd = sorted(d for m, s, d in fehl); print('Dauer: median', round(dd[len(dd)//2], 2) if dd else '-', '| <0.15 s:', sum(1 for d in dd if d < 0.15), '| >=0.3 s:', sum(1 for d in dd if d >= 0.3), '| Versatz', best)
if '--verteilung' in sys.argv:  # App-Noten ohne Zähler-Anschlag: wo, welche Tasten, wie lang
    ux = [(N[i][0], N[i][1] + best, N[i][2]) for i in range(len(N)) if i not in used]
    cx = collections.Counter(int(s // 20) * 20 for m, s, d in ux)
    print('App-Noten ohne Anschlag', len(ux), '| je 20 s:', sorted(cx.items()))
    print('Tasten:', collections.Counter(name(m) for m, s, d in ux).most_common(6))
    dx = sorted(d for m, s, d in ux); print('Dauer: median', round(dx[len(dx)//2], 2) if dx else '-', '| <0.15 s:', sum(1 for d in dx if d < 0.15), '| >=0.5 s:', sum(1 for d in dx if d >= 0.5))
if '--paare' in sys.argv:  # zeitgleich fehlender Anschlag und unbestätigte App-Note: Halbton-Abstand (Taste verwechselt?)
    fe = [(m, s) for m, s, e in ev if not any(i for i in [])]  # alle Anschläge
    usedN = set(i for i in used); un = [(i, N[i][0], N[i][1] + best) for i in range(len(N)) if i not in usedN]
    ue = [(m, s) for m, s, d in [(m, s, e - s) for m, s, e in ev] if not any(abs(N[i][1] + best - s) < 0.2 and N[i][0] == m for i in usedN)]
    hist = collections.Counter(); n_ok = 0
    for i, m, s in un:
        c = [(abs(m2 - m), m2 - m) for m2, s2 in ue if abs(s2 - s) < 0.25]
        if c: hist[min(c)[1]] += 1; n_ok += 1
    print('unbestätigte App-Noten mit zeitgleichem fehlendem Anschlag:', n_ok, 'von', len(un), '| Halbton-Differenz (Zähler−App):', sorted(hist.items()))
if '--paare' in sys.argv:  # unbestätigte App-Noten, deren Taste im Zähler schon durchgehend leuchtet (gleiche Taste ohne Lücke → Zähler zählt nur einen Anschlag)
    cov = sum(1 for i, m, s in un if any(m2 == m and s2 - 0.1 < s < e2 - 0.05 for m2, s2, e2 in ev))
    print('davon mitten in einem durchgehenden Zähler-Anschlag der gleichen Taste (Zähler verschmilzt):', cov, 'von', len(un))
