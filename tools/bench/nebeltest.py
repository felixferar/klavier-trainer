"""v4.86 „Nebel im Fluss“: fließend im Tempo mitspielen, ganze Takte verschwinden hinter Nebel.
Prüft: Takte an Pausen/Akkordwechseln (nie in klingende Töne, auf den Akkordwechseln), Fenster ≈ 20 s; Einzählen; die Uhr läuft weiter ohne Tastendruck;
Treffer nach Zeit (±0,18 s); verpasste Töne spielt die App; Rettungsanker: hängt man im Nebel, wird der Takt sofort aufgedeckt, ohne Stopp, und ist danach wieder offen;
Nebel wächst nur aus Erfolg; Takt sitzt nach 2× im Nebel geschafft; Fenster ganz im Nebel → Tempo 80 → 90 %; Tempo manuell einstellbar; Übersicht."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};let tones=[];window.playTone=(m)=>tones.push(m);KB.state='off';
 const LH=[47,43,50,45],SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0],SB=[66,69,71,74,76,74,71,69,71,69,66,64,66,69,71,0];
 const notes=[];let t=0;const ph=P=>{for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=P[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:q===2&&bar===3?0.95:0.45,hand:'R'})}t+=2}};
 for(const p of ['A','B','A','B'])ph(p==='A'?SA:SB);
 const it={id:'nb',type:'midi',title:'Nebel',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);
 o.here=$('#memHere').textContent;o.sum=$('#memSum').textContent;o.go=$('#memGo').textContent;o.tempoUI=$('#memTempo').textContent;
 const gs=MEM.gs,me=[];let m=-1;for(const g of gs){m=Math.max(m,g.end);me.push(m)}
 o.bars=MEM.bars.map(B=>[+B.t0.toFixed(2),+B.t1.toFixed(2)]);o.clean=MEM.bars.slice(0,-1).every(B=>gs[B.b+1].start-me[B.b]>=-0.06);o.onLH=MEM.bars.every(B=>[...gs[B.a].hands.values()].includes('L'));
 o.wins=MEM.wins.map(W=>+(gs[W.b].end-gs[W.a].start).toFixed(1));
 /* Start */
 $('#memGo').click();let R=MEM.run;o.warm=R.warm;o.fogW=MEM.rec.fl.st.slice(0,3);o.vt0=R.vt;o.t0=gs[R.a].start;
 /* Uhr läuft ohne Taste weiter, Einzählen klickt */
 tones=[];flowTick(R,1.0);flowTick(R,1.0);o.clicks=tones.filter(x=>x>=96).length;o.vtMoves=R.vt>o.vt0+1.5;
 /* Perfekt spielen: an jeden Anschlag springen, Töne drücken */
 const perfect=()=>{const R=MEM.run;for(let j=R.a;j<=R.b;j++){R.vt=gs[j].start;flowTick(R,0);for(const m of gs[j].mids)memPress(m,'kb')}R.vt=gs[R.b].end+1;flowTick(R,0)};
 const W0=MEM.wins[0];R.vt=gs[R.a].start-0.3;perfect();o.msgW=$('#memMsg').textContent;o.fog0=MEM.rec.fl.st.slice(0,3); /* v4.87: Aufwärmen ohne Nebel */
 flowStart(0);R=MEM.run;o.flow=R.flow;o.speed=R.speed;R.vt=gs[R.a].start-0.3;perfect();o.done1=R.done;o.fogA=MEM.rec.fl.st.slice(W0.b0,W0.b1+1);o.msg1=$('#memMsg').textContent;o.strip=document.querySelectorAll('#memEv .flStrip i').length;
 /* 2. Durchgang perfekt → Takt 1 sitzt (2×), Takt 2 hat 1×, Takt 3 kommt dazu */
 flowStart(0);R=MEM.run;R.vt=gs[R.a].start-0.3;perfect();o.fogB=MEM.rec.fl.st.slice(W0.b0,W0.b1+1);
 /* Rettungsanker: Takt 2 (im Nebel) nicht spielen */
 flowStart(0);R=MEM.run;const B2=MEM.bars[W0.b0]; /* v4.89: Takt 1 ist ganz im Nebel */R.vt=gs[R.a].start-0.3;tones=[];
 for(let j=R.a;j<=R.b;j++){R.vt=gs[j].start;flowTick(R,0);const inB2=j>=B2.a&&j<=B2.b;if(!inB2)for(const m of gs[j].mids)memPress(m,'kb');if(j===B2.a+2){o.rescNow=!!R.resc[W0.b0];o.notDone=!R.done}}
 R.vt=gs[R.b].end+1;flowTick(R,0);o.autoPlayed=tones.length>0;o.fogC=MEM.rec.fl.st.slice(W0.b0,W0.b1+1);o.resStripX=document.querySelectorAll('#memEv .flStrip i.x').length;
 /* falsche Taste hält nichts an */
 flowStart(0);R=MEM.run;R.vt=gs[R.a].start+0.05;flowTick(R,0);const pos0=R.vt;memPress(30,'kb');flowTick(R,0.5);o.wrongNoStop=R.vt>pos0&&!R.done;memStop();
 /* Fenster komplett im Nebel → Tempo 90 % */
 const fl=MEM.rec.fl;for(let k=W0.b0;k<=W0.b1;k++){fl.st[k]=3;fl.ok[k]=2}flowStart(0);R=MEM.run;R.vt=gs[R.a].start-0.3;perfect();o.tempoUp=fl.tempo;o.msgT=$('#memMsg').textContent;o.wdone0=!!fl.wdone[0];
 /* manuell */
 memHome();const bp=$('#memTempo').querySelector('[data-t="1"]');bp.click();o.manual=fl.manual;flowStart(0);o.manSpeed=MEM.run.speed;o.title=$('#memRunT').textContent;memStop();
 /* alter Modus weiter abschaltbar */
 window.MEM_FLOW=false;memHome();o.oldHome=$('#memHere').textContent.includes('Abschnitt');window.MEM_FLOW=true;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        st=[b[0] for b in r['bars']]
        c={'Übersicht: Fenster, Du kannst, Tempo':'Fenster 1' in r['here'] and 'Du kannst' in r['sum'] and 'Tempo' in r['tempoUI'] and r['go']=='Weiter: Fenster 1',
           'Takte nie in klingende Töne':r['clean'],'Takte beginnen auf Akkordwechsel':r['onLH'] and all(abs(s/2-round(s/2))<0.02 for s in st),
           'Takte 1,5–6 s':all(1.5<=b[1]-b[0]<=6 for b in r['bars']),'erstes Fenster ≈ 20 s':16<=r['wins'][0]<=32,
           'Aufwärmen ohne Nebel, danach Takt 1 (linke Hand) im Nebel':r['warm'] and r['fogW']==[0,0,0] and 'Nebel' in r['msgW'] and r['fog0'][0]==1,'Fluss, 80 %':r['flow'] and r['speed']==0.8,
           'Einzählen + Uhr läuft ohne Taste':r['clicks']>=3 and r['vtMoves'],
           'Durchgang 1 perfekt: Takt 1 jetzt ganz im Nebel (v4.89 Hand-Nebel)':r['done1'] and r['fogA'][:3]==[2,0,0] and 'Melodie' in r['msg1'] and r['strip']>=3,
           'Durchgang 2: Takt 2 linke Hand dazu':r['fogB'][:4]==[2,1,0,0],
           'Rettungsanker bei Hänger (2 Anschläge fehlen), ohne Stopp':r['rescNow'] and r['notDone'],'verpasste Töne spielt die App':r['autoPlayed'],
           'nicht geschafft → eine Stufe zurück, Leiste markiert':r['fogC'][0]==1 and r['resStripX']>=1,
           'falsche Taste hält nichts an':r['wrongNoStop'],
           'ganz im Nebel → 90 %':r['tempoUp']==0.9 and '90 %' in r['msgT'] and not r['wdone0'],
           'Tempo manuell':r['manual']==1.0 and r['manSpeed']==1.0 and '100 %' in r['title'],
           'alter Modus abschaltbar':r['oldHome'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
