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
        globals().__setitem__('_R',r);print(json.dumps(r,ensure_ascii=False));globals().__setitem__('_E',errs);print('pageerrors',errs);await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'erst ohne Titel':r['vorher']=='Song wird erstellt …','Titel wird nachgezeigt':r['nachher'].endswith('Spaeter Titel'),'Titel steht am Song':r['item']=='Spaeter Titel'}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
