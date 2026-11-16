"""v5.31: Schneeball-Dauerschleife behoben (echte Noten Fly Me, Schneeball über Häppchen 1–3).
1. Kein „zurück auf Los“: Fehler im 2./3. Häppchen → Restbogen ab 4 Griffen vor diesem Häppchen bis zum Ende (aus dem Kopf bzw. im Fluss), dann wieder alles
2. Hilfe am Stück: im Fluss erscheint bei Fehlgriff oder B der gesuchte Griff und bleibt, bis er gespielt ist
3. Anti-Dauerschleife: derselbe Schritt 3× gescheitert → 1× mit Noten (Übergang + Häppchen), danach zählt es neu
usage: python3 tools/bench/schneeballtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
S = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(ns)=>{window.toast=()=>{};window.playTone=()=>{};window.playClick=()=>{};window.AW_NOLOOP=true;KB.state='off';const o={};
 const it={id:'sb',type:'midi',title:'Fly',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);openMem(it);
 const gs=MEM.gs,C=MEM.C,v=MEM.rec.v10,tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs[j].mids)memPress(m,'kb')};
 const wrongKeyOf=j=>{let m=Math.max(...gs[j].mids)+1;while(gs[j].mids.has(m)||(gs[j+1]&&gs[j+1].mids.has(m)))m++;return m};
 const wait=(f)=>{const R=MEM.run;let g=0;while(!R.done&&g++<600&&MEM.run===R){if(R.pv){tick(0.5);continue}if(R.pos<=R.b){if(f)f(R);play(R.pos)}tick(0.1)}return R};
 const flow=(f)=>{const R=MEM.run;let q=R.a,g=0;while(!R.done&&g++<400000&&MEM.run===R){awTick(R,1/120);if(R.wait0&&!R.pv){tick(0.3);play(q++);continue}while(q<=R.b&&!R.pv&&R.vt>=gs[q].start+0.03*R.speed){if(f&&f(R,q)===false)break;play(q++)}}return R};
 for(let k=0;k<3;k++)v.ch[k].st=3;memSaveAll();
 /* 1a: am Stück aus dem Kopf 1–3, Hilfe im 3. Häppchen → Restbogen */
 awStart({k:2,mode:'snowk',s:0,e:2});let R=wait(R=>{if(R.pos===C[2].a+1&&!R.h){R.h=1;memPress(22,'kb')}});o.fail1=[R.ok,R.hints];
 let p=awPick();o.rest=[p.mode,p.rest,p.a,C[2].a-4,p.b,R.b];awNext();R=MEM.run;awDraw();o.restRun=[R.dark,R.anchor,R.timed,R.drawState];R=wait();o.restOk=[R.ok,!!v.spot];
 /* 1b + 2: im Fluss 1–3, Fehlgriff im 3. Häppchen → Griff erscheint sofort und bleibt; danach Restbogen im Fluss */
 awStart({k:2,mode:'snow',s:0,e:2});R=MEM.run;R=flow((R,q)=>{if(q===C[2].a+2&&!R.w){R.w=1;memPress(wrongKeyOf(q),'kb');R.showAfterWrong=[R.show===q,R.hints];awDraw();R.st=R.drawState;tick(1.5);R.stays=R.show===q}});
 o.flowWrong=[R.showAfterWrong,R.st,R.stays,R.ok];p=awPick();o.restFlow=[p.mode,p.rest,p.a];awNext();o.restFlowRun=[MEM.run.timed,MEM.run.sTimed];R=flow();o.restFlowOk=[R.ok,!!v.spot];
 /* B im Fluss am Stück */
 awStart({k:2,mode:'snow',s:0,e:2});R=MEM.run;tick(0.3);play(R.a);tick(0.2);memPress(22,'kb');o.bInFlow=[R.show===R.pos,R.hints];memStop();
 /* 3: dreimal derselbe Schritt gescheitert → einmal mit Noten */
 delete v.cf;delete v.spot;const res=[];
 for(let i=0;i<3;i++){awStart({k:2,mode:'snowk',s:0,e:2});R=wait(R=>{if(R.pos===C[2].a+1&&!R.h){R.h=1;memPress(22,'kb')}});p=awPick();res.push([p.mode,p.rest?'rest':p.learn?'learn':'spot']);if(i<2){awNext();wait()}}
 o.loop=res;awNext();R=MEM.run;awDraw();o.learnRun=[R.mode,R.sLearn,R.dark,R.drawState,R.a,C[2].a-4,R.b,C[2].b];R=wait(R=>{if(R.pos===R.a+2&&!R.w){R.w=1;memPress(wrongKeyOf(R.pos),'kb')}});
 o.learnOk=[R.ok,R.wrong,!!v.spot,(v.cf||{})['snowk:0-2']||0];
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 753, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, S['fly_me']); await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    c = {'aus dem Kopf am Stück: Hilfe im 3. Häppchen → nicht sauber': r['fail1'] == [False, 1],
         'Restbogen statt zurück auf Los: ab 4 Griffen vor Häppchen 3 bis zum Ende, dunkel mit Anker, wartend': r['rest'][0] == 'spot' and r['rest'][1] == 1 and r['rest'][2] == r['rest'][3] and r['rest'][4] == r['rest'][5] and r['restRun'] == [True, True, False, 'anker'] and r['restOk'] == [True, False],
         'im Fluss am Stück: Fehlgriff → Griff erscheint sofort, bleibt; nicht sauber': r['flowWrong'][0] == [True, 1] and r['flowWrong'][1] == 'hilfe' and r['flowWrong'][2] and r['flowWrong'][3] is False,
         'danach Restbogen im Fluss, geschafft → wieder alles': r['restFlow'][0] == 'spot' and r['restFlow'][1] == 1 and r['restFlowRun'] == [True, True] and r['restFlowOk'] == [True, False],
         'B im Fluss am Stück zeigt den Griff': r['bInFlow'] == [True, 1],
         'Anti-Dauerschleife: 1. und 2. Fehlschlag → Restbogen, 3. → einmal mit Noten': r['loop'] == [['spot', 'rest'], ['spot', 'rest'], ['spot', 'learn']],
         'mit Noten: Übergang + Häppchen 3, Noten sichtbar, 1 Vertipper ok, danach zählt es neu': r['learnRun'][:4] == ['spot', True, False, 'finden'] and r['learnRun'][4] == r['learnRun'][5] and r['learnRun'][6] == r['learnRun'][7] and r['learnOk'] == [True, 1, False, 0],
         'keine Fehler': not errs}
    for k, x in c.items(): print(('OK  ' if x else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
