"""v5.55: Farben ≠ Hände erkennen (finishCore). Spielt Handy-Aufnahmen aus dem Diagnose-Archiv nach und prüft SCAN.handFix.
- Runaway (KISHAKEYS, 4C0UA95-yko): Rot = tiefes UND hohes E → Tonhöhen-Trennung (split gesetzt), tiefes E = links, hohes E = rechts.
- Die 15 Referenzvideos mit Kanal-MIDI (refs/echt auf Branch v5.42-zerschnitten): nie umschalten.
usage: python3 tools/bench/farbhandtest.py $PWD/web/index.html [PFAD/klavier-diagnose]"""
import sys, os, glob, json, asyncio, subprocess, time, re
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
APP = sys.argv[1]; DIAG = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/klavier-diagnose'
REFS = ['KyYaCtLsAAk', 'ADiGiK75FMM', 'xOj7uhi3w80', '5OwchavoI0s', 'GBdqm09XWbQ', 'PufbzTlHfWY', '8MmOMEcZrz4', 'sBnPmRPAyBI', 'V7dy35ovtj0',
        '_3MNRYZWpmU', 'Kg8zA6sM85U', 'pR19Z4_jpLI', '3Sp4dW-JdJE', 'SdijhNhiq3s', '0iqbVD-VW4c']
IDS = ['4C0UA95-yko'] + REFS; OUT = '/tmp/farbhand'; os.makedirs(OUT, exist_ok=True)
for i in IDS:
    fs = sorted(glob.glob(os.path.join(DIAG, 'diag', f'*_{i}_done.ktd.gz')))
    if fs and not os.path.exists(f'{OUT}/{i}/rec.json'):
        subprocess.run([sys.executable, os.path.join(HERE, 'diag.py'), fs[-1], '--out', f'{OUT}/{i}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
JS = open(os.path.join(HERE, 'replay.js')).read()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8768', '--bind', '127.0.0.1'], cwd=OUT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
async def main():
    res = {}
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--allow-file-access-from-files', '--disable-web-security'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + APP); await pg.wait_for_timeout(300)
        for i in IDS:
            if not os.path.exists(f'{OUT}/{i}/rec.json'): continue
            got = await pg.evaluate('async ([u,js])=>{const rec=await (await fetch(u)).json();if(!rec.meta.scanDet){try{rec.meta.scanDet=(await (await fetch(u.replace("rec.json","meta.json"))).json()).scanDet}catch(e){}}return (eval(js))(rec)}', [f'http://127.0.0.1:8768/{i}/rec.json', JS])
            hf = await pg.evaluate('SCAN.handFix')
            res[i] = {'split': hf and hf.get('split'), 'e40': sorted({g[3] for g in got if g[0] == 40}), 'e88': sorted({g[3] for g in got if g[0] == 88})}
            print(i, res[i], flush=True)
        await br.close()
    return res, errs
try: r, errs = asyncio.run(main())
finally: srv.kill()
def t(f):
    try: return bool(f())
    except Exception: return False
c = {'Runaway: Farben ≠ Hände erkannt → Tonhöhen-Trennung': t(lambda: r['4C0UA95-yko']['split'] is not None),
     'Runaway: tiefes E links, hohes E rechts': t(lambda: r['4C0UA95-yko']['e40'] == ['L'] and r['4C0UA95-yko']['e88'] == ['R']),
     'Referenzvideos: nie umgeschaltet': t(lambda: len([i for i in REFS if i in r]) >= 10 and all(r[i]['split'] is None for i in REFS if i in r)),
     'keine JS-Fehler': not errs}
for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
sys.exit(0 if all(c.values()) else 1)
