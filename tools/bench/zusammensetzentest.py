"""v5.41: Zusammensetzen in kleinen Schritten bis „100 % auswendig“ (ersetzt die v5.40-Prüfung).
- „Sitzt“ = 2× sauber aus dem Kopf. Eine angefangene Zeile wird erst fertig gemacht.
- Am Stück: 1–2, 3–4, 1–4, 5–6, 7–8, 5–8 (60 %), dann der ganze Song 60 → 80 → 100 %.
- v5.43: Fehler zählen je Griff, jede Zeile erlaubt 1 Fehler (auch im langen Stück gilt eine Zeile mit ≤1 Fehler als ✓).
- Lange Stücke: 1 Fehler je 10 Griffe erlaubt; sauber gespielte Zeilen behalten ihr ✓; geschafft, wenn ein Durchgang in der Toleranz war UND jede Zeile ✓ hat.
- Nach 3 Fehlversuchen einmal die schwächste fehlende Zeile „aus dem Kopf“ (nachüben).
Befund 22.11.: v5.40 sprang von einer Zeile (13 Griffe) direkt auf 1–4 (46 Griffe) und riss Felix mitten aus Zeile 8.
usage: python3 tools/bench/zusammensetzentest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   demoEnd=()=>{let n=0;while(R()&&R().demo&&n++<5000)zlTick(R(),0.02)},
   play=(r,from,to,bad)=>{bad=bad||{};for(let j=from;j<=to;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}},
   felix=bl=>{const v={cv:2,n:89,cuts:[0,13,26,35,46,59,72,81],st:[4,4,4,4,4,4,4,2],eh:[0,0,0,0,0,0,0,0],stars:[2,2,2,2,2,2,2,0],song:0};if(bl)v.bl=bl;v.bh={'b0-1':1,'b2-3':1,'b0-3':1,'b4-5':1,'b6-7':1,'b4-7':1,s0:1}; /* v5.50: Hilfe-Durchgänge als erledigt – hier geht es um die Kopf-Regeln (weichtest prüft den Einstieg) */MEM.rec[zlKey()]=v;memSaveAll()};
 o.blocks8=zlBlocks(8);o.blocks={9:zlBlocks(9),5:zlBlocks(5),3:zlBlocks(3),4:zlBlocks(4),54:zlBlocks(54).length};
 /* 1) Felix' Stand: Zeile 8 im Echo → erst Zeile 8 fertig, nicht 1–4 */
 felix();zlHome();o.felix={pick:zlPick(z()),go:$('#zlGo').textContent,sum:$('#zlSum').textContent,kc:z().kc.join('')};
 /* 2) Übernahme aus v5.40 mit geschafftem 1–4 */
 felix([1,0]);o.mig40={bd:Object.keys(z().bd).sort().join(','),pick:zlPick(z()),bl:z().bl};
 /* 3) Zeile 8 aus dem Kopf: 1× sauber → noch nicht; 2× → sitzt; danach Zeilen 1–2 am Stück */
 felix();z().st[7]=3;let r=zlStart({k:7,stage:4});play(r,r.a,r.b);o.kc1={ok:r.res.ok,sub:r.res.sub,st:z().st[7],kc:z().kc[7],next:r.next};tick(4);r=R();
 play(r,r.a,r.b);o.kc2={sub:r.res.sub,st:z().st[7],next:r.next};tick(4);r=R();
 /* 4) 1–2 am Stück: 26 Griffe → 2 erlaubt; 3 Fehler in Zeile 2 → ✓ für Zeile 1 bleibt */
 o.b12={a:r.a,b:r.b,blk:r.blk,stat:$('#zlStat').textContent};play(r,r.a,r.b,{15:1,18:1,22:1});
 o.b12.f={ok:r.res.ok,sub:r.res.sub,bc:(z().bc['b0-1']||[]).join(','),chk:$('#zlPathR').querySelectorAll('.zlN.chk').length,blk:$('#zlPathR').querySelectorAll('.zlN.blk').length};tick(4);r=R();
 /* 5) dann 1 Fehler in Zeile 1, Zeile 2 sauber → in der Toleranz, alle ✓ → geschafft; danach 3–4 */
 play(r,r.a,r.b,{3:1});o.b12.ok={ok:r.res.ok,stars:r.res.stars,sub:r.res.sub,bd:!!z().bd['0-1'],next:r.next};tick(4);r=R();
 /* 6) 3–4: 1 Fehler in Zeile 3 → in der Toleranz, aber Zeile 3 fehlt → „Fast“ */
 o.b34={a:r.a,la:r.la,b:r.b};play(r,r.a,r.b,{28:1,30:1});o.b34.f={ok:r.res.ok,stars:r.res.stars,sub:r.res.sub};tick(4);r=R();
 /* 7) noch 2× gescheitert (Zeile 3) → Zeile 3 nachüben → zurück */
 play(r,r.a,r.b,{28:1,30:1});tick(4);r=R();play(r,r.a,r.b,{29:1,31:1,33:1});o.rep={sub:r.res.sub,rep:z().rep,next:r.next};tick(4);r=R();
 o.rep.run={k:r.k,rep:r.rep,stat:$('#zlStat').textContent};play(r,r.a,r.b);o.rep.ok={sub:r.res.sub,rep:z().rep,next:r.next};tick(4);r=R();
 play(r,r.a,r.b);o.b34.ok={ok:r.res.ok,next:r.next};memStop();
 /* 8) Reihenfolge danach: 1–4, dann (alles sitzt) 5–6, 7–8, 5–8, Song */
 const ord=[];{const c=JSON.parse(JSON.stringify(z()));for(let i=0;i<8;i++){const p=zlPick(c);if(!p)break;ord.push(p.blk||('s'+p.t));if(p.blk)c.bd[p.blk]=1;else c.song++}}o.order=ord;
 /* 9) Ganzer Song: 8 Fehler über 8 Zeilen → in der Toleranz, aber Zeilen fehlen; dann sauber → 80 % */
 const zz=z();for(const b of zlBlocks(8))zz.bd[zlBK(b)]=1;memSaveAll();zlHome();o.home={go:$('#zlGo').textContent,sum:$('#zlSum').textContent};
 r=zlStart(zlPick(z()));const b8={};[3,5,28,38,50,63,75,84].forEach(j=>b8[j]=1);play(r,r.a,r.b,b8);o.song={ok8:r.res.ok,msg:r.res.msg,sub:r.res.sub};tick(4);r=R();
 play(r,r.a,r.b);o.song.clean={ok:r.res.ok,song:z().song};tick(4);r=R();o.song.t2=r.tempo;play(r,r.a,r.b);tick(4);r=R();play(r,r.a,r.b);o.song.end={song:z().song,next:r.next};tick(4);
 o.song.home={go:$('#zlGo').textContent,sum:$('#zlSum').textContent};
 /* 10) Zurücksetzen */
 $('#zlReset').click();$('#zlReset').click();o.reset={st:z().st.join(''),bd:Object.keys(z().bd).length,bc:Object.keys(z().bc).length,kc:z().kc.join(''),song:z().song,rep:z().rep};
 o.log=(load('kt_v8log')||[]).filter(e=>e.zl).map(e=>[e.mode,e.ok,e.tol,e.blk==null?null:e.blk,e.rep||0,e.chk==null?null:e.chk,e.kc==null?null:e.kc]);
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
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'Einteilung 8 Zeilen: 1–2, 3–4, 1–4, 5–6, 7–8, 5–8': t(lambda: r['blocks8'] == [[0, 1], [2, 3], [0, 3], [4, 5], [6, 7], [4, 7]]),
         'Einteilung 9/5/3/4 Zeilen': t(lambda: r['blocks']['9'] == [[0, 1], [2, 3], [0, 3], [4, 5], [6, 8], [4, 8]] and r['blocks']['5'] == [[0, 1], [2, 4]] and r['blocks']['3'] == [] and r['blocks']['4'] == [[0, 1], [2, 3]]),
         'Felix-Stand: erst Zeile 8 fertig (kein Rausreißen), grüne Zeilen bleiben': t(lambda: r['felix']['pick'] == {'k': 7, 'stage': 3} and r['felix']['go'] == 'Weiter: Zeile 8 · Verblassen' and r['felix']['kc'] == '22222220'),
         'Übernahme v5.40: geschafftes 1–4 samt Paaren bleibt': t(lambda: r['mig40']['bd'] == '0-1,0-3,2-3' and r['mig40']['pick'] == {'k': 7, 'stage': 3} and r['mig40']['bl'] is None),
         'Sitzt erst nach 2× sauber aus dem Kopf': t(lambda: r['kc1']['ok'] and 'Noch 1×' in r['kc1']['sub'] and r['kc1']['st'] == 3 and r['kc1']['kc'] == 1 and r['kc1']['next'] == {'k': 7, 'stage': 4} and r['kc2']['st'] == 4 and 'sitzt' in r['kc2']['sub']),
         'danach Zeilen 1–2 am Stück (Griffe 0–25)': t(lambda: r['kc2']['next'] == {'k': -1, 'blk': '0-1', 'stage': 4, 't': 0} and r['b12']['a'] == 0 and r['b12']['b'] == 25 and 'Zeilen 1–2 am Stück' in r['b12']['stat']),
         '3 Fehler in Zeile 2: nicht geschafft, ✓ für Zeile 1 bleibt': t(lambda: not r['b12']['f']['ok'] and r['b12']['f']['bc'] == '0' and 'fehlt noch: Zeile 2' in r['b12']['f']['sub'] and r['b12']['f']['chk'] == 1 and r['b12']['f']['blk'] == 1),
         'dann Toleranz + alle ✓ → 1–2 geschafft, weiter mit 3–4': t(lambda: r['b12']['ok']['ok'] and r['b12']['ok']['stars'] == 2 and r['b12']['ok']['bd'] and r['b12']['ok']['next'] == {'k': -1, 'blk': '2-3', 'stage': 4, 't': 0} and r['b34']['a'] == 24 and r['b34']['la'] == 26 and r['b34']['b'] == 45),
         'in der Toleranz, aber Zeile fehlt → „Fast“': t(lambda: not r['b34']['f']['ok'] and r['b34']['f']['stars'] == 2 and r['b34']['f']['sub'].startswith('Fast') and 'Zeile 3' in r['b34']['f']['sub']),
         '3× gescheitert → Zeile 3 nachüben → zurück zu 3–4': t(lambda: r['rep']['rep'] == 2 and 'Zeile 3' in r['rep']['sub'] and r['rep']['next'] == {'k': 2, 'stage': 4, 'rep': 1} and r['rep']['run']['rep'] == 1 and r['rep']['ok']['rep'] is None and r['rep']['ok']['next'] == {'k': -1, 'blk': '2-3', 'stage': 4, 't': 0} and r['b34']['ok']['ok'] and r['b34']['ok']['next'] == {'k': -1, 'blk': '0-3', 'stage': 4, 't': 0}),
         'Reihenfolge: 1–4, 5–6, 7–8, 5–8, Song': t(lambda: r['order'] == ['0-3', '4-5', '6-7', '4-7', 's0', 's1', 's2']),
         'Übersicht vor dem Song': t(lambda: r['home']['go'] == 'Weiter: Ganzer Song · 60 %' and 'am Stück: 6 von 6' in r['home']['sum'] and 'jetzt: der ganze Song' in r['home']['sum']),
         'Ganzer Song: 8 Fehler verteilt → noch nicht; sauber → 80 % → 100 % → fertig': t(lambda: not r['song']['ok8'] and 'erlaubt sind 8' in r['song']['msg'] and 'fehlt noch: Zeile 1' in r['song']['sub'] and r['song']['clean']['ok'] and r['song']['clean']['song'] == 1 and r['song']['t2'] == 0.8 and r['song']['end']['song'] == 3 and r['song']['end']['next'] is None and r['song']['home']['go'] == 'Alles geschafft ⭐'),
         'Zurücksetzen löscht alles': t(lambda: r['reset'] == {'st': '00000000', 'bd': 0, 'bc': 0, 'kc': '00000000', 'song': 0, 'rep': None}),
         'Protokoll: block mit blk/tol/chk, kopf mit kc, nachüben': t(lambda: any(e[0] == 'block' and e[3] == '0-1' and e[2] == 2 and e[5] is not None for e in r['log']) and any(e[0] == 'kopf' and e[6] == 1 for e in r['log']) and any(e[0] == 'kopf' and e[4] == 1 for e in r['log']) and any(e[0] == 'song' and e[2] == 8 for e in r['log'])),
         'Version 5.52': t(lambda: r['ver'].startswith('Version 5.52')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
