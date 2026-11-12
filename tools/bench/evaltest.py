"""v4.65 Etappe 1: Messung & Bewertung je Durchgang (Konzept v5 §2/§5) – nur Anzeige, Stufen-Logik unverändert"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{window.__mp||(window.__mp=memPress,memPress=function(m,src){const R=MEM.run;if(R&&!R.watch&&R.vt!=null&&R.lvl<=2&&!window.__strict)R.vt=Math.max(R.vt,MEM.gs[R.pos].start);return window.__mp(m,src)}); /* Test: wie Warten, bis der Balken unten ist */const o={};let T=1000;performance.now=()=>T;
 // 12 Anschläge rechts im Abstand 0,5 s; Anschlag 6 ist ein Akkord mit linker Hand (48+52)
 const notes=[];for(let i=0;i<12;i++){if(i===5){notes.push({m:48,start:i*0.5,dur:0.4,hand:'L'},{m:52,start:i*0.5,dur:0.4,hand:'L'})}else notes.push({m:60+(i%5)*2,start:i*0.5,dur:0.4,hand:'R'})}
 const it={id:'ev1',type:'midi',title:'Ev',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];window.playTone=()=>{};
 openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1;r.lvl=3});
 const run=(plan,lvl,src)=>{memStop();MEM.rec.secs[0].lvl=lvl;memStart(0,false);const R=MEM.run;T=1000;
   for(let j=R.a;j<=R.b;j++){const st=plan.step?plan.step(j-R.a):600;T+=st;const ms=[...MEM.gs[j].mids].sort((x,y)=>x-y);
     if(plan.pre){const pr=plan.pre(j-R.a)||[];for(const [m,dt] of pr){T+=dt;memPress(m,src)}if(pr.length)T+=150}
     ms.forEach((m,q)=>{if(q>0)T+=(plan.chord?plan.chord(j-R.a):10);memPress(m,src);if(plan.slip&&plan.slip(j-R.a)&&q===0){T+=30;memPress(m+1,src)}})}
   const ev=R.ev;return {score:ev.score,cat:ev.cat,falsch:ev.falsch,extra:ev.extra,miss:ev.miss,hes:ev.hes,fix:ev.fix,rhy:[ev.rhyGood,ev.rhyN],rhyBad:ev.rhyBad,L:ev.L,R:ev.R,text:ev.text,shown:!$('#memEv').classList.contains('hidden'),strip:$$('#memEv .st i').length,x:$$('#memEv .st i.x').length,z:$$('#memEv .st i.z').length,lvlAfter:MEM.rec.secs[0].lvl}};
 const n=MEM.secs[0][1]-MEM.secs[0][0]+1;o.n=n;
 o.perfect=run({},3,'kb');                                     // gleichmäßig langsamer als Original → kein Rhythmusfehler
 o.hes1=run({step:i=>i===4?2600:600},3,'kb');                  // einmal lange gesucht
 o.hes2=run({step:i=>(i===4||i===8)?2600:600},3,'kb');
 o.rhythm=run({step:i=>i===3?950:600},3,'kb');                 // 1,58× → wackelig, aber kein Zögern
 o.wrongFix=run({pre:i=>i===2?[[71,0]]:null,step:i=>i===2?450:600},3,'kb'); // falscher Ton, sofort korrigiert
 o.chord=run({chord:i=>i===5?400:10},3,'kb');                 // Akkord nicht zusammen
 o.slip=run({slip:i=>i===7},3,'kb');                           // Nachbartaste mitgestreift
 o.leftBad=run({pre:i=>i===5?[[41,0],[43,100]]:null,step:i=>i===5?350:600},3,'kb');  // zwei falsche Töne bei der linken Hand
 o.touch=run({step:i=>i===3?950:600},3,'touch');              // Bildschirmtasten: Rhythmus nicht gewertet
 o.lvl1=run({step:i=>i===3?950:600},1,'kb');                  // Stufe 1: Rhythmus zählt nicht
 o.knopfSichtbar=getComputedStyle($('#memResBox')).display!=='none'&&$('#memNext').getBoundingClientRect().height>0;const L=load('kt_memeval');o.logN=L&&L.length;o.logG=L&&L[0].g.length;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False,indent=1),errs)
        c={
         'perfekt':r['perfect']['cat']=='s' and r['perfect']['score']==100 and r['perfect']['rhy'][0]==r['perfect']['rhy'][1]>0 and r['perfect']['shown'] and r['perfect']['strip']==r['n'],
         'zoegern1':r['hes1']['hes']==1 and r['hes1']['score']==92,
         'zoegern2':r['hes2']['hes']==2 and r['hes2']['cat']=='f' and 'gesucht' in r['hes2']['text'],
         'rhythmus':r['rhythm']['rhyBad']==1 and r['rhythm']['hes']==0 and r['rhythm']['falsch']==0 and r['rhythm']['score']==97,
         'falsch+korrigiert':r['wrongFix']['falsch']==1 and r['wrongFix']['fix']==1 and r['wrongFix']['cat']=='f' and r['wrongFix']['x']==1 and r['wrongFix']['score']==93 and r['wrongFix']['rhyBad']==0,
         'akkord':r['chord']['miss']==1 and r['chord']['falsch']==0 and r['chord']['L']>0,
         'danebengetippt':r['slip']['extra']==1 and r['slip']['falsch']==0 and r['slip']['score']==98,
         'linke Hand':r['leftBad']['L']>=2 and r['leftBad']['R']==0 and 'linke Hand' in r['leftBad']['text'],
         'touch':r['touch']['rhy'][1]==0,
         'stufe1':r['lvl1']['rhy'][1]==0,
         'stufen unveraendert':r['perfect']['lvlAfter']==3,
         'log':r['logN']==10 and r['logG']==r['n'],
         'Weiter-Knopf sichtbar':r['knopfSichtbar'],'keine Fehler':not errs}
        print(c);ok=all(c.values());print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
