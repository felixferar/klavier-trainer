"""Bewertung gegen echte Sollnoten (MIDI-Wahrheit), eine Formel für alles.

usage:  score.py SOLL.json IST.json [--tol 0.05,0.1] [-v]
  SOLL.json: Ausgabe von gen.py ({"notes":[{"m","s","d","h"}], "style":{...}}) oder eine Liste [[m,start,dur,hand],...]
  IST.json : Liste [[m,start,dur,hand],...], ein meta.json aus diag.py (Feld "notes") oder replay-notes.json

Messgrößen (je Toleranz):
  P / R / F1   Anschlag (Tonhöhe gleich, Anfang innerhalb ±tol nach Ausgleich EINES festen Zeitversatzes)
  onset_med/p90  Abweichung des Anfangs der getroffenen Noten (ms)
  dur_med      Längenfehler (Median, ms)
  hands        Anteil richtiger Hand (nur bei zweifarbigen Videos sinnvoll)
Zeitversatz: Die App legt die erste Note auf 1 s → ein globaler Versatz ist erlaubt (Median der Differenzen).
Oktave: wird NICHT stillschweigend korrigiert. Liegt der ganze Song um k Oktaven falsch, steht das in 'oct' und es wird
zusätzlich das Ergebnis nach Korrektur angegeben (F1_okt) – so sieht man Oktavfehler und Erkennungsfehler getrennt.
"""
import json, sys, collections, statistics


def _notes(x):
    if isinstance(x, dict):
        if 'notes' in x and x['notes'] and isinstance(x['notes'][0], dict):
            return [(n['m'], n['s'], n['d'], n.get('h', 'R')) for n in x['notes']]
        x = x.get('notes', [])
    return [(int(n[0]), float(n[1]), float(n[2]), n[3] if len(n) > 3 else 'R') for n in x]


def _match(exp, got, shift, oct_, tol):
    """greedy, zeitlich nächste Note zuerst; jede Ist-Note höchstens einmal"""
    by = collections.defaultdict(list)
    for i, g in enumerate(got): by[g[0] - oct_].append(i)
    pairs = []
    for j, e in enumerate(exp):
        for i in by.get(e[0], ()):
            d = got[i][1] - shift - e[1]
            if abs(d) <= tol: pairs.append((abs(d), j, i))
    pairs.sort(); ue, ug, res = set(), set(), []
    for _, j, i in pairs:
        if j in ue or i in ug: continue
        ue.add(j); ug.add(i); res.append((j, i))
    return res


def _best_shift(exp, got, oct_):
    c = collections.Counter(round(g[1] - e[1], 2) for g in got for e in exp if g[0] - oct_ == e[0])
    cands = [s for s, _ in c.most_common(15)] or [0.0]
    best = max(cands, key=lambda s: len(_match(exp, got, s, oct_, 0.1)))
    for _ in range(2):  # Median der Differenzen der Treffer → unverzerrter Versatz
        m = _match(exp, got, best, oct_, 0.1)
        if not m: break
        best = best + statistics.median(got[i][1] - best - exp[j][1] for j, i in m)
    return best


def score(truth, got, tols=(0.05, 0.1), one_color=None):
    exp = sorted(_notes(truth), key=lambda n: n[1]); got = sorted(_notes(got), key=lambda n: n[1])
    if one_color is None and isinstance(truth, dict): one_color = truth.get('style', {}).get('one_color', False)
    out = dict(n_soll=len(exp), n_ist=len(got))
    if not exp or not got:
        for t in tols: out[f'F1@{int(t*1000)}'] = 0.0
        return out
    c = collections.Counter(g[0] - e[0] for g in got for e in exp if (g[0] - e[0]) % 12 == 0 and abs(g[1] - e[1]) < 30)
    oct_ = c.most_common(1)[0][0] if c else 0
    sh0 = _best_shift(exp, got, 0); sh = _best_shift(exp, got, oct_) if oct_ else sh0
    out['oct'] = oct_ // 12; out['shift'] = round(sh, 3)
    for t in tols:
        k = int(round(t * 1000))
        for tag, o, s in (('', 0, sh0), ('_okt', oct_, sh)):
            if tag and not oct_: continue
            m = _match(exp, got, s, o, t); h = len(m)
            P = h / len(got); R = h / len(exp); F = 2 * P * R / (P + R) if h else 0.0
            out[f'P@{k}{tag}'] = round(P, 4); out[f'R@{k}{tag}'] = round(R, 4); out[f'F1@{k}{tag}'] = round(F, 4)
            if not tag or oct_:
                d = sorted(abs(got[i][1] - s - exp[j][1]) * 1000 for j, i in m)
                if d: out[f'onset_med@{k}'] = round(d[len(d) // 2], 1); out[f'onset_p90@{k}'] = round(d[int(len(d) * 0.9)], 1)
                du = sorted(abs(got[i][2] - exp[j][2]) * 1000 for j, i in m)
                if du: out[f'dur_med@{k}'] = round(du[len(du) // 2], 1)
                if not one_color and m: out[f'hands@{k}'] = round(sum(got[i][3] == exp[j][3] for j, i in m) / h, 4)
                out[f'_miss@{k}'] = [exp[j][:3] for j in range(len(exp)) if j not in {a for a, _ in m}][:10]
                out[f'_extra@{k}'] = [(got[i][0], round(got[i][1] - s, 2), round(got[i][2], 2)) for i in range(len(got)) if i not in {b for _, b in m}][:10]
    return out


def summary(rows):
    """Gesamt über mehrere Videos: Treffer/Soll/Ist aufsummieren (nicht Mittel der F1)"""
    tot = {}
    for r in rows:
        for k in ('50', '100'):
            for tag in ('', '_okt'):
                key = f'@{k}{tag}' if tag else f'@{k}'
                if f'F1{key}' not in r: key = f'@{k}'
                h = r.get(f'R{key}', 0) * r['n_soll']
                t = tot.setdefault(k + tag, [0, 0, 0]); t[0] += h; t[1] += r['n_soll']; t[2] += r['n_ist']
    res = {}
    for k, (h, s, g) in tot.items():
        P = h / max(1, g); R = h / max(1, s); res[k] = dict(P=round(P, 4), R=round(R, 4), F1=round(2 * P * R / max(1e-9, P + R), 4))
    return res


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('-')]
    tols = (0.05, 0.1)
    if '--tol' in sys.argv: tols = tuple(float(v) for v in sys.argv[sys.argv.index('--tol') + 1].split(','))
    r = score(json.load(open(a[0])), json.load(open(a[1])), tols)
    if '-v' not in sys.argv: r = {k: v for k, v in r.items() if not k.startswith('_')}
    print(json.dumps(r, ensure_ascii=False, indent=1))
