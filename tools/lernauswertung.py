"""Lernprotokolle auswerten – die Kennzahlen für die Testwoche.

Liest alle Lernprotokolle (diag/learn/*.json aus felixferar/klavier-diagnose), fasst doppelte
Einträge zusammen und schreibt einen kurzen Bericht in Markdown:

  1. Überblick: Tage, Übungszeit, Durchgänge, Anteil gelungener Durchgänge (Ziel ≈ 80 %)
  2. Je Tag: Durchgänge, gelungen, Minuten, Abbrüche, Hilfen
  3. Je Zeile: Durchgänge, gelungen, Minuten, längste Fehlserie, wo es hängt
  4. Verhalten: Vorspielen, Hilfe (B), Abbrüche mit dem tiefsten A, falsche Töne je Durchgang
  5. Ampel: was die Zahlen für den Ablauf bedeuten

Funktioniert mit jeder App-Version: unbekannte Felder werden ignoriert, Schritte (mode) werden
so gezählt, wie sie im Protokoll stehen.

usage: python3 tools/lernauswertung.py [PFAD/klavier-diagnose] [--seit 2026-11-21] [--song m1794740922940] [--version 5.36]
"""
import argparse, glob, json, os, datetime as dt
from collections import defaultdict, Counter

TZ = dt.timezone(dt.timedelta(hours=1))  # Europe/Berlin (Winterzeit)


def lade(pfad):
    E, titel = {}, {}
    for f in sorted(glob.glob(os.path.join(pfad, 'diag', 'learn', '*.json'))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        snap = d.get('snap') or {}
        if snap.get('song'):
            titel[snap['song']] = snap.get('title') or snap['song']
        for e in d.get('entries', []):
            e = dict(e, _app=d.get('v'))
            E[(e.get('t'), e.get('song'), e.get('mode'), e.get('k'))] = e
    return sorted(E.values(), key=lambda e: e.get('t') or 0), titel


def zeit(e):
    return dt.datetime.fromtimestamp((e.get('t') or 0) / 1000, TZ)


def proz(a, b):
    return f'{round(100 * a / b)} %' if b else '–'


def bericht(es, titel):
    out = []
    p = out.append
    if not es:
        return 'Keine Durchgänge im gewählten Zeitraum.'
    tage = sorted({zeit(e).date() for e in es})
    minuten = sum(e.get('dur', 0) for e in es) / 60000
    ok = sum(1 for e in es if e.get('ok'))
    songs = Counter(e.get('song') for e in es)
    p('# Lernauswertung')
    p(f"Zeitraum {tage[0]:%d.%m.} – {tage[-1]:%d.%m.%Y} · App {', '.join(sorted({str(e.get('_app')) for e in es}))}")
    p('')
    p('## Überblick')
    p(f'- **{len(tage)} Tage**, **{minuten:.0f} Minuten** gespielt, **{len(es)} Durchgänge**')
    p(f'- **Gelungen: {ok} von {len(es)} ({proz(ok, len(es))})** – Ziel sind etwa 80 %')
    for s, n in songs.most_common():
        p(f'- {titel.get(s, s)}: {n} Durchgänge')
    p('')
    p('## Je Tag')
    p('| Tag | Durchgänge | gelungen | Minuten | Abbrüche (A) | Hilfen (B) | Vorspielen |')
    p('|---|---|---|---|---|---|---|')
    for t in tage:
        x = [e for e in es if zeit(e).date() == t]
        p(f"| {'Mo Di Mi Do Fr Sa So'.split()[t.weekday()]} {t:%d.%m.} | {len(x)} | {proz(sum(1 for e in x if e.get('ok')), len(x))} | "
          f"{sum(e.get('dur', 0) for e in x) / 60000:.0f} | {sum(1 for e in x if e.get('abort'))} | "
          f"{sum(e.get('hints', 0) for e in x)} | {sum(e.get('demos', 0) for e in x)} |")
    p('')
    p('## Je Zeile')
    p('| Song · Zeile | Durchgänge | gelungen | Minuten | längste Fehlserie | Schritte (gelungen/gesamt) |')
    p('|---|---|---|---|---|---|')
    je = defaultdict(list)
    for e in es:
        je[(e.get('song'), e.get('k'))].append(e)
    schwer = []
    for (s, k), x in sorted(je.items(), key=lambda kv: (str(kv[0][0]), kv[0][1] if kv[0][1] is not None else -1)):
        serie = best = 0
        for e in x:
            serie = 0 if e.get('ok') else serie + 1
            best = max(best, serie)
        sch = Counter(e.get('mode') for e in x)
        sok = Counter(e.get('mode') for e in x if e.get('ok'))
        g = sum(1 for e in x if e.get('ok'))
        p(f"| {titel.get(s, s)[:24]} · {(k or 0) + 1} | {len(x)} | {proz(g, len(x))} | "
          f"{sum(e.get('dur', 0) for e in x) / 60000:.1f} | {best} | "
          + ', '.join(f'{m} {sok[m]}/{n}' for m, n in sch.most_common()) + ' |')
        if best >= 5:
            schwer.append(((k or 0) + 1, best))
    p('')
    p('## Verhalten')
    ab = [e for e in es if e.get('abort')]
    vor = sum(1 for e in ab if not e.get('waits'))
    p(f'- Abbrüche mit dem tiefsten A: {len(ab)} ({proz(len(ab), len(es))}), davon {vor} vor dem ersten Griff (nur zuhören)')
    p(f"- Hilfe mit B: {sum(e.get('hints', 0) for e in es)}× · Vorspielen: {sum(e.get('demos', 0) for e in es)}×")
    fw = [e.get('wrong', 0) for e in es if e.get('n')]
    p(f"- Falsche Töne je Durchgang: Mittel {sum(fw) / max(1, len(fw)):.1f}, je Griff {sum(fw) / max(1, sum(e.get('n', 0) for e in es)):.2f}")
    p('')
    p('## Ampel')
    q = ok / len(es)
    p(('🟢' if q >= 0.7 else '🟡' if q >= 0.5 else '🔴') + f' Gelungene Durchgänge {proz(ok, len(es))} '
      '(≥ 70 % gut, 50–70 % zu schwer eingestellt, < 50 % deutlich zu schwer)')
    p(('🟢 keine Zeile mit 5+ Fehlversuchen hintereinander' if not schwer else
       '🔴 Fehlserien ab 5: ' + ', '.join(f'Zeile {k} ({b}×)' for k, b in schwer)))
    p(('🟢' if len(ab) / len(es) < 0.2 else '🟡' if len(ab) / len(es) < 0.4 else '🔴')
      + f' Abbrüche {proz(len(ab), len(es))} (viele Abbrüche = die Stufe ist zu schwer oder unklar)')
    return '\n'.join(out)


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('pfad', nargs='?', default='/home/claude/klavier-diagnose')
    a.add_argument('--seit')
    a.add_argument('--song')
    a.add_argument('--version')
    o = a.parse_args()
    es, titel = lade(o.pfad)
    if o.seit:
        ab = dt.datetime.fromisoformat(o.seit).replace(tzinfo=TZ)
        es = [e for e in es if zeit(e) >= ab]
    if o.song:
        es = [e for e in es if e.get('song') == o.song]
    if o.version:
        es = [e for e in es if str(e.get('_app', '')).startswith(o.version)]
    print(bericht(es, titel))
