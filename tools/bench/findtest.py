"""v4.92: „Erst finden, dann fließen, dann Nebel“.
Prüft: neuer Abschnitt startet im Warte-Modus (≤ 3 Takte / 9 s, das Lied bleibt am Anschlag stehen, nächste Tasten leuchten vor, falsche Taste bringt nichts
weiter, bei Akkorden reichen die meisten Töne); einmal geschafft = gefunden; danach Fluss ab 50 % ohne Nebel, Tempo wächst 50 → 65 → 80 bei sauberen
Durchgängen, Nebel erst ab 80 %; viele Fehler → langsamer; im Fluss leuchten die nächsten sichtbaren Tasten vor; alter Stand wird übernommen."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};KB.state='off';
 const LH=[47,43,50,45],SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0];const notes=[];let t=0;
 for(let r=0;r<3;r++)for(let bar=0;bar<4;bar++){if(bar===0){for(const m of [48,52,55])notes.push({m,start:t,dur:1.9,hand:'L'})}else notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});
   for(let q=0;q<4;q++){const m=SA[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2}
 const it={id:'fd',type:'midi',title:'Find',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);memHome();const gs=MEM.gs,fl=MEM.rec.fl,W0=MEM.wins[0];
 o.home=$('#memHere').textContent;o.tempo0=fl.tempo;
 flowStart(0);let R=MEM.run;o.find=!!R.find;o.chunkBars=R.k1-R.k0+1;o.chunkDur=MEM.bars[R.k1].t1-MEM.bars[R.k0].t0;o.spd=R.speed;
 flowTick(R,30);o.waited=Math.abs(R.vt-gs[R.a].start)<1e-6&&R.pos===R.a;flowDraw();o.pre=[...R.pre].sort().join()==[...gs[R.a].mids].sort().join();o.msg=$('#memMsg').textContent;
 const G0=gs[R.a];o.g0=G0.mids.size;memPress(30,'kb');o.wrongStay=R.pos===R.a;const ms=[...G0.mids],need=Math.ceil(ms.length*0.6);for(let q=0;q<need-1;q++)memPress(ms[q],'kb');o.oneNotEnough=R.pos===R.a;memPress(ms[need-1],'kb');o.most=R.pos===R.a+1&&need<ms.length;
 /* nach einem gefundenen Anschlag kommt der nächste schnell heran, auch bei langer Pause */
 {const nx=gs[R.pos],exp=(nx.start-R.vt)/R.speed;let tt=0;while(R.vt<nx.start-1e-6&&tt<5){flowTick(R,0.016);tt+=0.016}o.glideRatio=tt/exp}
 /* Rest des Stücks finden */
 const findAll=()=>{let R=MEM.run;let g=0;while(R.pos<=R.b&&g++<500){flowTick(R,5);for(const m of gs[R.pos].mids)memPress(m,'kb')}flowTick(R,5);flowTick(R,5)};
 findAll();o.seen1=fl.seen.slice(R.k0,R.k1+1).every(x=>x===1);o.msgF=$('#memMsg').textContent;
 let g=0;while(flowFindChunk(0)&&g++<20){flowStart(0);findAll()}o.allSeen=fl.seen.slice(W0.b0,W0.b1+1).every(x=>x===1);o.msgAll=$('#memMsg').textContent;
 const perfect=(skip)=>{const R=MEM.run;R.vt=gs[R.a].start-0.3;for(let j=R.a;j<=R.b;j++){R.vt=gs[j].start;flowTick(R,0);if(!skip)for(const m of gs[j].mids)memPress(m,'kb')}R.vt=gs[R.b].end+1;flowTick(R,0);return R};
 flowStart(0);R=MEM.run;o.flow=!R.find&&R.warm;o.sp1=R.speed;
 R.vt=gs[R.a].start-0.3;flowTick(R,0);flowDraw();o.preFlow=R.pre.size>0&&[...R.pre].every(m=>gs[R.a].mids.has(m));
 perfect();o.t2=fl.tempo;o.fog2=fl.st.slice(W0.b0,W0.b1+1).every(x=>x===0);o.msg2=$('#memMsg').textContent;
 flowStart(0);perfect();o.t3=fl.tempo;o.fog3=fl.st.slice(W0.b0,W0.b1+1).every(x=>x===0);
 flowStart(0);o.sp4=MEM.run.speed;perfect();o.fog4=fl.st.slice(W0.b0,W0.b1+1).some(x=>x>0);
 flowStart(0);perfect(true);o.t5=fl.tempo;
 /* Übernahme: alter Stand ohne „gefunden“ */
 delete fl.seen;fl.tempo=0.8;fl.st[W0.b0]=2;flowPrep();o.migSeen=MEM.rec.fl.seen[W0.b0]===1&&MEM.rec.fl.seen[W0.b0+1]===(fl.st[W0.b0+1]>=1?1:0);o.migT=MEM.rec.fl.tempo;
 /* lange Pause im Stück (3 s) und langer Schlusston */
 {const n2=[60,62,64,65].map((m,i)=>({m,start:i*0.5,dur:0.4,hand:'R'})).concat([{m:67,start:4.5,dur:0.4,hand:'R'},{m:69,start:5,dur:0.4,hand:'R'},{m:72,start:5.5,dur:3,hand:'R'}]);const it2={id:'fd2',type:'midi',title:'Pause',artist:'x',data:b64FromBuf(writeMidi(n2))};LIB.push(it2);memStop();openMem(it2);memHome();flowPrep();
  flowStart(0);const R2=MEM.run,g2=MEM.gs;for(let j=0;j<4;j++){flowTick(R2,30);memPress([...g2[R2.pos].mids][0],'kb')}let tt=0;while(R2.vt<g2[4].start-1e-6&&tt<9){flowTick(R2,0.016);tt+=0.016}o.longGap=tt;
  for(let j=4;j<7;j++){flowTick(R2,30);memPress([...g2[R2.pos].mids][0],'kb')}tt=0;while(!R2.done&&tt<9){flowTick(R2,0.016);tt+=0.016}o.endT=tt}
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'Übersicht kündigt „Tasten finden“ an, Start 50 %':'Tasten finden' in r['home'] and r['tempo0']==0.5,
           'neuer Abschnitt: Warte-Modus, kurz':r['find'] and r['chunkBars']<=3 and r['chunkDur']<=9.01 and r['spd']<=0.6,
           'Lied wartet am Anschlag':r['waited'],'nächste Tasten leuchten vor':r['pre'] and 'blauen Tasten' in r['msg'],
           'falsche Taste bringt nicht weiter':r['wrongStay'],'Akkord: die meisten Töne reichen':r['g0']>=3 and r['oneNotEnough'] and r['most'],
           'gleichmäßiges Tempo zwischen Anschlägen':0.9<=r['glideRatio']<=1.15,'lange Pause auf ≤ 1 s gekürzt':0.9<=r['longGap']<=1.1,'Schluss nicht im Schneckentempo':r['endT']<=0.9,'einmal geschafft = gefunden':r['seen1'] and 'Gefunden' in r['msgF'],'alles gefunden → Fluss':r['allSeen'] and 'Fluss' in r['msgAll'],
           'Fluss ab 50 %, ohne Nebel':r['flow'] and r['sp1']==0.5,'im Fluss leuchten die nächsten Tasten vor':r['preFlow'],
           'sauber → 65 %, noch kein Nebel':r['t2']==0.65 and r['fog2'] and '65 %' in r['msg2'],'sauber → 80 %, noch kein Nebel':r['t3']==0.8 and r['fog3'],
           'ab 80 % kommt der Nebel':r['sp4']==0.8 and r['fog4'],'viele Fehler → langsamer':r['t5']==0.7,
           'alter Stand übernommen, Tempo neu langsam':r['migSeen'] and r['migT']==0.5,'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
