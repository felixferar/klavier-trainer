"""v5.43: „Macht keinen Spaß“ – fairer zählen, Verblassen statt Echo, Fortschritt zeigen.
Befund 22.11. (Felix' Protokolle, ohne Frust-Versuche): 15 von 40 geschafft; mit 1 erlaubten Fehler wären es 25 von 40.
20 Versuche mit mehr Fehlern als Griffen (Frust-Drücken), davon 12 im Echo.
usage: python3 tools/bench/spasstest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   noSpot=()=>{const r=MEM.run;if(r&&r.spot){const p={k:r.k,stage:r.spot.stage};if(r.spot.rep)p.rep=1;memStop();zlStart(p)}return MEM.run}, /* v5.44: Stellen-Übung hier überspringen (eigener Test: stelletest) */
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,from,to,bad)=>{bad=bad||{};for(let j=from;j<=to;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30+i%5,'kb');press(j)}};
 const zz=z();zz.st=[4,4,4,4,4,4,4,2];zz.kc=[2,2,2,2,2,2,2,0];memSaveAll();
 /* 1) Frust: 8 Tasten in einer Sekunde → 1 Fehler, Hinweis „Kurz durchatmen“, nach 3 s weg */
 let r=zlStart({k:7,stage:4});press(r.a);for(let i=0;i<8;i++){memPress(30+i,'kb');zlTick(r,0.05)}zlUI(r);
 o.mash={wrong:r.wrong,wraw:r.wraw,txt:$('#zlStat').textContent};for(let i=0;i<160;i++)zlTick(r,0.02);zlUI(r);o.mash.later=$('#zlStat').textContent;
 /* laufender Fortschritt: „noch x Griffe“ */
 play(r,r.a+1,r.a+3);zlUI(r);o.left=$('#zlStat').textContent;memStop();
 /* 2) Verlauf + „Besser!“: 4 → 2 Fehler */
 r=zlStart({k:7,stage:4});play(r,r.a,r.b,{80:1,82:1,84:1,86:1});o.h1={kind:r.res.kind,head:$('#zlFb .zlFbH').textContent};tick(4);r=noSpot();
 play(r,r.a,r.b,{81:1,85:1});o.h2={kind:r.res.kind,head:$('#zlFb .zlFbH').textContent,hist:$('#zlFb .zlHist')?.textContent,sub:r.res.sub,cls:$('#zlFb').className};tick(4);r=noSpot();
 memStop();r=zlStart({k:6,stage:4});play(r,r.a,r.b,{71:1,73:1,75:1,77:1,79:1});tick(4);r=noSpot();play(r,r.a,r.b,{72:1,74:1,76:1});o.h3={kind:r.res.kind,head:$('#zlFb .zlFbH').textContent,cls:$('#zlFb').className};memStop();r=zlStart({k:7,stage:4});
 /* 3) Geschafft: grüne Erfolgsanzeige, bleibt etwas länger stehen */
 play(r,r.a,r.b);o.win={kind:r.res.kind,cls:$('#zlFb').className,head:$('#zlFb .zlFbH').textContent,doneT:+r.doneT.toFixed(2)};memStop();
 /* 4) Verblassen: Stufe 2/3 dreimal nicht geschafft → wieder 1/3 */
 z().st[7]=2;z().eh[7]=1;r=zlStart({k:7,stage:3});o.f={start:r.fade};
 for(let i=0;i<3;i++){play(r,r.a,r.b,{81:1,83:1,85:1});o.f['s'+i]={ok:r.res.ok,eh:z().eh[7],sub:r.res.sub};tick(4);r=noSpot()}
 o.f.after={fade:r.fade,stage:r.stage,txt:$('#zlStat').textContent};memStop();
 /* 5) Verblassen 1/3 ohne Vorspielen; B hilft auch bei halb sichtbaren Noten */
 z().eh[7]=0;r=zlStart({k:7,stage:3});o.f1={demo:!!r.demo};press(r.a);memPress(AW.helpKey,'kb');o.f1.help=r.help;o.f1.peek=zlVis(r,r.pos);memStop();
 /* 6) Protokoll */
 o.log=(load('kt_v8log')||[]).filter(e=>e.zl).map(e=>({mode:e.mode,ok:e.ok,wrong:e.wrong,wraw:e.wraw,fade:e.fade,tol:e.tol}));
 o.help=document.body.innerHTML.includes('Verblassen</span>')&&document.body.innerHTML.includes('höchstens 1 Griff daneben')&&document.body.innerHTML.includes('einfach nochmal von vorne</b>, ohne Unterbrechung')&&document.body.innerHTML.includes('tiefes A</b>');
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 800, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        try: r = await pg.evaluate(JS, SONGS)
        except Exception as e: r = {'crash': str(e)[:300]}
        await br.close()
    print(json.dumps(r, ensure_ascii=False))
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'Frust-Drücken: 8 Tasten = 1 Fehler, Hinweis „Kurz durchatmen“, verschwindet wieder': t(lambda: r['mash']['wrong'] == 1 and r['mash']['wraw'] == 8 and 'Kurz durchatmen' in r['mash']['txt'] and 'Kurz durchatmen' not in r['mash']['later']),
         'beim Spielen: „noch x Griffe“': t(lambda: 'noch 6 Griffe' in r['left']),
         'Verlauf: 4 → 2 Fehler = „Knapp!“, Verlauf 4 → 2 sichtbar': t(lambda: r['h1']['kind'] == 'again' and r['h1']['head'] == 'Noch einmal' and r['h2']['kind'] == 'near' and r['h2']['head'] == 'Knapp!' and r['h2']['hist'].startswith('4→2') and 'Hier hakt' not in r['h2']['sub'] and 'near' in r['h2']['cls']),
         'Verlauf: 5 → 3 Fehler = „Besser!“': t(lambda: r['h3']['kind'] == 'better' and r['h3']['head'] == 'Besser!' and 'better' in r['h3']['cls']),
         'Geschafft: grüne Erfolgsanzeige, bleibt länger stehen': t(lambda: r['win']['kind'] == 'win' and 'win' in r['win']['cls'] and r['win']['head'] in ('Geschafft!', 'Perfekt!') and r['win']['doneT'] > 2.0),
         'Verblassen 2/3: 3× nicht geschafft → zurück auf 1/3': t(lambda: r['f']['start'] == 1 and r['f']['s0']['eh'] == 1 and r['f']['s1']['eh'] == 1 and r['f']['s2']['eh'] == 0 and 'deutlicher' in r['f']['s2']['sub'] and r['f']['after']['fade'] == 0 and '1/3' in r['f']['after']['txt']),
         'Verblassen ohne Vorspielen, B hilft': t(lambda: not r['f1']['demo'] and r['f1']['help'] == 1 and r['f1']['peek'] == 1),
         'Protokoll: wraw, fade, tol, mode blass': t(lambda: all(isinstance(e['wraw'], int) and e['wraw'] >= e['wrong'] for e in r['log']) and any(e['mode'] == 'blass' and e['fade'] == 1 for e in r['log']) and all(e['tol'] == 1 for e in r['log'] if e['mode'] in ('kopf', 'blass'))),
         'Hilfetext erklärt Verblassen und 1 erlaubten Fehler': t(lambda: r['help']),
         'keine JS-Fehler': not errs and 'crash' not in r}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
