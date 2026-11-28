"""Echte Videos gegen die MIDI-Datei des Kanals bewerten (Sollwert aus der MIDI, Zeitachse an das Video angepasst).

usage: python3 tools/bench/midiref.py REF.mid IST.json [--tracks auto|all|0,2] [-v] [--json OUT.json]
  IST.json: meta.json aus diag.py (Feld notes = [[m, start, dur, hand], …]) oder eine Notenliste.

Schritte:
  1. MIDI lesen (Tempo-Wechsel beachtet) → Noten in Sekunden, je Spur. Spuren ohne Noten fallen weg; Schlagzeug-Kanal 10 fällt weg.
  2. Zeitachse anpassen: t_video = a · t_midi + b. Das Video kann ein anderes Tempo haben (a ≠ 1) und einen Versatz (b).
     a wird in 0,80…1,25 gesucht (grob, dann fein), b über die häufigste Differenz gleicher Tonhöhen; danach Kleinste Quadrate
     über die Paare, die innerhalb ±100 ms passen. Oktave wird wie in score.py getrennt erkannt.
  3. --tracks auto: jede Spur-Kombination wird probiert (bei ≤ 4 Spuren mit Noten), die beste nach F1@100 gilt – so fällt z. B. eine
     Gesangs-Spur weg, die im Video nicht gezeigt wird. Welche Spuren genommen wurden, steht in der Ausgabe.
  4. Bewertung mit score.py (F1 ±50/±100 ms, Längen, zerschnitten/verschmolzen).
  5. (27.11.2026) Der Sollwert wird bereinigt, bevor verglichen wird – sonst zählt die Messung Fehler, die keine sind:
     a) Doppelte Töne (gleiche Taste, Anfang ≤ 50 ms auseinander: dieselbe Note in zwei Spuren, oder zwei Note-on im selben Moment → Ton mit Dauer 0)
        sind EIN Anschlag. Vorher galt der zweite als „übersehen“ (q6HM 48, V7dy 82, 0qyO 57, Kg8z 835 solche Scheinfehler).
     b) Beginnt ein Ton, während derselbe Ton aus einer anderen Spur noch klingt, endet der erste dort (im Video läuft ein Balken in den nächsten).
     c) Mehr als 4 Spuren: statt „alle Spuren“ wird schrittweise gewählt (Spur dazu/weg, solange F1@100 steigt). Lost Sky hat 8 Spuren, das Video
        zeigt aber weder Streicher noch Chor.
Warnung: passt die beste Zuordnung schlecht (F1@100 < 0,6), ist die MIDI vermutlich nicht die Datei des Videos → aussortieren.
"""
import sys, os, json, itertools, collections
import mido
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import score as S


def midi_tracks(path):
    m = mido.MidiFile(path); tempo_map = []                       # (tick, tempo) über alle Spuren
    for tr in m.tracks:
        t = 0
        for msg in tr:
            t += msg.time
            if msg.type == 'set_tempo': tempo_map.append((t, msg.tempo))
    tempo_map.sort(); tempo_map = tempo_map or [(0, 500000)]
    if tempo_map[0][0] != 0: tempo_map.insert(0, (0, 500000))
    tpb = m.ticks_per_beat

    def sec(tick):
        s = 0.0; last_t, last_tempo = 0, 500000
        for t, tempo in tempo_map:
            if t >= tick: break
            s += (t - last_t) * last_tempo / tpb / 1e6; last_t, last_tempo = t, tempo
        return s + (tick - last_t) * last_tempo / tpb / 1e6
    out = []
    for i, tr in enumerate(m.tracks):
        t = 0; on = {}; notes = []
        for msg in tr:
            t += msg.time
            if msg.type in ('note_on', 'note_off') and getattr(msg, 'channel', 0) != 9:
                k = (msg.channel, msg.note)
                if msg.type == 'note_on' and msg.velocity > 0:
                    if k in on: notes.append((msg.note, on[k], t))
                    on[k] = t
                elif k in on:
                    notes.append((msg.note, on.pop(k), t))
        if notes:
            out.append(dict(track=i, name=tr.name.strip('\x00 '), notes=[(n, sec(a), sec(b) - sec(a)) for n, a, b in notes]))
    return out


def fit(exp, got):
    """t_video ≈ a·t_midi + b; returns (a, b, oct)"""
    c = collections.Counter(g[0] - e[0] for g in got[:400] for e in exp[:400] if (g[0] - e[0]) % 12 == 0)
    oct_ = c.most_common(1)[0][0] if c else 0
    gp = collections.defaultdict(list)
    for g in got: gp[g[0] - oct_].append(g[1])
    def count(a, b, tol=0.1):
        n = 0
        for e in exp:
            t = a * e[1] + b
            if any(abs(x - t) < tol for x in gp.get(e[0], ())): n += 1
        return n
    best = (0, 1.0, 0.0)
    for a in [x / 1000 for x in range(800, 1251, 5)]:
        h = collections.Counter(round(g - a * e[1], 1) for e in exp[::3] for g in gp.get(e[0], ()))
        for b, _ in h.most_common(3):
            n = count(a, b, 0.15)
            if n > best[0]: best = (n, a, b)
    _, a, b = best
    for _ in range(3):                                            # Kleinste Quadrate über die Paare
        pairs = []
        for e in exp:
            t = a * e[1] + b; xs = [x for x in gp.get(e[0], ()) if abs(x - t) < 0.1]
            if xs: pairs.append((e[1], min(xs, key=lambda x: abs(x - t))))
        if len(pairs) < 10: break
        n = len(pairs); sx = sum(p[0] for p in pairs); sy = sum(p[1] for p in pairs)
        sxx = sum(p[0] ** 2 for p in pairs); sxy = sum(p[0] * p[1] for p in pairs)
        den = n * sxx - sx * sx
        if den == 0: break
        a = (n * sxy - sx * sy) / den; b = (sy - a * sx) / n
    return a, b, oct_


def dedupe(notes, tol=0.05):
    """[(m, s, d, …)] → doppelte Anschläge derselben Taste (Anfang ≤ tol auseinander) zu einem; ein Ton endet, wo der nächste derselben Taste beginnt"""
    by = collections.defaultdict(list)
    for n in notes: by[n[0]].append([n[1], n[1] + n[2], n[3:]])
    out = []
    for m, l in by.items():
        l.sort(key=lambda x: x[0]); res = []; cur = None
        for s, e, rest in l:
            if cur is not None and s - cur[0] <= tol: cur[1] = max(cur[1], e); continue
            if cur is not None: res.append(cur)
            cur = [s, e, rest]
        if cur is not None: res.append(cur)
        for i, (s, e, rest) in enumerate(res):
            if i + 1 < len(res) and res[i + 1][0] < e: e = res[i + 1][0]
            out.append((m, s, max(0.0, e - s)) + tuple(rest))
    return sorted(out, key=lambda x: x[1])


def _f1(exp, got, tol=0.1):
    if not exp or not got: return 0.0
    sh = S._best_shift([(m, s, d, 'R') for m, s, d in exp], got, 0)
    return 2 * len(S._match(exp, [(g[0], g[1] - sh, g[2]) for g in got], 0, 0, tol)) / (len(exp) + len(got))


def pick_tracks(trs, got):
    """Spurauswahl bei mehr als 4 Spuren: mit der besten Einzelspur anfangen, dann Spuren dazunehmen/weglassen, solange F1@100 steigt (Zeitachse aus allen Spuren)"""
    n = len(trs); allexp = sorted(((x[0], x[1], x[2], 'R') for t in trs for x in t['notes']), key=lambda x: x[1])
    a, b, o = fit(allexp, got)
    conv = lambda idx: dedupe([(m + o, a * s + b, a * d) for i in idx for m, s, d in trs[i]['notes']])
    cur = (max(range(n), key=lambda i: _f1(conv((i,)), got)),); sc = _f1(conv(cur), got); ch = True
    while ch:
        ch = False
        for i in range(n):
            c2 = tuple(sorted(set(cur) ^ {i}))
            if not c2: continue
            s2 = _f1(conv(c2), got)
            if s2 > sc + 1e-9: cur, sc, ch = c2, s2, True
    return cur


def evaluate(midi, got, tracks='auto'):
    trs = midi_tracks(midi); got = sorted(S._notes(got), key=lambda x: x[1])
    if tracks == 'all': combos = [tuple(range(len(trs)))]
    elif tracks != 'auto': combos = [tuple(int(x) for x in tracks.split(','))]
    else:
        idx = list(range(len(trs)))
        combos = [c for r in range(1, len(idx) + 1) for c in itertools.combinations(idx, r)] if len(idx) <= 4 else [pick_tracks(trs, got)]
    best = None
    for co in combos:
        exp = []
        lows = sorted(co, key=lambda i: sum(n[0] for n in trs[i]['notes']) / len(trs[i]['notes']))
        for i in co:
            h = 'L' if (len(co) > 1 and i == lows[0]) else 'R'
            exp += [(n, s, d, h) for n, s, d in trs[i]['notes']]
        exp.sort(key=lambda x: x[1])
        a, b, oct_ = fit(exp, got)
        exp = dedupe(exp)                                             # Schritt 5: doppelte Töne sind ein Anschlag
        truth = dict(notes=[dict(m=n + oct_, s=a * s + b, d=a * d, h=h) for n, s, d, h in exp], style=dict(one_color=False))
        r = S.score(truth, got)
        r.update(tracks=[trs[i]['name'] or str(trs[i]['track']) for i in co], tempo=round(a, 4), versatz=round(b, 3), midi_oct=oct_ // 12)
        if best is None or r.get('F1@100', 0) > best.get('F1@100', 0): best = r
    if best.get('F1@100', 0) < 0.6: best['warnung'] = 'MIDI passt kaum zum Video – vermutlich andere Fassung, aussortieren'
    return best


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('-')]
    tr = 'auto'
    if '--tracks' in sys.argv: tr = sys.argv[sys.argv.index('--tracks') + 1]; a = [x for x in a if x != tr]
    out = None
    if '--json' in sys.argv: out = sys.argv[sys.argv.index('--json') + 1]; a = [x for x in a if x != out]
    r = evaluate(a[0], json.load(open(a[1])), tr)
    if '-v' not in sys.argv: r = {k: v for k, v in r.items() if not k.startswith('_')}
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if out: json.dump(r, open(out, 'w'), ensure_ascii=False, indent=1)
