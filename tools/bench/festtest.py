"""v5.68: Fingersatz ist FEST – einmal gerechnet, beim Song gespeichert, beim Öffnen gelesen statt neu gerechnet.
Anlass (Felix 27.11.): Der Fingersatz soll bei jedem Song zum Lernen taugen. Messung: Die App rechnete bei jedem Öffnen neu; ein neuer Scan,
ein korrigierter Ton oder eine neue Modul-Version konnten Finger an schon gelernten Stellen ändern. Bei 22 von 276 Hand-Stimmen brach die Rechnung ab.
Prüft: speichern, lesen ohne Rechnung, Modul-Update ändert nichts, Korrektur ändert nur die Umgebung des Tons, neuer Scan übernimmt,
Knopf „Fingersatz neu rechnen“ (mit Rückfrage), Griff mit 6 Tönen bricht nicht mehr ab (Marke statt Zahl), Speicher voll = alter Stand bleibt.
usage: python3 tools/bench/festtest.py $PWD/web/index.html"""
import sys, os, asyncio
from playwright.async_api import async_playwright
app = 'file://' + os.path.abspath(sys.argv[1])
JS = r"""async()=>{const o={};const mk=(chg)=>{const ns=[];let t=1.5;
   for(let r=0;r<8;r++){for(const m of [70,73,77])ns.push({m,start:t,dur:1.3,hand:'R'});for(let i=0;i<4;i++)ns.push({m:58,start:t+i*0.42,dur:0.18,hand:'L'});t+=1.7;
     for(const m of [72,74,76,77,79,77,76,74])ns.push({m,start:(t+=0.3),dur:0.25,hand:'R'});t+=0.5;
     for(const m of [69,72,77])ns.push({m,start:t,dur:1.3,hand:'R'});for(let i=0;i<4;i++)ns.push({m:53,start:t+i*0.42,dur:0.18,hand:'L'});t+=1.7}
   if(chg)chg(ns);return ns};
 const item=(id,ns)=>({id,type:'midi',title:'T',artist:'x',data:b64FromBuf(writeMidi(ns)),video:{v:2}});
 S.fingers=true;S.fingStyle='einfach';
 LIB=[item('fa',mk())];save('kt_lib',LIB);
 const F0=Fingering.computeHand;let calls=0;Fingering.computeHand=function(){calls++;return F0.apply(this,arguments)};
 const snap=()=>MEM.notes.map(n=>n.fing).join('');
 // 1) erstes Öffnen: rechnen + speichern
 openMem(LIB[0]);o.fest1=MEM.song.fingFest;o.calls1=calls;const a=snap();o.all=MEM.notes.every(n=>n.fing>=1&&n.fing<=5);
 const st=LIB[0].fing;o.stored=!!st&&st.mv===Fingering.VERSION&&st.st==='einfach'&&st.d.f===a&&st.d.m.length===MEM.notes.length;
 o.persist=(()=>{const L=load('kt_lib');return !!(L&&L[0]&&L[0].fing&&L[0].fing.d.f===a)})();o.size=JSON.stringify(st).length;o.n=MEM.notes.length;
 // 2) zweites Öffnen: lesen, keine Rechnung
 calls=0;openMem(LIB[0]);o.fest2=MEM.song.fingFest;o.calls2=calls;o.same2=snap()===a;o.cue2=MEM.notes.some(n=>n.fingCue);
 // 3) „Modul-Update“: eine andere Rechnung würde überall 5 liefern – gespeicherte Finger bleiben
 Fingering.computeHand=function(ns){calls++;return {fingers:ns.map(()=>5),open:ns.map(()=>false),cue:ns.map(()=>''),mark:ns.map(()=>''),status:[]}};
 calls=0;openMem(LIB[0]);o.same3=snap()===a;o.calls3=calls;
 Fingering.computeHand=function(){calls++;return F0.apply(this,arguments)};
 // 4) Korrektur: EIN Ton der rechten Hand in der Mitte wird eine andere Taste (wie ceSave: gleicher Eintrag, neue Daten, fing bleibt)
 const base=mk();const ri=base.map((n,i)=>n.hand==='R'?i:-1).filter(i=>i>=0);const mid=ri[Math.floor(ri.length/2)];const tChg=base[mid].start;
 const ed=mk(ns=>{ns[mid].m+=2});LIB[0]=Object.assign({},LIB[0],{data:b64FromBuf(writeMidi(ed)),edited:true});save('kt_lib',LIB);
 const before=MEM.notes.map(n=>({m:n.midi,s:n.start,h:n.hand,f:n.fing}));
 calls=0;openMem(LIB[0]);o.fest4=MEM.song.fingFest;o.calls4=calls;
 let far=0,farSame=0,nearN=0;MEM.notes.forEach(n=>{const b=before.find(q=>q.h===n.hand&&q.m===n.midi&&Math.abs(q.s-n.start)<0.02);if(!b)return;if(n.hand==='R'&&Math.abs(n.start-tChg)<=1.2){nearN++;return}far++;if(b.f===n.fing)farSame++});
 o.far=far;o.farSame=farSame;o.nearN=nearN;o.all4=MEM.notes.every(n=>n.fing>=1&&n.fing<=5);o.stored4=LIB[0].fing.d.f===snap();
 // 5) neuer Scan desselben Songs: alle Zeiten 0,07 s später, neuer Eintrag mit übernommenem fing → gleiche Finger
 const a5=snap();const sh=mk(ns=>{ns[mid].m+=2;ns.forEach(n=>{n.start+=0.07})});const it5=item('fb',sh);it5.fing=LIB[0].fing;LIB=[it5];save('kt_lib',LIB);
 Fingering.computeHand=function(ns,op){calls++;o.keep5=(o.keep5||0)+Object.keys(op.keep||{}).length;return F0.apply(this,arguments)};
 calls=0;openMem(LIB[0]);o.fest5=MEM.song.fingFest;o.same5=snap()===a5;o.n5=MEM.notes.length;
 Fingering.computeHand=function(){calls++;return F0.apply(this,arguments)};
 // 6) Knopf „Fingersatz neu rechnen“: erstes Tippen = Rückfrage, zweites = neu
 openSongMenu(LIB[0]);const b=document.querySelector('#smFing');o.btnVis=!b.classList.contains('hidden');b.click();o.ask=b.textContent;o.stillSame=LIB[0].fing.d.f===a5;
 Fingering.computeHand=function(ns){return {fingers:ns.map(()=>3),open:ns.map(()=>false),cue:ns.map(()=>''),mark:ns.map(()=>''),status:[]}};
 b.click();o.recalc=/^3+$/.test(LIB[0].fing.d.f)&&MEM.notes.every(n=>n.fing===3);
 Fingering.computeHand=F0;
 // 7) Griff mit 6 Tönen in einer Hand: kein Abbruch, diese Töne ohne Zahl mit Marke, der Rest mit Zahl
 const big=mk(ns=>{for(const m of [60,62,64,65,67,69])ns.push({m,start:40,dur:1,hand:'R'});ns.sort((x,y)=>x.start-y.start||x.m-y.m)});
 // (40 s liegt mitten im Song)
 LIB=[item('fc',big)];save('kt_lib',LIB);openMem(LIB[0]);o.ok7=MEM.song.fingOk===true;
 const six=MEM.notes.filter(n=>Math.abs(n.start-40)<0.01&&n.hand==='R');o.six=six.length;o.sixNo=six.every(n=>!n.fing&&n.fingMark==='zuviel');
 o.rest7=MEM.notes.filter(n=>!six.includes(n)).every(n=>n.fing>=1&&n.fing<=5);
 // 8) Speicher voll beim Speichern: nichts kaputt, Zahlen trotzdem da, alter Stand bleibt
 LIB=[item('fd',mk())];save('kt_lib',LIB);const sv=window.save;let blocked=0;const ls=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='kt_lib'){blocked++;throw new Error('voll')}return ls.call(this,k,v)};
 openMem(LIB[0]);o.full=MEM.song.fingFest==='nicht gespeichert'&&!LIB[0].fing&&MEM.notes.every(n=>n.fing>=1)&&blocked>0;Storage.prototype.setItem=ls;
 o.ver=document.querySelector('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(app); await pg.wait_for_timeout(400); r = await pg.evaluate(JS); await br.close()
    c = {'erstes Öffnen: gerechnet, jeder Ton hat einen Finger': r['fest1'] == 'neu' and r['calls1'] >= 2 and r['all'],
         'Fingersatz steht beim Song (Modul-Version, Stil, eine Ziffer je Ton) und im Speicher': r['stored'] and r['persist'],
         'Platzbedarf höchstens 8 Zeichen je Ton': r['size'] <= 8 * r['n'] + 200,
         'zweites Öffnen: gelesen, KEINE Rechnung, gleiche Finger, Marken wieder da': r['fest2'] == 'gelesen' and r['calls2'] == 0 and r['same2'] and r['cue2'],
         'andere Modul-Version ändert einen gespeicherten Song nicht': r['same3'] and r['calls3'] == 0,
         'ein Ton korrigiert: nur ergänzt – alle Finger außerhalb ±1,2 s bleiben': r['fest4'] == 'ergänzt' and r['far'] > 100 and r['farSame'] == r['far'] and r['all4'] and r['stored4'],
         'neuer Scan (0,07 s versetzt) übernimmt den gespeicherten Fingersatz vollständig': r['fest5'] == 'ergänzt' and r['same5'] and r.get('keep5', 0) == r['n5'],
         'Knopf „Fingersatz neu rechnen“ sichtbar, erstes Tippen fragt nach und ändert nichts': r['btnVis'] and 'Wirklich' in r['ask'] and r['stillSame'],
         'zweites Tippen rechnet neu und speichert': r['recalc'],
         'Griff mit 6 Tönen: kein Abbruch; diese Töne ohne Zahl mit Marke „zuviel“, alle anderen mit Zahl': r['ok7'] and r['six'] == 6 and r['sixNo'] and r['rest7'],
         'Speicher voll: Zahlen trotzdem da, nichts halb gespeichert': r['full'],
         'Version 5.81': r['ver'].startswith('Version 5.81'),
         'keine JS-Fehler': not errs}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    if not all(c.values()): print(r, errs)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
