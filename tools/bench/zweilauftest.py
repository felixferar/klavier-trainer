"""v5.12: Zwei Umwandlungen hintereinander (Warteschlange) auf derselben Seite, mit verschieden vielen Tasten.
Seit v5.06 war versehentlich Mess-Code (SCAN.flog aus instrument.py) in der App: er wurde nie zurückgesetzt → die zweite Umwandlung stürzte ab
(„Cannot read properties of undefined (reading 'push')“), und er sammelte am Handy je Taste und Bild 15 Werte.
usage: python3 tools/bench/zweilauftest.py $PWD/web/index.html"""
import sys, os, json, gzip, asyncio
from playwright.async_api import async_playwright
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'refs', 'hand')
JS = open(os.path.join(H, 'replay.js')).read()
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(1500)
        res = []
        for s in ('104', '123', '104'):
            rec = json.load(gzip.open(os.path.join(D, s + '.rec.json.gz')))
            r = await pg.evaluate("(rec)=>{try{const f=" + JS + ";const n=f(rec);return {n:n.length,flog:!!SCAN.flog}}catch(e){return {err:String(e)}}}", rec)
            res.append((s, r))
        await br.close()
    ok = all('err' not in r and r['n'] > 20 for s, r in res) and not any(r.get('flog') for s, r in res) and not errs
    for s, r in res: print(s, r)
    print('ALLES OK' if ok else 'FEHLGESCHLAGEN'); sys.exit(0 if ok else 1)
asyncio.run(main())
