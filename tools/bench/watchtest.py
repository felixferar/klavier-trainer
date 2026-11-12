"""v4.66: Nach dem Anhören ist 'Jetzt spielen' sichtbar, und der erste Ton am Klavier startet das Nachspielen direkt"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{window.__mp||(window.__mp=memPress,memPress=function(m,src){const R=MEM.run;if(R&&!R.watch&&R.vt!=null&&R.lvl<=2&&!window.__strict)R.vt=Math.max(R.vt,MEM.gs[R.pos].start);return window.__mp(m,src)}); /* Test: wie Warten, bis der Balken unten ist */const notes=[];for(let i=0;i<30;i++)notes.push({m:60+(i%7)*2,start:i*0.5,dur:0.4,hand:'R'});
 const it={id:'w1',type:'midi',title:'W',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];window.playTone=()=>{};
 openMem(it);$('#memGo').click();let R=MEM.run;const o={watch:!!(R&&R.watch)};
 memPress(60,'kb');o.ignoredDuringWatch=MEM.run.watch===true&&MEM.run.errors===0;
 R.watchStart-=60000;memTick();const b=$('#memNext');o.btnTxt=b.textContent;o.btnVisible=b.getBoundingClientRect().height>0;
 const first=[...MEM.gs[MEM.secs[0][0]].mids][0];memPress(first,'kb');R=MEM.run;o.started=!R.watch&&R.lvl===1&&R.pos===R.a+1&&R.errors===0;
 o.btnHidden=getComputedStyle($('#memResBox')).display==='none';return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':400,'height':860});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        ok=r['watch'] and r['ignoredDuringWatch'] and r['btnTxt']=='Jetzt spielen' and r['btnVisible'] and r['started'] and r['btnHidden'] and not errs
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
