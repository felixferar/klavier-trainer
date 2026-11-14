"""v4.97: Verbinden – klappen zwei Nachbarabschnitte aus dem Kopf, spielt man sie am Stück (dunkel, ohne Tempo); die Kette wächst (1+2 → 1–3 → 1–4, max. 4 am Stück);
nicht geschafft → in 3 min nochmal, dazwischen anderer Stoff; fällige kalte Wiederholungen haben Vorrang; Song-Karte zeigt Verbundenes zusammenhängend; tiefstes A startet die Kette neu."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};KB.state='off';
 const P=[[72,74,76,77,79,77,76,74,72,71,72,74,76,74,72,0],[69,71,72,74,76,74,72,71,69,67,69,71,72,71,69,0],[64,65,67,69,71,72,74,76,77,76,74,72,71,69,67,0]];const notes=[];let t=0;
 for(const ph of [0,1,2,1,0,2]){for(let bar=0;bar<4;bar++){notes.push({m:48+ph+bar*2,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++){const m=P[ph][bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2}t+=0.8}
 const it={id:'kt',type:'midi',title:'Kette',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];const T0=Date.now();window.V8_NOW=T0;openMem(it);memHome();const gs=MEM.gs,C=v8Chunks(),v=MEM.rec.v8;o.n=C.length;
 const play=(wrong)=>{const R=MEM.run;R.anchorUntil=0;R.previewUntil=0;let g=0;while(R.pos<=R.b&&g++<500){flowTick(R,5);if(wrong&&R.pos-R.a===1){for(const x of [30,31,32,33])memPress(x,'kb')}for(const m of gs[R.pos].mids)memPress(m,'kb')}flowTick(R,5);flowTick(R,5);return R};
 const set=(k,box)=>{v.ch[k].box=box;v.ch[k].st=1;v.ch[k].due=T0+36e5};
 set(0,1);set(1,1);memHome();o.go1=$('#memGo').textContent;o.out1=document.querySelectorAll('#memSum .v8map i[style*="solid"]').length;
 $('#memGo').click();let R=MEM.run;o.r1=[R.mode,R.a===C[0].a,R.b===C[1].b,!!R.dark];play();o.ln0=!!v.ln[0];o.msg1=$('#memMsg').textContent;
 set(2,1);o.p2=v8Pick();memStop();memHome();$('#memGo').click();R=MEM.run;o.r2=[R.a===C[0].a,R.b===C[2].b];play();
 set(3,1);set(4,1);o.p3=v8Pick();memStop();memHome();$('#memGo').click();play();o.p4=v8Pick();
 /* nicht geschafft → später */
 memStop();memHome();$('#memGo').click();R=MEM.run;o.r4=[R.mode,R.span&&R.span.s,R.span&&R.span.e];play(true);o.fail=!v.ln[3]&&v.lw[3]>T0;o.msgF=$('#memMsg').textContent;o.after=v8Pick();
 window.V8_NOW=T0+4*60e3;o.again=v8Pick();
 /* fällige Wiederholung hat Vorrang */
 v.ch[1].due=T0;o.prio=v8Pick();v.ch[1].due=T0+36e5;
 /* Karte: verbundene Felder zusammenhängend */
 memStop();memHome();const fs=[...document.querySelectorAll('#memSum .v8map i')];o.merged=fs[1].style.marginLeft==='-2px'&&fs[2].style.marginLeft==='-2px'&&fs[5].style.marginLeft!=='-2px';o.legend=$('#memSum').textContent.includes('verbunden');o.how=$('#memHow').textContent.includes('Verbinden');
 /* tiefstes A in der Kette */
 $('#memGo').click();R=MEM.run;o.m6=R.mode;memPress(21,'kb');const R2=MEM.run;o.aRestart=R2!==R&&R2.mode==='link'&&R2.a===R.a&&R2.b===R.b&&R2.previewUntil>performance.now();
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':400});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'genug Abschnitte':r['n']>=6,
           'zwei Nachbarn aus dem Kopf → verbinden angeboten':'Verbinden: Abschnitt 1–2' in r['go1'] and r['out1']==2,
           'am Stück, dunkel':r['r1']==['link',True,True,True],'geschafft → verbunden':r['ln0'] and 'Verbunden' in r['msg1'],
           'Kette wächst: 1–3':r['p2']['mode']=='link' and r['p2']['s']==0 and r['p2']['e']==2 and r['r2']==[True,True],
           'Kette wächst: 1–4, dann höchstens 4 am Stück (2–5)':r['p3']['s']==0 and r['p3']['e']==3 and r['p4']['s']==1 and r['p4']['e']==4,
           'nicht geschafft → später nochmal, dazwischen anderes':r['r4']==['link',1,4] and r['fail'] and 'nochmal' in r['msgF'] and r['after']['mode']!='link',
           'nach 3 min wieder dran':r['again']['mode']=='link' and r['again']['e']==4,
           'fällige kalte Wiederholung hat Vorrang':r['prio']['mode']=='review' and r['prio']['k']==1,
           'Karte: verbunden = zusammenhängend, Legende, Erklärung':r['merged'] and r['legend'] and r['how'],
           'tiefstes A startet die Kette neu':r['m6']=='link' and r['aRestart'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
