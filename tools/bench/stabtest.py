"""v4.55 Stabilitaet: Fab im Player weg, Zurueck im Auswendig-Modus, Hintergrund kostet keine Fehler, Speicher-voll-Warnung, CMP-Autosave, Klavier getrennt pausiert"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS="""async()=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));
 const notes=[];let t=0;for(let i=0;i<30;i++){notes.push({m:60+(i%7)*2,start:t,dur:0.4,hand:'R'});t+=0.5;if(i%10===9)t+=0.6}
 const it={id:'s1',type:'midi',title:'S',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 // 1 Fab im Player
 document.body.classList.add('inplayer');const f=$('#shotFab');o.fabHidden=getComputedStyle(f).display==='none';document.body.classList.remove('inplayer');
 // 2 appBack im Auswendig-Modus
 openMem(it);o.curMem=navStack[navStack.length-1]==='mem';const r=appBack();o.backTrue=r===true;o.leftMem=navStack[navStack.length-1]!=='mem';
 // 3 Hintergrund (v5.04): Durchgang endet, zählt nicht, Übersicht
 openMem(it);awStart({k:0,mode:'head'});const R=MEM.run;
 const realVis=Object.getOwnPropertyDescriptor(Document.prototype,'visibilityState');
 const setVis=v=>{Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>v});document.dispatchEvent(new Event('visibilitychange'))};
 setVis('hidden');setVis('visible');o.shifted=!MEM.run&&!$('#memHome').classList.contains('hidden');o.noHint=R.hints===0;
 // 5 Speicher voll
 const oldSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new Error('quota')};
 let n=0;const ot=window.toast;window.toast=(m)=>{n++;o.warnMsg=m};
 const a=saveW('kt_x',1),b=saveW('kt_x',2);o.saveFalse=a===false&&b===false;o.warnOnce=n===1;
 Storage.prototype.setItem=oldSet;window.toast=ot;
 // 7 Klavier getrennt
 /* v5.04: Klavier getrennt → Durchgang endet, zählt nicht */
 KB.state='on';memStop();awStart({k:0,mode:'head'});const R2=MEM.run;o.kbWasSet=R2.kb0===true;KB.state='off';awTick(R2,0.05);o.paused=!MEM.run;o.resumed=!$('#memHome').classList.contains('hidden');KB.state='off';
 memStop();
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r),errs)
        keys=['fabHidden','curMem','backTrue','leftMem','shifted','noHint','saveFalse','warnOnce','kbWasSet','paused','resumed']
        ok=all(r.get(k) for k in keys) and not errs
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
