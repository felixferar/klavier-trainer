"""v4.82: Flüssiger lernen.
1) Aus dem Kopf: hängt man, erscheint nach 2 s der nächste Anschlag als Balken (vorher erst nach 5 s, nur leuchtende Tasten). Verblassen: Hilfe nach 1,5 s.
2) Verblassen hat 4 Etappen (100/70/40/15 %) – ⭐ nach 6 guten Durchgängen, nicht schon nach 5.
3) Mit Klavier geht es nach dem Durchgang von selbst weiter: nach 3 s oder sofort mit der nächsten Taste; „Pause“ hält an."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{window.MEM_V8=false;window.FLOW_FIND=false;FL.start=0.8; /* v4.92: Nebel-Logik ohne Kennenlern-Runde prüfen */ const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};window.playTone=()=>{};window.__instantEnd=true;
 KB.state='on';KB.name='GZUT-MIDI';
 const notes=[];let t=0;for(let i=0;i<40;i++){notes.push({m:60+(i%5)*2,start:t,dur:0.4,hand:'R'});t+=0.6}
 const it={id:'fl',type:'midi',title:'Fl',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 const px=()=>{const cv=$('#memCv'),k=cv.height/cv.clientHeight,h=Math.floor((MEM.hn-6)*k);const d=cv.getContext('2d').getImageData(0,0,cv.width,Math.max(1,h)).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>20)n++;return n};
 /* 1) Aus dem Kopf, 2,1 s gehangen */
 const r0=MEM.rec.secs[0];r0.lvl=3;r0.fe=3;memStart(0,false);let R=MEM.run;R.vt=MEM.gs[R.a].start;R.gStart=memNow()-500;memDraw();o.px05=px();
 R.gStart=memNow()-2100;memDraw();o.px21=px();o.hint21=memHintOn();memStop();
 /* Verblassen: Hilfe nach 1,5 s */
 r0.lvl=2;r0.fe=3;memStart(0,false);R=MEM.run;R.arrAt=memNow()-1600;o.hintV=memHintOn();memStop();
 /* 2) Etappen */
 const A=(rec,cat)=>memApply(rec,{ev:{cat,score:80,hints:0},errors:0,hints:0},1e12);const r={lvl:1,box:0,due:0,runs:0,passed:0};let n=0;while(!(r.passed>0)&&n<10){A(r,'f');n++}o.runsToStar=n;o.fades=MEM_FADE;
 /* 3) Automatisch weiter */
 const play=()=>{const R=MEM.run;let k=0;while(!R.done&&k++<200){R.vt=Math.max(R.vt,MEM.gs[R.pos].start);for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}};
 r0.lvl=2;r0.fe=0;r0.passed=0;r0.box=0;memStart(0,false);const R1=MEM.run;play();await w(200);o.btn=$('#memNext').textContent;o.hold=!$('#memHold').classList.contains('hidden');
 await w(3300);o.autoStarted=MEM.run!==R1&&!MEM.run.done;
 /* Taste startet sofort */
 const R2=MEM.run;play();await w(900);memPress(MEM.gs[MEM.secs[0][0]].mids.values().next().value,'kb');o.keyStarted=MEM.run!==R2&&!MEM.run.done;o.keyCounted=MEM.run.pos>MEM.run.a||MEM.run.hit.size>0;
 /* Pause hält an */
 const R3=MEM.run;play();await w(300);$('#memHold').click();await w(3500);o.paused=MEM.run===R3&&R3.done;
 /* ohne Klavier: nichts automatisch */
 KB.state='off';const R4=(memStart(0,false),MEM.run);play();await w(3500);o.noKb=MEM.run===R4;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'Aus dem Kopf: nach 0,5 s noch nichts':r['px05']<50,'Aus dem Kopf: nach 2 s Balken':r['hint21'] and r['px21']>200,
           'Verblassen: Hilfe nach 1,5 s':r['hintV'],'4 Etappen, ⭐ nach 6':r['fades']==[1,0.7,0.4,0.15] and r['runsToStar']==6,
           'Countdown + Pause-Knopf':'(3)' in r['btn'] and r['hold'],'nach 3 s von selbst weiter':r['autoStarted'],
           'Taste startet sofort und zählt':r['keyStarted'] and r['keyCounted'],'Pause hält an':r['paused'],'ohne Klavier kein Automatik':r['noKb'],
           'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
