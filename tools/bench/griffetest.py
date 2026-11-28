"""v5.78: „Griffe üben“ vor dem Verblassen.
Felix 28.11.: „Ich komme relativ schnell zum Verblassen, obwohl ich die Akkorde noch gar nicht mit den Fingern richtig hinbekomme … erst muss ich die Akkorde
auswendig lernen, wie ich meine Finger machen muss, und dann schnell wechseln.“
 1. Stufe 2 einer neuen Zeile beginnt mit „Griffe üben“: kein Takt, das Lied wartet bei jedem Griff (nichts ist zu spät oder zu früh), Noten voll sichtbar.
 2. Danach dieselbe Zeile im Takt (60 %). Geschafft erst, wenn höchstens 1 Griff mehr als 1 s länger gedauert hat als im Lied (Fehler-Regel bleibt: 1 erlaubt).
 3. 3× hintereinander zu lange gesucht → noch einmal Griffe üben.
 4. Alter Lernstand: Zeilen, die schon über „Mit Noten“ hinaus sind, üben keine Griffe mehr.
usage: python3 tools/bench/griffetest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 /* alter Stand (v5.77) ohne gq: Zeilen 0,1 sitzen, Zeile 2 steht bei Mit Noten, Zeile 3 neu */
 openMem(it);{const z0=zlState();delete z0.gq;z0.st=[4,4,1,0,4,4,0,0];z0.kc=[2,2,0,0,2,2,0,0];memSaveAll();MEMS[it.id]=JSON.parse(JSON.stringify(MEMS[it.id]||{}))}
 const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,from,to,o2)=>{o2=o2||{};for(let j=from;j<=to;j++){if(j>r.a&&!o2.fast){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}if(o2.wait&&o2.wait[j])tick(o2.wait[j]);for(let i=0;i<((o2.bad||{})[j]||0);i++)memPress(30,'kb');press(j)}};
 o.mig=z().gq.slice();
 o.pick=zlPick(z());o.pickName=zlPickName(o.pick,true);
 /* 1. Griffe üben: 8 s nach dem ersten Griff nichts tun – das Lied steht am nächsten Griff, kein „zu spät“ */
 let r=zlStart(o.pick);o.g={gr:r.gr,chip:$('#zlChip').textContent,stat:$('#zlStat').textContent};press(r.a);tick(8);
 o.g.vt=+(r.vt-gs[r.a+1].start).toFixed(3);o.g.late=r.late;o.g.slips=r.slips;o.g.al=zlAlpha(r,r.a+1);
 /* …und dann alles so schnell wie möglich (vor der Zeit) – nie „zu früh“ */
 play(r,r.a+1,r.b,{fast:true});o.g.early=r.early;o.g.res={ok:r.res.ok,stars:r.res.stars,sub:r.res.sub,next:r.next};o.g.gq=z().gq[2];o.g.st=z().st[2];
 tick(4);r=R();o.t={k:r.k,stage:r.stage,gr:r.gr,chip:$('#zlChip').textContent};
 /* 2. im Takt, aber an zwei Griffen je 3 s gesucht → nicht geschafft, dieselbe Stufe im Takt */
 play(r,r.a,r.b,{wait:{[r.la+2]:3,[r.la+4]:3}});o.t.res={ok:r.res.ok,msg:r.res.msg,sub:r.res.sub,next:r.next};o.t.st=z().st[2];o.t.gf=z().gf[2];
 tick(4);r=R();
 /* 3. im Takt, 1× gesucht → geschafft, weiter Verblassen */
 play(r,r.a,r.b,{wait:{[r.la+3]:3}});o.t1={ok:r.res.ok,msg:r.res.msg,next:r.next,st:z().st[2],gf:z().gf[2]};tick(4);memStop();
 /* 4. Griffe üben mit 3 Fehlgriffen → nochmal Griffe üben */
 z().st[3]=1;memSaveAll();r=zlStart({k:3,stage:2});o.gbad={gr:r.gr};play(r,r.a,r.b,{fast:true,bad:{[r.la+1]:1,[r.la+3]:1,[r.la+5]:1}});
 o.gbad.res={ok:r.res.ok,sub:r.res.sub,next:r.next};o.gbad.gq=z().gq[3];tick(4);r=R();o.gbad.again=r.gr;memStop();
 /* 5. dreimal hintereinander zu lange gesucht → zurück zu Griffe üben */
 z().gq[3]=1;z().gf[3]=0;memSaveAll();const fails=[];
 for(let i=0;i<3;i++){r=zlStart({k:3,stage:2});play(r,r.a,r.b,{wait:{[r.la+1]:3,[r.la+3]:3}});fails.push({ok:r.res.ok,sub:r.res.sub,gf:z().gf[3],gq:z().gq[3]});tick(4);memStop()}
 r=zlStart({k:3,stage:2});o.back={fails,gr:r.gr,stat:$('#zlStat').textContent};memStop();
 /* 6. eine Zeile mit langen Tönen: Warten, solange das Lied selbst wartet, ist kein Suchen */
 const lg=(load('kt_v8log')||[]).filter(e=>e.zl);o.log={gr:lg.filter(e=>e.gr===1).length,zoeg:lg.filter(e=>e.zoeg!=null).map(e=>e.zoeg)};
 o.how=$('#zlHow')?$('#zlHow').textContent:document.body.textContent.includes('Griffe üben');
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
    c = {'alter Stand: nur Zeilen ab „Verblassen“ gelten als geübt': t(lambda: r['mig'] == [1, 1, 0, 0, 1, 1, 0, 0]),
         'Weiter-Knopf nennt „Griffe üben“': t(lambda: r['pick'] == {'k': 2, 'stage': 2} and 'Griffe üben' in r['pickName']),
         'Griffe üben: Chip und Leiste sagen „Griffe üben (ohne Takt)“': t(lambda: r['g']['gr'] == 1 and r['g']['chip'] == 'Griffe üben' and 'ohne Takt' in r['g']['stat']),
         'Griffe üben: das Lied steht am nächsten Griff, auch nach 8 s nichts „zu spät“, Noten voll': t(lambda: r['g']['vt'] == 0 and r['g']['late'] == 0 and r['g']['slips'] == 0 and r['g']['al'] == 1),
         'Griffe üben: schneller greifen ist nie „zu früh“ → ★★★': t(lambda: r['g']['early'] == 0 and r['g']['res']['ok'] and r['g']['res']['stars'] == 3),
         'Griffe üben geschafft → dieselbe Zeile im Takt, noch kein Verblassen': t(lambda: r['g']['res']['next'] == {'k': 2, 'stage': 2} and r['g']['gq'] == 1 and r['g']['st'] == 1 and r['t']['k'] == 2 and r['t']['stage'] == 2 and r['t']['gr'] == 0 and r['t']['chip'] == 'Mit Noten'),
         'im Takt, 2× lange gesucht (alle Töne richtig) → nicht geschafft, nochmal im Takt': t(lambda: not r['t']['res']['ok'] and '2× lange gesucht' in r['t']['res']['msg'] and 'ohne langes Suchen' in r['t']['res']['sub'] and r['t']['res']['next'] == {'k': 2, 'stage': 2, 't': 0} and r['t']['st'] == 1 and r['t']['gf'] == 1),
         'im Takt, 1× lange gesucht → geschafft, weiter Verblassen': t(lambda: r['t1']['ok'] and '1× lange gesucht' in r['t1']['msg'] and r['t1']['next'] == {'k': 2, 'stage': 3} and r['t1']['st'] == 2 and r['t1']['gf'] == 0),
         'Griffe üben mit 3 Fehlgriffen → nochmal Griffe üben': t(lambda: r['gbad']['gr'] == 1 and not r['gbad']['res']['ok'] and 'Griffe üben' in r['gbad']['res']['sub'] and r['gbad']['gq'] == 0 and r['gbad']['again'] == 1),
         '3× hintereinander zu lange gesucht → zurück zu Griffe üben': t(lambda: [f['gf'] for f in r['back']['fails']] == [1, 2, 0] and r['back']['fails'][2]['gq'] == 0 and 'Griffe üben' in r['back']['fails'][2]['sub'] and r['back']['gr'] == 1),
         'Protokoll: Griffe üben mit gr=1, im Takt mit Anzahl „lange gesucht“': t(lambda: r['log']['gr'] >= 2 and 2 in r['log']['zoeg'] and 1 in r['log']['zoeg']),
         "„So geht's“ erklärt Griffe üben": t(lambda: r['how']),
         'Version 5.79': t(lambda: r['ver'].startswith('Version 5.79')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
