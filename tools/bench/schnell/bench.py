"""Schnelle Messung ohne Browser: Aufnahme → Node (scanCore/finishScan aus APP) → Noten → Bewertung gegen die Kanal-MIDI.
usage: python3 bench.py APP.html TAG [ID...] [--set K=V ...] [--par 2] [--base TAG] [--quiet]
Ablage: ROOT/<id>/<TAG>.json (Noten), runs/<TAG>.json (Ergebnis). Der Sollwert (MIDI an das Video angepasst) wird je Video einmal
aus dem Lauf BASIS (truth.json) bestimmt und dann festgehalten – so sind alle Läufe auf derselben Zeitachse vergleichbar."""
import sys, os, re, json, subprocess, collections, concurrent.futures as cf, time
HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE); sys.path.insert(0, BENCH)
import midiref as R, score as S, fehlerarten as F
ROOT = os.environ.get('KLAVIER_ECHT', '/home/claude/work/echt'); DIAG = os.path.join(os.environ.get('KLAVIER_DIAG', '/home/claude/klavier-diagnose'), 'diag'); RUNS = os.environ.get('KLAVIER_RUNS', '/home/claude/work/runs')
EINSTELL1 = 'KyYaCtLsAAk ADiGiK75FMM xOj7uhi3w80 5OwchavoI0s GBdqm09XWbQ PufbzTlHfWY 8MmOMEcZrz4 sBnPmRPAyBI V7dy35ovtj0 _3MNRYZWpmU'.split()
PRUEF = 'Kg8zA6sM85U pR19Z4_jpLI SdijhNhiq3s 0iqbVD-VW4c'.split()
EINSTELL2 = 'TdacNfWymGQ N23HHa0LJ5U D2WOWFi_Oxw gUuZIBKlbPU 0qyOH7Xt0pk L_uwufdfKLg QwKbNj0OJSg 9PbxTdTkNnc Lh8A9Pugwgw 2FeFGvxKYeQ CN_G21YPmIA Uvyw6d_O-pM q6HM_Qoo85w 7vlj8Jceiqo BVgQCW087ak'.split()
ANDERE_FASSUNG = 'HQozceVazhI 3Sp4dW-JdJE'.split()
SETS = dict(e1=EINSTELL1, e2=EINSTELL2, pruef=PRUEF, fassung=ANDERE_FASSUNG, einstell=EINSTELL1 + EINSTELL2, alle=EINSTELL1 + EINSTELL2 + PRUEF)
ref = {}
for line in open(os.path.join(BENCH, 'refs/echt/README.md')):
    m = re.match(r'\|\s*([\w.]+\.mid)\s*\|[^|]*\|\s*([\w-]{11})\s*\|', line)
    if m: ref[m.group(2)] = m.group(1)


def run_node(app, vid, tag, sets, dbg=None):
    src = open(f'{ROOT}/{vid}/SOURCE.txt').read().strip(); out = f'{ROOT}/{vid}/{tag}.full.json'
    cmd = ['node', '--max-old-space-size=3000', os.path.join(HERE, 'replay_node.js'), app, f'{DIAG}/{src}', out]
    if not os.environ.get('NO_RELAYOUT'): cmd += ['--relayout', f'{ROOT}/{vid}']
    for s in sets: cmd += ['--set', s]
    if dbg: cmd += ['--dbg', dbg]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(vid + ': ' + r.stderr[-800:])
    d = json.load(open(out)); json.dump(d['notes'], open(f'{ROOT}/{vid}/{tag}.json', 'w')); return d


def truth(vid, got=None):
    p = f'{ROOT}/{vid}/truth2.json'
    if os.path.exists(p): return [tuple(x) for x in json.load(open(p))]
    import truth2
    exp, info = truth2.build(os.path.join(BENCH, 'refs/echt', ref[vid]), got)
    json.dump(exp, open(p, 'w')); json.dump(info, open(f'{ROOT}/{vid}/truth2.info.json', 'w')); return exp


def evaluate(vid, notes):
    got = sorted(S._notes(notes), key=lambda x: x[1]); exp = truth(vid, got)
    errs, h, ne, ng = F.classify(exp, [g[:3] for g in got])
    c = collections.Counter(e[0] for e in errs)
    # F1@50 auf derselben Zuordnung
    sh = S._best_shift([(m, s, d, 'R') for m, s, d in exp], [(m, s, d, 'R') for m, s, d in [g[:3] for g in got]], 0)
    g2 = [(m, s - sh, d) for m, s, d in [g[:3] for g in got]]
    h50 = len(S._match(exp, g2, 0, 0, 0.05))
    return dict(f1=2 * h / (ne + ng), f50=2 * h50 / (ne + ng), soll=ne, ist=ng, hit=h, errs=dict(c), fehler=ne - h + ng - h, detail=errs)


def main():
    a = sys.argv[1:]; sets = []; par = 2; base = None; quiet = False; dbg = None; evalonly = False
    i = 0
    while i < len(a):
        if a[i] == '--set': sets.append(a[i + 1]); del a[i:i + 2]
        elif a[i] == '--par': par = int(a[i + 1]); del a[i:i + 2]
        elif a[i] == '--base': base = a[i + 1]; del a[i:i + 2]
        elif a[i] == '--dbg': dbg = a[i + 1]; del a[i:i + 2]
        elif a[i] == '--quiet': quiet = True; del a[i]
        elif a[i] == '--eval': evalonly = True; del a[i]
        else: i += 1
    app, tag = os.path.abspath(a[0]), a[1]; ids = []
    for x in a[2:]: ids += SETS.get(x, [x])
    ids = ids or SETS['alle'] + ANDERE_FASSUNG
    ids = [next((v for v in ref if v.startswith(x)), x) for x in ids]
    t0 = time.time(); res = {}
    with cf.ThreadPoolExecutor(par) as ex:
        futs = {v: ex.submit((lambda v: json.load(open(f'{ROOT}/{v}/{tag}.full.json'))) if evalonly else (lambda v: run_node(app, v, tag, sets, dbg)), v) for v in ids}
        for v in ids:
            d = futs[v].result(); r = evaluate(v, d['notes']); r['barDelay'] = d.get('barDelay'); res[v] = r
    bres = json.load(open(f'{RUNS}/{base}.json')) if base and os.path.exists(f'{RUNS}/{base}.json') else {}
    K = F.KINDS
    if not quiet: print(f"{'Video':12} {'Soll':>5} {'Ist':>5} {'F1@100':>7} {'Δ':>6} {'F1@50':>6} {'Fehler':>6} | " + ' '.join(f'{k[:6]:>6}' for k in K))
    def row(name, rs, brs):
        E = sum(r['soll'] for r in rs); G = sum(r['ist'] for r in rs); H = sum(r['hit'] for r in rs)
        mean = sum(r['f1'] for r in rs) / len(rs); m50 = sum(r['f50'] for r in rs) / len(rs)
        bm = sum(r['f1'] for r in brs) / len(brs) if brs and len(brs) == len(rs) else None
        c = collections.Counter()
        for r in rs: c.update(r['errs'])
        print(f"{name:12} {E:5d} {G:5d} {mean:7.4f} {(mean-bm)*100 if bm is not None else 0:+6.2f} {m50:6.4f} {E-H+G-H:6d} | " + ' '.join(f'{c[k]:6d}' for k in K) + f"   (≥99,5 %: {sum(r['f1']>=0.995 for r in rs)}, ≥99 %: {sum(r['f1']>=0.99 for r in rs)}, ≥98 %: {sum(r['f1']>=0.98 for r in rs)} von {len(rs)})")
    for v in ids:
        r = res[v]; b = bres.get(v)
        if not quiet: print(f"{v[:12]:12} {r['soll']:5d} {r['ist']:5d} {r['f1']:7.4f} {(r['f1']-b['f1'])*100 if b else 0:+6.2f} {r['f50']:6.4f} {r['fehler']:6d} | " + ' '.join(f"{r['errs'].get(k,0):6d}" for k in K))
    print()
    for name, st in (('Einstell 1', EINSTELL1), ('Einstell 2', EINSTELL2), ('Einstell', EINSTELL1 + EINSTELL2), ('Prüfmenge', PRUEF), ('alle 29', SETS['alle'])):
        rs = [res[v] for v in st if v in res]
        if len(rs) == len(st): row(name, rs, [bres[v] for v in st if v in bres])
    json.dump(res, open(f'{RUNS}/{tag}.json', 'w'))
    print(f'({time.time()-t0:.0f} s)')


if __name__ == '__main__': main()
