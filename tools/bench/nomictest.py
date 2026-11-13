"""v4.78: Die App fragt nie mehr von selbst nach dem Mikrofon (Funktion ist entfernt). Lernmodus ohne Klavier → kein Mikrofon-Zugriff, Bildschirmtasten bleiben."""
import sys,asyncio,json
from playwright.async_api import async_playwright
INIT=r"""(()=>{window.__gum=0;const md=navigator.mediaDevices||{};
 md.getUserMedia=()=>{window.__gum++;return Promise.reject(new Error('nein'))};try{Object.defineProperty(navigator,'mediaDevices',{value:md,configurable:true})}catch(e){}})()"""
JS=r"""async()=>{const o={};window.playTone=()=>{};const W=ms=>new Promise(r=>setTimeout(r,ms));await W(800);const toasts=[];const t0=window.toast;window.toast=(m,d)=>{toasts.push(m);try{t0(m,d)}catch(e){}};
 const notes=[];let t=0;for(let i=0;i<8;i++){notes.push({m:60+i,start:t,dur:.4,hand:'R'});t+=.5}
 const it={id:'nm',type:'midi',title:'N',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 openItemPlay(it);await W(400);setMode(true);await W(200);setPlaying(true);await W(500);setPlaying(false);
 S.score=true;await ensureInput();await W(200);
 o.gum=window.__gum;o.toasts=toasts;return o}"""
async def main(url):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx=await b.new_context(viewport={'width':1280,'height':800});await ctx.add_init_script(INIT)
        pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+url);await pg.wait_for_timeout(600)
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'kein Mikrofon-Zugriff':r['gum']==0,'keine Mikrofon-Meldung':not any('Mikrofon' in t for t in r['toasts']),'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await b.close()
asyncio.run(main(sys.argv[1]))
