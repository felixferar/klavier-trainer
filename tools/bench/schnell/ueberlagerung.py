"""Wie viele Restfehler liegen an übereinanderliegenden Balken derselben Taste (zwei Spuren spielen denselben Ton gleichzeitig)?
usage: python3 tools/bench/schnell/ueberlagerung.py TAG   (Ergebnis eines bench.py-Laufs)"""
import sys, json, re, collections
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
import midiref as R
import os
BENCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.environ.get('KLAVIER_ECHT', '/home/claude/work/echt'); RUNS = os.environ.get('KLAVIER_RUNS', '/home/claude/work/runs')
ref = {}
for line in open(BENCH + '/refs/echt/README.md'):
    m = re.match(r'\|\s*([\w.]+\.mid)\s*\|[^|]*\|\s*([\w-]{11})\s*\|', line)
    if m: ref[m.group(2)] = m.group(1)
def raw_notes(v):
    info = json.load(open(f'{ROOT}/{v}/truth2.info.json')); trs = R.midi_tracks(f'{BENCH}/refs/echt/{ref[v]}')
    names = [t['name'] or str(t['track']) for t in trs]; want = list(info['tracks']); idx = []
    for i, n in enumerate(names):
        if n in want: idx.append(i); want.remove(n)
    a, b, o = info['tempo'], info['versatz'], info['okt'] * 12
    return [(m + o, a * s + b, a * (s + d) + b, i) for i in idx for m, s, d in trs[i]['notes']], len(trs), len(idx)
def classify(v, detail):
    raw, nt, ns = raw_notes(v); by = collections.defaultdict(list)
    for m, s, e, i in raw: by[m].append((s, e, i))
    out = []
    for kind, m, t, x in detail:
        l = by.get(m, []); amb = False
        if kind in ('zerschnitten', 'erfunden'):
            # ein Ton endet hier, während ein anderer derselben Taste weiterklingt (Farbwechsel im Balken)
            amb = any(abs(e - t) <= 0.08 and any(s2 < e - 0.05 and e2 > e + 0.05 for s2, e2, i2 in l if (s2, e2, i2) != (s, e, i)) for s, e, i in l)
        elif kind in ('verschmolzen', 'uebersehen'):
            # ein Ton beginnt hier, während ein anderer derselben Taste schon klingt und weiterklingt (Anschlag verdeckt)
            amb = any(abs(s - t) <= 0.08 and any(s2 < s - 0.05 and e2 > s + 0.05 for s2, e2, i2 in l if (s2, e2, i2) != (s, e, i)) for s, e, i in l)
        out.append(amb)
    return out, nt, ns
if __name__ == '__main__':
    tag = sys.argv[1]; res = json.load(open(f'{RUNS}/{tag}.json')); T = 0; A = 0
    for v, r in res.items():
        amb, nt, ns = classify(v, r['detail']); n = sum(amb); T += r['fehler']; A += n
        if n: print(f"{v[:4]} Spuren {ns}/{nt}  Fehler {r['fehler']:4d}  davon Überlagerung {n:3d}  " + str(dict(collections.Counter(d[0] for d, a in zip(r['detail'], amb) if a))))
    print('alle', T, 'davon Überlagerung', A)
