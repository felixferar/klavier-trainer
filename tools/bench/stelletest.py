"""v5.44: „Stelle üben“ – nach einer gescheiterten Zeile kurz nur die Problemstelle, dann wieder die ganze Zeile.
Felix 22.11.: „Ich mache einen Fehler in der Mitte. Den Anfang kann ich, dann muss ich immer warten, bis ich beim Fehler bin.“
Seine Protokolle: in 27 von 41 Versuchen lag das längste Zögern an derselben Stelle (±1 Griff).
usage: python3 tools/bench/stelletest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,from,to,bad,help,wait)=>{bad=bad||{};help=help||{};wait=wait||{};for(let j=from;j<=to;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}
     if(wait[j])for(let i=0;i<wait[j]*50;i++)zlTick(r,0.02);if(help[j])memPress(AW.helpKey,'kb');for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 const zz=z();zz.st=[4,4,4,4,4,4,4,3];zz.kc=[2,2,2,2,2,2,2,0];memSaveAll();
 /* 1) Aus dem Kopf, Zeile 8 (Griffe 79–88, eigene ab 81): 2 Fehler um Griff 85 → Stelle 83–86 */
 let r=zlStart({k:7,stage:4});play(r,r.a,r.b,{85:1,86:1});o.f={ok:r.res.ok,sub:r.res.sub,next:r.next};tick(3);r=R();
 const sp0=Object.assign({},r.spot);o.spot={k:r.k,stage:r.stage,a:r.a,b:r.b,spot:!!r.spot,anchor:zlVis(r,r.a),n:zlAlpha(r,r.a+1),tgt:zlVis(r,r.a+1),demo:!!r.demo};
 press(r.a);zlUI(r);o.spot.stat=$('#zlStat').textContent;memStop();r=zlStart({k:7,stage:4,spot:sp0});
 /* Finger-Fehler (keine Hilfe, kein Zögern) → Noten der Stelle sichtbar */
 play(r,r.a,r.b,{84:1});o.sf={ok:r.res.ok,next:r.next&&r.next.spot&&{fails:r.next.spot.fails,sv:r.next.spot.sv}};tick(3);r=R();
 play(r,r.a,r.b);o.sok={ok:r.res.ok,head:$('#zlFb .zlFbH').textContent,sub:r.res.sub,next:r.next,st:z().st[7],kc:z().kc[7]};tick(3);r=R();
 o.back={k:r.k,stage:r.stage,spot:!!r.spot,a:r.a,b:r.b};
 /* 2) „vergessen“ (Hilfe B an Griff 86) → Stelle im Kopf-Modus (nur Anker); 2× nicht geschafft → deutlicher; nach 4 → zurück zur Zeile */
 play(r,r.a,r.b,{85:1},{84:1});tick(3);r=R();o.v={type:r.spot&&r.spot.type,sv:r.spot&&r.spot.sv,n:zlAlpha(r,r.a+1),a:r.a,b:r.b};
 const svs=[];for(let i=0;i<4;i++){play(r,r.a,r.b,{[r.a+1]:1});svs.push(r.next&&r.next.spot?r.next.spot.sv:'zeile');o.v['sub'+i]=r.res.sub;tick(3);r=R()}
 o.v.svs=svs;o.v.after={spot:!!r.spot,k:r.k,stage:r.stage};
 /* 3) Zögern ≥ 2 s gilt als „vergessen“ */
 memStop();r=zlStart({k:7,stage:4});play(r,r.a,r.b,{84:1,85:1},{},{85:2.4});o.wait={type:r.next.spot&&r.next.spot.type};memStop();
 /* 4) Stelle am Übergang (Fehler im Anlauf-Bereich) */
 r=zlStart({k:7,stage:4});play(r,r.a,r.b,{80:1,81:1});o.edge={sub:r.res.sub,spot:r.next.spot&&[r.next.spot.a,r.next.spot.b]};memStop();
 /* 5) Verblassen: Stelle startet mit der Blässe der Stufe; Mit Noten: sichtbar */
 z().st[7]=2;z().eh[7]=1;r=zlStart({k:7,stage:3});play(r,r.a,r.b,{85:1,86:1},{86:1});o.fade={sv:r.next.spot&&r.next.spot.sv,type:r.next.spot&&r.next.spot.type};memStop();
 /* 6) geschafft (1 Fehler erlaubt) → keine Stelle; langes Stück → keine Stelle (dort gibt es Nachüben) */
 z().st[7]=3;r=zlStart({k:7,stage:4});play(r,r.a,r.b,{85:1});o.okNoSpot={ok:r.res.ok,spot:!!(r.next&&r.next.spot)};memStop();
 r=zlStart({k:-1,blk:'0-1',stage:4,t:0});play(r,r.a,r.b,{5:1,15:1,16:1,18:1});o.blk={ok:r.res.ok,spot:!!(r.next&&r.next.spot)};memStop();
 /* 7) Protokoll */
 o.log=(load('kt_v8log')||[]).filter(e=>e.zl&&e.mode==='stelle').map(e=>({ok:e.ok,spot:e.spot,why:e.why,parent:e.parent,n:e.n}));
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
    c = {'gescheitert mit Fehlern um Griff 5 → „Hier hakt’s: um Griff 5“, als Nächstes die Stelle': t(lambda: not r['f']['ok'] and 'um Griff 5' in r['f']['sub'] and r['f']['next']['spot']['a'] == 83 and r['f']['next']['spot']['b'] == 86),
         'Stelle: nur Griffe 83–86, kein Vorspielen, Text „Stelle üben“': t(lambda: r['spot']['spot'] and r['spot']['a'] == 83 and r['spot']['b'] == 86 and not r['spot']['demo'] and 'Stelle üben' in r['spot']['stat'] and 'Danach: ganze Zeile' in r['spot']['stat']),
         'Finger-Fehler: Noten der Stelle sichtbar, Zieltaste leuchtet': t(lambda: r['spot']['anchor'] == 1 and r['spot']['n'] == 1 and r['spot']['tgt'] == 1),
         'Stelle muss sauber sein: 1 Fehler → noch einmal': t(lambda: not r['sf']['ok'] and r['sf']['next']['fails'] == 1),
         'Stelle sauber → „Stelle sitzt!“ → ganze Zeile, Lernstand unverändert': t(lambda: r['sok']['ok'] and r['sok']['head'] == 'Stelle sitzt!' and 'ganze Zeile' in r['sok']['sub'] and r['sok']['next'] == {'k': 7, 'stage': 4} and r['sok']['st'] == 3 and r['sok']['kc'] == 0 and r['back'] == {'k': 7, 'stage': 4, 'spot': False, 'a': 79, 'b': 88}),
         'Hilfe genutzt = vergessen: Stelle aus dem Kopf (nur Anker)': t(lambda: r['v']['type'] == 'vergessen' and r['v']['sv'] == 0 and r['v']['n'] == 0),
         'vergessen: 2× nicht → deutlicher (50 %), 4× nicht → zurück zur Zeile': t(lambda: r['v']['svs'] == [0, 0.5, 0.5, 'zeile'] and 'deutlicher' in r['v']['sub1'] and r['v']['after'] == {'spot': False, 'k': 7, 'stage': 4}),
         'langes Zögern (≥ 2 s) = vergessen': t(lambda: r['wait']['type'] == 'vergessen'),
         'Fehler am Übergang → „am Übergang“, Stelle ab Zeilenanfang': t(lambda: 'am Übergang' in r['edge']['sub'] and r['edge']['spot'] == [79, 82]),
         'Verblassen: Stelle in der Blässe der Stufe (30 %)': t(lambda: r['fade']['type'] == 'vergessen' and r['fade']['sv'] == 0.3),
         'geschafft (1 Fehler) → keine Stelle; langes Stück → keine Stelle': t(lambda: r['okNoSpot'] == {'ok': True, 'spot': False} and not r['blk']['ok'] and not r['blk']['spot']),
         'Protokoll: mode stelle mit spot, why, parent': t(lambda: len(r['log']) >= 6 and r['log'][0]['spot'] == [83, 86] and r['log'][0]['why'] == 'finger' and r['log'][0]['parent'] == 4 and r['log'][0]['n'] == 4),
         'Version 5.46': t(lambda: r['ver'].startswith('Version 5.46')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
