"""Fast: replay recorded pixel rows (DIR/SEED.rec.json from run.py) through scanCore/finishScan and score against the gen.py truth.
usage: replay.py DIR [SEED...] [-v] [--json OUT.json]      (no SEED = every SEED.rec.json in DIR)
App file: env APP=/path/to/index.html (default: web/index.html of this repo) – so a test copy can be compared with the live version.
Prints the old numbers (recall/precision/extra, 70 ms, like run.py) AND the new ones from score.py (F1 at ±50 / ±100 ms)."""
import json, sys, asyncio, os, glob
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import score as S
src = open(os.path.join(HERE, 'run.py')).read(); exec('import collections\nTOL' + src.split('TOL', 1)[1].split('async def one')[0])
APP = 'file://' + os.path.abspath(os.environ.get('APP') or os.path.join(HERE, '..', '..', 'web', 'index.html'))
args = sys.argv[1:]; out_json = None
if '--json' in args: i = args.index('--json'); out_json = args[i + 1]; del args[i:i + 2]
verbose = '-v' in args; args = [a for a in args if a != '-v']
D = args[0]; seeds = args[1:] or sorted((os.path.basename(p)[:-9] for p in glob.glob(f'{D}/*.rec.json')), key=lambda s: int(s) if s.isdigit() else s)
JS = open(os.path.join(HERE, 'replay.js')).read()


async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(300)
        tot = dict(exp=0, hit=0, got=0, extra=0); rows = []; res = {}
        for s in seeds:
            truth = json.load(open(f'{D}/{s}.json')); rec = json.load(open(f'{D}/{s}.rec.json'))
            got = await pg.evaluate(JS, rec); r = score(truth, got); st = truth['style']; n = S.score(truth, got)
            for k in tot: tot[k] += r[k]
            rows.append(n); res[s] = dict(old={k: r[k] for k in ('recall', 'prec', 'extra', 'dur_bad', 'hands')}, new={k: v for k, v in n.items() if not k.startswith('_')}, notes=got)
            print(f"{s:>4} glow{int(st['glow'])} bk{int(st.get('bk_real', 0))} {','.join(st.get('stoer', [])) or '-':<22} recall {r['recall']} prec {r['prec']} extra {r['extra']} | F1@50 {n.get('F1@50')} F1@100 {n.get('F1@100')} onset_med {n.get('onset_med@100')} ms dur_med {n.get('dur_med@100')} ms oct {n.get('oct')}")
            if verbose: print('      miss', r['miss'], '\n      extra', r['extras'], '\n      dur', r['durl'])
        sm = S.summary(rows)
        print('TOTAL recall', round(tot['hit'] / max(1, tot['exp']), 3), 'precision', round(tot['hit'] / max(1, tot['got']), 3), 'extra', tot['extra'],
              '| F1@50', sm['50']['F1'], 'F1@100', sm['100']['F1'], '(P/R@50', sm['50']['P'], sm['50']['R'], ')')
        if errs: print('PAGEERRORS', errs[:3])
        if out_json: json.dump(dict(app=APP, total=dict(old=tot, new=sm), videos=res), open(out_json, 'w'))
        await br.close()
asyncio.run(main())
