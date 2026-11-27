"""Startet ALLE App-Tests und zählt ehrlich. Anlass (27.11.2026): Ein Sammellauf nur nach Exit-Code hat Tests als grün gezählt, die nie starteten,
kein Urteil hatten oder ihr „FEHLER“ nur ausgaben.
Einordnung je Test:  bestanden · GESCHEITERT · ohne Urteil (lief, sagt aber weder OK noch FEHLER) · übersprungen (SKIP, Eingabe fehlt) · veraltet (prüft etwas, das es nicht mehr gibt)
usage: python3 tools/bench/alle.py [APP.html] [-j 8] [--nur TEIL]        Ende mit 1, wenn etwas scheitert oder ohne Urteil bleibt."""
import sys, os, re, glob, subprocess, concurrent.futures as cf, time
H = os.path.dirname(os.path.abspath(__file__))
A = sys.argv[1:]
app = next((a for a in A if a.endswith('.html')), os.path.join(H, '..', '..', 'web', 'index.html'))
jobs = int(A[A.index('-j') + 1]) if '-j' in A else 8
nur = A[A.index('--nur') + 1] if '--nur' in A else ''
VERALTET = {'memtest2.py': 'prüft den Auswendig-Modus von v4.54 (MEM.rec.secs); seit dem Zeilen-Modus (20.11.) gibt es diese Funktionen nicht mehr'}
def lauf(f):
    n = os.path.basename(f)
    if n in VERALTET: return n, 'veraltet', VERALTET[n]
    try: p = subprocess.run([sys.executable, f, os.path.abspath(app)], capture_output=True, text=True, timeout=300); out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired: return n, 'GESCHEITERT', 'läuft länger als 300 s'
    L = [l.strip() for l in out.splitlines()]
    fehl = [l for l in L if l.startswith('FEHL ') or l == 'FEHLER' or l.endswith('ERGEBNIS FEHLER') or l == 'FEHLGESCHLAGEN' or re.search(r'^\w+ FEHLER\b', l)]
    if rc != 0 or fehl: return n, 'GESCHEITERT', (fehl[0] if fehl else next((l for l in reversed(L) if l), 'Exit-Code %d' % rc))[:140]
    if any(l.startswith('SKIP') for l in L): return n, 'übersprungen', next(l for l in L if l.startswith('SKIP'))[:140]
    if any(l == 'OK' or l.startswith('OK   ') or l.startswith('OK ') or 'ERGEBNIS OK' in l or l.startswith('ZIEL erreicht') or l == 'ALLES OK' or re.fullmatch(r'\w+ OK', l) for l in L): return n, 'bestanden', ''
    return n, 'ohne Urteil', (next((l for l in reversed(L) if l), ''))[:140]
tests = sorted(f for f in glob.glob(os.path.join(H, '*test*.py')) if nur in os.path.basename(f))
t0 = time.time(); res = []
with cf.ThreadPoolExecutor(jobs) as ex:
    for r in ex.map(lauf, tests): res.append(r)
by = {}
for n, k, info in res: by.setdefault(k, []).append((n, info))
for k in ['GESCHEITERT', 'ohne Urteil', 'übersprungen', 'veraltet']:
    for n, info in by.get(k, []): print(f'{k:13} {n:24} {info}')
print(f"\n{len(res)} Tests in {time.time() - t0:.0f} s: " + ' · '.join(f"{len(by.get(k, []))} {k}" for k in ['bestanden', 'GESCHEITERT', 'ohne Urteil', 'übersprungen', 'veraltet']))
sys.exit(1 if by.get('GESCHEITERT') or by.get('ohne Urteil') else 0)
