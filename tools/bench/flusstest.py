"""v5.53: im Fluss bleiben – nach einem Fehler einfach nochmal (keine Hilfe an der Stelle, kein „Hier hakt’s“),
Vorspielen überspringen per Knopf oder tiefem A. Felix 24.11.: „Dass die Fehlerstellen neu angezeigt werden … zerstört komplett den Flow.“
„… ein Knopf, dass ich das schnell überspringen kann, ohne dass ich die ganze Animation von vorne sehen muss.“
usage: python3 tools/bench/flusstest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,bad)=>{bad=bad||{};{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}for(let j=r.pos;j<=r.b;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 const zz=z();zz.st=[4,4,4,4,4,4,4,3];zz.kc=[2,2,2,2,2,2,2,0];zz.hint={7:{a:84,b:85,c:85,ok:0,why:'alt'}};memSaveAll();
 let r=zlStart({k:7,stage:4});o.old={hint:!!r.hint};play(r,{85:1,86:1});o.f={ok:r.res.ok,sub:r.res.sub,next:r.next,doneT:r.doneT,hintState:!!z().hint};tick(4);r=R();
 o.run2={k:r.k,stage:r.stage,a:r.a,hint:!!r.hint,al:[84,85,86].map(j=>zlAlpha(r,j))};memStop();
 /* Überspringen per Knopf */
 r=zlStart({k:7,stage:4});zlDemo(r,false);tick(0.5);zlUI(r);o.btn={demo:!!r.demo,vis:!$('#zlSkip').classList.contains('hidden'),bar:$('#zlStat').textContent};$('#zlSkip').click();
 o.btn.after={demo:!!r.demo,vis:!$('#zlSkip').classList.contains('hidden'),pos:r.pos===r.a};press(r.a);o.btn.started=r.pos>r.a;memStop();
 /* tiefes A: außerhalb = vorspielen, währenddessen = überspringen */
 r=zlStart({k:7,stage:4});memPress(AW.restart,'kb');o.a1=!!r.demo;tick(0.3);memPress(AW.restart,'kb');o.a2=!r.demo;press(r.a);o.a3=r.pos>r.a;memStop();
 /* Hören (Stufe 1) überspringen → Mit Noten */
 z().st[0]=0;memSaveAll();r=zlStart({k:0,stage:1});tick(0.3);o.h={demo:!!r.demo};$('#zlSkip').click();o.h.after={demo:!!r.demo,stage:r.stage};memStop();
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
    c = {'alte gespeicherte Hilfe wird nicht mehr gezeigt': t(lambda: not r['old']['hint']),
         'gescheitert → einfach nochmal dieselbe Zeile, kein „Hier hakt’s“, kurze Pause': t(lambda: not r['f']['ok'] and r['f']['next'] == {'k': 7, 'stage': 4, 't': 0} and 'Hier hakt' not in r['f']['sub'] and 'Hinweis' not in r['f']['sub'] and r['f']['doneT'] < 2.5 and not r['f']['hintState']),
         'nächster Durchgang ohne blasse Hilfe (alles aus dem Kopf)': t(lambda: r['run2']['k'] == 7 and not r['run2']['hint'] and r['run2']['al'] == [0, 0, 0]),
         'Knopf „Überspringen“ nur beim Vorspielen sichtbar, Leiste bleibt kurz': t(lambda: r['btn']['demo'] and r['btn']['vis'] and 'tiefes A' not in r['btn']['bar'] and not r['btn']['after']['vis']),
         'Knopf → sofort dran, erster Griff startet': t(lambda: not r['btn']['after']['demo'] and r['btn']['after']['pos'] and r['btn']['started']),
         'tiefes A: startet Vorspielen, nochmal = überspringen, dann spielbar': t(lambda: r['a1'] and r['a2'] and r['a3']),
         'Hören überspringen → gleich Mit Noten': t(lambda: r['h']['demo'] and not r['h']['after']['demo'] and r['h']['after']['stage'] == 2),
         'Version 5.53': t(lambda: r['ver'].startswith('Version 5.53')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
