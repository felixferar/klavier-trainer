"""v4.70: Durchgang endet erst, wenn der letzte Ton zu Ende ist; richtige Taste leuchtet grün, falsche rot; Klaviatur nur so breit wie der Abschnitt (≥ 12 weiße Tasten)"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};window.playTone=()=>{};
 const notes=[];let t=0;for(let i=0;i<9;i++){notes.push({m:64+(i%3),start:t,dur:i===8?1.5:0.3,hand:'R'});t+=0.4}
 const it={id:'en',type:'midi',title:'En',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 memStart(0,false);const R=MEM.run;o.range=[R.lo,R.hi];let wc=0;for(let m=R.lo;m<=R.hi;m++)if(!isBlack(m))wc++;o.white=wc;o.songRange=[MEM.lo,MEM.hi];
 while(R.pos<=R.b){R.vt=Math.max(R.vt,MEM.gs[R.pos].start);for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}
 o.endingAfterLast=R.ending===true&&!R.done;o.msg=$('#memMsg').textContent;await w(700);o.stillHolding=!R.done;await w(1300);o.doneAfter=R.done;
 // Farben: richtig grün, falsch rot
 memStop();memStart(0,false);const R2=MEM.run;R2.vt=MEM.gs[R2.a].start;const m0=[...MEM.gs[R2.a].mids][0];
 const cols={};const orig=drawKeys;window.drawKeys=function(c,lo,hi,w,h,fn,l){cols.ok=fn(m0,false);cols.bad=fn(m0+5,false);return orig(c,lo,hi,w,h,fn,l)};
 memPress(m0,'kb');memPress(m0+5,'kb');memDraw();window.drawKeys=orig;o.cols=cols;return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'wartet am Ende':r['endingAfterLast'] and r['stillHolding'] and 'Halten' in r['msg'],'dann fertig':r['doneAfter'],
           'Bereich klein':r['white']>=12 and r['white']<=14,'gruen':r['cols']['ok']=='#3BB273','rot':r['cols']['bad']=='#E5484D','keine Fehler':not errs}
        print(c);ok=all(c.values());print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
