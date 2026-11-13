"""v4.54 Etappe 1: Noten sichtbar je Stufe, Ansehen mit Klang, Knopf 'Noten pruefen', Rueckkehr laedt die Noten neu"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS="""async()=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));
 const notes=[];let t=0;for(let i=0;i<30;i++){notes.push({m:60+(i%7)*2,start:t,dur:0.4,hand:'R'});t+=0.5;if(i%10===9)t+=0.6}
 const geo={x:[0.15,0.85],kw:0.0166,yT:0.479,yA:0.53,yB:0.632,yC:0.446,sh:0,kx:Array.from({length:61},(_,i)=>0.15+i*0.0115),ar:2.3531};
 const it={id:'m2',type:'midi',title:'T2',artist:'x',data:b64FromBuf(writeMidi(notes)),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:0,first:2,fps:25,keys:[36,96],geo}};LIB=[it];
 window.openYT=()=>{cmpMode(!!CMP);show('yt')};let tones=[];const pt=playTone;window.playTone=(m)=>{tones.push(m)};
 openMem(it);o.checkVisible=!$('#memCheck').classList.contains('hidden');
 MEM.rec.secs.forEach(r=>r.watched=true);
 const blue=(lo,hi)=>{const cv=$('#memCv'),x=cv.getContext('2d');const d=x.getImageData(0,0,cv.width,Math.round(MEM.hn*(cv.height/cv.getBoundingClientRect().height))-2);let n=0;for(let i=0;i<d.data.length;i+=4){if(d.data[i+2]>180&&d.data[i]<140)n++}return n};
 memStart(0,false);memDraw();o.bars1=blue();
 MEM.run.lvl=2;memDraw();o.bars2=blue();
 MEM.run.lvl=3;MEM.rec.secs[0].sk=85;delete MEM.run._fade;memDraw(); /* v4.79: bei 85 % Sicherheit sind in Stufe 3 alle Noten verblasst */ o.bars3=blue();
 // Ansehen mit Klang: neuer Abschnitt ohne watched
 memStop();MEM.rec.secs[0].watched=false;MEM.rec.secs[0].runs=0;tones=[];memStart(0,false);const R=MEM.run;o.watchMode=!!R.watch;
 R.watchStart-=1200;memTick();o.tonesEarly=tones.length;memDraw();o.watchBars=blue();
 R.watchStart-=30000;memTick();o.tonesAll=tones.length;o.done=R.watchDone;
 memStop();memHome();
 // Noten pruefen -> Vergleichsansicht, zurueck -> Noten neu geladen
 $('#memCheck').click();o.cmpOpen=!!CMP&&CMP.it.id==='m2';
 // Noten aendern (wie Speichern in der Vergleichsansicht), dann zurueck
 const n2=notes.slice();n2.push({m:72,start:t+1,dur:0.4,hand:'R'});LIB[0]=Object.assign({},LIB[0],{data:b64FromBuf(writeMidi(n2))});
 const before=MEM.gs.length;navStack.push('yt');back();await wait(50);o.reloaded=MEM.gs.length!==before||MEM.gs.length===31;o.memShown=!$('#mem').classList.contains('hidden');
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r),errs)
        ok=(r['checkVisible'] and r['bars1']>=r['bars2']>0 and r['bars3']==0 and r['watchMode'] and 0<r['tonesEarly']<r['tonesAll'] and r['watchBars']>0 and r['done'] and r['cmpOpen'] and r['reloaded'] and r['memShown'] and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
