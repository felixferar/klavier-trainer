"""v4.94: Zielbild v8 Schritt 1 – Stufe 3 „aus dem Kopf“ (Bildschirm dunkel, Start-Anker, Hilfe übers Ohr nach 2 s Stocken) + Stufe 5 (Leitner-Kästen, kalt, nur erster Versuch).
Prüft: Übersicht ehrlich („Gelernt … Nacht“, fällig); Finden → aus dem Kopf (dunkel, Start-Anker klingt + kurz sichtbar, sonst nichts); Hilfe → nicht geschafft;
2 Hilfen → zurück zu Finden; sauber → Kasten 1, kalt nach 10 min, dazwischen nächster Abschnitt; kalt sauber → Kasten 2 (= gelernt), nächste in ~1 Tag;
kalt falsch → Kasten zurück + sofort auffrischen; tiefstes A = vorspielen + neu (laufende kalte Wiederholung zählt als nicht geschafft); alter Ablauf per MEM_V8=false."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};let tones=[];window.playTone=(m,d,v,g)=>tones.push(m);KB.state='off';
 const LH=[47,43,50,45],SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0];const notes=[];let t=0;
 for(let r=0;r<2;r++)for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=SA[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2}
 const it={id:'ab',type:'midi',title:'Abruf',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];const T0=Date.now();window.V8_NOW=T0;openMem(it);memHome();const gs=MEM.gs;
 o.sum=$('#memSum').textContent;o.here=$('#memHere').textContent;o.go=$('#memGo').textContent;
 const play=(wrongAt)=>{const R=MEM.run;R.anchorUntil=0;let g=0;while(R.pos<=R.b&&g++<200){flowTick(R,5);if(wrongAt&&wrongAt.includes(R.pos-R.a)){memPress(30,'kb');memPress(31,'kb')}for(const m of gs[R.pos].mids)memPress(m,'kb')}flowTick(R,5);flowTick(R,5);return R};
 const v=()=>MEM.rec.v8.ch;
 $('#memGo').click();let R=MEM.run;o.m1=[R.mode,R.k,!!R.dark];play();o.c0=JSON.parse(JSON.stringify(v()[0]));o.msgF=$('#memMsg').textContent;
 /* Stufe 3: dunkel, Start-Anker */
 tones=[];$('#memNext').click();R=MEM.run;o.m2=[R.mode,R.k,!!R.dark,$('#mem').classList.contains('blind')];o.anchorTone=[...gs[R.a].mids].every(m=>tones.includes(m));
 flowDraw();o.anchorMsg=$('#memMsg').textContent;o.anchorPre=[...R.pre].sort().join()==[...gs[R.a].mids].sort().join();
 R.anchorUntil=0;flowDraw();o.darkMsg=$('#memMsg').textContent;
 /* Stocken > 2 s → App spielt an, Versuch nicht geschafft */
 flowTick(R,5);tones=[];R.waitT0=performance.now()-2500;flowTick(R,0);o.hint=R.hints===1&&[...gs[R.pos].mids].every(m=>tones.includes(m));
 for(const m of gs[R.pos].mids)memPress(m,'kb');play();o.c1=JSON.parse(JSON.stringify(v()[0]));o.msgH=$('#memMsg').textContent;
 /* 2 Hilfen → zurück zu Finden */
 $('#memNext').click();R=MEM.run;R.anchorUntil=0;for(let q=0;q<2;q++){flowTick(R,5);R.waitT0=performance.now()-2500;flowTick(R,0);for(const m of gs[R.pos].mids)memPress(m,'kb')}play();o.back=v()[0].st===0&&v8Pick().mode==='find';
 $('#memNext').click();play();
 /* sauber aus dem Kopf → Kasten 1, kalt nach 10 min */
 $('#memNext').click();R=MEM.run;o.m3=R.mode;play();const c=v()[0];o.box1=c.box===1&&Math.abs(c.due-(T0+600e3))<1000;o.msgOk=$('#memMsg').textContent;
 o.nextOther=v8Pick().k===1&&v8Pick().mode==='find';
 /* nach 11 min: kalt wiederholen kommt zuerst */
 window.V8_NOW=T0+11*60e3;memStop();memHome();o.hereRev=$('#memHere').textContent;o.goRev=$('#memGo').textContent;
 $('#memGo').click();R=MEM.run;o.m4=[R.mode,R.k,!!R.dark];play();o.box2=v()[0].box===2&&Math.abs(v()[0].due-(window.V8_NOW+20*36e5))<1000;o.msgRev=$('#memMsg').textContent;
 memStop();memHome();o.sum2=$('#memSum').textContent;
 /* am nächsten Tag kalt sauber → Kasten 3 = gelernt */
 window.V8_NOW=T0+21*36e5;memStop();memHome();$('#memGo').click();R=MEM.run;o.m45=[R.mode,R.k];play();o.box3=v()[0].box===3;o.msgGel=$('#memMsg').textContent;memStop();memHome();o.sum3=$('#memSum').textContent;
 /* Tage später: kalt mit 2 falschen Tönen → Kasten zurück + auffrischen */
 window.V8_NOW=T0+4*864e5;memStop();memHome();$('#memGo').click();R=MEM.run;o.m5=[R.mode,R.k];play([1,2]);o.fail=v()[0].box===2&&v()[0].relearn===1;o.msgFail=$('#memMsg').textContent;
 o.relearn=v8Pick().k===0&&v8Pick().mode==='recall';
 /* tiefstes A in laufender kalter Wiederholung */
 v()[0].relearn=0;v()[0].box=3;v()[0].due=window.V8_NOW-1;memStop();memHome();$('#memGo').click();R=MEM.run;o.m6=R.mode;tones=[];memPress(21,'kb');const R2=MEM.run;
 o.aRestart=R2!==R&&R2.mode==='recall'&&R2.previewUntil>performance.now()&&v()[0].box===2&&v()[0].relearn===1;
 const pos0=R2.pos;for(const m of gs[R2.a].mids)memPress(m,'kb');o.ignoredInPreview=R2.pos===pos0;flowDraw();o.prevMsg=$('#memMsg').textContent;
 /* alter Ablauf */
 window.MEM_V8=false;memStop();memHome();o.oldHome=$('#memHere').textContent.includes('Fenster');window.MEM_V8=true;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'Übersicht ehrlich: Gelernt/Nacht/fällig':'Gelernt' in r['sum'] and 'nächsten Tag' in r['sum'] and 'fällig' in r['sum'] and 'finden' in r['go'],
           'neu: erst Tasten finden (Bildschirm an)':r['m1']==['find',0,False] and r['c0']['st']==1 and 'aus dem Kopf' in r['msgF'],
           'dann aus dem Kopf, dunkel':r['m2']==['recall',0,True,True],
           'Start-Anker: erster Anschlag klingt und ist kurz zu sehen':r['anchorTone'] and r['anchorPre'] and 'fängt' in r['anchorMsg'],
           'danach nur dunkel':'Augen aufs Klavier' in r['darkMsg'],
           'Stocken > 2 s → App spielt an':r['hint'],
           'mit Hilfe = nicht geschafft':r['c1']['box']==0 and r['c1']['fails']==1 and 'Nochmal' in r['msgH'],
           '2 Hilfen → zurück zu Finden':r['back'],
           'sauber → Kasten 1, kalt in 10 min':r['m3']=='recall' and r['box1'] and 'kalt wieder' in r['msgOk'],
           'dazwischen der nächste Abschnitt':r['nextOther'],
           'nach 10 min kommt kalt wiederholen zuerst':'kalt' in r['hereRev'] and 'Wiederholen' in r['goRev'] and r['m4']==['review',0,True],
           'kalt sauber → Kasten 2, nächste in ~1 Tag':r['box2'] and 'Kasten 2' in r['msgRev'],
           'nach 10 min noch nicht „gelernt“':'0 von' in r['sum2'],'Test am nächsten Tag → Kasten 3 = gelernt':r['m45']==['review',0] and r['box3'] and 'gelernt' in r['msgGel'] and '1 von' in r['sum3'],
           'kalt falsch → Kasten zurück + auffrischen':r['m5']==['review',0] and r['fail'] and r['relearn'] and 'zurück' in r['msgFail'],
           'tiefstes A: vorspielen + neu, kalter Versuch zählt nicht':r['m6']=='review' and r['aRestart'] and r['ignoredInPreview'] and 'vorgespielt' in r['prevMsg'],
           'alter Ablauf weiter erreichbar':r['oldHome'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
