"""v5.03: Hand über der Tastatur – Geisternoten. Eine Hand (Hautfarbe) über den schwarzen Tasten färbt sie blass ein; ohne eigenen Balken
wurden daraus Noten. Neu: In Videos mit lesbaren Balken fällt eine Note OHNE eigenen Balken weg, wenn sie blass ist (Sättigung < 0,6× der Noten mit
Balken derselben Tastenart) oder dunkel (Sättigung×Helligkeit < 0,6×), während eine Taste ≤ 2 Halbtöne daneben kräftig leuchtet (Überstrahlen).

Aufnahmen (Prüfstand, gen.py STOER=1): refs/hand/123 = Hand über der Tastatur, refs/hand/104 = ohne Hand (darf sich nicht verschlechtern).
usage: python3 tools/bench/handtest.py $PWD/web/index.html"""
import sys, os, json, gzip, asyncio
from playwright.async_api import async_playwright
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'refs', 'hand')
sys.path.insert(0, H)
exec('import collections\nTOL' + open(os.path.join(H, 'run.py')).read().split('TOL', 1)[1].split('async def one')[0])  # score()
JS = open(os.path.join(H, 'replay.js')).read()

async def main():
    res = {}
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(1500)
        for s in ('123', '104'):
            rec = json.load(gzip.open(os.path.join(D, s + '.rec.json.gz')))
            got = await pg.evaluate(JS, rec)
            res[s] = score(json.load(open(os.path.join(D, s + '.json'))), got)
        await br.close()
    ok = True
    def chk(name, cond, info):
        nonlocal ok; ok &= bool(cond); print(('OK  ' if cond else 'FEHLER ') + name, info)
    a, b = res['123'], res['104']
    chk('Hand: Zusatznoten ≤ 3', a['extra'] <= 3, f"extra {a['extra']} precision {a['prec']}")
    chk('Hand: Treffer ≥ 0,97', a['recall'] >= 0.97, f"recall {a['recall']}")
    chk('ohne Hand: Treffer ≥ 0,97, keine Zusatznoten', b['recall'] >= 0.97 and b['extra'] == 0, f"recall {b['recall']} extra {b['extra']}")
    chk('keine Seitenfehler', not errs, errs[:2])
    print('ALLES OK' if ok else 'FEHLGESCHLAGEN'); sys.exit(0 if ok else 1)
asyncio.run(main())
