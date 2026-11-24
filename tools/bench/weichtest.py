"""v5.50: Weicher Einstieg ins Zusammensetzen.
Jedes lange Stück (am Stück und der ganze Song) kommt zuerst einmal mit blassen Noten (30 %), dann aus dem Kopf.
Der Song sitzt ab 60 % aus dem Kopf; 80 % und 100 % sind Bonus.
Felix 22.11.: „Es gibt noch keine smoothe Lösung von den einzelnen Teilen zu größeren Teilen bzw. dann auch den ganzen Song.“
usage: python3 tools/bench/weichtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,bad)=>{bad=bad||{};{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}for(let j=r.pos;j<=r.b;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 MEM.rec[zlKey()]={cv:2,n:89,cuts:[0,13,26,35,46,59,72,81],st:[4,4,4,4,4,4,4,4],eh:[0,0,0,0,0,0,0,0],stars:[2,2,2,2,2,2,2,2],song:0,kc:[2,2,2,2,2,2,2,2]};memSaveAll();
 zlHome();o.home={go:$('#zlGo').textContent};
 /* 1) 1–2 am Stück: erst mit blassen Noten */
 let r=zlStart(zlPick(z()));o.b1={stage:r.stage,blk:r.blk,alpha:zlAlpha(r,r.la+3),tgt:zlVis(r,r.la+3),chip:$('#zlChip').textContent,txt:(zlUI(r),$('#zlStat').textContent),world:$('#zlRun').className};
 /* 3 Fehler > Toleranz 2 → noch einmal mit blassen Noten */
 play(r,{5:1,15:1,20:1});o.b1.fail={ok:r.res.ok,sub:r.res.sub,next:r.next,bc:(z().bc['b0-1']||[]).length};tick(4);r=R();
 /* sauber → „jetzt aus dem Kopf“, kein ✓ je Zeile aus dem Hilfe-Durchgang */
 play(r);o.b1.ok={ok:r.res.ok,sub:r.res.sub,next:r.next,bh:!!z().bh['b0-1'],bd:!!z().bd['0-1'],bc:(z().bc['b0-1']||[]).length};tick(4);r=R();
 o.b1.kopf={stage:r.stage,alpha:zlAlpha(r,r.la+3),chip:$('#zlChip').textContent};play(r);o.b1.done={ok:r.res.ok,bd:!!z().bd['0-1'],next:r.next};memStop();
 /* 2) Reihenfolge danach: jeweils erst blass, dann Kopf */
 const ord=[];{const c=JSON.parse(JSON.stringify(z()));for(let i=0;i<20;i++){const p=zlPick(c);if(!p)break;ord.push((p.blk||'song'+(p.t||0))+':'+p.stage+(p.bonus?'b':''));
   if(p.stage===3)(c.bh=c.bh||{})[p.blk?'b'+p.blk:'s0']=1;else if(p.blk)c.bd[p.blk]=1;else c.song++}}o.order=ord;
 /* 3) Song: blass → Kopf 60 % = sitzt; Startseite/Song-Seite „sitzt“; Bonus 80 % angeboten */
 const zz=z();for(const b of zlBlocks(8)){zz.bd[zlBK(b)]=1;zz.bh['b'+zlBK(b)]=1}memSaveAll();zlHome();o.preSong={go:$('#zlGo').textContent,sum:$('#zlSum').textContent};
 r=zlStart(zlPick(z()));o.song={stage:r.stage,tempo:r.tempo,a:r.a,b:r.b};play(r);o.song.help={ok:r.res.ok,sub:r.res.sub};tick(4);r=R();
 o.song.kopf={stage:r.stage,tempo:r.tempo};play(r);o.song.ok={ok:r.res.ok,sub:r.res.sub,song:z().song,next:r.next};tick(4);
 o.song.bonusRun={bonus:R()&&R().bonus,tempo:R()&&R().tempo,chip:$('#zlChip').textContent};memStop();zlHome();
 o.after={go:$('#zlGo').textContent,sum:$('#zlSum').textContent,info:memSub(it,memInfo(it)),state:songState(it)};
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
    c = {'Übersicht: „Weiter: Zeilen 1–2 am Stück · mit blassen Noten“': t(lambda: r['home']['go'] == 'Weiter: Zeilen 1–2 am Stück · mit blassen Noten'),
         'Hilfe-Durchgang: Noten 30 %, keine Zieltaste, lila Farbwelt, Chip „Am Stück · blass“': t(lambda: r['b1']['stage'] == 3 and r['b1']['alpha'] == 0.3 and r['b1']['tgt'] == 0 and 'w-blass' in r['b1']['world'] and r['b1']['chip'] == 'Am Stück · blass' and 'mit blassen Noten' in r['b1']['txt']),
         'zu viele Fehler → noch einmal mit blassen Noten, kein ✓ je Zeile': t(lambda: not r['b1']['fail']['ok'] and r['b1']['fail']['next'] == {'k': -1, 'stage': 3, 't': 0, 'blk': '0-1'} and r['b1']['fail']['bc'] == 0 and 'blassen Noten' in r['b1']['fail']['sub']),
         'geschafft → „Jetzt dasselbe aus dem Kopf“, Stück noch nicht fertig': t(lambda: r['b1']['ok']['ok'] and 'aus dem Kopf' in r['b1']['ok']['sub'] and r['b1']['ok']['next'] == {'k': -1, 'blk': '0-1', 'stage': 4, 't': 0} and r['b1']['ok']['bh'] and not r['b1']['ok']['bd'] and r['b1']['ok']['bc'] == 0),
         'dann aus dem Kopf (keine Noten) → Stück geschafft': t(lambda: r['b1']['kopf']['stage'] == 4 and r['b1']['kopf']['alpha'] == 0 and r['b1']['kopf']['chip'] == 'Am Stück' and r['b1']['done']['ok'] and r['b1']['done']['bd']),
         'Reihenfolge: jedes Stück blass → Kopf, dann Song blass → Kopf, dann Bonus 80/100': t(lambda: r['order'] == ['2-3:3', '2-3:4', '0-3:3', '0-3:4', '4-5:3', '4-5:4', '6-7:3', '6-7:4', '4-7:3', '4-7:4', 'song0:3', 'song0:4', 'song1:4b', 'song2:4b']),
         'vor dem Song: „Ganzer Song · 60 % · mit blassen Noten“': t(lambda: r['preSong']['go'] == 'Weiter: Ganzer Song · 60 % · mit blassen Noten' and 'jetzt: der ganze Song' in r['preSong']['sum']),
         'Song: blass 60 % → Kopf 60 % → „sitzt auswendig ⭐“': t(lambda: r['song']['stage'] == 3 and r['song']['tempo'] == 0.6 and r['song']['a'] == 0 and r['song']['b'] == 88 and r['song']['help']['ok'] and r['song']['kopf'] == {'stage': 4, 'tempo': 0.6} and r['song']['ok']['ok'] and r['song']['ok']['song'] == 1 and 'sitzt auswendig' in r['song']['ok']['sub']),
         'danach Bonus 80 % (als Bonus gekennzeichnet)': t(lambda: r['song']['ok']['next'] == {'k': -1, 'stage': 4, 't': 1, 'bonus': 1} and r['song']['bonusRun']['bonus'] == 1 and r['song']['bonusRun']['tempo'] == 0.8 and r['song']['bonusRun']['chip'] == 'Bonus'),
         'Übersicht/Startseite: Song sitzt ⭐, Bonus angeboten': t(lambda: r['after']['go'] == 'Weiter: Bonus: Ganzer Song · 80 %' and 'sitzt auswendig' in r['after']['sum'] and 'alles geschafft' in r['after']['info'] and r['after']['state'] == 2),
         'Version 5.53': t(lambda: r['ver'].startswith('Version 5.53')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
