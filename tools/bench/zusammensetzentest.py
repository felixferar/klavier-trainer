"""v5.40: Zusammensetzen bis „100 % auswendig“.
Nach je 4 Zeilen diese am Stück (60 %), dann der ganze Song 60 → 80 → 100 %. Lange Stücke erlauben 1 Fehler je 10 eigene Griffe
(Zeilen weiter 0). Nach 3 gescheiterten Versuchen eines langen Stücks: einmal die Zeile mit den meisten Fehlern „aus dem Kopf“, dann zurück.
Befund 22.11.: mit 0 Fehlern über 89 Griffe lag Felix' Chance je Versuch praktisch bei 0 (echte Kopf-Durchgänge: 0,66 falsche Töne je Griff).
usage: python3 tools/bench/zusammensetzentest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,from,to,bad)=>{bad=bad||{};for(let j=from;j<=to;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 /* 1) Felix' echter Stand (21.11.): Zeilen 1–7 sitzen, Zeile 8 im Echo → zuerst Zeilen 1–4 am Stück */
 MEM.rec[zlKey()]={cv:2,n:89,cuts:[0,13,26,35,46,59,72,81],st:[4,4,4,4,4,4,4,2],eh:[0,0,0,0,0,0,0,0],stars:[2,2,2,2,2,2,2,0],song:0};memSaveAll();
 zlHome();o.felix={pick:zlPick(z()),go:$('#zlGo').textContent,sum:$('#zlSum').textContent,bl:z().bl.join('')};
 /* 2) Am Stück 1–4: Bereich, Toleranz (46 eigene Griffe → 4 erlaubt), Pfad markiert die Zeilen */
 let r=zlStart(zlPick(z()));o.b1={a:r.a,la:r.la,b:r.b,tempo:r.tempo,stat:$('#zlStat').textContent,blkNodes:$('#zlPathR').querySelectorAll('.zlN.blk').length,songNow:!!$('#zlPathR').querySelector('.zlN.song.now')};
 play(r,r.a,r.b,{5:1,20:1,30:1,40:1});o.b1.tol4={ok:r.res.ok,stars:r.res.stars,msg:r.res.msg,bl:z().bl.join(''),next:r.next};tick(1.7);r=R();
 o.after={k:r.k,stage:r.stage}; /* danach: Zeile 8 */
 /* 3) zu viele Fehler: 5 > 4 → nicht geschafft, gleiche Aufgabe */
 memStop();z().bl[0]=0;r=zlStart({k:-1,blk:0,stage:4,t:0});play(r,r.a,r.b,{5:1,20:1,30:1,40:1,41:1});o.b1.tol5={ok:r.res.ok,stars:r.res.stars,next:r.next,lf:z().lf.b0};
 /* 4) dreimal gescheitert → Zeile mit den meisten Fehlern nachüben (Zeile 3 = Griffe 26–34) */
 tick(1.7);r=R();play(r,r.a,r.b,{27:3,28:2,5:1});tick(1.7);r=R();play(r,r.a,r.b,{29:3,30:2,40:1});o.rep={sub:r.res.sub,rep:z().rep,next:r.next};tick(1.7);r=R();
 o.rep.run={k:r.k,stage:r.stage,rep:r.rep,stat:$('#zlStat').textContent,a:r.a,b:r.b};
 play(r,r.a,r.b,{28:1});o.rep.fail={ok:r.res.ok,next:r.next};tick(1.7);r=R();play(r,r.a,r.b);o.rep.ok={ok:r.res.ok,sub:r.res.sub,rep:z().rep,next:r.next};tick(1.7);r=R();
 o.rep.back={k:r.k,blk:r.blk};memStop();
 /* 5) Ganzer Song: 89 Griffe → 8 erlaubt; 60 → 80 → 100 %; Übersicht */
 const zz=z();zz.st=zz.st.map(()=>4);zz.bl=zz.bl.map(()=>1);zz.rep=null;zlHome();o.home={go:$('#zlGo').textContent,sum:$('#zlSum').textContent,songNow:!!$('#zlPathH').querySelector('.zlN.song.now')};
 r=zlStart(zlPick(z()));const bad8={};[3,13,23,33,43,53,63,73].forEach(j=>bad8[j]=1);play(r,r.a,r.b,bad8);o.song={a:r.a,b:r.b,ok8:r.res.ok,msg:r.res.msg,song:z().song};tick(1.7);r=R();
 const bad9=Object.assign({83:1},bad8);play(r,r.a,r.b,bad9);o.song.ok9=r.res.ok;o.song.tempo=r.tempo;tick(1.7);r=R();play(r,r.a,r.b);tick(1.7);r=R();o.song.t3=r.tempo;play(r,r.a,r.b);
 o.song.end={song:z().song,next:r.next};tick(1.7);o.song.home={go:$('#zlGo').textContent,sum:$('#zlSum').textContent};
 /* 6) Zurücksetzen löscht auch „am Stück“ und Nachüben */
 $('#zlReset').click();$('#zlReset').click();o.reset={st:z().st.join(''),bl:z().bl.join(''),song:z().song,rep:z().rep};
 /* 7) Einteilung */
 o.blocks={8:zlBlocks(8),9:zlBlocks(9),5:zlBlocks(5),6:zlBlocks(6),54:zlBlocks(54).length};
 o.log=(load('kt_v8log')||[]).filter(e=>e.zl).map(e=>[e.mode,e.ok,e.tol,e.blk==null?null:e.blk,e.rep||0]);
 o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        try: r = await pg.evaluate(JS, SONGS)
        except Exception as e: r = {'crash': str(e)[:300]}
        await br.close()
    print(json.dumps(r, ensure_ascii=False))
    g = lambda f: (lambda: f())
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'Felix-Stand: zuerst Zeilen 1–4 am Stück': t(lambda: r['felix']['pick'] == {'k': -1, 'blk': 0, 'stage': 4, 't': 0} and r['felix']['go'] == 'Weiter: Zeilen 1–4 am Stück' and 'am Stück: 0 von 2' in r['felix']['sum']),
         'Am Stück 1–4: Griffe 0–45, 60 %, Zeilen im Pfad markiert': t(lambda: r['b1']['a'] == 0 and r['b1']['b'] == 45 and r['b1']['tempo'] == 0.6 and r['b1']['blkNodes'] == 4 and not r['b1']['songNow'] and 'Zeilen 1–4 am Stück' in r['b1']['stat']),
         '4 Fehler erlaubt → ★★ geschafft, danach Zeile 8': t(lambda: r['b1']['tol4']['ok'] and r['b1']['tol4']['stars'] == 2 and 'erlaubt sind 4' in r['b1']['tol4']['msg'] and r['b1']['tol4']['bl'] == '10' and r['after'] == {'k': 7, 'stage': 3}),
         '5 Fehler → ★, gleiche Aufgabe noch einmal': t(lambda: not r['b1']['tol5']['ok'] and r['b1']['tol5']['stars'] == 1 and r['b1']['tol5']['next'] == {'k': -1, 'stage': 4, 't': 0, 'blk': 0} and r['b1']['tol5']['lf'] == 1),
         '3× gescheitert → Zeile 3 (meiste Fehler) nachüben': t(lambda: r['rep']['rep'] == 2 and 'Zeile 3' in r['rep']['sub'] and r['rep']['next'] == {'k': 2, 'stage': 4, 'rep': 1} and r['rep']['run']['rep'] == 1 and 'nachüben' in r['rep']['run']['stat'] and r['rep']['run']['a'] == 24 and r['rep']['run']['b'] == 34),
         'Nachüben: Fehler → nochmal, sauber → zurück zum Stück': t(lambda: not r['rep']['fail']['ok'] and r['rep']['fail']['next'] == {'k': 2, 'stage': 4, 't': 0, 'rep': 1} and r['rep']['ok']['ok'] and r['rep']['ok']['rep'] is None and 'zurück zum Stück' in r['rep']['ok']['sub'] and r['rep']['back'] == {'k': -1, 'blk': 0}),
         'Übersicht vor dem Song': t(lambda: r['home']['go'] == 'Weiter: Ganzer Song · 60 %' and r['home']['songNow'] and 'ganzer Song: 0 von 3' in r['home']['sum']),
         'Ganzer Song: 8 Fehler erlaubt, 9 nicht': t(lambda: r['song']['a'] == 0 and r['song']['b'] == 88 and r['song']['ok8'] and 'erlaubt sind 8' in r['song']['msg'] and r['song']['song'] == 1 and not r['song']['ok9'] and r['song']['tempo'] == 0.8),
         '80 → 100 % → alles geschafft': t(lambda: r['song']['t3'] == 1 and r['song']['end']['song'] == 3 and r['song']['end']['next'] is None and r['song']['home']['go'] == 'Alles geschafft ⭐' and 'Der ganze Song sitzt' in r['song']['home']['sum']),
         'Zurücksetzen löscht alles': t(lambda: r['reset'] == {'st': '00000000', 'bl': '00', 'song': 0, 'rep': None}),
         'Einteilung 8→4+4, 9→4+5, 5→keine, 6→4+2, 54→14': t(lambda: r['blocks'] == {'8': [[0, 3], [4, 7]], '9': [[0, 3], [4, 8]], '5': [], '6': [[0, 3], [4, 5]], '54': 14}),
         'Protokoll: mode block/song, tol, blk, rep': t(lambda: any(e[0] == 'block' and e[2] == 4 and e[3] == 0 for e in r['log']) and any(e[0] == 'song' and e[2] == 8 for e in r['log']) and any(e[0] == 'kopf' and e[4] == 1 for e in r['log']) and all(e[2] == 0 for e in r['log'] if e[0] in ('kopf',))),
         'Version 5.40': t(lambda: r['ver'].startswith('Version 5.40')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
