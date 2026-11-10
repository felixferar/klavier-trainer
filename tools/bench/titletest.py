"""Test convShowTitle: Titel im Umwandlungs-Panel, mit (n/N) in der Warteschlange, Rückfall ohne Titel (kein alter Titel bleibt stehen)."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(400)
        r=await pg.evaluate("""()=>{const o={},t=()=>document.getElementById('convTitle').textContent;
          convShowTitle({title:'Secret Garden – Piano'});o.einzeln=t();
          Q.on=true;Q.i=1;Q.n=3;convShowTitle({title:'Fly'});o.queue=t();Q.i=0;convShowTitle({title:'Erster'});o.queueErster=t();Q.i=1;
          convShowTitle({title:'YouTube-Video'});o.ohneTitel=t();
          convShowTitle(null);o.nullItem=t();Q.on=false;
          document.getElementById('yt').classList.add('convL');document.body.classList.add('convL');const el=document.getElementById('convTitle');o.querformat={sichtbar:getComputedStyle(el).display!=='none',nowrap:getComputedStyle(el).whiteSpace};
          return o}""")
        print(json.dumps(r,ensure_ascii=False)); print('pageerrors',errs); await br.close()
asyncio.run(main())
