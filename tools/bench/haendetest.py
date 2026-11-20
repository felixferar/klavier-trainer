"""v5.38: Im Zeilen-Modus immer beide Hände, kein Sprung in den alten Ablauf.
Befund 20.11. (Golden Hour, m1795178544628): „Lernen“ in der Songliste startete den alten Ablauf (awNext → „linke Hand allein“),
danach blieb MEM.gs auf den Griffen der linken Hand stehen; zlState passte nicht mehr dazu und legte bei jedem Aufruf einen neuen Stand an
→ Zeile 1 lief in einer Schleife (Mit Noten → Echo → Mit Noten …), obwohl jeder Durchgang ★★★ war.
usage: python3 tools/bench/haendetest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 /* alter Hand-Filter „nur links“ aus dem alten Ablauf */
 MEMS.fly_me={hand:'L'};memSaveAll();
 startLearn(it);o.start={run:!!MEM.run,zlHome:!$('#zlHome').classList.contains('hidden'),oldRun:!$('#memRunV').classList.contains('hidden'),hand:MEM.hand,gs:MEM.gs.length,all:MEM.gsAll&&MEM.gsAll.length};
 /* alter Zustand „linke Hand allein“ hängt noch: Übersicht und Durchgang müssen wieder beide Hände nehmen */
 awUseL(true);zlHome();o.home={gs:MEM.gs.length,all:MEM.gsAll.length};
 awUseL(true);const z=zlState();z.st[0]=1;memSaveAll();const r=zlStart({k:0,stage:2});o.run={gs:MEM.gs.length,b:r.b,same:zlState()===z,st0:zlState().st[0]};
 const gs=MEM.gs;for(let j=r.a;j<=r.b;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(const m of gs[j].mids)memPress(m,'kb')}
 o.after={ok:r.res&&r.res.ok,st0:zlState().st[0],next:r.next,log:(load('kt_v8log')||[]).slice(-1)[0].st};
 /* v5.38: viele Zeilen → nur ein Ausschnitt im Pfad (sonst läuft er über den ✕-Knopf) */
 const big={st:Array(54).fill(0).map((x,i)=>i<5?4:0),song:0},d=document.createElement('div');d.innerHTML=zlPath(big,{k:5});o.path={nodes:d.querySelectorAll('.zlN').length,more:[...d.querySelectorAll('.zlMore')].map(x=>x.textContent),now:d.querySelector('.zlN.now').textContent};
 d.innerHTML=zlPath(big,{k:5},{big:1});o.pathBig=d.querySelectorAll('.zlN').length;
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, SONGS); await br.close()
    print(json.dumps(r, ensure_ascii=False)); print(errs)
    c = {'„Lernen“ aus der Songliste: Zeilen-Übersicht, kein alter Durchgang': not r['start']['run'] and r['start']['zlHome'] and not r['start']['oldRun'],
         'alter Hand-Filter „nur links“ wird im Zeilen-Modus ignoriert (beide Hände, alle 89 Griffe)': r['start']['hand'] == 'LR' and r['start']['gs'] == 89,
         'Übersicht nimmt wieder beide Hände, auch wenn „linke Hand allein“ hängen geblieben ist': r['home']['gs'] == r['home']['all'] == 89,
         'Durchgang nimmt beide Hände; Lernstand bleibt derselbe': r['run']['gs'] == 89 and r['run']['b'] == 12 and r['run']['same'] and r['run']['st0'] == 1,
         'geschaffte Stufe wird gespeichert (keine Schleife Mit Noten → Echo → Mit Noten)': r['after']['ok'] and r['after']['st0'] == 2 and r['after']['next'] == {'k': 0, 'stage': 3} and r['after']['log'].startswith('2'),
         'viele Zeilen: Pfad zeigt nur einen Ausschnitt um die aktuelle Zeile (+ Song)': r['path']['nodes'] == 10 and r['path']['more'] == ['2 ✓', '+43'] and r['path']['now'] == '6' and r['pathBig'] == 7,
         'keine Fehler': not errs}
    for k, v in c.items(): print(('OK  ' if v else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
