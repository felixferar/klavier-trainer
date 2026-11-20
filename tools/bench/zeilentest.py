"""v5.36: Auswendig „Zeilen“ – 4 feste Stufen je Zeile (Vorspielen · Mit Noten · Halb blind · Aus dem Kopf), weiter nur ohne Vertipper und ohne Hilfe,
Anlauf = letzte 2 Griffe der vorigen Zeile, tiefstes A = vorspielen (zählt nie), B = nächsten Griff 1,5 s zeigen, am Ende ganzer Song (bis 2 Vertipper).
usage: python3 tools/bench/zeilentest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,tick=(sec)=>{for(let t=0;t<sec;t+=0.05){const R=MEM.run;if(!R)break;zlTick(R,0.05)}},
   play=(R,from,to)=>{for(let j=from;j<=to;j++){for(const m of gs[j].mids)memPress(m,'kb');tick(0.3)}},R=()=>MEM.run,z=()=>zlState();
 o.home={vis:!$('#zlHome').classList.contains('hidden'),old:$('#memHome').classList.contains('hidden'),tiles:$('#zlTilesH').querySelectorAll('.zlT').length,cuts:[...z().cuts],st:z().st.join('')};
 o.line8end=+gs[gs.length-1].end.toFixed(1);
 /* Zeile 1, Stufe 1: Vorspielen läuft von selbst, danach Stufe 2 */
 zlGo();o.s1={stage:R().stage,demo:!!R().demo,stat:$('#zlStat').textContent};tick(20);o.s1b={stage:R().stage,demo:!!R().demo,st:z().st[0]};
 /* Stufe 2 sauber → Stufe 3 */
 let r=R();play(r,r.a,r.b);o.s2={done:r.done,ok:r.res.ok,next:r.next,msg:r.res.msg};tick(1.6);
 r=R();o.s3vis={first:zlVis(r,r.a),last:zlVis(r,r.b),stage:r.stage};
 /* Stufe 3 mit einem korrigierten Vertipper → dieselbe Stufe */
 play(r,r.a,r.a+2);memPress(30,'kb');o.wrongStop={pos:r.pos-r.a,wrong:r.wrong,stat:$('#zlStat').textContent.includes('Falsche Taste')||(zlUI(r),$('#zlStat').textContent.includes('Falsche Taste'))};play(r,r.a+3,r.b);
 o.s3={ok:r.res.ok,next:r.next,msg:r.res.msg};tick(1.6);r=R();play(r,r.a,r.b);tick(1.6);
 /* Stufe 4: nur der erste Griff ist zu sehen, bleibt bis gespielt */
 r=R();o.s4a={stage:r.stage,a:zlVis(r,r.a),n:zlVis(r,r.a+1)};tick(5);o.s4a.after5s=zlVis(r,r.a);play(r,r.a,r.a);o.s4a.afterPlay=zlVis(r,r.a);
 memPress(22,'kb');o.peek={help:r.help,vis:zlVis(r,r.pos)};tick(1.6);o.peek.after=zlVis(r,r.pos);play(r,r.pos,r.b);o.s4b={ok:r.res.ok,next:r.next,msg:r.res.msg};tick(1.6);
 r=R();play(r,r.a,r.b);o.sits={ok:r.res.ok,msg:r.res.msg,st:z().st[0],next:r.next,flash:$('#zlTilesR').querySelector('.zlT.pop')?.dataset.k,tile:$('#zlTilesR').querySelector('[data-k="0"]').className};
 tick(1.6);r=R();o.l2={k:r.k,stage:r.stage,a:r.a,la:r.la,ov:r.la-r.a};
 /* A mitten im Versuch: vorspielen, zählt nicht */
 tick(20);play(r,r.a,r.a+3);memPress(31,'kb');memPress(21,'kb');o.aKey={demo:!!r.demo,wrong:r.wrong,pos:r.pos-r.a,stage:r.stage,st:z().st[1]};
 /* Stufe 4 in Zeile 2: Anlauf-Anker, danach blitzt der erste Griff der eigentlichen Zeile kurz auf */
 r=zlStart({k:1,stage:4});o.flash={anchor:zlVis(r,r.a),la0:zlVis(r,r.la)};play(r,r.a,r.a);tick(0.0);for(const m of gs[r.a+1].mids)memPress(m,'kb');o.flash.laNow=zlVis(r,r.la);tick(1.0);o.flash.laLater=zlVis(r,r.la);
 /* ganzer Song: bis 2 Vertipper erlaubt, 3 nicht */
 z().st=z().st.map(()=>4);r=zlStart(zlPick(z()));o.song={k:r.k,stage:r.stage,a:r.a,b:r.b};memPress(30,'kb');memPress(31,'kb');play(r,r.a,r.b);o.song.ok2=r.res.ok;o.song.whole=z().whole;
 z().whole=0;r=zlStart({k:-1,stage:4});memPress(30,'kb');memPress(31,'kb');memPress(32,'kb');play(r,r.a,r.b);o.song.ok3=r.res.ok;o.song.msg3=r.res.msg;
 /* Text im Übungsbildschirm: keine internen Zahlen/Begriffe */
 o.runText=$('#zlRun').innerText;
 /* Schnitt verschieben */
 memStop();z().st=z().st.map(()=>4);const c0=z().cuts[2];zlMoveCut(2,1);o.cut={from:c0,to:z().cuts[2],st:z().st.join('')};
 /* Übernahme aus dem alten Lernstand (v10): was saß, sitzt */
 delete MEM.rec[zlKey()];const v=awState();v.ch.forEach((c,k)=>c.st=[3,3,2,1,3,3,0,0][k]);memSaveAll();o.mig=zlState().st.join('');
 o.log=(load('kt_v8log')||[]).filter(e=>e.zl).map(e=>[e.line,e.stage,e.ok,e.wrong,e.help,e.ev||'']);
 /* App in den Hintergrund / Klavier getrennt: Durchgang endet, zählt nicht, Übersicht */
 z().st=z().st.map(()=>0);r=zlStart({k:0,stage:2});play(r,r.a,r.a+1);Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});document.dispatchEvent(new Event('visibilitychange'));
 delete document.visibilityState;o.bg={run:!!MEM.run,home:!$('#zlHome').classList.contains('hidden'),log:(load('kt_v8log')||[]).slice(-1)[0].why};
 KB.state='on';r=zlStart({k:0,stage:2});KB.state='off';zlTick(r,0.05);o.kb={run:!!MEM.run,home:!$('#zlHome').classList.contains('hidden'),log:(load('kt_v8log')||[]).slice(-1)[0].why};KB.state='off';
 o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, SONGS)
        await pg.evaluate("()=>{window.AW_NOLOOP=false;MEMS.fly_me[zlKey()].st=[4,4,0,0,0,0,0,0];zlStart({k:2,stage:3});const R=MEM.run;for(const m of MEM.gs[R.a].mids)memPress(m,'kb');memPress(30,'kb')}")
        await pg.wait_for_timeout(300); os.makedirs('/tmp/zl', exist_ok=True); await pg.screenshot(path='/tmp/zl/stufe3.png')
        await pg.evaluate("()=>{zlStart({k:2,stage:4})}"); await pg.wait_for_timeout(400); await pg.screenshot(path='/tmp/zl/stufe4.png')
        await pg.evaluate("()=>{memStop();zlHome()}"); await pg.wait_for_timeout(200); await pg.screenshot(path='/tmp/zl/home.png', full_page=True)
        await br.close()
    print(json.dumps({k: v for k, v in r.items() if k != 'log'}, ensure_ascii=False)); print('log', r['log']); print(errs)
    lg = r['log']
    c = {'Übersicht: Zeilen-Ansicht statt alter Ansicht, 8 Kacheln + Song': r['home']['vis'] and r['home']['old'] and r['home']['tiles'] == 9,
         'Fly Me: 8 Zeilen aus dem Takt-Schnitt (erste Griffe 0,13,26,35,46,59,72,81)': r['home']['cuts'] == [0, 13, 26, 35, 46, 59, 72, 81],
         'Zeile 8 endet mit dem ganzen Schlusston (C2+C5 bis 1:26)': r['line8end'] >= 86,
         'Stufe 1: App spielt von selbst vor, danach Stufe 2': r['s1']['stage'] == 1 and r['s1']['demo'] and 'Stufe 1/4' in r['s1']['stat'] and r['s1b']['stage'] == 2 and not r['s1b']['demo'] and r['s1b']['st'] == 1,
         'Stufe 2 sauber → Stufe 3': r['s2']['ok'] and r['s2']['next'] == {'k': 0, 'stage': 3},
         'Stufe 3: vorne sichtbar, hintere Hälfte aus': r['s3vis']['first'] == 1 and r['s3vis']['last'] == 0 and r['s3vis']['stage'] == 3,
         'falscher Ton: rot, Fortschritt stoppt, Hinweis in der Statuszeile': r['wrongStop']['wrong'] == 1 and r['wrongStop']['pos'] == 3 and r['wrongStop']['stat'],
         'korrigierter Vertipper → dieselbe Stufe noch einmal': not r['s3']['ok'] and r['s3']['next'] == {'k': 0, 'stage': 3} and 'noch einmal' in r['s3']['msg'],
         'Stufe 4: nur der erste Griff, bleibt bis gespielt (auch nach 5 s)': r['s4a']['stage'] == 4 and r['s4a']['a'] == 1 and r['s4a']['n'] == 0 and r['s4a']['after5s'] == 1 and r['s4a']['afterPlay'] == 0,
         'B: nächster Griff 1,5 s sichtbar, Durchgang läuft weiter, danach dieselbe Stufe': r['peek']['help'] == 1 and r['peek']['vis'] == 1 and r['peek']['after'] == 0 and not r['s4b']['ok'] and r['s4b']['next'] == {'k': 0, 'stage': 4},
         'Stufe 4 sauber → Zeile sitzt, Kachel grün, dann Zeile 2 ab Stufe 1': r['sits']['ok'] and r['sits']['st'] == 4 and r['sits']['flash'] == '0' and 'ok' in r['sits']['tile'] and r['sits']['next'] == {'k': 1, 'stage': 1} and r['l2']['k'] == 1 and r['l2']['stage'] == 1,
         'Zeile 2 beginnt mit den letzten 2 Griffen von Zeile 1': r['l2']['ov'] == 2,
         'tiefstes A mitten im Versuch: vorspielen, nichts zählt, Stufe bleibt': r['aKey']['demo'] and r['aKey']['wrong'] == 0 and r['aKey']['pos'] == 0 and r['aKey']['stage'] == 2 and r['aKey']['st'] == 1,
         'Stufe 4 mit Anlauf: Anker stehen, erster Griff der neuen Zeile blitzt kurz auf': r['flash']['anchor'] == 1 and r['flash']['la0'] == 0 and r['flash']['laNow'] == 1 and r['flash']['laLater'] == 0,
         'ganzer Song: kommt, wenn alle Zeilen sitzen; 2 Vertipper erlaubt, 3 nicht': r['song']['k'] == -1 and r['song']['stage'] == 4 and r['song']['a'] == 0 and r['song']['ok2'] and r['song']['whole'] == 1 and not r['song']['ok3'],
         'Übungsbildschirm ohne interne Zahlen/Begriffe': not any(w in r['runText'] for w in ['Häppchen', 'Formteil', 'Last', 'Anschl', 'Naht', ' s ']),
         'Schnitt verschieben: Grenze +1 Griff, beide Zeilen wieder Stufe 1': r['cut']['to'] == r['cut']['from'] + 1 and r['cut']['st'] == '40044444',
         'Übernahme: was saß, sitzt (alt 3 3 2 1 3 3 0 0 → 44004400)': r['mig'] == '44004400',
         'Protokoll: jeder Versuch mit Zeile/Stufe/Fehler/Hilfe, dazu Vorspielen, Abbruch, Schnitt': any(e[5] == 'demo' for e in lg) and any(e[5] == 'abort' for e in lg) and any(e[5] == 'cut' for e in lg) and any(e[1] == 3 and e[3] == 1 and e[2] == 0 for e in lg) and any(e[4] == 1 for e in lg) and any(e[5] == 'stage1' for e in lg),
         'App im Hintergrund: Durchgang endet, zählt nicht (Abbruch im Protokoll), Übersicht': not r['bg']['run'] and r['bg']['home'] and r['bg']['log'] == 'bg',
         'Klavier getrennt: Durchgang endet, Übersicht': not r['kb']['run'] and r['kb']['home'] and r['kb']['log'] == 'kb',
         'Version 5.36': r['ver'].startswith('Version 5.36'),
         'keine Fehler': not errs}
    for k, v in c.items(): print(('OK  ' if v else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
