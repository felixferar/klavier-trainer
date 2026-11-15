"""v5.04: Virtueller Lerner für den Auswendig-Modus.
Ein simulierter Spieler (fester Zufall, reproduzierbar) lernt einen Song über viele Tage: er findet Tasten, vergisst Anschläge, denkt lange nach
(bis 20 s), greift daneben, bittet um Hilfe (B ganz links / Knopf), spielt im Puls mit Bluetooth-Verzögerung und Zittern, vergisst über Nacht.
Alles läuft über die eine Uhr des Auswendig-Modus (awTick) – ohne Warten.

Geprüft wird:
- Keine Zeit-Hilfe: während langem Nachdenken passiert nichts (keine Hilfe, Bildschirm bleibt dunkel, kein Ton)
- Hilfe nur auf Wunsch oder nach 3 falschen Tönen am selben Anschlag; die Hilfe bleibt, bis der Anschlag gespielt ist
- Suchen während der Hilfe / beim Start-Anker zählt nicht als Fehler
- Keine Sackgasse, kein hängender Durchgang, keine Seitenfehler
- Der Weg: Finden → aus dem Kopf → Puls 75/90/100 % → Kasten 1–3 → sitzt; Verbinden; Auffrischen nach Fehlschlag
- Die Bluetooth-Verzögerung wird gelernt
usage: python3 tools/bench/lernertest.py $PWD/web/index.html [seed]"""
import sys, asyncio, json
from playwright.async_api import async_playwright

JS = r"""async([seed,maxMiss,stp])=>{if(stp)window.AW_STEP=stp;if(maxMiss!=null)AW.maxMiss=maxMiss;
 let S0=seed>>>0;const rnd=()=>{S0|=0;S0=S0+0x6D2B79F5|0;let t=Math.imul(S0^S0>>>15,1|S0);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
 const out={err:[],viol:[],stats:{att:{},abort:0,askHelp:0,autoHelp:0,longThink:0,searchWhileShown:0,relearn:0,links:0,stuck:0},days:[]};
 const V=(k,msg)=>{if(out.viol.length<30)out.viol.push(k+': '+msg)};
 window.AW_NOLOOP=true;let tones=[];window.playTone=(m,d,v,g)=>tones.push(m);KB.state='off';
 /* Song: 2 Hände, gleichmäßiger Schlag 0,5 s, 16 Takte mit Wiederholungen und Varianten */
 const LH=[[36,43],[41,48],[43,50],[36,43],[45,52],[41,48],[43,50],[36,43]],MEL=[[64,67,72,67],[65,69,72,69],[67,71,74,71],[64,67,72,0],[69,72,76,72],[65,69,72,69],[67,71,74,77],[72,67,64,0]];
 const notes=[];let t=0;for(let r=0;r<2;r++)for(let bar=0;bar<8;bar++){for(const m of LH[bar])notes.push({m,start:t,dur:1.9,hand:'L'});const M=MEL[bar];for(let q=0;q<4;q++){const m=M[q]+(r&&q===3&&M[q]?2:0);if(M[q])notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2}
 const it={id:'lerner',type:'midi',title:'Lerner-Song',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);
 const T0=Date.UTC(2026,10,16,8,0,0);window.AW_NOW=T0;openMem(it);
 const gs=MEM.gs,C=MEM.C,nC=C.length;out.chunks=C.map(c=>[c.a,c.b,+(c.t1-c.t0).toFixed(1)]);out.beat=awBeat();
 const str=C.map(()=>0),L_USER=0.06; /* Gedächtnis je Abschnitt 0..1; Bluetooth-Verzögerung des Spielers 60 ms */
 const st=()=>MEM.rec.v9.ch;
 const step=window.AW_STEP||1/30,tick=(sec)=>{let x=0;while(x<sec-1e-9){const R=MEM.run;if(!R)return;awTick(R,step);x+=step}};
 const press=ms=>{for(const m of ms)memPress(m,'kb')};
 const wrongKey=G=>{let m=Math.max(...G.mids)+1;while(G.mids.has(m))m++;return m};
 const watch=(R,label,f)=>{const h0=R.hints,tn=tones.length;f();if(MEM.run!==R)return;if(R.hints!==h0)V('Zeit-Hilfe',`${label}: Hilfe ohne Anlass (Abschnitt ${R.k+1}, ${R.mode})`);
   const nt=tones.slice(tn).filter(m=>m<90);if(nt.length&&!R.timed)V('Ton',`${label}: App spielte Töne ${nt} ohne Anlass`);awDraw();if(!R.done&&R.dark&&R.show==null&&!R.anchor&&R.drawState!=='dunkel')V('Bildschirm',`${label}: Bildschirm nicht dunkel (${R.drawState})`)};
 /* ein Anschlag im Warte-Modus */
 function playWaitGroup(R){const j=R.pos,G=gs[j],ks=[...G.mids];
   if(R.mode==='find'){tick(0.4+rnd());if(rnd()<0.15){press([wrongKey(G)])}press(ks);return}
   if(R.anchor){ /* Start-Anker: sichtbar bis gespielt; einmal danebengreifen beim Suchen zählt nicht */
     tick(1+rnd()*4);if(!R.anchor)V('Anker','Start-Anker verschwand von selbst');const w0=R.wrong;if(rnd()<0.5){press([wrongKey(G)]);if(R.wrong!==w0)V('Anker','Suchen beim Anker zählte als Fehler')}press(ks);return}
   const k=R.span?null:R.k,s=str[R.k],pf=Math.min(0.6,Math.max(0.03,(1-s)*0.45));
   if(rnd()>=pf){tick(0.3+rnd()*1.2);press(ks);return}
   const r=rnd();
   if(r<0.4){out.stats.longThink++;const th=5+rnd()*15;watch(R,`${th.toFixed(0)} s nachdenken`,()=>tick(th));if(MEM.run===R)press(ks);return}
   if(r<0.75){ /* danebengreifen bis die Hilfe von selbst kommt */
     let n=0;while(MEM.run===R&&R.show==null&&n<3){const h0=R.hints;press([wrongKey(G)]);n++;if(MEM.run!==R)return;if(R.hints!==h0&&(R.wpos[j]||0)<3)V('Hilfe','Hilfe vor dem 3. Fehler');tick(0.5)}
     if(MEM.run!==R)return;if(R.show===j){out.stats.autoHelp++;tick(3+rnd()*5);if(R.show!==j)V('Hilfe','Hilfe verschwand von selbst');
       const w0=R.wrong;press([wrongKey(G)]);out.stats.searchWhileShown++;if(R.wrong!==w0)V('Hilfe','Suchen während der Hilfe zählte als Fehler')}
     press(ks);if(R.show===j)V('Hilfe','Hilfe blieb nach dem Spielen stehen');return}
   out.stats.askHelp++;const h0=R.hints;if(rnd()<0.5)press([22]);else $('#memHelp').click();if(R.hints!==h0+1||R.show!==j)V('Hilfe','B / Knopf zeigte den Anschlag nicht');tick(2+rnd()*4);press(ks)}
 /* ein Durchgang im Puls */
 function playTimed(R){const s=str[R.k];let q=R.a;const plan={};
   for(let j=R.a;j<=R.b;j++){const pf=R.mode==='puls'?Math.min(0.25,(1-s)*0.12):Math.min(0.4,(1-s)*0.35);plan[j]={miss:rnd()<pf,jit:(rnd()-0.5)*0.08,wrong:rnd()<0.02}}
   let guard=0;const fs=Math.min(step,1/120);while(MEM.run===R&&!R.done&&guard++<80000){awTick(R,fs);if(R.done||MEM.run!==R)break;
     while(q<=R.b&&R.vt>=gs[q].start+(L_USER+plan[q].jit)*R.speed){const P=plan[q];if(!P.miss){press([...gs[q].mids]);if(P.wrong)press([wrongKey(gs[q])])}q++;if(MEM.run!==R)break}}
   if(guard>=80000)V('Hängt','Puls-Durchgang endet nicht')}
 function playRun(){let R=MEM.run,guard=0;const mode0=R.mode;
   while(R&&!R.done&&guard++<400){if(R.pvNs){tick(0.2);continue}
     if(R.timed)playTimed(R);else if(R.pos<=R.b)playWaitGroup(R);else tick(0.2);
     if(MEM.run!==R){out.stats.abort++;R=MEM.run}}
   if(guard>=400){out.stats.stuck++;V('Hängt',`Durchgang hängt (${R&&R.mode})`)}return MEM.run}
 const learn=(R)=>{const k=R.k,ok=R.ok,ks=R.span?[...Array(R.span.e-R.span.s+1)].map((_,i)=>R.span.s+i):[k];for(const x of ks){if(R.mode==='find')str[x]=Math.max(str[x],0.4);else str[x]+=(ok?0.25:0.08)*(1-str[x])}};
 const decay=days=>{st().forEach((c,k)=>{const tau=1.5*(1+3*c.box);str[k]*=Math.exp(-days/tau)})};
 const ladder=C.map(()=>new Set());let day=0,totalAtt=0,firstSitzt=null,allBox1=null;
 for(day=0;day<30;day++){const dStart=T0+day*864e5;if(day>0){decay(1);window.AW_NOW=dStart}let n=0,mins=0;const sess0=window.AW_NOW;
   while(n<60){let p=awPick();
     if(!p){const fut=st().filter(c=>c.box>=1&&c.due>window.AW_NOW).map(c=>c.due);const nd=fut.length?Math.min(...fut):Infinity;if(nd-window.AW_NOW<=15*60e3&&window.AW_NOW-sess0<40*60e3){window.AW_NOW=nd+1000;continue}break}
     const tag=p.mode+(p.mode==='puls'?Math.round(AW.tempi[st()[p.k].tp]*100):'');out.stats.att[tag]=(out.stats.att[tag]||0)+1;
     if(p.mode==='head'&&st()[p.k].relearn)out.stats.relearn++;
     awNext();let R=MEM.run;if(!R||R.mode!==p.mode){V('Ablauf','Weiter startete etwas anderes als angekündigt');break}
     R=playRun();if(!R||!R.done)break;(out.latHist=out.latHist||[]).push(+(MEM.rec.v9.lat*1000).toFixed(0));learn(R);ladder[R.k].add(R.mode+(R.ok?'+':'-'));if(R.mode==='link'&&R.ok)out.stats.links++;
     window.AW_NOW+=Math.round(R.clock*1000)+15000;mins+=R.clock/60;n++;totalAtt++}
   const ch=st();out.days.push({day,att:n,min:+mins.toFixed(1),box:ch.map(c=>c.box).join(''),st:ch.map(c=>c.st).join('')});
   if(allBox1==null&&ch.every(c=>c.box>=1))allBox1=day;if(firstSitzt==null&&ch.every(c=>c.box>=AW.solid))firstSitzt=day;if(firstSitzt!=null&&day>=firstSitzt+15)break}
 const v=MEM.rec.v9;out.allBox1=allBox1;out.sitzt=firstSitzt;out.lat=v.lat;{const h=out.latHist||[];const t=h.slice(-12);out.latAvg=t.length?t.reduce((x,y)=>x+y,0)/t.length/1000:0}out.ln=v.ln.filter(Boolean).length;out.totalAtt=totalAtt;
 out.stages=['find','head','puls','review','link'].filter(m=>Object.keys(out.stats.att).some(k=>k.startsWith(m)));
 out.deadEnd=!(firstSitzt!=null||st().some(c=>c.box>=1&&c.due>window.AW_NOW));
 return out}"""

async def main():
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, [seed, int(sys.argv[3]) if len(sys.argv) > 3 else None, float(sys.argv[4]) if len(sys.argv) > 4 else None]); await br.close()
    print('Abschnitte:', r['chunks'], ' Schlag:', r['beat'])
    for d in r['days']:
        if d['att'] or d['day'] < 3: print(f"Tag {d['day']:2}: {d['att']:2} Versuche, {d['min']:5} min · Kästen {d['box']} · Stufen {d['st']}")
    print('Versuche je Modus:', r['stats']['att'])
    print('Lerner:', {k: v for k, v in r['stats'].items() if k != 'att'})
    print(f"alle im Tempo (Kasten ≥1) an Tag {r['allBox1']} · alles sitzt an Tag {r['sitzt']} · verbunden {r['ln']} · gelernte Verzögerung {r['lat']} s (Mittel zuletzt {r['latAvg']:.3f}) (Spieler 0,06 s) · Versuche gesamt {r['totalAtt']}")
    print('Verzögerung (ms) im Verlauf:', r.get('latHist', [])[::6])
    for x in r['viol']: print('  VERSTOSS', x)
    c = {'keine Seitenfehler': not errs,
         'keine Zeit-Hilfe / Hilfe nur auf Anlass / Suchen zählt nicht (0 Verstöße)': not r['viol'],
         'langes Nachdenken kam vor': r['stats']['longThink'] >= 5,
         'Hilfe auf Wunsch und nach 3 Fehlern kam vor': r['stats']['askHelp'] >= 2 and r['stats']['autoHelp'] >= 2,
         'kein hängender Durchgang': r['stats']['stuck'] == 0,
         'alle Stufen durchlaufen (Finden, Kopf, Puls, Wiederholen, Verbinden)': r['stages'] == ['find', 'head', 'puls', 'review', 'link'],
         'Puls 75 → 90 → 100 %': all(k in r['stats']['att'] for k in ['puls75', 'puls90', 'puls100']),
         'keine Sackgasse: alles sitzt irgendwann': r['sitzt'] is not None and not r['deadEnd'],
         'nach ein paar Tagen alles im Tempo': r['allBox1'] is not None and r['allBox1'] <= 4,
         'Song wächst zusammen (verbunden)': r['ln'] >= 1,
         'Verzögerung gelernt (Mittel der letzten 12 Durchgänge ±25 ms)': abs(r['latAvg'] - 0.06) <= 0.025,
         'keine Fehler': not errs}
    print(c, errs[:3])
    print('OK' if all(c.values()) else 'FEHLER')

asyncio.run(main())
