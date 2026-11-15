"""v5.04: Regeln des neuen Auswendig-Modus einzeln (ersetzt die Tests der alten Modi Stufen/Nebel/v8).
Finden · Aus dem Kopf (Anker bis gespielt, keine Zeit-Hilfe, Hilfe auf Wunsch / nach 3 Fehlern bis gespielt, Suchen zählt nicht, 2 Hilfen → Finden, 6 Fehler → vorspielen + neu,
tiefstes A) · Vorgriff (versetzt erkannter Akkordton) · Ende erst nach dem letzten Ton · Im Puls (Einzählen, Metronom, Anlauf, 75 → 90 → 100 %, verpasst = nochmal)
· Kästen (10 min → morgen → 3 Tage → 14 Tage, gelernt/sitzt, Fehlschlag → Kasten zurück + auffrischen) · Verbinden · Taste nach dem Versuch = weiter
· gleiche Noten wie beim Abspielen (Falten, Hände, Akkord-Versatz) · Hintergrund beendet den Durchgang · keine Zeitgeber im Lernablauf.
usage: python3 tools/bench/awregeltest.py $PWD/web/index.html"""
import sys, asyncio, json
from playwright.async_api import async_playwright
JS = r"""()=>{window.AW_NOLOOP=true;let tones=[];window.playTone=(m,d,v,g)=>tones.push({m,g});KB.state='off';const o={};
 window.toast=()=>{};let timers=0;const sT=window.setTimeout,sI=window.setInterval;window.setTimeout=(f,t)=>{timers++;return sT(f,t)};window.setInterval=(f,t)=>{timers++;return sI(f,t)};
 const notes=[];let t=0;for(let bar=0;bar<8;bar++){notes.push({m:48,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:60+((bar+q)%5)*2,start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 /* Akkord mit versetzt erkanntem Ton (golden hour) am Anfang von Takt 3: 54/57/61 bei 4,000 s + 64 bei 4,118 s */
 notes.push({m:54,start:4.0,dur:0.4,hand:'L'},{m:57,start:4.0,dur:0.4,hand:'L'},{m:66,start:4.118,dur:0.3,hand:'R'});
 const it={id:'regel',type:'midi',title:'Regel',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);const T0=Date.UTC(2026,10,16,9);window.AW_NOW=T0;openMem(it);
 const gs=MEM.gs,v=()=>MEM.rec.v9,ch=k=>v().ch[k],tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs[j].mids)memPress(m,'kb')};
 const runWait=(f)=>{const R=MEM.run;let g=0;while(!R.done&&g++<200){if(R.pos<=R.b){f?f(R):0;play(R.pos)}tick(0.1)}return R};
 o.n=MEM.C.length;o.c0=[MEM.C[0].a,MEM.C[0].b];
 /* gleiche Noten wie beim Abspielen */
 o.vorgriffGrp=gs.some(G=>G.mids.has(54)&&G.mids.has(57)&&!G.mids.has(66))&&gs.some(G=>G.mids.has(66));
 /* 1 Finden */
 let p=awPick();o.p1=p.mode;timers=0;awNext();let R=MEM.run;o.findScreen=!R.dark;memPress(30,'kb');o.findWrong=R.wrong;runWait();o.findSt=ch(0).st;o.findMsg=$('#memMsg').textContent;
 /* Ende erst nach dem letzten Ton: */
 awNext();R=MEM.run;o.p2=R.mode;o.anchor0=R.anchor&&(awDraw(),R.drawState==='anker');tick(30);o.anchorStays=R.anchor;memPress(30,'kb');o.anchorSearch=R.wrong;
 play(R.pos);o.anchorGone=!R.anchor&&(awDraw(),R.drawState==='dunkel');const h0=R.hints;tones=[];tick(25);o.thinkNoHelp=R.hints===h0&&R.show==null&&!tones.length;
 memPress(22,'kb');o.bShow=R.show===R.pos&&R.hints===1;tick(20);o.showStays=R.show===R.pos;memPress(30,'kb');memPress(31,'kb');o.showSearch=R.wrong===0;const sp=R.pos;play(R.pos);o.showGone=R.show==null&&R.pos===sp+1;
 for(let i=0;i<2;i++){memPress(30,'kb');o['w'+i]=R.show}memPress(30,'kb');o.auto3=R.show===R.pos&&R.hints===2;
 runWait();o.twoHints=[ch(0).st,R.ok];o.backMsg=$('#memMsg').textContent;
 /* zurück zu Finden, dann sauber aus dem Kopf (mit Vorgriff-Akkord im Abschnitt?) */
 awNext();runWait();awNext();R=MEM.run;o.p3=R.mode;runWait();o.headOk=[R.ok,ch(0).st];
 /* tiefstes A und 6 Fehler */
 awNext();R=MEM.run;o.p4=[R.mode,Math.round(R.speed*100)];const Rp=R;
 /* 2 Puls: Einzählen + Metronom */
 const cnt=R.clicks.filter(x=>x.cnt).length,inPlay=R.clicks.filter(x=>!x.cnt).length;o.clicks=[cnt,inPlay,+(R.beat.p).toFixed(2),R.beat.ok];
 const pulse=(R,skip,lat)=>{let q=R.a,g=0;while(!R.done&&g++<20000&&MEM.run===R){awTick(R,1/120);while(q<=R.b&&R.vt>=gs[q].start+(lat||0.03)*R.speed){if(!(skip&&skip.includes(q)))play(q);q++}}return R};
 tones=[];pulse(R);o.pulsTones=tones.filter(x=>x.m>=96).length;o.puls1=[R.ok,ch(0).tp];
 awNext();R=MEM.run;o.p5=[R.mode,Math.round(R.speed*100)];pulse(R,[R.a+2]);o.pulsMiss=[R.ok,R.miss,ch(0).tp,ch(0).box];
 awNext();pulse(MEM.run);awNext();R=MEM.run;o.p6=Math.round(R.speed*100);pulse(R);o.box1=[ch(0).box,Math.round((ch(0).due-window.AW_NOW)/6e4)];
 /* Abschnitt 2 dazwischen: Finden, Kopf, Puls – mit Anlauf (Abschnitt 1 klingt leise) */
 awNext();R=MEM.run;o.p7=[R.mode,R.k];runWait();awNext();runWait();awNext();R=MEM.run;o.lead=R.acc.length>0&&R.acc.every(n=>n.start<gs[R.a].start);tones=[];pulse(R);o.leadSoft=tones.some(x=>x.g===AW.accGain);
 awNext();pulse(MEM.run);awNext();pulse(MEM.run);o.k1box=ch(1).box;
 /* Verbinden 1–2 */
 const pl=awPick();o.link=[pl.mode,pl.s,pl.e];awNext();R=MEM.run;o.linkSp=Math.round(R.speed*100);pulse(R);o.linkOk=[R.ok,!!v().ln[0]];
 /* Kästen: nach 10 min kalt */
 window.AW_NOW+=11*60e3;const pr=awPick();o.rev=[pr.mode,pr.k];awNext();R=MEM.run;o.revSp=Math.round(R.speed*100);pulse(R);o.box2=[ch(0).box,Math.round((ch(0).due-window.AW_NOW)/36e5)];
 window.AW_NOW=ch(0).due+1;awNext();while(MEM.run.k!==0){pulse(MEM.run);awNext()}pulse(MEM.run);o.box3=[ch(0).box,Math.round((ch(0).due-window.AW_NOW)/36e5),$('#memMsg').textContent];
 window.AW_NOW=ch(0).due+1;awNext();while(MEM.run.k!==0){pulse(MEM.run);awNext()}pulse(MEM.run);o.box4=[ch(0).box,Math.round((ch(0).due-window.AW_NOW)/864e5),$('#memMsg').textContent];
 /* Fehlschlag beim Check → Kasten zurück, aus dem Kopf, dann Puls 100 % */
 window.AW_NOW=ch(0).due+1;awNext();while(MEM.run.k!==0){pulse(MEM.run);awNext()}R=MEM.run;pulse(R,[R.a,R.a+1]);o.fail=[R.ok,ch(0).box,ch(0).relearn];
 awNext();R=MEM.run;o.re1=[R.mode,R.k];runWait();awNext();R=MEM.run;o.re2=[R.mode,Math.round(R.speed*100)];pulse(R);o.re3=[ch(0).relearn,ch(0).box,Math.round((ch(0).due-window.AW_NOW)/6e4)];
 /* Taste nach dem Versuch = weiter */
 tick(1);const Rd=MEM.run;memPress(70,'kb');o.keyNext=MEM.run!==Rd;
 /* 6 Fehler → vorspielen + neu; beim Vorspielen zählt nichts */
 R=MEM.run;if(!R.timed){}const k6=R.k;awStart({k:k6,mode:'head'});R=MEM.run;play(R.pos);let ww=0;for(const m of [30,31,32,33,34,35]){memPress(m,'kb');if(MEM.run!==R)break;ww++;if(R.show!=null){play(R.pos)}}
 /* nach 3 Fehlern kommt die Hilfe (zählt nicht weiter) – also über 2 Anschläge verteilt */
 R=MEM.run;awStart({k:k6,mode:'head'});R=MEM.run;play(R.pos);for(let i=0;i<3;i++)memPress(30,'kb');play(R.pos);for(let i=0;i<2;i++)memPress(30,'kb');const RB=MEM.run;memPress(30,'kb');memPress(31,'kb');memPress(32,'kb');
 o.six=[MEM.run!==R,!!MEM.run.pvNs,MEM.run.mode];const pos0=MEM.run.pos;play(MEM.run.pos);o.prevIgnore=MEM.run.pos===pos0;
 /* tiefstes A */
 tick(10);R=MEM.run;memPress(21,'kb');o.aRestart=MEM.run!==R&&!!MEM.run.pvNs;
 /* Vorgriff: Takt 3 aus dem Kopf, Ton 66 (0,118 s später) zuerst */
 const kV=MEM.C.findIndex(c=>gs[c.a].start<=4.01&&gs[c.b].start>=4.0);awStart({k:kV,mode:'head'});R=MEM.run;let jj=gs.findIndex(G=>G.mids.has(54));while(R.pos<jj)play(R.pos);
 memPress(66,'kb');for(const m of gs[jj].mids)memPress(m,'kb');o.vorgriff=[R.wrong,R.pos>jj+1];
 /* 4-Ton-Akkord: nach 3 Tönen geht es weiter – der 4. Ton direkt danach ist kein Fehler; derselbe Ton 1 s später schon */
 awStart({k:kV,mode:'head'});R=MEM.run;const ks=[...gs[jj].mids];for(const m of ks)memPress(m,'kb');o.chord4=[R.wrong,R.pos];tick(1.2);memPress(ks[3],'kb');o.chord4late=R.wrong;
 /* Ende erst nach dem letzten Ton */
 awStart({k:0,mode:'head'});R=MEM.run;while(R.pos<=R.b)play(R.pos);tick(0.2);o.endWait=!R.done;tick(3);o.endDone=R.done;
 /* Hintergrund */
 awStart({k:0,mode:'head'});document.dispatchEvent(new Event('visibilitychange'));
 o.timers=timers;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS)
        await pg.evaluate("()=>{window.__bg0=[(load('kt_v8log')||[]).length,JSON.stringify(MEM.rec.v9.ch)];Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true});awStart({k:0,mode:'head'});const R=MEM.run;for(const m of MEM.gs[R.pos].mids)memPress(m,'kb');memPress(30,'kb');document.dispatchEvent(new Event('visibilitychange'))}")
        r['bg'] = await pg.evaluate("({run:!!MEM.run,home:!$('#memHome').classList.contains('hidden'),zaehlt:(load('kt_v8log')||[]).length!==window.__bg0[0]||JSON.stringify(MEM.rec.v9.ch)!==window.__bg0[1]})")
        await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    c = {'Akkord-Versatz bleibt ein Anschlag, versetzter Ton eigener Anschlag': r['vorgriffGrp'],
         'Finden: Bildschirm an, Fehler zählen nicht, danach „gefunden“': r['p1'] == 'find' and r['findScreen'] and r['findWrong'] == 0 and r['findSt'] == 1,
         'Anker: sichtbar bis gespielt (auch nach 30 s), Suchen zählt nicht': r['anchor0'] and r['anchorStays'] and r['anchorSearch'] == 0 and r['anchorGone'],
         'keine Zeit-Hilfe: 25 s nachdenken → nichts, kein Ton': r['thinkNoHelp'],
         'B ganz links → Anschlag sichtbar bis gespielt (20 s), Suchen zählt nicht': r['bShow'] and r['showStays'] and r['showSearch'] and r['showGone'],
         '3 falsche Töne am selben Anschlag → Hilfe': r['auto3'],
         '2 Hilfen → zurück zu Finden': r['twoHints'] == [0, False],
         'sauber aus dem Kopf → im Puls': r['p3'] == 'head' and r['headOk'] == [True, 2] and r['p4'] == ['puls', 75],
         'Puls: 4 Klicks Einzählen + Metronom auf dem Schlag (0,5 s)': r['clicks'][0] == 4 and r['clicks'][1] >= 6 and abs(r['clicks'][2] - 0.5) < 0.02 and r['clicks'][3] and r['pulsTones'] >= 10,
         'Puls 75 % geschafft → 90 %': r['puls1'] == [True, 1] and r['p5'] == ['puls', 90],
         'Puls: verpasster Anschlag → nochmal im selben Tempo': r['pulsMiss'][0] is False and r['pulsMiss'][1] >= 1 and r['pulsMiss'][2:] == [1, 0],
         '100 % geschafft → Kasten 1, kalt in 10 min': r['p6'] == 100 and r['box1'] == [1, 10],
         'nächster Abschnitt mit leisem Anlauf vom gekonnten davor': r['p7'] == ['find', 1] and r['lead'] and r['leadSoft'] and r['k1box'] == 1,
         'Verbinden im Puls 100 %': r['link'] == ['link', 0, 1] and r['linkSp'] == 100 and r['linkOk'] == [True, True],
         'nach 10 min kalt im Puls 100 % → Kasten 2, morgen': r['rev'] == ['review', 0] and r['revSp'] == 100 and r['box2'][0] == 2 and 18 <= r['box2'][1] <= 21,
         'morgen bestanden → gelernt (Kasten 3, in 3 Tagen)': r['box3'][0] == 3 and 66 <= r['box3'][1] <= 70 and 'Gelernt' in r['box3'][2],
         'nach 3 Tagen bestanden → sitzt, Check alle 14 Tage': r['box4'][0] == 4 and r['box4'][1] == 14 and 'Sitzt' in r['box4'][2],
         'Check verpatzt → Kasten zurück, aus dem Kopf, dann Puls 100 %, dann 10 min': r['fail'] == [False, 3, 1] and r['re1'] == ['head', 0] and r['re2'] == ['puls', 100] and r['re3'] == [0, 3, 10],
         'Taste nach dem Versuch = weiter': r['keyNext'],
         '6 Fehler → vorspielen + neu, beim Vorspielen zählt nichts': r['six'][0] and r['six'][1] and r['prevIgnore'],
         'tiefstes A → vorspielen + neu': r['aRestart'],
         'Vorgriff: versetzter Akkordton zuerst gespielt zählt nicht als Fehler': r['vorgriff'] == [0, True],
         '4-Ton-Akkord: 4. Ton direkt nach dem Weiterspringen zählt nicht als Fehler, 1 s später schon': r['chord4'][0] == 0 and r['chord4late'] == 1,
         'Ende erst nach dem letzten Ton': r['endWait'] and r['endDone'],
         'Hintergrund → Durchgang endet, Übersicht, zählt nicht (kein Protokoll, Kasten gleich)': r['bg'] == {'run': False, 'home': True, 'zaehlt': False},
         'keine Zeitgeber im Lernablauf (setTimeout/setInterval, ohne Hinweis-Meldungen)': r['timers'] == 0,
         'keine Fehler': not errs}
    for k, v in c.items():
        if not v: print('  NICHT OK:', k)
    print('OK' if all(c.values()) else 'FEHLER')
asyncio.run(main())
