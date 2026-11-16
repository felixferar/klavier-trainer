"""v5.30: Naht + Orientierung im Dunkeln, an echten Noten (Fly Me to the Moon).
- Jedes Häppchen ab dem zweiten beginnt mit den letzten 3 Griffen des vorigen (Übergang); der Start-Anker liegt auf dem Übergang
- Positionsleiste im Dunkeln („Häppchen 2 · Griff x von y“), keine Noten
- Hilfe von selbst nach 5 s (vorher nicht); Souffleur: letzter Griff grau, gesuchter farbig, die nächsten zwei blass
- Am Stück aus dem Kopf scheitert an der Naht → knifflige Stelle um die Naht, dann wieder am Stück
usage: python3 tools/bench/nahttest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
S = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(ns)=>{window.toast=()=>{};window.playTone=()=>{};window.playClick=()=>{};window.AW_NOLOOP=true;KB.state='off';const o={};
 const it={id:'naht',type:'midi',title:'Fly',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);openMem(it);
 const gs=MEM.gs,C=MEM.C,v=MEM.rec.v10,tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs[j].mids)memPress(m,'kb')};
 v.ch[0].st=3;v.ch[1].st=1;memSaveAll();
 /* Übergang */
 let p=awPick();o.p=p;awNext();let R=MEM.run;awDraw();o.lead=[R.lead,R.a,C[1].a-3,R.anchor,R.drawState,R.n];
 /* Anker spielen → dunkel, Positionsleiste */
 play(R.a);tick(0.2);awDraw();o.dark=[R.drawState,R.posTxt];
 /* weiterspielen bis zum ersten Griff von Häppchen 2, dann hängen: vor 5 s keine Hilfe, danach Souffleur */
 while(R.pos<C[1].a)play(R.pos);tick(4);awDraw();o.before5=[R.show,R.hints];
 const alphas=[];const ctx=$('#memCv').getContext('2d'),fr=ctx.fillRect;ctx.fillRect=function(){alphas.push(+this.globalAlpha.toFixed(2));return fr.apply(this,arguments)};
 tick(1.5);awDraw();ctx.fillRect=fr;o.after5=[R.show===R.pos,R.hints,R.drawState,R.autoHelp,R.posTxt];o.alphas=[alphas.includes(0.45),alphas.includes(0.3),alphas.includes(1)];o.helpMsg=$('#memMsg').textContent;
 play(R.pos);o.helpGone=R.show==null;let g=0;while(!R.done&&g++<300){if(R.pos<=R.b)play(R.pos);tick(0.1)}o.headRes=[R.ok,R.hints];
 /* sauber nochmal → Häppchen 2 aus dem Kopf, dann Fluss */
 awNext();R=MEM.run;g=0;while(!R.done&&g++<300){if(R.pos<=R.b)play(R.pos);tick(0.1)}o.headOk=[R.mode,R.ok,v.ch[1].st];
 { awNext();const RR=MEM.run;let q=RR.a;g=0;while(!RR.done&&g++<400000){awTick(RR,1/120);if(RR.wait0){tick(0.3);play(q++);continue}while(q<=RR.b&&RR.vt>=gs[q].start+0.03)play(q++)}o.flowOk=[RR.mode,RR.ok,RR.lead,v.ch[1].st] }
 /* am Stück aus dem Kopf: hängt an der Naht (Hilfe), danach knifflige Stelle um die Naht */
 p=awPick();o.chain=[p.mode,p.s,p.e];awNext();R=MEM.run;g=0;while(!R.done&&g++<400){if(R.pos===C[1].a&&!R.h1){R.h1=1;memPress(22,'kb')}if(R.pos<=R.b)play(R.pos);tick(0.1)}o.chainRes=[R.ok,R.hints];
 p=awPick();o.spot=[p.mode,p.a,p.b,C[1].a];awNext();R=MEM.run;awDraw();o.spotRun=[R.mode,R.a,R.b,R.anchor,R.dark];g=0;while(!R.done&&g++<300){if(R.pos<=R.b)play(R.pos);tick(0.1)}o.spotRes=[R.ok,!!v.spot];
 o.back=awPick().mode;
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 753, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, S['fly_me']); await pg.screenshot(path='/tmp/nahttest.png'); await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    c = {'Häppchen 2 beginnt mit den letzten 3 Griffen von Häppchen 1 (Anker darauf)': r['p'] == {'k': 1, 'mode': 'head'} and r['lead'][0] == 3 and r['lead'][1] == r['lead'][2] and r['lead'][3] and r['lead'][4] == 'anker' and r['lead'][5] == 16,
         'im Dunkeln: Positionsleiste „Übergang · Griff …“': r['dark'][0] == 'dunkel' and r['dark'][1].startswith('Übergang · Griff 2 von 3'),
         'vor 5 s keine Hilfe': r['before5'] == [None, 0],
         'nach 5 s Hilfe von selbst, Position „Häppchen 2 · Griff 1 von 13“': r['after5'][0] and r['after5'][1] == 1 and r['after5'][2] == 'hilfe' and r['after5'][3] == 1 and r['after5'][4] == 'Häppchen 2 · Griff 1 von 13',
         'Souffleur: letzter Griff grau (blass), gesuchter farbig, nächste blass': r['alphas'] == [True, True, True] and 'grau' in r['helpMsg'],
         'Griff gespielt → Hilfe weg; Durchgang mit Hilfe nicht sauber, sauber danach': r['helpGone'] and r['headRes'] == [False, 1] and r['headOk'] == ['head', True, 2],
         'Im Fluss mit Übergang': r['flowOk'] == ['flow', True, 3, 3],
         'am Stück aus dem Kopf: Hilfe an der Naht → nicht sauber': r['chain'] == ['snowk', 0, 1] and r['chainRes'] == [False, 1],
         'danach knifflige Stelle um die Naht (±3 Griffe), dunkel mit Anker; geschafft → zurück am Stück': r['spot'][0] == 'spot' and r['spot'][1] <= r['spot'][3] <= r['spot'][2] and r['spotRun'][3] and r['spotRun'][4] and r['spotRes'] == [True, False] and r['back'] == 'snowk',
         'keine Fehler': not errs}
    for k, x in c.items(): print(('OK  ' if x else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
