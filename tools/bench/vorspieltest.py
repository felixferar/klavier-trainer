"""v5.39: Vorspielen endet kurz nach dem letzten Anschlag – und wer danach anfängt, ist sofort dran.
Befund 22.11. (Testwoche): Fly Me Zeile 8 endet mit einem 5,3 s langen Schlussakkord. Das Vorspielen lief bis zum Ausklingen weiter
(bei 60 % Tempo ≈ 9 s nach dem letzten Anschlag). Alles, was Felix in dieser Zeit richtig spielte, galt als „mitspielen“ und zählte nicht → „geht nicht weiter“.
usage: python3 tools/bench/vorspieltest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,z=zlState(),
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   untilAfterLast=(r,dt)=>{let n=0;while(r.demo&&r.demo.t<gs[r.b].start+dt&&n++<9999)zlTick(r,0.02)},
   playAll=r=>{for(let j=r.pos;j<=r.b;j++){press(j);for(let i=0;i<40;i++)zlTick(r,0.02)}};
 z.st=[4,4,4,4,4,4,4,1];z.gq[7]=1; /* v5.78: Griffe schon geübt – hier geht es um den Durchgang im Takt */memSaveAll();
 /* v5.43: kein Echo mehr – Vorspielen per tiefstem A in „Mit Noten“ (Zeile 8 mit dem 5,3 s langen Schlussakkord) */
 const sA=()=>{const r=zlStart({k:7,stage:2});memPress(AW.restart,'kb');return r};
 /* 1) Nachklang höchstens ~3 s (vorher 9,2 s) */
 let r=sA();o.tail=+((r.demo.end-gs[r.b].start)/r.tempo).toFixed(1);
 /* 2) direkt nach dem letzten vorgespielten Anschlag richtig spielen → Durchgang zählt, Stufe geschafft */
 untilAfterLast(r,0.5);o.stillDemo=!!r.demo;playAll(r);o.played={done:r.done,ok:r.res&&r.res.ok,st:z.st[7]};memStop();
 /* 3) den letzten Griff MITspielen (gleichzeitig mit dem Vorspielen) beendet das Vorspielen nicht */
 z.st[7]=1;r=sA();untilAfterLast(r,0.05);press(r.b);o.along={demo:!!r.demo,pos:r.pos-r.a,wrong:r.wrong};memStop();
 /* 4) falsche Taste im Nachklang: Vorspielen läuft weiter, nichts zählt */
 r=sA();untilAfterLast(r,0.5);memPress(30,'kb');o.wrongKey={demo:!!r.demo,wrong:r.wrong};
 {let n=0;while(r.demo&&n++<9999)zlTick(r,0.02)}o.ends={demo:!!r.demo,pos:r.pos-r.a};memStop();
 /* 5) Stufe 1 „Hören“: nach dem letzten Anschlag anfangen → direkt Stufe 2, Durchgang läuft */
 z.st[7]=0;r=zlStart({k:7,stage:1});untilAfterLast(r,0.5);press(r.a);o.hear={demo:!!r.demo,stage:r.stage,st:z.st[7],pos:r.pos-r.a,run:r.run};memStop();
 /* 6) A (vorspielen) mitten im Kopf-Durchgang: auch dort kurzer Nachklang */
 z.st[7]=3;r=zlStart({k:7,stage:4});press(r.a);memPress(AW.restart,'kb');o.aTail=+((r.demo.end-gs[r.b].start)/r.tempo).toFixed(1);
 o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, SONGS); await br.close()
    c = {'Nachklang Zeile 8 (Vorspielen mit A) ≤ 3 s': r['tail'] <= 3.0,
         'nach letztem Anschlag gespielt → zählt, Stufe geschafft': r['stillDemo'] is False or (r['played']['done'] and r['played']['ok'] and r['played']['st'] == 2),
         'Durchgang abgeschlossen': bool(r['played']['done'] and r['played']['ok'] and r['played']['st'] == 2),
         'letzten Griff mitspielen beendet Vorspielen nicht': r['along']['demo'] and r['along']['pos'] == 0 and r['along']['wrong'] == 0,
         'falsche Taste im Nachklang zählt nicht': r['wrongKey']['demo'] and r['wrongKey']['wrong'] == 0 and r['ends'] == {'demo': False, 'pos': 0},
         'Hören → anfangen = Stufe 2 läuft': r['hear']['demo'] is False and r['hear']['stage'] == 2 and r['hear']['st'] == 1 and r['hear']['run'],
         'A im Kopf-Durchgang: Nachklang ≤ 3 s': r['aTail'] <= 3.0,
         'keine JS-Fehler': not errs}
    print(json.dumps(r, ensure_ascii=False)); bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
