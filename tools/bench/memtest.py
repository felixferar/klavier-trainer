"""v4.44 Auswendig lernen: Abschnitte, Hilfe-Leiter, Fehler, Hilfe nach Wartezeit, Stufen, Bestehen/Terminplan, Wiederholung, Mischen, Eingabe-Haken, Speichern"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS="""async()=>{window.__instantEnd=true;window.__mp||(window.__mp=memPress,memPress=function(m,src){const R=MEM.run;if(R&&!R.watch&&R.vt!=null&&R.lvl<=2&&!window.__strict)R.vt=Math.max(R.vt,MEM.gs[R.pos].start);return window.__mp(m,src)}); /* Test: wie Warten, bis der Balken unten ist */const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));
 memSplit2=g=>memSplit(g); /* v4.83: dieser Test prüft den Lernablauf mit 3 festen Abschnitten – die neue Aufteilung prüft teiletest.py */
 // Song: 30 Anschlaege, nach je 10 eine Pause von 0.6 s; ein Akkord (Nr. 4: 60+64)
 const notes=[];let t=0;for(let i=0;i<30;i++){const m=60+(i%7);notes.push({m,start:t,dur:0.4,hand:'R'});if(i===3)notes.push({m:64,start:t,dur:0.4,hand:'R'});t+=0.5;if(i%10===9)t+=0.6}
 const it={id:'mt1',type:'midi',title:'Merk',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 // reine Funktionen
 const gs=memGroups(songFromMidi(bufFromB64(it.data),'x').notes);o.groups=gs.length;o.split=memSplit(gs);
 const ex=Array.from({length:13},(_,i)=>({start:i,end:i+0.5,mids:new Set([60])}));o.splitShortTail=memSplit(ex);   // 13: 8+5 -> Schluss 5 bleibt
 o.split12=memSplit(Array.from({length:12},(_,i)=>({start:i,end:i+0.5,mids:new Set([60])})));const ex2=Array.from({length:10},(_,i)=>({start:i,end:i+0.5,mids:new Set([60])}));o.splitSmall=memSplit(ex2);
 const T=1e9;const r1={lvl:1,box:0,due:0};const A=(r,run)=>memApply(r,Object.assign({errors:0,hints:0,review:false},run),T);
 o.apply={clean1:[A(r1,{}),r1.lvl],clean2:[A(r1,{}),r1.lvl],bad1:[A(r1,{errors:1}),r1.lvl]};
 const r3={lvl:3,box:0,due:0};o.apply.down=[A(r3,{errors:2,hints:1}),r3.lvl];const r4={lvl:4,box:0,due:0};o.apply.pass=[A(r4,{}),r4.box,Math.round((r4.due-T)/864e5)];
 const r4b={lvl:4,box:0,due:0};o.apply.pass1=[A(r4b,{errors:1}),r4b.box];const r4c={lvl:4,box:0,due:0};o.apply.same=[A(r4c,{errors:2}),r4c.lvl];
 const rv={lvl:4,box:3,due:0,passed:1};o.apply.rvFail=[A(rv,{errors:3,review:true}),rv.box,rv.lvl,rv.due===T];const rv2={lvl:4,box:3,due:0,passed:1};o.apply.rvPass=[A(rv2,{review:true}),rv2.box,Math.round((rv2.due-T)/864e5)];
 // Ansicht
 window.openYT=()=>{};openSongMenu(it);o.btn=!$('#smMem').classList.contains('hidden');$('#smMem').click();
 o.shown=!$('#mem').classList.contains('hidden');o.secsN=MEM.secs.length;o.list=$$('#memList .mk').length;o.go=$('#memGo').textContent;o.mixHidden=$('#memMix').classList.contains('hidden');
 const play=(n)=>{for(let k=0;k<n;k++){const R=MEM.run;if(!R||R.done)break;for(const m of MEM.gs[R.pos].mids)userPress(m,false)}};
 // Abschnitt 1 Stufe 1 spielen: Fehler zaehlen
 MEM.rec.secs[1].watched=true;MEM.rec.secs[2].watched=true;$('#memGo').click();o.watch1=!!MEM.run.watch;const wp=MEM.run.pos;MEM.run.watchStart-=30000;memTick();o.watchDone=!!(MEM.run.watchDone&&MEM.rec.secs[0].watched&&$('#memNext').textContent==='Jetzt spielen');$('#memNext').click();o.run1={lvl:MEM.run.lvl,a:MEM.run.a,b:MEM.run.b,title:$('#memRunT').textContent};
 userPress(30,false);o.err1=MEM.run.errors;      // falsche Taste
 play(3);o.pos=MEM.run.pos-MEM.run.a;
 // Akkord: erst eine Taste -> noch kein Fortschritt
 const gi=MEM.run.pos;const mids=[...MEM.gs[gi].mids];userPress(mids[0],false);o.chordHalf=MEM.run.pos===gi&&MEM.run.hit.size===1;userPress(mids[0],false);o.chordRepeatIgnored=MEM.run.errors===1;
 userPress(mids[1]||mids[0],false);play(50);o.done1=MEM.run.done;o.rec1=JSON.parse(JSON.stringify(MEM.rec.secs[0]));
 // Stufen hochspielen (je Lauf fehlerfrei) bis Stufe 4 und Bestehen
 for(let k=0;k<16&&MEM.rec.secs[0].box===0;k++){if(MEM.run&&MEM.run.done){$('#memAgain').click()}else if(!MEM.run)$('#memGo').click();play(50)}
 o.after={lvl:MEM.rec.secs[0].lvl,box:MEM.rec.secs[0].box,passed:MEM.rec.secs[0].passed,dueDays:Math.round((MEM.rec.secs[0].due-Date.now())/864e5),chainBtn:$('#memChain').style.display};
 o.persist=JSON.parse(localStorage.getItem('kt_mem')).mt1.secs[0].box;
 // Hilfe nach Wartezeit (Stufe 3): Uhr verschieben
 MEM.rec.secs[1].lvl=3;memStop();memHome();memStart(1,false);const R=MEM.run;let fake=memNow();const real=memNow;window.__t=0;
 o.hint3={before:memHintOn()};R.gStart-=6000;memTick();o.hint3.after=memHintOn();o.hint3.hints=R.hints;memTick();o.hint3.once=R.hints;
 // Stufe 4: Hilfe nach 8 s zaehlt als Fehler
 memStop();MEM.rec.secs[1].lvl=4;memStart(1,false);MEM.run.gStart-=9000;memTick();o.hint4=MEM.run.hints;
 // Eingabe ueber Tastatur-Weg (kbNoteOn)
 memStop();memStart(1,false);const g0=MEM.gs[MEM.run.pos].mids;for(const m of g0)kbNoteOn(m);o.kbPos=MEM.run.pos-MEM.run.a;
 // Verbinden: Abschnitt 2 bestehen -> Verbinden-Knopf
 // Wiederholung faellig: Abschnitt 1 auf faellig setzen
 memStop();MEM.rec.secs[0].due=Date.now()-1000;memHome();o.dueTxt=$('#memSum').textContent;o.goDue=$('#memGo').textContent;
 // Mischen: beide Abschnitte gelernt
 MEM.rec.secs[1].box=1;MEM.rec.secs[1].passed=1;MEM.rec.secs[1].due=Date.now()+864e5;memHome();o.mix=!$('#memMix').classList.contains('hidden');$('#memMix').click();o.mixRun={review:MEM.run.review,lvl:MEM.run.lvl,queue:MEM.queue.length};
 // Review nicht bestanden: 3 Fehler
 const i0=MEM.run.i;for(let k=0;k<12;k++)userPress(30,false);play(60);o.rvfail={box:MEM.rec.secs[i0].box,lvl:MEM.rec.secs[i0].lvl,msg:$('#memMsg').textContent.slice(0,30)};
 // Zurueck beendet den Lauf
 back();o.backStops=MEM.run===null&&MEM.timer===null;
 // Touch auf der Mini-Tastatur
 openMem(it);memStart(1,false);const rr=$('#memCv').getBoundingClientRect();const exp=[...MEM.gs[MEM.run.pos].mids][0];memDraw();const k=MEM.pos[exp];
 $('#memCv').dispatchEvent(new PointerEvent('pointerdown',{clientX:rr.left+k.x+k.w/2,clientY:rr.top+MEM.hn+(k.b?MEM.kbH*0.3:MEM.kbH*0.85),bubbles:true}));o.touchPos=MEM.run.pos-MEM.run.a;
 // Verbinden: Abschnitt 2 (i=1) bis zum Bestehen spielen -> Verbinden-Knopf, Verbindungslauf
 memStop();openMem(it);MEM.rec.secs[1]={lvl:4,box:0,due:0,runs:3,passed:0};memStart(1,false);play(50);o.chainBtn=$('#memChain').style.display;$('#memChain').click();o.chainRun={a:MEM.run.a,b:MEM.run.b,chain:MEM.run.chain,lvl:MEM.run.lvl};play(60);o.chained=MEM.rec.secs[1].chained===true&&MEM.rec.secs[1].box===1;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False,indent=0));print('pageerrors',errs)
        c={'gruppen':r['groups']==30,'split':r['split']==[[0,9],[10,19],[20,30]] or len(r['split'])==3,'kurzer Rest':r['splitShortTail']==[[0,7],[8,12]] and r['split12']==[[0,11]],'klein':r['splitSmall']==[[0,9]],
           'apply':r['apply']['clean1']==['up',2] and r['apply']['clean2']==['fade',2] and r['apply']['bad1']==['fade',2] and r['apply']['down']==['same',3] and r['apply']['pass']==['pass',1,1] and r['apply']['pass1']==['pass',1] and r['apply']['same']==['pass',4] and r['apply']['rvFail']==['fail',0,2,False] and r['apply']['rvPass']==['pass',4,14],
           'Knopf':r['btn'] and r['shown'] and r['secsN']==3 and r['list']==3 and r['go'].startswith('Weiter: Abschnitt 1') and r['mixHidden'],
           'Ansehen':r['watch1'] and r['watchDone'],'Lauf1':r['run1']['lvl']==1 and r['run1']['a']==0 and r['err1']==1 and r['pos']==3,'Akkord':r['chordHalf'] and r['chordRepeatIgnored'],'fertig1':r['done1'] and r['rec1']['lvl']==2 and r['rec1']['runs']==1,
           'Stufen':r['after']['box']==1 and r['after']['passed']==1 and r['after']['dueDays']==1,'speichern':r['persist']==1,
           'Hilfe3':(not r['hint3']['before']) and r['hint3']['after'] and r['hint3']['hints']==1 and r['hint3']['once']==1,'Hilfe4':r['hint4']==1,'kb':r['kbPos']==1,
           'faellig':('1 zum Auffrischen' in r['dueTxt']) and r['goDue'].startswith('Auffrischen: Abschnitt'),'mischen':r['mix'] and r['mixRun']['review'] and r['mixRun']['lvl']==4 and r['mixRun']['queue']==1,
           'rvfail':r['rvfail']['lvl']==2,'zurueck':r['backStops'],'touch':r['touchPos']==0,  # v4.67: Bildschirm-Tasten im Auswendig-Modus aus
           'Verbinden':r['chainBtn']=='' and r['chainRun']=={'a':0,'b':19,'chain':True,'lvl':4} and r['chained'],'fehlerfrei':not errs}
        print(c);ok=all(c.values());print('ERGEBNIS','OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
