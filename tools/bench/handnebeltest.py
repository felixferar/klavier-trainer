"""v4.89: Hand-Nebel, ruhiger Bildschirm, Hilfe übers Ohr, Prüfung ohne Bildschirm, Neustart-Taste.
Song: 2 Takte nur linke Hand (Intro), dann Takte mit beiden Händen.
Prüft: Takt mit beiden Händen → zuerst nur linke Hand im Nebel (Melodie sichtbar), danach ganz; Takt mit nur einer Hand → gleich ganz;
höchstens ein neues Stück Nebel je Durchgang; ruhiger Bildschirm im ganz verdeckten Takt; Hänger im Nebel → App spielt an, nichts wird eingeblendet;
Fenster sitzt bei 100 % → Prüfung ohne Bildschirm (schwarz, keine Begleitung) → bestanden = Fenster ⭐; tiefstes A = sofort neu; alter Nebel-Stand wird übernommen."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{window.MEM_V8=false;window.FLOW_FIND=false;FL.start=0.8; /* v4.92: Nebel-Logik ohne Kennenlern-Runde prüfen */ const o={};let tones=[];window.playTone=(m,d,v,g)=>tones.push({m,g});KB.state='off';
 const LH=[47,43,50,45],SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0],SB=[66,69,71,74,76,74,71,69,71,69,66,64,66,69,71,0];
 const notes=[];let t=0;for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});t+=2} /* Intro nur links */
 const ph=P=>{for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=P[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:q===2&&bar===3?0.95:0.45,hand:'R'})}t+=2}};
 for(const p of ['A','B','A'])ph(p==='A'?SA:SB);
 const it={id:'hn',type:'midi',title:'Hand',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);flowPrep();const gs=MEM.gs,fl=MEM.rec.fl,W0=MEM.wins[0];
 o.both=MEM.bars.slice(W0.b0,W0.b1+1).map(B=>B.both);
 const perfect=(skip)=>{const R=MEM.run;R.vt=gs[R.a].start-0.3;for(let j=R.a;j<=R.b;j++){R.vt=gs[j].start;flowTick(R,0);if(!(skip&&skip(j)))for(const m of gs[j].mids)memPress(m,'kb')}R.vt=gs[R.b].end+1;flowTick(R,0);return R};
 const st=()=>fl.st.slice(W0.b0,W0.b1+1);const fb=o.both.indexOf(true); /* erster Takt mit beiden Händen (relativ) */
 /* Intro-Takte (nur links) zuerst: Aufwärmen → Takt 1 ganz (nur eine Hand) */
 flowStart(0);perfect();o.s1=st();flowStart(0);perfect();o.s2=st();
 /* bis zum ersten Takt mit beiden Händen weiterspielen */
 let guard=0;while(fl.st[W0.b0+fb]===0&&guard++<20){flowStart(0);perfect()}o.sBoth=fl.st[W0.b0+fb];o.msgBoth=$('#memMsg').textContent;
 /* in Stufe 1: linke Hand verdeckt, Melodie sichtbar */
 flowStart(0);let R=MEM.run;const kB=W0.b0+fb;o.hidL=flowHid(R,kB,'L');o.hidR=flowHid(R,kB,'R');const before=st();perfect();const after=st();
 o.advance=after[fb]===2;o.oneStep=after.filter((x,i)=>x!==before[i]&&!(i===fb)).every((x,i)=>true)&&after.filter((x,i)=>before[i]===0&&x>0).length===0;o.msgAdv=$('#memMsg').textContent;
 /* ruhiger Bildschirm im ganz verdeckten Takt */
 flowStart(0);R=MEM.run;R.vt=gs[MEM.bars[W0.b0].a].start+0.05;R.ck=4;flowTick(R,0);flowDraw();o.calm=$('#memMsg').textContent.includes('Augen aufs Klavier');memStop();
 /* Hänger im ganz verdeckten Takt 1: App spielt an, Takt bleibt verdeckt */
 flowStart(0);R=MEM.run;const B1=MEM.bars[W0.b0];tones=[];R.vt=gs[R.a].start-0.3;for(let j=R.a;j<=R.b;j++){R.vt=gs[j].start;flowTick(R,0);if(j<B1.a||j>B1.b)for(const m of gs[j].mids)memPress(m,'kb');if(j===B1.b){o.earHint=tones.some(x=>x.g==null&&x.m<90);o.stillHid=flowHid(R,W0.b0,'L')}}
 R.vt=gs[R.b].end+1;flowTick(R,0);
 /* Neustart-Taste */
 flowStart(0);R=MEM.run;R.vt=gs[R.a].start+1;flowTick(R,0);memPress(21,'kb');o.restart=MEM.run!==R&&!MEM.run.done&&MEM.run.vt<gs[MEM.run.a].start;memStop();
 /* Prüfung ohne Bildschirm */
 for(let k=W0.b0;k<=W0.b1;k++){fl.st[k]=3;fl.ok[k]=2}fl.tempo=1;fl.manual=null;flowStart(0);perfect();o.examSet=!!fl.exam[0];o.msgExam=$('#memMsg').textContent;o.nextBtn=$('#memNext').textContent;
 flowStart(0);R=MEM.run;o.blind=R.blind;o.blindCls=$('#mem').classList.contains('blind');tones=[];R.ck=4;flowDraw();o.blindMsg=$('#memMsg').textContent;
 perfect();o.blindAcc=tones.filter(x=>x.g!=null).length;o.wdone=!!fl.wdone[0];o.msgPass=$('#memMsg').textContent;
 /* Übernahme alter Stand */
 delete fl.st;fl.fog=fl.ok.map((_,k)=>k===0?2:k===1?1:0);MEM._fp=null;flowPrep();o.mig=MEM.rec.fl.st.slice(0,3);
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'Takte erkannt: erst nur links, dann beide':r['both'][0] is False and True in r['both'],
           'einhändiger Takt kommt gleich ganz in den Nebel':r['s1'][0]==2,
           'beidhändiger Takt: erst linke Hand':r['sBoth']==1 and 'linke Hand' in r['msgBoth'],
           'Stufe 1: links verdeckt, Melodie sichtbar':r['hidL'] and not r['hidR'],
           'danach auch die Melodie, sonst nichts Neues':r['advance'] and r['oneStep'] and 'Melodie' in r['msgAdv'],
           'ruhiger Bildschirm im Nebel':r['calm'],'Hänger: App spielt an, bleibt verdeckt':r['earHint'] and r['stillHid'],
           'tiefstes A startet sofort neu':r['restart'],
           'Fenster sitzt bei 100 % → Prüfung ohne Bildschirm':r['examSet'] and 'ohne Bildschirm' in r['msgExam'] and r['nextBtn']=='Prüfung starten',
           'Prüfung: schwarz, keine Begleitung':r['blind'] and r['blindCls'] and 'ohne Bildschirm' in r['blindMsg'] and r['blindAcc']==0,
           'Prüfung bestanden → Fenster ⭐':r['wdone'] and 'bestanden' in r['msgPass'],
           'alter Nebel-Stand übernommen':r['mig']==[3,2,0],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
