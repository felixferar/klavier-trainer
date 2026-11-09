"""Fast: replay recorded pixel rows through the current scanCore/finishScan and score. usage: replay.py DIR SEED..."""
import json, sys, asyncio
sys.argv_saved=list(sys.argv)
from playwright.async_api import async_playwright
import collections, os
HERE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(HERE,'run.py')).read();exec('TOL'+src.split('TOL',1)[1].split('async def one')[0])
APP='file://'+os.path.abspath(os.path.join(HERE,'..','..','web','index.html'))
D=sys.argv[1]; seeds=sys.argv[2:]; verbose='-v' in seeds; seeds=[s for s in seeds if s!='-v']
JS=open(os.path.join(HERE,'replay.js')).read()
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();await pg.goto(APP);await pg.wait_for_timeout(300)
        tot=dict(exp=0,hit=0,got=0,extra=0)
        for s in seeds:
            truth=json.load(open(f'{D}/{s}.json'));rec=json.load(open(f'{D}/{s}.rec.json'))
            got=await pg.evaluate(JS,rec);r=score(truth,got);st=truth['style']
            for k in tot: tot[k]+=r[k]
            print(f"{s:>4} glow{int(st['glow'])} res{st['lowres']} lit{st['lit_part']} recall {r['recall']} prec {r['prec']} extra {r['extra']} durbad {r['dur_bad']} hands {r['hands']} serr {r['start_err']}")
            if verbose: print('      miss',r['miss'],'\\n      extra',r['extras'],'\\n      dur',r['durl'])
        print('TOTAL recall',round(tot['hit']/max(1,tot['exp']),3),'precision',round(tot['hit']/max(1,tot['got']),3),'extra',tot['extra'])
        await br.close()
asyncio.run(main())
