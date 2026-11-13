"""v4.66: Auswendig nutzt dieselben Noten wie Abspielen/Üben (Tastatur-Falten, Hände), Akkord-Versatz aus dem Video bleibt ein Anschlag, Anhören mit echten Tonlängen und Handfarben, Lernstand bleibt bei alter Gruppierung"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=(m,d,v)=>{tones.push([m,d])};let tones=[];
 // Akkord mit Video-Versatz: 54 @0, 57 @+41 ms, 61/64 @+82 ms (wie golden hour 6.595/6.636/6.677); danach Töne im Abstand 0,13 s; ein Ton außerhalb einer 61er-Tastatur (C1=24)
 const notes=[{m:54,start:1.000,dur:0.36,hand:'L'},{m:57,start:1.041,dur:0.3,hand:'R'},{m:61,start:1.082,dur:0.3,hand:'R'},{m:64,start:1.082,dur:0.3,hand:'R'}];
 let t=1.5;for(let i=0;i<20;i++){notes.push({m:60+(i%5),start:t,dur:i===3?1.2:0.12,hand:'R'});t+=0.13}notes.push({m:24,start:t+0.5,dur:0.5,hand:'L'});
 const it={id:'s1',type:'midi',title:'S',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 // alter Lernstand mit alter Signatur
 let n0=0,g0=-9;for(const x of songForItem(it).notes.slice().sort((a,b)=>a.start-b.start)){if(x.start-g0>=0.06){n0++;g0=x.start}}
 S.layout=61;
 openMem(it);o.firstGroup=[...MEM.gs[0].mids].sort((a,b)=>a-b);o.fastSplit=MEM.gs.length;
 const secs=memSplit(MEM.gs).length;MEMS['s1']={sig:n0+':'+secs,secs:memSplit(MEM.gs).map(()=>({lvl:3,box:0,due:0,runs:5,passed:0}))};openMem(it);o.kept=MEMS['s1'].secs[0].lvl===2&&MEMS['s1'].secs[0].fe===2; /* v4.81: alter Stand Stufe 3 → Verblassen 30 % */
 // gleiche Noten wie Abspielen
 openSong(songForItem(it),it.id);const play=song.notes.map(n=>n.midi).sort((a,b)=>a-b).join();back();openMem(it);const mem=MEM.song.notes.map(n=>n.midi).sort((a,b)=>a-b).join();o.sameAsPlay=play===mem;o.folded=!MEM.song.notes.some(n=>n.midi===24);
 // Anhören: echte Längen
 memStop();MEM.rec.secs[0].runs=0;MEM.rec.secs[0].watched=false;memStart(0,false);const R=MEM.run;o.watch=!!R.watch;R.watchStart-=60000;memTick();
 o.durs=tones.map(x=>Math.round(x[1]*100)/100);o.tones=tones.length;o.longTone=tones.some(x=>x[1]>0.5)&&tones.some(x=>x[1]<0.2);o.secNotes=memSecNotes(R).length;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':400,'height':860});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r),errs)
        ok=(r['firstGroup']==[54,57,61,64] and r['fastSplit']>=21 and r['kept'] and r['sameAsPlay'] and r['folded'] and r['watch'] and r['tones']==r['secNotes']>0 and r['longTone'] and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
