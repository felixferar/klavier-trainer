"""v4.96: Abschnitte nach Menge statt nach Takt + Song-Karte.
Prüft: kein Mini-Abschnitt (Last < 3, z. B. „nur zwei Töne halten“) außer ganz am Ende; jeder Abschnitt ≤ 10 s; jede Phrasenpause wird als Schnitt genutzt;
wiederholte Stellen gelten als bekannt (weniger Last); alter Lernstand (Takt-Abschnitte) wird durch neuen ersetzt; Übersicht zeigt eine Song-Karte
(ein Feld je Abschnitt, Breite nach Dauer, der nächste markiert, Legende); Durchgang nennt die Zeit des Abschnitts."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};KB.state='off';
 const PA=[72,74,76,77,79,77,76,74,72,71,72,74,76,74,72,0],PB=[69,71,72,74,76,74,72,71,69,67,69,71,72,71,69,0];const notes=[];let t=0;const rests=[];
 const phrase=P=>{for(let bar=0;bar<4;bar++){notes.push({m:48+bar*2,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++){const m=P[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2}rests.push(t);t+=0.8};
 phrase(PA);/* Takt nur mit zwei gehaltenen Tönen */notes.push({m:55,start:t,dur:1.9,hand:'L'},{m:64,start:t,dur:1.9,hand:'R'});t+=2;phrase(PB);phrase(PA);phrase(PB);
 const it={id:'sc',type:'midi',title:'Schnitt',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 localStorage.setItem('kt_mem',JSON.stringify({}));openMem(it);
 /* alter v8-Stand (Takt-Abschnitte, ohne cv) */
 MEM.rec.v8={n:MEM.bars.length,ch:MEM.bars.map(()=>({box:2,due:0,st:1,fails:0,last:0,reps:0,relearn:0}))};memSaveAll();MEM.v8c=null;memHome();
 const gs=MEM.gs,C=v8Chunks(),ld=v8Load(gs);o.n=C.length;o.oldBars=MEM.bars.length;
 o.small=C.slice(0,-1).filter(c=>c.load<3).length;o.maxDur=Math.max(...C.map(c=>c.t1-c.t0));
 const cutT=C.slice(0,-1).map(c=>gs[c.b+1].start);o.atRest=cutT.filter(x=>rests.some(r=>Math.abs(x-(r+0.8))<0.15)).length;o.cuts=cutT.length;o.nRests=rests.length;
 const half=gs.findIndex(G=>G.start>=rests[2]-0.01);o.knownLater=ld.slice(half).filter(x=>x<1).length/ld.slice(half).length;o.knownEarly=ld.slice(0,8).filter(x=>x<1).length;
 o.reset=MEM.rec.v8.cv===2&&MEM.rec.v8.ch.length===C.length&&MEM.rec.v8.ch.every(c=>c.box===0);
 const map=document.querySelectorAll('#memSum .v8map i');o.mapN=map.length;o.outlined=[...map].filter(e=>e.style.outline.includes('solid')).length;o.leg=$('#memSum').textContent;
 const w0=parseFloat(map[0].style.flexGrow),wl=C.map(c=>c.t1-c.t0);o.prop=Math.abs(w0-Math.max(0.6,wl[0]))<0.01;
 $('#memGo').click();o.runT=$('#memRunT').textContent;o.rng=[MEM.run.a,MEM.run.b,C[0].a,C[0].b];
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'kein Mini-Abschnitt (außer am Ende)':r['small']==0,'jeder Abschnitt ≤ 10 s':r['maxDur']<=10.01,
           'jede Phrasenpause ist ein Schnitt':r['atRest']==r['nRests']-1,
           'Wiederholungen gelten als bekannt':r['knownEarly']==0 and r['knownLater']>=0.5,
           'weniger Abschnitte als Takte':r['n']<r['oldBars'],
           'alter Takt-Lernstand ersetzt':r['reset'],
           'Song-Karte: ein Feld je Abschnitt, nach Dauer, nächster markiert, Legende':r['mapN']==r['n'] and r['outlined']==1 and r['prop'] and 'gelernt' in r['leg'] and 'Nächstes' in r['leg'],
           'Durchgang nutzt den Abschnitt und nennt die Zeit':r['rng'][0]==r['rng'][2] and r['rng'][1]==r['rng'][3] and '0:00' in r['runT'],
           'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
