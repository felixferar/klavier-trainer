"""„Sing – I'm Still Standing“ (Piano Monkeys, RgMoK2SUEyw) nachspielen – ZWEI Handy-Scans desselben Videos (26.11. v5.57 und 27.11. v5.63).
Prüft die Fehler, die Felix gemeldet hat: kurze Bb-Anschläge wurden zu langen Tönen verbunden, Anfang (YouTube-Feld „Weitere Videos“
über den Tasten: F5 fehlte, F#5 zerschnitten, D#5 kam 0,5 s zu spät) und Ende (Endkarte: Geistertöne G#3/F#3/D#3 von mehreren Sekunden).
v5.64: Der zweite Scan hat eine andere Lesezeile (Balken-Vorlauf 0,48 s statt 1,04 s) – eine Regel muss an BEIDEN bestehen, sonst repariert sie nur einen Zufall.
usage: python3 tools/bench/singtest.py web/index.html [DIAG.ktd.gz ...]
Die Diagnosen liegen in klavier-diagnose/diag/ (Standard: /home/claude/klavier-diagnose, sonst $KLAVIER_DIAG)."""
import sys, os, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
app = os.path.abspath(sys.argv[1])
root = os.environ.get('KLAVIER_DIAG', '/home/claude/klavier-diagnose')
srcs = sys.argv[2:] or [os.path.join(root, 'diag', f) for f in ('2026-11-26T21-29-47_RgMoK2SUEyw_done.ktd.gz', '2026-11-27T11-33-23_RgMoK2SUEyw_done.ktd.gz')]
srcs = [s for s in srcs if os.path.exists(s)]
if not srcs:
    print('SKIP – Diagnose nicht gefunden'); sys.exit(0)
sys.path.insert(0, HERE); os.environ['DIAG_APP'] = 'file://' + app
import diag
nm = lambda m: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B'][m % 12] + str(m // 12 - 1)
bad = 0
for src in srcs:
    out = tempfile.mkdtemp()
    subprocess.run([sys.executable, os.path.join(HERE, 'diag.py'), src, '--out', out], check=True, stdout=subprocess.DEVNULL)
    diag.replay(out)
    n = json.load(open(os.path.join(out, 'replay-notes.json')))
    t0 = min(x[1] for x in n if x[0] == 70)          # erster Akkord (Bb4) – die beiden Scans sind um ~0,07 s versetzt
    T = lambda x: x[1] - t0
    bb = [x for x in n if x[0] == 58]; longbb = [x for x in bb if x[2] > 0.3]
    first = sorted(nm(x[0]) for x in n if T(x) < 0.1 and x[0] > 60)
    second = sorted(nm(x[0]) for x in n if 1.4 < T(x) < 1.7 and x[0] > 60 and x[2] > 1.2)
    end = [x for x in n if T(x) > 85.05]
    c = {'Bb3 (linke Hand) kurz: höchstens 2 Töne > 0,3 s (echte längere Töne bei 76 s und 83 s)': len(longbb) <= 2 and len(bb) >= 100,
         'erster Akkord vollständig und gleichzeitig: Bb4 C#5 F5 (F5 lag unter „Weitere Videos“)': first == ['Bb4', 'C#5', 'F5'],
         'zweiter Akkord vollständig und gleichzeitig, jeder Ton am Stück: Bb4 D#5 F#5': second == ['Bb4', 'D#5', 'F#5'],
         'Ende: keine Geistertöne der Endkarte (nichts ≥ 1 s auf C#3–Bb3)': not any(49 <= x[0] <= 58 and x[2] >= 1 for x in end),
         'Ende: F3-Anschläge der linken Hand unter der Karte bleiben': sum(1 for x in end if x[0] == 53) >= 4}
    print('==', os.path.basename(src)[:19])
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k); bad += not v
sys.exit(1 if bad else 0)
