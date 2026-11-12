"""v4.70: Akkord mit leicht versetzt erkanntem Ton (golden hour: 54/57/61 bei 1,000 s, 64 bei 1,118 s) – alle vier zusammen gespielt zählt richtig"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};window.__instantEnd=true;
 const notes=[{m:54,start:1,dur:.36,hand:'L'},{m:57,start:1,dur:.26,hand:'L'},{m:61,start:1,dur:.32,hand:'R'},{m:64,start:1.118,dur:.23,hand:'R'}];let t=2;for(let i=0;i<10;i++){notes.push({m:60+(i%5),start:t,dur:.3,hand:'R'});t+=.5}
 const it={id:'vg',type:'midi',title:'Vg',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 o.groups=MEM.gs.slice(0,2).map(g=>[...g.mids]);memStart(0,false);const R=MEM.run;R.vt=MEM.gs[R.a].start;
 for(const m of [64,54,61,57])memPress(m,'kb');o.pos=R.pos-R.a;o.errors=R.errors;
 // falscher Ton bleibt falsch
 memPress(70,'kb');o.err2=R.errors;return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r),errs)
        ok=r['pos']==2 and r['errors']==0 and r['err2']==1 and not errs
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
