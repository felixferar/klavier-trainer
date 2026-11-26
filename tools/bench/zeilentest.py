"""v5.37/v5.43: Auswendig „Zeilen“ im Takt (Design 4b).
Je Zeile: 1 Hören (Vorspielen + Muster) · 2 Mit Noten im Takt · 3 Verblassen (v5.43: Noten 50 % → 30 % → jeder 2. Griff) · 4 Aus dem Kopf.
v5.43: Fehler zählen je Griff, jede Zeile erlaubt 1 Fehler (★★).
Der erste Griff startet den Takt; zu spät → das Lied wartet; zu früh → die App folgt. Sterne: ★★★ richtig + im Takt, ★★ richtig + Timing wackelt, ★ falscher Ton/Hilfe; weiter ab ★★.
Tiefstes A = vorspielen (zählt nie), B = nächsten Griff 1,5 s zeigen. Anlauf = letzte 2 Griffe der vorigen Zeile. Ganzer Song in 60 → 80 → 100 %.
usage: python3 tools/bench/zeilentest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   noSpot=()=>{const r=MEM.run;if(r&&r.spot){const p={k:r.k,stage:r.spot.stage};if(r.spot.rep)p.rep=1;memStop();zlStart(p)}return MEM.run}, /* v5.44: Stellen-Übung hier überspringen (eigener Test: stelletest) */
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   /* im Takt: jeweils warten, bis der Griff fällig ist */
   play=(r,from,to)=>{for(let j=from;j<=to;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}press(j)}},
   playBad=(r,from,to,bad)=>{for(let j=from;j<=to;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}},
   demoEnd=()=>{let n=0;while(R()&&R().demo&&n++<5000)zlTick(R(),0.02)};
 o.home={vis:!$('#zlHome').classList.contains('hidden'),old:$('#memHome').classList.contains('hidden'),nodes:$('#zlPathH').querySelectorAll('.zlN').length,cuts:[...z().cuts],st:z().st.join(''),pat:$('#zlPat').textContent,go:$('#zlGo').textContent,meta:$('#zlMeta').textContent};
 o.pat=[0,1,2,3,4,5].map(k=>zlPattern(k));
 /* Stufe 1 Hören → Stufe 2 */
 zlGo();o.s1={stage:R().stage,demo:!!R().demo,stat:$('#zlStat').textContent};demoEnd();o.s1b={stage:R().stage,st:z().st[0],run:R().run};
 /* Stufe 2 im Takt, sauber → ★★★ */
 let r=R();play(r,r.a,r.b);o.s2={stars:r.res.stars,ok:r.res.ok,next:r.next,slips:r.slips,fb:$('#zlFb').textContent};
 tick(4);r=noSpot();o.s3start={stage:r.stage,fade:r.fade,demo:!!r.demo,a:r.a,b:r.b,txt:$('#zlStat').textContent};
 o.s3vis={a:zlVis(r,r.a),n:zlVis(r,r.a+1),al:zlAlpha(r,r.a+1)};
 /* Verblassen 1/3: einmal zu spät → ★★, trotzdem weiter */
 play(r,r.a,r.a+1);{let n=0;while(n++<300)zlTick(r,0.02)}o.late={late:r.late,vt:+(r.vt-gs[r.a+2].start).toFixed(3),pos:r.pos-r.a};play(r,r.a+2,r.b);
 o.e1={stars:r.res.stars,ok:r.res.ok,late:r.late,sub:r.res.sub,tim:r.res.tim,eh:z().eh[0],st:z().st[0]};
 tick(4);r=noSpot();o.e2start={fade:r.fade,al:zlAlpha(r,r.a+1),demo:!!r.demo,txt:$('#zlStat').textContent};
 /* Verblassen 2/3: zu früh gespielt → ★★ */
 press(r.a);for(let j=r.a+1;j<=r.b;j++)press(j);o.e2={stars:r.res.stars,early:r.early,ok:r.res.ok,st:z().st[0],eh:z().eh[0]};
 tick(4);r=noSpot();o.e3start={fade:r.fade,odd:zlAlpha(r,r.la+1),even:zlAlpha(r,r.la+2)};
 /* Verblassen 3/3: sauber → Stufe 3 fertig */
 play(r,r.a,r.b);o.e3={ok:r.res.ok,st:z().st[0],eh:z().eh[0],next:r.next};tick(4);r=noSpot();
 /* Stufe 4: falscher Ton → ★, gleiche Stufe; Anker bleibt bis gespielt */
 o.s4={stage:r.stage,a:zlVis(r,r.a),n:zlVis(r,r.a+1)};tick(4);o.s4.after4=zlVis(r,r.a);
 press(r.a);o.s4.afterPlay=zlVis(r,r.a);memPress(30,'kb');memPress(31,'kb');o.s4.wrongStat=$('#zlStat').textContent.includes('Falsche Taste')||(zlUI(r),$('#zlStat').textContent.includes('Falsche Taste'));playBad(r,r.a+1,r.b,{[r.a+5]:1});o.s4.cnt={wrong:r.wrong,wraw:r.wraw};
 o.s4.res={stars:r.res.stars,ok:r.res.ok,next:r.next,msg:r.res.msg,kind:r.res.kind,hist:r.res.hist,head:$('#zlFb .zlFbH')?.textContent,hint:!!(zlState().hint&&zlState().hint[0]),sub:r.res.sub};tick(4);r=noSpot();
 /* B: Hilfe → ★ */
 press(r.a);memPress(22,'kb');o.peek={help:r.help,vis:zlVis(r,r.pos)};tick(1.6);o.peek.after=zlVis(r,r.pos);play(r,r.pos,r.b);o.peek.stars=r.res.stars;o.peek.ok=r.res.ok;o.peek.sub=r.res.sub;o.peek.head=$('#zlFb .zlFbH')?.textContent;tick(4);r=noSpot();
 /* v5.41: sitzt erst nach 2× sauber aus dem Kopf */
play(r,r.a,r.b);o.sits={stars:r.res.stars,st:z().st[0],best:z().stars[0],flash:$('#zlPathR').querySelector('.zlN.pop')?.dataset.k,next:r.next};tick(4);r=noSpot();
 o.l2={k:r.k,stage:r.stage,ov:r.la-r.a,pat:$('#zlPatR').textContent};
 /* A mitten im Versuch: vorspielen, nichts zählt */
 demoEnd();play(r,r.a,r.a+2);memPress(31,'kb');memPress(21,'kb');o.aKey={demo:!!r.demo,wrong:r.wrong,pos:r.pos-r.a,stage:r.stage,st:z().st[1]};
 /* Stufe 4 mit Anlauf: erster eigener Griff blitzt kurz auf */
 r=zlStart({k:1,stage:4});press(r.a);tick(0.02);press(r.a+1);o.flash={la:zlVis(r,r.la)};tick(1.0);o.flash.later=zlVis(r,r.la);
 /* ganzer Song: 60 → 80 → 100 % */
 /* v5.40: erst Zeilen 1–4 und 5–8 am Stück, dann der ganze Song; lange Stücke erlauben 1 Fehler je 10 Griffe */
 const zz=z();zz.st=zz.st.map(()=>4);for(const b of zlBlocks(zz.st.length))zz.bd[zlBK(b)]=1;zz.bh={s0:1};for(let q=1;q<8;q++)zz.nd[q]=1; /* v5.55: Übergänge als geschafft (nahttest) */r=zlStart(zlPick(zz));o.song={k:r.k,tempo:r.tempo,a:r.a,b:r.b};play(r,r.a,r.b);o.song.ok1=r.res.ok;o.song.s1=z().song;tick(4);r=noSpot();o.song.tempo2=r.tempo;
playBad(r,r.a,r.b,{3:1,13:1,23:1,33:1,43:1,53:1,63:1,73:1,83:1});o.song.bad=r.res.ok;o.song.tempo3=z().ts;o.song.s2=z().song;o.song.tol=r.res.msg;
 o.runText=$('#zlRun').innerText;
 /* App im Hintergrund / Klavier getrennt */
 memStop();r=zlStart({k:0,stage:2});play(r,r.a,r.a+1);Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});document.dispatchEvent(new Event('visibilitychange'));delete document.visibilityState;
 o.bg={run:!!MEM.run,home:!$('#zlHome').classList.contains('hidden'),why:(load('kt_v8log')||[]).slice(-1)[0].why};
 KB.state='on';r=zlStart({k:0,stage:2});play(r,r.a,r.a);KB.state='off';zlTick(r,0.05);o.kb={run:!!MEM.run,why:(load('kt_v8log')||[]).slice(-1)[0].why};
 /* Schnitt verschieben (Notlösung) */
 memStop();const c0=z().cuts[2];zlMoveCut(2,1);o.cut={from:c0,to:z().cuts[2],st:z().st.join(''),moved:z().moved};
 /* Übernahme v5.36 (cv 1) → v5.37 */
 MEM.rec[zlKey()]={cv:1,n:gs.length,cuts:[0,13,26,35,46,59,72,81],st:[4,4,1,0,4,4,0,0],whole:0};o.from536=JSON.stringify(zlState());
 delete MEM.rec[zlKey()];const v=awState();v.ch.forEach((c,k)=>c.st=[3,3,2,1,3,3,0,0][k]);memSaveAll();o.mig=zlState().st.join('');
 o.log=(load('kt_v8log')||[]).filter(e=>e.zl).map(e=>[e.k,e.mode,e.ok,e.wrong,e.hints,e.abort||0,e.why||'',e.demos,e.n,(e.waits||[]).length,typeof e.dur,e.stars||0,e.slips,e.tempo]);
 o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, SONGS)
        os.makedirs('/tmp/zl', exist_ok=True)
        open('/tmp/zl/log.json', 'w').write(await pg.evaluate("JSON.stringify({kind:'learn',v:'5.37',entries:load('kt_v8log'),snap:{song:'fly_me',title:'Fly Me'}})"))
        await pg.evaluate("()=>{window.AW_NOLOOP=false;const z=zlState();z.st=[4,4,1,0,4,4,0,0];z.stars=[3,2,0,0,2,2,0,0];zlStart({k:2,stage:2});const R=MEM.run;R.demo=null;for(const m of MEM.gs[R.a].mids)memPress(m,'kb');memPress(30,'kb')}")
        await pg.wait_for_timeout(700); await pg.screenshot(path='/tmp/zl/noten.png')
        await pg.evaluate("()=>{zlStart({k:2,stage:4})}"); await pg.wait_for_timeout(400); await pg.screenshot(path='/tmp/zl/kopf.png')
        await pg.evaluate("()=>{const R=MEM.run;R.wrong=0;R.slips=1;R.late=1;for(let j=R.a;j<=R.b;j++)for(const m of MEM.gs[j].mids)memPress(m,'kb')}"); await pg.wait_for_timeout(300); await pg.screenshot(path='/tmp/zl/sterne.png')
        await pg.evaluate("()=>{memStop();zlHome()}"); await pg.wait_for_timeout(200); await pg.screenshot(path='/tmp/zl/home.png', full_page=True)
        await br.close()
    print(json.dumps({k: v for k, v in r.items() if k != 'log'}, ensure_ascii=False)); print('log', r['log']); print(errs)
    lg = r['log']
    c = {'Übersicht: Pfad mit 8 Zeilen + Song, Serie/Minuten, Muster der nächsten Zeile': r['home']['vis'] and r['home']['old'] and r['home']['nodes'] == 9 and 'in Folge' in r['home']['meta'] and r['home']['pat'].startswith('Bass:'),
         'Fly Me: 8 Zeilen aus dem Takt-Schnitt': r['home']['cuts'] == [0, 13, 26, 35, 46, 59, 72, 81],
         'Muster: Zeile 1 „A – D – G – C · immer 5 Töne runter“, Zeile 5/6 = wie Zeile 1/2': r['pat'][0] == 'Bass: A – D – G – C · immer 5 Töne runter' and r['pat'][4].startswith('Wie Zeile 1') and r['pat'][5].startswith('Wie Zeile 2'),
         'Stufe 1 Hören: spielt von selbst vor, danach Stufe 2, wartet auf den ersten Ton': r['s1']['stage'] == 1 and r['s1']['demo'] and 'Hören' in r['s1']['stat'] and r['s1b']['stage'] == 2 and r['s1b']['st'] == 1 and r['s1b']['run'] is False,
         'Stufe 2 im Takt sauber → ★★★, weiter mit Verblassen': r['s2']['stars'] == 3 and r['s2']['ok'] and r['s2']['slips'] == 0 and r['s2']['next'] == {'k': 0, 'stage': 3} and '★★★' in r['s2']['fb'],
         'Verblassen 1/3: kein Vorspielen, Noten halb sichtbar (50 %), Anker voll': r['s3start']['stage'] == 3 and r['s3start']['fade'] == 0 and not r['s3start']['demo'] and 'Verblassen 1/3' in r['s3start']['txt'] and r['s3vis']['a'] == 1 and r['s3vis']['n'] == 0 and r['s3vis']['al'] == 0.5,
         'zu spät: das Lied wartet (eine Viertel-Zählzeit nach der Note), zählt als Wackler': r['late']['late'] == 1 and r['late']['pos'] == 2 and 0.1 < r['late']['vt'] < 0.2,
         'Wackler → ★★, weiter: Verblassen 2/3 (30 %)': r['e1']['stars'] == 2 and r['e1']['ok'] and r['e1']['eh'] == 1 and r['e1']['st'] == 2 and r['e1']['tim'] == '1× zu spät' and r['e2start']['fade'] == 1 and r['e2start']['al'] == 0.3 and not r['e2start']['demo'] and '2/3' in r['e2start']['txt'],
         'zu früh: App folgt, ★★ → Verblassen 3/3: nur jeder 2. Griff': r['e2']['stars'] == 2 and r['e2']['early'] >= 1 and r['e2']['eh'] == 2 and r['e3start']['fade'] == 2 and r['e3start']['odd'] == 0 and r['e3start']['even'] == 0.3,
         'Verblassen 3/3 geschafft → Stufe 3 fertig, weiter Aus dem Kopf': r['e3']['ok'] and r['e3']['st'] == 3 and r['e3']['eh'] == 0 and r['e3']['next'] == {'k': 0, 'stage': 4},
         'Stufe 4: nur Anker, bleibt bis gespielt (auch nach 4 s)': r['s4']['stage'] == 4 and r['s4']['a'] == 1 and r['s4']['n'] == 0 and r['s4']['after4'] == 1 and r['s4']['afterPlay'] == 0,
         'Fehler je Griff: 2× an einer Stelle + 1× woanders = 2 Fehler → ★, Knapp!, danach einfach nochmal, ohne Hilfe (v5.53)': r['s4']['wrongStat'] and r['s4']['cnt'] == {'wrong': 2, 'wraw': 3} and r['s4']['res']['stars'] == 1 and not r['s4']['res']['ok'] and r['s4']['res']['next'] == {'k': 0, 'stage': 4, 't': 0} and not r['s4']['res']['hint'] and 'Hier hakt' not in r['s4']['res']['sub'] and r['s4']['res']['kind'] == 'near' and r['s4']['res']['head'] == 'Knapp!',
         'B: nächster Griff 1,5 s sichtbar, zählt als 1 Fehler → ★★ geschafft, Verlauf 2 → 1': r['peek']['help'] == 1 and r['peek']['vis'] == 1 and r['peek']['after'] == 0 and r['peek']['stars'] == 2 and r['peek']['ok'] and 'Noch 1×' in r['peek']['sub'] and r['peek']['head'] == 'Geschafft!',
         'sauber aus dem Kopf (2. Mal) → Zeile sitzt mit ★★★, Punkt springt, dann Zeile 2 Hören': r['sits']['stars'] == 3 and r['sits']['st'] == 4 and r['sits']['best'] == 3 and r['sits']['flash'] == '0' and r['sits']['next'] == {'k': 1, 'stage': 1},
         'Zeile 2: 2 Griffe Anlauf, Muster wird angezeigt': r['l2']['k'] == 1 and r['l2']['ov'] == 2 and r['l2']['pat'].startswith('Bass:'),
         'tiefstes A mitten im Versuch: vorspielen, nichts zählt': r['aKey']['demo'] and r['aKey']['wrong'] == 0 and r['aKey']['pos'] == 0 and r['aKey']['stage'] == 2 and r['aKey']['st'] == 1,
         'aus dem Kopf mit Anlauf: erster eigener Griff blitzt kurz auf': r['flash']['la'] == 1 and r['flash']['later'] == 0,
         'ganzer Song: 60 % → flüssig geschafft → 70 %; v5.59: mit 9 Griffen daneben, aber flüssig → auch geschafft (80 %)': r['song']['k'] == -1 and r['song']['tempo'] == 0.6 and r['song']['a'] == 0 and r['song']['b'] == 88 and r['song']['ok1'] and r['song']['s1'] == 1 and r['song']['tempo2'] == 0.7 and r['song']['bad'] and r['song']['s2'] == 1 and r['song']['tempo3'] == 8 and 'Durchgespielt' in r['song']['tol'],
         'Übungsbildschirm ohne interne Begriffe': not any(w in r['runText'] for w in ['Häppchen', 'Formteil', 'Last', 'Anschl', 'Naht']),
         'App im Hintergrund / Klavier getrennt: Durchgang endet, Abbruch im Protokoll': not r['bg']['run'] and r['bg']['home'] and r['bg']['why'] == 'bg' and not r['kb']['run'] and r['kb']['why'] == 'kb',
         'Schnitt verschieben: beide Zeilen von vorn': r['cut']['to'] == r['cut']['from'] + 1 and r['cut']['st'][1:3] == '00' and r['cut']['moved'] == 1,
         'Übernahme v5.36 → v5.37 ohne Verlust': '"st":[4,4,1,0,4,4,0,0]' in r['from536'] and '"cv":2' in r['from536'] and '"song":0' in r['from536'],
         'Übernahme alter Stand: 3 3 2 1 3 3 0 0 → 44004400': r['mig'] == '44004400',
         'Protokoll (lernauswertung.py): k, mode, ok, wrong, hints, n, dur, demos, waits, Sterne, Tempo': all(e[10] == 'number' for e in lg) and {e[1] for e in lg} >= {'noten', 'blass', 'kopf', 'song'} and any(e[11] == 2 and e[12] >= 1 for e in lg) and any(e[1] == 'song' and e[13] == 0.7 for e in lg) and any(e[5] == 1 and e[6] == 'A' for e in lg) and not any(e[1] == 'hoeren' for e in lg) and any(e[1] == 'noten' and e[7] >= 1 for e in lg),
         'Version 5.60': r['ver'].startswith('Version 5.60'),
         'keine Fehler': not errs}
    for k, v in c.items(): print(('OK  ' if v else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
