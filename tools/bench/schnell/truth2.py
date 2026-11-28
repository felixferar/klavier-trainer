"""Sollwert aus der Kanal-MIDI, bereinigt:
 1. doppelte Töne (gleiche Taste, Anfang ≤ 50 ms auseinander – dieselbe Note in zwei Spuren oder zwei Note-on im selben Moment) sind EIN Anschlag;
 2. beginnt ein Ton, während derselbe Ton noch klingt (zweite Spur), endet der erste dort (im Video: ein Balken läuft in den nächsten);
 3. Spurauswahl: bei ≤ 4 Spuren alle Kombinationen, sonst schrittweise (Spur dazunehmen/weglassen, solange F1@100 steigt) – so fallen Spuren weg, die das Video nicht zeigt."""
import sys, os, itertools, collections
BENCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BENCH)
import midiref as R, score as S


def dedupe(notes, tol=0.05):
    by = collections.defaultdict(list)
    for n in notes: by[n[0]].append([n[1], n[1] + n[2]])
    out = []
    for m, l in by.items():
        l.sort(); cur = None; res = []
        for s, e in l:
            if cur is not None and s - cur[0] <= tol: cur[1] = max(cur[1], e); continue
            if cur is not None: res.append(cur)
            cur = [s, e]
        if cur is not None: res.append(cur)
        for i, (s, e) in enumerate(res):
            if i + 1 < len(res) and res[i + 1][0] < e: e = res[i + 1][0]
            out.append((m, s, max(0.0, e - s)))
    return sorted(out, key=lambda x: x[1])


def f1(exp, got, tol=0.1):
    if not exp or not got: return 0.0
    sh = S._best_shift([(m, s, d, 'R') for m, s, d in exp], got, 0)
    h = len(S._match(exp, [(g[0], g[1] - sh, g[2]) for g in got], 0, 0, tol))
    return 2 * h / (len(exp) + len(got))


def build(midi, got):
    """got: [(m, start, dur, hand)] sortiert → (Soll-Töne in Video-Zeit [(m,s,d)], info)"""
    trs = R.midi_tracks(midi); n = len(trs)
    allexp = sorted(((x[0], x[1], x[2], 'R') for t in trs for x in t['notes']), key=lambda x: x[1])
    a, b, o = R.fit(allexp, got)
    conv = lambda idx: dedupe([(m + o, a * s + b, a * d) for i in idx for m, s, d in trs[i]['notes']])
    if n <= 4:
        cands = [c for r in range(1, n + 1) for c in itertools.combinations(range(n), r)]
        best = max(cands, key=lambda c: f1(conv(c), got))
    else:
        cur = (max(range(n), key=lambda i: f1(conv((i,)), got)),); sc = f1(conv(cur), got); ch = True
        while ch:
            ch = False
            for i in range(n):
                c2 = tuple(sorted(set(cur) ^ {i}))
                if not c2: continue
                s2 = f1(conv(c2), got)
                if s2 > sc + 1e-9: cur, sc, ch = c2, s2, True
        best = cur
    # Zeitachse mit der gewählten Auswahl neu anpassen
    exp4 = sorted(((m, s, d, 'R') for i in best for m, s, d in trs[i]['notes']), key=lambda x: x[1])
    a2, b2, o2 = R.fit(exp4, got)
    exp = dedupe([(m + o2, a2 * s + b2, a2 * d) for m, s, d, _ in exp4])
    if f1(exp, got) < f1(conv(best), got): exp = conv(best); a2, b2, o2 = a, b, o
    info = dict(tracks=[trs[i]['name'] or str(trs[i]['track']) for i in best], alle=[t['name'] or str(t['track']) for t in trs], tempo=round(a2, 5), versatz=round(b2, 3), okt=o2 // 12,
                roh=sum(len(trs[i]['notes']) for i in best), soll=len(exp))
    return exp, info


if __name__ == '__main__':
    import json
    ROOT = os.environ.get('KLAVIER_ECHT', '/home/claude/work/echt'); import re
    ref = {}
    for line in open(os.path.join(BENCH, 'refs/echt/README.md')):
        m = re.match(r'\|\s*([\w.]+\.mid)\s*\|[^|]*\|\s*([\w-]{11})\s*\|', line)
        if m: ref[m.group(2)] = m.group(1)
    tag = sys.argv[1]
    for v in sorted(os.listdir(ROOT)):
        if len(sys.argv) > 2 and not any(v.startswith(x) for x in sys.argv[2:]): continue
        got = sorted(S._notes(json.load(open(f'{ROOT}/{v}/{tag}.json'))), key=lambda x: x[1])
        exp, info = build(os.path.join(BENCH, 'refs/echt', ref[v]), got)
        json.dump(exp, open(f'{ROOT}/{v}/truth2.json', 'w')); json.dump(info, open(f'{ROOT}/{v}/truth2.info.json', 'w'))
        print(v, 'F1', round(f1(exp, got), 4), info, flush=True)
