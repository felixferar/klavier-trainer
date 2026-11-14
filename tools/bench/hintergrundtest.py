"""v5.01: App im Hintergrund → laufender Auswendig-Durchgang endet sofort (zählt nicht, kein Protokolleintrag), geplante Töne (Vorspielen/Start-Anker)
werden gestrichen, kein automatisches Weiter; beim Zurückkommen Übersicht, nichts startet von selbst."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};let tones=[];window.playTone=(m)=>tones.push(m);KB.state='off';
 const SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,72];const notes=[];let t=0;for(let r=0;r<2;r++)for(let bar=0;bar<4;bar++){notes.push({m:47+bar,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:SA[bar*4+q]+r,start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 const it={id:'hg',type:'midi',title:'HG',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);memHome();MEM.rec.v8.ch[0].st=1;MEM.rec.v8.ch[0].box=2;MEM.rec.v8.ch[0].due=Date.now()-1;memHome();
 let vis='visible';Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>vis});
 $('#memGo').click();let R=MEM.run;o.mode=R.mode;memPress(21,'kb'); /* vorspielen + neu → Töne sind geplant */
 const box0=MEM.rec.v8.ch[0].box,log0=(load('kt_v8log')||[]).length;
 vis='hidden';document.dispatchEvent(new Event('visibilitychange'));tones=[];
 o.stopped=MEM.run===null;o.home=!$('#memHome').classList.contains('hidden');
 await new Promise(r=>setTimeout(r,2500));o.silent=tones.length===0;o.noAuto=MEM.run===null&&!MEM.autoT;
 o.noCount=MEM.rec.v8.ch[0].box===box0&&(load('kt_v8log')||[]).length===log0;
 vis='visible';document.dispatchEvent(new Event('visibilitychange'));await new Promise(r=>setTimeout(r,300));o.back=MEM.run===null&&$('#memGo').textContent.length>0;
 /* nach einem fertigen Versuch: Auto-Weiter läuft nicht im Hintergrund */
 $('#memGo').click();R=MEM.run;R.anchorUntil=0;R.previewUntil=0;let g=0;while(R.pos<=R.b&&g++<200){flowTick(R,5);for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}flowTick(R,5);flowTick(R,5);MEM.autoT=setInterval(()=>{},1000);
 vis='hidden';document.dispatchEvent(new Event('visibilitychange'));o.autoOff=!MEM.autoT&&MEM.run===null;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'im Hintergrund: Durchgang endet, Übersicht':r['mode']=='review' and r['stopped'] and r['home'],
           'geplante Töne gestrichen':r['silent'],'kein automatisches Weiter':r['noAuto'] and r['autoOff'],
           'zählt nicht (kein Kasten-Abzug, kein Protokoll)':r['noCount'],'beim Zurückkommen startet nichts':r['back'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
