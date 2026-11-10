"""v4.29: Titel erst spaeter verfuegbar -> convTitlePoll zeigt ihn nach."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500)
        r=await pg.evaluate("""async()=>{const o={};const it={title:'YouTube-Video'};ytAuto=true;let t0=Date.now();
          ytp={getVideoData:()=>({title:Date.now()-t0>1200?'Spaeter Titel':''})};
          Q.on=false;convShowTitle(it);o.vorher=document.querySelector('#convTitle').textContent;convTitlePoll(it);
          await new Promise(r=>setTimeout(r,2500));o.nachher=document.querySelector('#convTitle').textContent;o.item=it.title;
          ytAuto=false;return o}""")
        print(json.dumps(r,ensure_ascii=False));print('pageerrors',errs);await br.close()
asyncio.run(main())
