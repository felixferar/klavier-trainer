"""v4.84: (1) Verbinden: sitzt ein neuer Teil, kommt gleich „Verbinden“ mit dem Teil davor (jeder 3. mit zwei Teilen davor), aus dem Kopf; gut → verbunden, nach 3 Versuchen geht es trotzdem weiter.
(2) Hände einzeln nur wenn es wirklich schwer ist: erst nach 2× „Nicht geschafft“ hintereinander; die andere Hand spielt die App; ändert keine Schritte.
(3) Weniger Zahlen: keine Fehlerzahl beim Spielen, Ergebnis nur Urteil + ein Satz + Farbleiste."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{window.MEM_FLOW=false; /* v4.86: prüft den bisherigen Schritte-Modus */const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};let tones=[];window.playTone=(m)=>tones.push(m);window.__instantEnd=true;KB.state='off';
 const LH=[47,43,50,45],P=[[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0],[66,69,71,74,76,74,71,69,71,69,66,64,66,69,71,0],[62,64,66,69,71,69,66,64,62,64,66,62,61,62,64,0]];
 const notes=[];let t=0;for(const P1 of P){for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=P1[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:q===2&&bar===3?0.95:0.45,hand:'R'})}t+=2}}
 const it={id:'kt',type:'midi',title:'Kette',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);const rs=MEM.rec.secs;o.n=MEM.secs.length;o.st=MEM.secs.map(([a,b])=>[+MEM.gs[a].start.toFixed(1),+MEM.gs[b].end.toFixed(1)]);if(o.n<3)return o;
 const play=(bad)=>{const R=MEM.run;let k=0;while(!R.done&&k++<400){R.vt=Math.max(R.vt??0,MEM.gs[R.pos].start);if(R.only)memOnlyTick(R);if(R.done)break;if(bad)for(let x=0;x<4;x++)memPress(30+x,'kb');for(const m of MEM.gs[R.pos].mids){if(R.only&&MEM.gs[R.pos].hands.get(m)!==R.only)continue;memPress(m,'kb')}}return R};
 /* (1) Teil 1 und 2 sitzen frisch → Verbinden 1–2 */
 rs.forEach(r=>{r.watched=true;r.runs=1});rs[0].passed=1;rs[0].box=1;rs[0].due=Date.now()+9e8;rs[1].passed=1;rs[1].box=1;rs[1].due=Date.now()+9e8;
 let nx=memPickNext(Date.now());o.nx1=nx&&nx.chain&&nx.i===1&&nx.k===0;memHome();o.go1=$('#memGo').textContent;
 $('#memGo').click();let R=MEM.run;o.title1=$('#memRunT').textContent;o.chainRun=R.chain&&R.a===MEM.secs[0][0]&&R.b===MEM.secs[1][1]&&R.lvl===4;o.prog=$('#memProg').textContent;
 play(false);o.chained1=!!rs[1].chained;o.msg1=$('#memMsg').textContent;o.next1=$('#memNext').textContent;
 /* jeder 3. mit zwei Teilen davor */
 rs[2].passed=1;rs[2].box=1;rs[2].due=Date.now()+9e8;nx=memPickNext(Date.now());o.nx2=nx&&nx.chain&&nx.i===2&&nx.k===0;
 /* 3× schief → geht trotzdem weiter */
 for(let k=0;k<3;k++){memGoTo(memPickNext(Date.now()));play(true)}o.skip=!!rs[2].chained;o.msgSkip=$('#memMsg').textContent;
 /* (3) Ergebnis-Karte kompakt */
 o.card=$('#memEv').textContent;o.cardNums=!!$('#memEv .nums');
 /* (2) Hände einzeln erst nach 2× Nicht geschafft */
 const r0=rs[0];r0.passed=0;r0.box=0;r0.lvl=2;r0.fe=1;r0.nf=0;KB.state='on';
 memStart(0,false);play(true);o.cat1=MEM.run.ev.cat;o.offer1=!$('#memHandR').classList.contains('hidden');
 memStart(0,false);play(true);o.offer2=!$('#memHandR').classList.contains('hidden')&&!$('#memHandL').classList.contains('hidden');o.noAuto=!MEM.autoT;o.tip=$('#memMsg').textContent.includes('einer Hand');
 const lvlB=[r0.lvl,r0.fe];$('#memHandR').click();R=MEM.run;o.only=R.only;o.titleH=$('#memRunT').textContent;tones=[];play(false);o.autoL=tones.length>0;o.handDone=R.done;o.nextH=$('#memNext').textContent;o.lvlSame=r0.lvl===lvlB[0]&&r0.fe===lvlB[1];
 memStop();KB.state='off';return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'3 Teile':r['n']==3,'nach Teil 2 kommt Verbinden 1–2':r['nx1'] and 'verbinden' in r['go1'],'Verbinden aus dem Kopf über beide Teile':r['chainRun'] and 'Verbinden: Abschnitt 1–2' in r['title1'],
           'gut gespielt → verbunden':r['chained1'] and 'Verbunden' in r['msg1'],'jeder 3. mit zwei Teilen davor':r['nx2'],'nach 3 Versuchen geht es weiter':r['skip'] and 'weiter' in r['msgSkip'],
           'keine Fehlerzahl beim Spielen':'Fehler' not in r['prog'],'Ergebnis ohne Zahlen':not r['cardNums'] and 'Punkte' not in r['card'],
           '1× Nicht geschafft: noch keine Hände-Hilfe':r['cat1']=='n' and not r['offer1'],'2× Nicht geschafft: Hände einzeln angeboten':r['offer2'] and r['tip'] and r['noAuto'],
           'nur rechte Hand – linke spielt die App':r['only']=='R' and 'nur rechte Hand' in r['titleH'] and r['autoL'] and r['handDone'],
           'danach wieder beide Hände, Schritte unverändert':r['nextH'].startswith('Jetzt mit beiden Händen') and r['lvlSame'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
