"""v5.79: Akkorde zählen nur, wenn alle Töne gleichzeitig angeschlagen werden.
Felix 28.11.: „Akkorde werden noch nicht zusammengezählt. Wenn ich die 3 Noten nacheinander spiele, geht es einfach weiter. Es soll aber gleichzeitig gespielt werden.“
 1. Akkordtöne nacheinander (je 0,3 s Abstand) → der Griff ist NICHT geschafft, das Lied wartet weiter; Hinweis „gleichzeitig anschlagen“; kein Fehler.
 2. Danach den ganzen Akkord zusammen → weiter.
 3. Leicht versetzt (je 0,05 s, zusammen 0,1 s) → zählt als gleichzeitig.
 4. Einzeltöne sind nicht betroffen. Protokoll: zs = wie oft nicht gleichzeitig.
usage: python3 tools/bench/akkordtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{const msgs=[];window.toast=(t)=>msgs.push(t);window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,z=()=>zlState();
 const tick=sec=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){if(MEM.run!==r0)break;zlTick(r0,0.02)}};
 /* eine Zeile mit einem Akkord (≥ 2 Töne) suchen, Griffe üben */
 let k=-1,j=-1;for(let q=0;q<MEM.C.length&&k<0;q++){const r=zlStart({k:q,stage:2});for(let i=r.a+1;i<=r.b;i++)if(gs[i].mids.size>=2){k=q;j=i;break}memStop()}
 o.found={k,j,n:j>=0?gs[j].mids.size:0};if(k<0)return o;
 let r=zlStart({k,stage:2});o.gr=r.gr;
 const upTo=r=>{for(let i=r.a;i<j;i++){for(const m of gs[i].mids)memPress(m,'kb');tick(0.3)}};
 upTo(r);o.atChord=r.pos===j;const w0=r.wrong;
 /* 1. nacheinander */
 for(const m of gs[j].mids){memPress(m,'kb');tick(0.3)}
 o.seq={pos:r.pos===j,wrong:r.wrong-w0,apart:r.apart,msg:msgs.some(t=>t.includes('gleichzeitig'))};
 /* 2. zusammen */
 for(const m of gs[j].mids)memPress(m,'kb');o.together=r.pos===j+1;
 /* 3. leicht versetzt: nächster Akkord in der Zeile (oder derselbe nach Neustart) */
 memStop();r=zlStart({k,stage:2});upTo(r);for(const m of gs[j].mids){memPress(m,'kb');tick(0.04)}o.near={pos:r.pos===j+1,apart:r.apart||0};
 /* 4. ganze Zeile sauber zu Ende → geschafft, Protokoll */
 memStop();r=zlStart({k,stage:2});upTo(r);for(const m of gs[j].mids){memPress(m,'kb');tick(0.3)}for(const m of gs[j].mids)memPress(m,'kb');
 for(let i=j+1;i<=r.b;i++){for(const m of gs[i].mids)memPress(m,'kb');tick(0.3)}
 o.fin={done:!!r.res,ok:r.res&&r.res.ok,wrong:r.wrong};tick(4);memStop();
 const lg=(load('kt_v8log')||[]).filter(e=>e.zl);o.zs=lg.map(e=>e.zs||0);
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
    c = {'Zeile mit Akkord (≥ 2 Töne) gefunden, Griffe üben, Akkord erreicht': t(lambda: r['found']['j'] >= 0 and r['gr'] == 1 and r['atChord']),
         'nacheinander (0,3 s Abstand) → Griff nicht geschafft, kein Fehler, Hinweis „gleichzeitig“': t(lambda: r['seq']['pos'] and r['seq']['wrong'] == 0 and r['seq']['apart'] >= 1 and r['seq']['msg']),
         'danach zusammen angeschlagen → weiter': t(lambda: r['together']),
         'leicht versetzt (0,04 s je Ton) → zählt als gleichzeitig': t(lambda: r['near']['pos'] and r['near']['apart'] == 0),
         'Zeile danach sauber zu Ende → geschafft (nicht gleichzeitig ist kein Fehler)': t(lambda: r['fin']['done'] and r['fin']['ok'] and r['fin']['wrong'] == 0),
         'Protokoll: zs zählt „nicht gleichzeitig“': t(lambda: r['zs'] == [1]),
         'Version 5.80': t(lambda: r['ver'].startswith('Version 5.80')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
