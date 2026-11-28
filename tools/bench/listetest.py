"""v5.55: Startseite und Songliste bleiben gefüllt, wenn ein Song beim „Ganzen Song“ steht (v5.53 warf beim App-Start einen Fehler → alle Listen leer).
usage: python3 tools/bench/listetest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""async (S)=>{window.toast=()=>{};const o={};
 const mk=(id,t)=>({id,type:'midi',title:t,artist:'x',data:b64FromBuf(writeMidi(S.fly_me.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))});
 const a=mk('fly_me','Fly Me'),b=mk('xmas','Christmas'),c=mk('neu','Neu');LIB=[a,b,c];save('kt_lib',LIB);MEMS={};
 openMem(a);const z=zlState();z.st=z.st.map(()=>4);z.bd={};for(const bb of zlBlocks(z.st.length))z.bd[zlBK(bb)]=1;z.song=0;memSaveAll();o.pick=zlPick(z); /* Fly Me: nächster Schritt = Ganzer Song */
 save('kt_mem',MEMS);return o}"""
CHECK = r"""()=>{renderHome();const o={};o.recent=$$('#recentList .song').length;o.songs=$$('#songList .song').length;
 o.fly=[...$$('#songList .song')].map(d=>d.textContent).find(t=>t.includes('Fly Me'))||'';o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 360, 'height': 753}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        try:
            await pg.evaluate(JS, SONGS)
            errs.clear(); await pg.reload(); await pg.wait_for_timeout(2500)  # App neu starten, wie beim Handy
            r = await pg.evaluate(CHECK)
        except Exception as e: r = {'crash': str(e)[:300]}
        await br.close()
    print(json.dumps(r, ensure_ascii=False)); print('Seitenfehler:', errs[:3])
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'Startseite zeigt die Songs': t(lambda: r['recent'] >= 3),
         'Songs-Tab zeigt alle Songs': t(lambda: r['songs'] >= 3),
         'Fly Me mit Stand „Am Lernen“': t(lambda: 'Am Lernen' in r['fly']),
         'Version 5.80': t(lambda: r['ver'].startswith('Version 5.80')),
         'keine JS-Fehler beim Start': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
