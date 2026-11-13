"""v4.80: Nach einem Durchgang ist der Knopf „Nächster Durchgang/Weiter“ sofort sichtbar und antippbar – ohne Scrollen (Handy quer und hoch)."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));window.playTone=()=>{};window.__instantEnd=true;
 const notes=[];let t=0;for(let i=0;i<20;i++){notes.push({m:60+(i%5)*2,start:t,dur:0.4,hand:'R'});if(i%3===0)notes.push({m:48,start:t,dur:0.4,hand:'L'});t+=0.6}
 const it={id:'wk',type:'midi',title:'Wk',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 memStart(0,false);const R=MEM.run;let n=0;
 /* mit ein paar Fehlern spielen, damit die Ergebnis-Karte groß ist */
 while(!R.done&&n++<200){R.vt=Math.max(R.vt,MEM.gs[R.pos].start);if(n%4===0)memPress(30,'kb');for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}
 {const x=document.createElement('div');x.style.height='500px';x.textContent='(lange Ergebnis-Karte)';$('#memEv').appendChild(x)}await w(400);const b=$('#memNext'),r=b.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,top=document.elementFromPoint(x,y);
 return {done:R.done,txt:b.textContent,bottom:r.bottom,top:r.top,h:innerHeight,hit:!!top&&(top===b||b.contains(top)),evShown:!$('#memEv').classList.contains('hidden')}}"""
async def run(p,vw,vh):
    br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=await br.new_page(viewport={'width':vw,'height':vh});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
    r=await pg.evaluate(JS);await br.close();r['errs']=errs;return r
async def main():
    async with async_playwright() as p:
        q=await run(p,753,360);h=await run(p,390,780)
        print(json.dumps({'quer':q,'hoch':h},ensure_ascii=False))
        vis=lambda r:r['done'] and r['evShown'] and r['top']>=0 and r['bottom']<=r['h'] and r['hit']
        c={'quer: Knopf sichtbar ohne Scrollen':vis(q),'hoch: Knopf sichtbar ohne Scrollen':vis(h),'keine Fehler':not q['errs'] and not h['errs']}
        print(c);print('OK' if all(c.values()) else 'FEHLER')
asyncio.run(main())
