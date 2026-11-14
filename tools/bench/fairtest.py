"""v4.87: fairer zählen und verständlich anzeigen.
(1) Ein einzelner verpasster Ton im Nebel deckt den Takt NICHT auf und der Takt kann trotzdem geschafft sein (≥ 80 %).
(2) Gleichbleibende Verspätung (Bluetooth/Spieler) wird gemessen und ausgeglichen: wer 0,2 s zu spät spielt, trifft nach einem Durchgang trotzdem.
(3) Erster Durchgang eines Fensters ohne Nebel (Aufwärmen wie beim Video).
(4) Anzeigen: Takt-Leiste mit Nummern, Legende (sitzt / im Nebel / noch sichtbar / diesmal gehakt), aktueller Takt markiert; Ergebnis-Text „Im Nebel geschafft … · sitzt …“."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};KB.state='off';
 const LH=[47,43,50,45],SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0],SB=[66,69,71,74,76,74,71,69,71,69,66,64,66,69,71,0];
 const notes=[];let t=0;const ph=P=>{for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=P[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:q===2&&bar===3?0.95:0.45,hand:'R'})}t+=2}};
 for(const p of ['A','B','A','B'])ph(p==='A'?SA:SB);
 const it={id:'fa',type:'midi',title:'Fair',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);const gs=MEM.gs,fl=MEM.rec.fl,W0=(flowPrep(),MEM.wins[0]);
 const run=(late,skip)=>{const R=MEM.run;R.vt=gs[R.a].start-0.3;for(let j=R.a;j<=R.b;j++){R.vt=gs[j].start+late*R.speed;flowTick(R,0);if(!(skip&&skip(j)))for(const m of gs[j].mids)memPress(m,'kb')}R.vt=gs[R.b].end+1;flowTick(R,0);return R};
 o.legHome=!!$('#memHere .flLeg');o.nums=$('#memHere .flStrip').textContent.startsWith('12');
 /* (3) Aufwärmen */
 flowStart(0);o.warm=MEM.run.warm;o.fogStart=fl.st[W0.b0];o.nowMark=!!$('#memGoal .flStrip i.n');
 run(0);o.afterWarm=fl.st[W0.b0];
 /* (1) ein einzelner Ausrutscher in Takt 1 (Nebel) */
 const B1=MEM.bars[W0.b0];let single=-1;for(let j=B1.a;j<=B1.b;j++)if(gs[j].mids.size===1){single=j;break}
 flowStart(0);const R1=run(0,j=>j===single);o.singleResc=!!R1.resc[W0.b0];o.singleOk=R1.res[W0.b0].ok;o.okCount=fl.ok[W0.b0];o.msg=$('#memMsg').textContent;o.legRes=!!$('#memEv .flLeg');
 /* (2) Verspätung: 0,12 s zu spät → zählt; danach 0,22 s zu spät → zählt dank Ausgleich */
 fl.lat=0;flowStart(0);const R2=run(0.12);let h2=0,t2=0;for(const k in R2.res){h2+=R2.res[k].hit;t2+=R2.res[k].tot}o.hit12=h2/t2;o.lat=fl.lat;
 flowStart(0);const R3=run(0.22);let h3=0,t3=0;for(const k in R3.res){h3+=R3.res[k].hit;t3+=R3.res[k].tot}o.hit22=h3/t3;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'Legende + Nummern in der Übersicht':r['legHome'] and r['nums'],'Aufwärmen ohne Nebel, aktueller Takt markiert':r['warm'] and r['fogStart']==0 and r['nowMark'],
           'nach dem Aufwärmen Takt 1 (linke Hand) im Nebel':r['afterWarm']==1,
           'einzelner Ausrutscher: keine Hilfe, Takt geschafft':not r['singleResc'] and r['singleOk'],
           'Ergebnis verständlich + Legende':'sitzt' in r['msg'] and r['legRes'],
           '0,12 s zu spät zählt':r['hit12']>=0.95 and r['lat']>0.05,'0,22 s zu spät zählt nach Ausgleich':r['hit22']>=0.95,'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
