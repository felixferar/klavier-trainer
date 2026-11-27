"""Fehlerarten der Notenerkennung über alle Referenzvideos (Kanal-MIDI = Sollwert).
Nicht „wie viel Prozent“, sondern „welche Art Fehler kostet die Prozente“ – damit an der größten Fehlerart gearbeitet wird und nicht am zuletzt gemeldeten Song.

usage: python3 tools/bench/fehlerarten.py ROOT NAME [--ohne ID,ID] [--json OUT]
ROOT/<id>/NAME.json = erkannte Noten (echtreplay.py mit NOTES=NAME). Zuordnung Video → MIDI aus refs/echt/README.md.

Fehlende Soll-Töne (in ±100 ms kein Ton auf der Taste):
  verschmolzen  – ein erkannter Ton derselben Taste läuft über den Anschlag hinweg (Tonwiederholung als ein langer Ton)
  verschoben    – derselbe Ton wurde erkannt, aber 100–350 ms daneben
  uebersehen    – auf der Taste ist dort gar nichts
Zusätzliche erkannte Töne (zu keinem Soll-Ton in ±100 ms):
  zerschnitten  – ein Soll-Ton derselben Taste wird dort gerade gehalten (ein langer Ton als zwei)
  verschoben    – Gegenstück zu oben (wird nur einmal gezählt)
  nachbar       – gleichzeitig (±120 ms) klingt ein Soll-Ton 1–2 Halbtöne daneben (Leucht-Geist)
  oktave        – gleichzeitig klingt derselbe Ton eine Oktave daneben
  erfunden      – nichts davon
Zusatz je Fehler: anfang (erste 5 s des Songs), ende (letzte 8 s), kurz (erkannter Zusatzton < 0,09 s)."""
import sys, os, re, json, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import midiref as R, score as S

KINDS = ['verschmolzen', 'zerschnitten', 'verschoben', 'uebersehen', 'nachbar', 'oktave', 'erfunden']


def truth_for(midi, got):
    """wie midiref.evaluate: beste Spur-Kombination, Tempo und Versatz angepasst → Soll-Töne in Video-Zeit"""
    trs = R.midi_tracks(midi); idx = list(range(len(trs)))
    combos = [c for r in range(1, len(idx) + 1) for c in itertools.combinations(idx, r)] if len(idx) <= 4 else [tuple(idx)]
    best = None
    for co in combos:
        exp = sorted(((n, s, d, 'R') for i in co for n, s, d in trs[i]['notes']), key=lambda x: x[1])
        a, b, o = R.fit(exp, got)
        tr = [(n + o, a * s + b, a * d) for n, s, d, _ in exp]
        f = S.score(dict(notes=[dict(m=m, s=s, d=d, h='R') for m, s, d in tr], style=dict(one_color=True)), got).get('F1@100', 0)
        if best is None or f > best[0]: best = (f, tr)
    return best


def classify(exp, got, tol=0.1):
    """exp/got: [(m, start, dur)] in derselben Zeit. → Liste (art, m, t, zusatz) und Trefferzahl"""
    sh = S._best_shift([(m, s, d, 'R') for m, s, d in exp], [(m, s, d, 'R') for m, s, d in got], 0)
    got = [(m, s - sh, d) for m, s, d in got]
    pairs = S._match(exp, got, 0, 0, tol); me = {j for j, _ in pairs}; mg = {i for _, i in pairs}
    t0 = min(e[1] for e in exp); t1 = max(e[1] + e[2] for e in exp)
    zone = lambda t: 'anfang' if t < t0 + 5 else 'ende' if t > t1 - 8 else ''
    byE = collections.defaultdict(list); byG = collections.defaultdict(list)
    for j, e in enumerate(exp): byE[e[0]].append(j)
    for i, g in enumerate(got): byG[g[0]].append(i)
    out = []; usedG = set()
    for j, e in enumerate(exp):
        if j in me: continue
        m, s, d = e
        near = [i for i in byG[m] if i not in mg and i not in usedG and tol < abs(got[i][1] - s) <= 0.35]
        if any(got[i][1] < s - tol and got[i][1] + got[i][2] > s + 0.02 for i in byG[m]): out.append(('verschmolzen', m, s, zone(s)))
        elif near: usedG.add(min(near, key=lambda i: abs(got[i][1] - s))); out.append(('verschoben', m, s, zone(s)))
        else: out.append(('uebersehen', m, s, zone(s)))
    for i, g in enumerate(got):
        if i in mg or i in usedG: continue
        m, s, d = g; z = zone(s) + (' kurz' if d < 0.09 else '')
        snd = lambda mm: any(exp[j][1] - 0.12 <= s <= exp[j][1] + max(exp[j][2], 0.12) for j in byE[mm])
        if any(exp[j][1] < s - tol and exp[j][1] + exp[j][2] > s + 0.02 for j in byE[m]): out.append(('zerschnitten', m, s, z))
        elif any(snd(m + k) for k in (-2, -1, 1, 2)): out.append(('nachbar', m, s, z))
        elif any(snd(m + k) for k in (-12, 12)): out.append(('oktave', m, s, z))
        else: out.append(('erfunden', m, s, z))
    return out, len(pairs), len(exp), len(got)


if __name__ == '__main__':
    a = sys.argv[1:]; ohne = set(); jout = None
    if '--ohne' in a: i = a.index('--ohne'); ohne = set(a[i + 1].split(',')); del a[i:i + 2]
    if '--json' in a: i = a.index('--json'); jout = a[i + 1]; del a[i:i + 2]
    root, name = a[0], a[1]; ref = {}
    for line in open(os.path.join(HERE, 'refs/echt/README.md')):
        m = re.match(r'\|\s*([\w.]+\.mid)\s*\|[^|]*\|\s*([\w-]{11})\s*\|', line)
        if m: ref[m.group(2)] = m.group(1)
    tot = collections.Counter(); zus = collections.Counter(); H = E = G = 0; rows = {}
    print(f"{'Video':12} {'Soll':>5} {'F1':>6} | " + ' '.join(f'{k[:8]:>8}' for k in KINDS))
    for vid in sorted(os.listdir(root)):
        f = f'{root}/{vid}/{name}.json'
        if vid not in ref or vid in ohne or not os.path.exists(f): continue
        got = sorted(S._notes(json.load(open(f))), key=lambda x: x[1])
        _, exp = truth_for(os.path.join(HERE, 'refs/echt', ref[vid]), got)
        errs, h, ne, ng = classify(exp, [g[:3] for g in got])
        c = collections.Counter(e[0] for e in errs); tot.update(c); H += h; E += ne; G += ng
        for e in errs:
            for w in e[3].split(): zus[(e[0], w)] += 1
        f1 = 2 * h / (ne + ng); rows[vid] = dict(f1=round(f1, 4), soll=ne, ist=ng, **c)
        print(f"{vid:12} {ne:5d} {f1:6.3f} | " + ' '.join(f'{c[k]:8d}' for k in KINDS))
    n = sum(tot.values())
    print(f"\nGesamt: {E} Soll-Töne, {G} erkannt, {H} Treffer → F1 {2*H/(E+G):.4f}; {n} Fehler")
    for k, v in tot.most_common():
        print(f"  {k:13} {v:5d}  {100*v/n:5.1f} % der Fehler   (anfang {zus[(k,'anfang')]}, ende {zus[(k,'ende')]}, kurz {zus[(k,'kurz')]})")
    if jout: json.dump(dict(rows=rows, gesamt=dict(tot), soll=E, ist=G, treffer=H), open(jout, 'w'), indent=1)
