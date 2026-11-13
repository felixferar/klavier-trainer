"""v4.81 (Konzept v6): 3 Schritte statt 4 Stufen mit 85-%-Schwelle. „Fast“ reicht.
Kennenlernen (1 Durchgang) → Verblassen (100 % → 60 % → 30 % sichtbar, je guter Durchgang eine Etappe) → Aus dem Kopf (1× gut ohne Hilfe) → ⭐.
Ein Abschnitt braucht im guten Fall 5 Durchgänge. „Wackelig“ bleibt, „Nicht geschafft“ geht eine Etappe zurück. Alter Lernstand wird übernommen.
Übersicht zeigt „Du kannst m:ss von m:ss“, der Wert wächst, wenn ein Abschnitt sitzt."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};window.__instantEnd=true;
 const notes=[];let t=0;for(let i=0;i<64;i++){notes.push({m:60+(i%5)*2,start:t,dur:0.4,hand:'R'});t+=0.6}
 const it={id:'sch',type:'midi',title:'Sch',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);
 const A=(rec,cat,extra)=>memApply(rec,Object.assign({ev:{cat,score:cat==='s'?95:cat==='f'?80:cat==='w'?55:20,hints:0},errors:0,hints:0},extra||{}),1e12);
 /* Ablauf mit lauter „Fast“ */
 const r={lvl:1,box:0,due:0,runs:0,passed:0},seq=[];
 for(let k=0;k<8&&!(r.passed>0);k++)seq.push([A(r,'f'),r.lvl,r.fe||0]);
 o.seq=seq;o.runsToStar=seq.length;o.star=r.passed>0;
 /* Wackelig bleibt, Nicht geschafft geht zurück */
 const w={lvl:2,fe:1};o.wack=[A(w,'w'),w.lvl,w.fe];const nn={lvl:2,fe:2};o.nicht=[A(nn,'n'),nn.lvl,nn.fe];
 /* Schritt 3 mit Hilfe zählt nicht */
 const h={lvl:3,fe:2};o.mitHilfe=[A(h,'f',{ev:{cat:'f',score:80,hints:1}}),h.lvl,h.passed||0];
 /* Auffrischen schief → Verblassen 30 %, nicht auf null */
 const rv={lvl:3,box:2,due:0,passed:1};o.review=[A(rv,'n',{review:true}),rv.lvl,rv.fe,rv.passed];
 /* Verblassen zeichnet: 100 % → alle, 60 % → weniger */
 const R0=MEM.rec.secs[0];R0.lvl=2;R0.fe=0;R0.watched=true;R0.runs=1;memStart(0,false);o.frac0=memFadeFrac(MEM.run);memStop();
 R0.fe=1;memStart(0,false);o.frac1=memFadeFrac(MEM.run);o.set1=memFadeSet(MEM.run).size;o.n=MEM.run.b-MEM.run.a+1;memStop();
 R0.fe=2;memStart(0,false);o.frac2=memFadeFrac(MEM.run);o.title=$('#memRunT').textContent;o.goal=$('#memGoal').textContent;memStop();
 /* Übersicht: Sekunden */
 MEM.rec.secs.forEach(x=>{x.lvl=1;x.passed=0;x.box=0});memHome();o.sum0=$('#memSum').textContent;
 MEM.rec.secs[0].passed=1;MEM.rec.secs[0].box=1;MEM.rec.secs[0].due=memNow()+864e5;memHome();o.sum1=$('#memSum').textContent;
 /* Migration: alter Stand Stufe 3 → Verblassen 30 %, Stufe 4 → Aus dem Kopf */
 const sig=MEMS['sch'].sig;MEMS['sch2']={sig,secs:MEM.secs.map((_,i)=>({lvl:[1,2,3,4][i%4],box:0,due:0,runs:3,passed:0}))};
 const it2=Object.assign({},it,{id:'sch2'});LIB.push(it2);openMem(it2);o.mig=MEMS['sch2'].secs.slice(0,4).map(x=>[x.lvl,x.fe||0]);
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        import re
        sec=lambda s:[int(a)*60+int(b) for a,b in re.findall(r'(\d+):(\d\d)',s)]
        s0,s1=sec(r['sum0']),sec(r['sum1'])
        c={'⭐ nach 6 Durchgängen mit „Fast“ (v4.82: 4 Etappen)':r['star'] and r['runsToStar']==6,
           'Ablauf Kennenlernen→Verblassen→Aus dem Kopf':[x[1] for x in r['seq']]==[2,2,2,2,3,3] and [x[2] for x in r['seq'][:4]]==[0,1,2,3],
           'Wackelig bleibt':r['wack']==['same',2,1],'Nicht geschafft: eine Etappe zurück':r['nicht']==['back',2,1],
           'Aus dem Kopf mit Hilfe zählt nicht':r['mitHilfe'][0]=='same' and r['mitHilfe'][2]==0,
           'Auffrischen schief → Verblassen 30 %':r['review'][0]=='fail' and r['review'][1]==2 and r['review'][2]==2,
           'Verblassen 100/70/40 %':r['frac0']==1 and r['frac1']==0.7 and r['frac2']==0.4 and 0<r['set1']<r['n'],
           'Titel Schritt x von 3':'Schritt 2 von 3' in r['title'] and 'Verblassen' in r['goal'],
           'Sekunden-Balken':'Du kannst' in r['sum0'] and len(s0)==2 and s0[0]==0 and len(s1)==2 and s1[0]>0 and s1[1]==s0[1],
           'alter Stand übernommen':r['mig']==[[1,0],[2,1],[2,2],[3,0]],
           'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
