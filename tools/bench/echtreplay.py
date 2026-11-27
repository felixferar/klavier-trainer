"""Echte Diagnosen (diag.py-Ausgabe /tmp/echt/<id>/rec.json) mit einer App-Version nachspielen und gegen die Kanal-MIDI bewerten.
usage: APP=/pfad/index.html python3 tools/bench/echtreplay.py ROOT [ID...] [--json OUT]
ROOT: Ordner mit <id>/rec.json; MIDI-Zuordnung aus refs/echt/README.md. Große rec.json werden über einen lokalen http.server im Browser geladen."""
import sys, os, json, asyncio, subprocess, time, re
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import midiref as R
APP = 'file://' + os.path.abspath(os.environ.get('APP') or os.path.join(HERE, '..', '..', 'web', 'index.html'))
args = sys.argv[1:]; out = None
if '--json' in args: i = args.index('--json'); out = args[i + 1]; del args[i:i + 2]
root = os.path.abspath(args[0]); ids = args[1:]
ref = {}
for line in open(os.path.join(HERE, 'refs/echt/README.md')):
    m = re.match(r'\|\s*([\w.]+\.mid)\s*\|[^|]*\|\s*([\w-]{11})\s*\|', line)
    if m: ref[m.group(2)] = m.group(1)
ids = ids or sorted(d for d in os.listdir(root) if d in ref and os.path.exists(f'{root}/{d}/rec.json'))
JS = open(os.path.join(HERE, 'replay.js')).read()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8766', '--bind', '127.0.0.1'], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)


async def main():
    res = {}
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--allow-file-access-from-files', '--disable-web-security'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(300)
        for i in ids:
            got = await pg.evaluate('async ([u,js])=>{const rec=await (await fetch(u)).json();if(!rec.meta.scanDet){try{rec.meta.scanDet=(await (await fetch(u.replace("rec.json","meta.json"))).json()).scanDet}catch(e){}}return (eval(js))(rec)}', [f'http://127.0.0.1:8766/{i}/rec.json', JS])
            octfix = await pg.evaluate('SCAN.octFix||0'); hj = await pg.evaluate('[SCAN.headJ||0,SCAN.headR==null?null:+SCAN.headR.toFixed(2)]')
            r = R.evaluate(os.path.join(HERE, 'refs/echt', ref[i]), got)
            if os.environ.get('NOTES'): json.dump(got, open(f"{root}/{i}/{os.environ['NOTES']}.json", 'w'))  # NOTES=name: erkannte Noten je Video ablegen (für fehlerarten.py)
            res[i] = {k: v for k, v in r.items() if not k.startswith('_')}; res[i]['octFix'] = octfix
            print(f"{i} {ref[i][:30]:30} F1@50 {r.get('F1@50')} F1@100 {r.get('F1@100')} midi_oct {r.get('midi_oct')} octFix {octfix} kopf {hj} z {r.get('zerschnitten')} v {r.get('verschmolzen')} {r.get('warnung','')}", flush=True)
        if errs: print('PAGEERRORS', errs[:3])
        await br.close()
    if out: json.dump(res, open(out, 'w'), indent=1)
try: asyncio.run(main())
finally: srv.kill()
