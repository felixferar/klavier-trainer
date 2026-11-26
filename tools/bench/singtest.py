"""v5.58: „Sing – I'm Still Standing“ (Piano Monkeys, RgMoK2SUEyw, Handy-Scan 26.11.2026) nachspielen.
Prüft die drei Fehler, die Felix gemeldet hat: kurze Bb-Anschläge wurden zu langen Tönen verbunden, Anfang (YouTube-Feld „Weitere Videos“
über den Tasten: F5 fehlte, F#5 zerschnitten) und Ende (Endkarte: Geistertöne G#3/F#3/D#3 von mehreren Sekunden).
usage: python3 tools/bench/singtest.py web/index.html [DIAG.ktd.gz]
Die Diagnose liegt in klavier-diagnose/diag/2026-11-26T21-29-47_RgMoK2SUEyw_done.ktd.gz (Standard: /home/claude/klavier-diagnose, sonst $KLAVIER_DIAG)."""
import sys, os, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
app = os.path.abspath(sys.argv[1])
src = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get('KLAVIER_DIAG', '/home/claude/klavier-diagnose'), 'diag/2026-11-26T21-29-47_RgMoK2SUEyw_done.ktd.gz')
if not os.path.exists(src):
    print('SKIP – Diagnose nicht gefunden:', src); sys.exit(0)
out = tempfile.mkdtemp()
subprocess.run([sys.executable, os.path.join(HERE, 'diag.py'), src, '--out', out], check=True, stdout=subprocess.DEVNULL)
sys.path.insert(0, HERE); os.environ['DIAG_APP'] = 'file://' + app
import diag; diag.replay(out)
n = json.load(open(os.path.join(out, 'replay-notes.json')))
nm = lambda m: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B'][m % 12] + str(m // 12 - 1)
bb = [x for x in n if x[0] == 58]; longbb = [x for x in bb if x[2] > 0.3]
first = sorted(nm(x[0]) for x in n if x[1] < 1.0 and x[0] > 60)
f5 = [x for x in n if x[0] == 78 and 2.2 < x[1] < 4]
end = [x for x in n if x[1] > 85.9]
c = {'Bb3 (linke Hand) kurz: höchstens 2 Töne > 0,3 s (echte längere Töne bei 76 s und 83 s)': len(longbb) <= 2 and len(bb) >= 100,
     'erster Akkord vollständig: Bb4 C#5 F5 (F5 lag unter „Weitere Videos“)': first == ['Bb4', 'C#5', 'F5'],
     'F#5 im zweiten Akkord ein Ton, nicht zerschnitten': len(f5) == 1 and f5[0][2] > 1.2,
     'Ende: keine Geistertöne der Endkarte (nichts ≥ 1 s auf C#3–Bb3)': not any(49 <= x[0] <= 58 and x[2] >= 1 for x in end),
     'Ende: F3-Anschläge der linken Hand unter der Karte bleiben': sum(1 for x in end if x[0] == 53) >= 4}
for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
sys.exit(0 if all(c.values()) else 1)
