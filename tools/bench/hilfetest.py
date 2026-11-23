"""v5.51: Hilfe im Fluss (ersetzt die eigene Stellen-Übung aus v5.44/45, stelletest).
Nach einem gescheiterten Durchgang (Verblassen / Aus dem Kopf) spielst du die Zeile wieder von vorne; nur an der Problemstelle
(Griff davor + Problemgriff) tauchen die Noten blass auf (45 %, rot gestrichelt). 2× hintereinander dort sauber → Hilfe weg.
Felix 23.11.: „Ich bin im Flow … und dann werde ich rausgeworfen, indem ich eine einzelne Stelle lernen muss … aus dem Song rausgeschossen.“
usage: python3 tools/bench/hilfetest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,bad,upto)=>{bad=bad||{};{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}const end=upto==null?r.b:upto;for(let j=r.pos;j<=end;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 const zz=z();zz.st=[4,4,4,4,4,4,4,3];zz.kc=[2,2,2,2,2,2,2,0];memSaveAll();
 let r=zlStart({k:7,stage:4});play(r,{85:1,86:1});o.f={ok:r.res.ok,sub:r.res.sub,next:r.next,doneT:r.doneT,hint:z().hint&&z().hint[7]&&Object.assign({},z().hint[7])};tick(4);r=R();
 o.run2={k:r.k,stage:r.stage,a:r.a,b:r.b,spot:!!r.spot,hint:r.hint&&[r.hint.a,r.hint.b],al:[83,84,85,86].map(j=>zlAlpha(r,j)),anchor:zlAlpha(r,r.a),tgt:zlVis(r,84)};
 play(r,{},82);zlUI(r);o.run2.bar=$('#zlStat').textContent;
 play(r);o.run2.res={ok:r.res.ok,hintOk:z().hint[7]&&z().hint[7].ok,kc:z().kc[7]};tick(4);r=R();
 play(r,{85:1,84:1});o.reset={ok:r.res.ok,hintOk:z().hint[7]&&z().hint[7].ok,a:z().hint[7]&&z().hint[7].a};tick(4);r=R();
 z().kc[7]=0;play(r);o.c1={ok:r.res.ok,hintOk:z().hint[7]&&z().hint[7].ok};tick(4);r=R();
 o.c2pre={hint:!!r.hint,k:r.k};play(r);o.c2={ok:r.res.ok,hint:!!(z().hint&&z().hint[7]),st:z().st[7]};memStop();
 z().st[7]=3;z().kc[7]=0;z().hint={7:{a:84,b:85,c:85,ok:1,why:'x'}};memSaveAll();r=zlStart({k:7,stage:4});play(r,{81:1,82:1});o.repl={hint:[z().hint[7].a,z().hint[7].b],ok:z().hint[7].ok};memStop();
 z().st[7]=2;z().eh[7]=2;z().hint={7:{a:84,b:85,c:85,ok:0,why:'x'}};memSaveAll();r=zlStart({k:7,stage:3});o.fade={al84:zlAlpha(r,84),al85:zlAlpha(r,85),al86:zlAlpha(r,86)};memStop();
 z().st[7]=1;r=zlStart({k:7,stage:2});o.noten={hint:!!r.hint};play(r,{84:1,85:1,86:1});o.noten.after=!!(z().hint[7]&&z().hint[7].a===84);memStop();
 r=zlStart({k:-1,blk:'0-1',stage:4,t:0});o.blk={hint:!!r.hint};play(r,{5:1,15:1,16:1,18:1});o.blk.next=r.next;memStop();
 o.log=(load('kt_v8log')||[]).filter(e=>e.zl&&e.k===7&&e.mode==='kopf').map(e=>({ok:e.ok,hint:e.hint||null}));o.modes=[...new Set((load('kt_v8log')||[]).map(e=>e.mode))];
 o.ver=$('#verTxt').textContent;return o}"""
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
    c = {'gescheitert → keine Stellen-Übung, nochmal die ganze Zeile; Erklärung im Ergebnis': t(lambda: not r['f']['ok'] and r['f']['next'] == {'k': 7, 'stage': 4, 't': 0} and 'Hier hakt' in r['f']['sub'] and 'Griff 5' in r['f']['sub'] and 'blasser Hinweis' in r['f']['sub'] and r['f']['doneT'] > 2.5),
         'Hilfe gemerkt: Griff davor + Problemgriff (84–85)': t(lambda: r['f']['hint']['a'] == 84 and r['f']['hint']['b'] == 85 and r['f']['hint']['ok'] == 0),
         'nächster Durchgang: ganze Zeile von vorne, nur 84–85 blass (45 %), keine Zieltaste': t(lambda: r['run2']['a'] == 79 and r['run2']['b'] == 88 and not r['run2']['spot'] and r['run2']['hint'] == [84, 85] and r['run2']['al'] == [0, 0.45, 0.45, 0] and r['run2']['anchor'] == 1 and r['run2']['tgt'] == 0),
         'Leiste kündigt die Stelle an': t(lambda: 'gleich die Stelle von eben' in r['run2']['bar']),
         'sauber → Hilfe 1× bestanden, Zeile zählt normal (1× aus dem Kopf)': t(lambda: r['run2']['res'] == {'ok': True, 'hintOk': 1, 'kc': 1}),
         'wieder Fehler an der Stelle → Zähler 0': t(lambda: not r['reset']['ok'] and r['reset']['hintOk'] == 0 and r['reset']['a'] == 84),
         '2× hintereinander sauber → Hilfe verschwindet (spätestens wenn die Zeile sitzt)': t(lambda: r['c1']['hintOk'] == 1 and r['c2pre']['hint'] and r['c2']['ok'] and not r['c2']['hint'] and r['c2']['st'] == 4),
         'neue Problemstelle ersetzt die alte': t(lambda: r['repl']['hint'] == [80, 81] and r['repl']['ok'] == 0),
         'Verblassen 3/3: Hilfe zeigt auch versteckte Griffe (mind. 45 %), Rest wie die Stufe': t(lambda: r['fade']['al84'] == 0.45 and r['fade']['al85'] == 0.45 and r['fade']['al86'] == 0),
         'Mit Noten und am Stück: keine Hilfe nötig/gesetzt': t(lambda: not r['noten']['hint'] and r['noten']['after'] and not r['blk']['hint'] and not (r['blk']['next'] or {}).get('spot')),
         'Protokoll: hint im Durchgang, kein mode „stelle“ mehr': t(lambda: any(e['hint'] == [84, 85] for e in r['log']) and 'stelle' not in r['modes']),
         'Version 5.52': t(lambda: r['ver'].startswith('Version 5.52')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
