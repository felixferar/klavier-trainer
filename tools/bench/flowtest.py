"""v5.57 „Flow“: kein Metronom im Auswendig-Modus · dezente WebAudio-Töne (Fehler / Zeile / Song) · langer Song setzt nach Fehlschlag/Abbruch
kurz vor der Problemstelle neu an · Song-Tempo +10 % je geschafftem Durchgang, nie zurück.
usage: python3 tools/bench/flowtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""async (SG)=>{window.toast=(m)=>{(window.TOASTS=window.TOASTS||[]).push(String(m))};window.AW_NOLOOP=true;window.playTone=()=>{};
 const CNT={click:0,knock:0,line:0,big:0};window.playClick=()=>{CNT.click++};
 const rKnock=window.fxKnock,rLine=window.fxLine;
 window.fxKnock=()=>{CNT.knock++};window.fxLine=()=>{CNT.line++};window.fxBig=()=>{CNT.big++};
 const o={},sl=ms=>new Promise(r=>setTimeout(r,ms));
 const mk=(id,ns)=>({id,type:'midi',title:id,artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))});
 const it=mk('fly_me',SG.fly_me),short=mk('kurz',SG.fly_me.slice(0,40));LIB=[it,short];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState();o.N=gs.length;
 const press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   tick=(r,sec)=>{for(let t=0;t<sec;t+=0.02){if(MEM.run!==r)break;zlTick(r,0.02)}},
   play=(r,bad,upto,wait,st)=>{bad=bad||{};st=st||{};{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}const end=upto==null?r.b:upto;
     for(let j=r.pos;j<=end;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}if(wait)for(let i=0;i<60;i++)zlTick(r,0.02);if(st[j])for(let i=0;i<300;i++)zlTick(r,0.02); /* v5.59: Stocken = 6 s */for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 /* --- 1. kein Metronom: Zeile aus dem Kopf und Song, auch mit alter Einstellung „Klick: an“ --- */
 S.zlClick=true;z().st=[4,4,4,4,4,4,4,4];memSaveAll();
 let r=zlStart({k:2,stage:4});play(r,{},null,true);o.clickLine=CNT.click;memStop();
 o.btn=$('#zlFx')?$('#zlFx').textContent:null;o.oldBtn=!!$('#zlClick');
 /* --- 2. Töne: richtiger Griff still, falscher Griff klopft, Zeile geschafft → Arpeggio --- */
 CNT.knock=0;CNT.line=0;CNT.big=0;r=zlStart({k:1,stage:4});{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}
 press(r.a);press(r.a+1);o.quietOk={knock:CNT.knock,line:CNT.line,big:CNT.big};memPress(30,'kb');o.knock1=CNT.knock;play(r);o.lineOk=r.res&&r.res.ok;o.lineSnd={line:CNT.line,big:CNT.big};memStop();
 /* echte Funktionen: stumm bei „Klavierklang aus“ und bei „Töne: aus“ */
 S.sound=false;o.fxMuted1=!fxOn();S.sound=true;S.zlFx=false;o.fxMuted2=!fxOn();S.zlFx=true;o.fxOnNow=fxOn();
 let thr=null;try{rKnock();rKnock();rLine();thr=true}catch(e){thr=String(e)}o.realFx=thr;
 /* --- 3. Song-Tempo: geschafft (auch mit vielen „zu spät“) → +10 %, Fehlschlag → bleibt --- */
 {const y=z();y.song=1;y.ts=6;y.tf={s:1};y.tu={};y.bc={};y.nq=null;y.rep=null;for(let q=1;q<8;q++)y.nd[q]=1;for(const bb of zlBlocks(8))y.bd[zlBK(bb)]=1;y.bh={s0:1};memSaveAll()}
 CNT.big=0;r=zlStart(zlPick(z()));o.t0=r.tempo;play(r,{},null,true);o.okLate={ok:r.res.ok,late:r.late,sub:r.res.sub,big:CNT.big};memStop();
 r=zlStart(zlPick(z()));o.t1=r.tempo;
 const many={};for(let j=3;j<89;j+=4)many[j]=1;play(r,{},null,false,many);o.fail1=r.res.ok;memStop();
 r=zlStart(zlPick(z()));o.t2=r.tempo;play(r,{},null,false,many);memStop();r=zlStart(zlPick(z()));o.t3=r.tempo;memStop();
 /* Leiter bis 100 % */
 z().bc={};z().lf={};z().nq=null;z().rep=null;memSaveAll();const lad=[];
 for(let i=0;i<5;i++){const p=zlPick(z());if(!p){lad.push('fertig');break}r=zlStart(p);lad.push(r.tempo);play(r);memStop()}
 o.ladder=lad;o.songLvl=z().song;o.pickEnd=zlPick(z());
 /* --- 4. langer Song: Fehlschlag hinten → nächster Versuch 1 Zeile vor der ersten Zeile ohne ✓ --- */
 {const y=z();y.song=1;y.ts=6;y.bc={};y.lf={};y.nj={};y.nq=null;y.rep=null;memSaveAll()}
 const cuts=z().cuts.slice();o.cuts=cuts;
 const badL4={};for(let j=cuts[4];j<cuts[5];j+=2)badL4[j]=1;for(let j=cuts[6];j<cuts[7];j+=3)badL4[j]=1;for(let j=cuts[7];j<89;j+=3)badL4[j]=1;
 r=zlStart(zlPick(z()));o.r1={a:r.a,from:r.from};play(r,{},null,false,badL4);o.r1.ok=r.res.ok;o.r1.sub=r.res.sub;o.r1.bc=(z().bc.s1||[]).slice().sort();memStop();
 let p=zlPick(z());o.p2={from:p.from,name:zlPickName(p,1)};r=zlStart(p);o.p2.a=r.a;o.p2.la=r.la;o.p2.tol=zlTol(r);
 CNT.big=0;play(r);o.p2.ok=r.res.ok;o.p2.song=z().song;o.p2.sub=r.res.sub;o.p2.bc=z().bc.s1||null;o.p2.big=CNT.big;o.p2.ts=z().ts;memStop();
 o.p3=zlPick(z());r=zlStart(o.p3);o.p3t=r.tempo;o.p3a=r.a;play(r);o.p3ok=r.res.ok;o.p3sub=r.res.sub;memStop();o.p4t=zlTempoFor(z(),zlPick(z()));
 /* --- 5. Abbruch mit A mitten im Song → neuer Anlauf kurz vor der Stelle (Vorspielen ab dort) --- */
 {const y=z();y.bc={};y.lf={};y.nq=null;y.rep=null;memSaveAll()}
 r=zlStart(zlPick(z()));play(r,{},cuts[5]+2);await sl(500);memPress(AW.restart,'kb');memRelease(AW.restart);
 const n=R();o.ab={newRun:n!==r,from:n.from,a:n.a,demo:!!n.demo,toast:(window.TOASTS||[]).slice(-1)[0]||'',bc:(z().bc.s1||[]).slice().sort()};
 const lg=load('kt_v8log')||[];o.ab.log=lg.slice(-1)[0];
 /* 2× A schnell bleibt „sofort selbst dran“ */
 await sl(500);memPress(AW.restart,'kb');memRelease(AW.restart);memPress(AW.restart,'kb');memRelease(AW.restart);o.ab.dbl=!R().demo&&R().pos===R().a;memStop();
 /* --- 6. kurzer Song (40 Griffe-Grenze): immer ab Griff 1 --- */
 openMem(short);o.shortN=MEM.gs.length;const zs=zlState();o.shortFrom=zlSongFrom(Object.assign({},zs,{bc:{s0:[0,1,2]}}),'s0');
 o.ver=$('#verTxt').textContent;o.click=CNT.click;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 800, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        try: r = await pg.evaluate(JS, SONGS)
        except Exception as e: r = {'crash': str(e)[:400]}
        await br.close()
    print(json.dumps(r, ensure_ascii=False))
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'kein Metronom-Klick im Auswendig-Modus (auch mit alter Einstellung „Klick: an“)': t(lambda: r['clickLine'] == 0 and r['click'] == 0),
         'Knopf „Töne: an“ statt „Klick“': t(lambda: r['btn'] is not None and r['btn'].startswith('Töne') and not r['oldBtn']),
         'richtige Griffe: kein Extra-Ton': t(lambda: r['quietOk'] == {'knock': 0, 'line': 0, 'big': 0}),
         'falsche Taste → Holz-Klopfen': t(lambda: r['knock1'] == 1),
         'Zeile geschafft → Arpeggio (kein großer Akkord)': t(lambda: r['lineOk'] and r['lineSnd'] == {'line': 1, 'big': 0}),
         'Töne schweigen bei Klavierklang aus / Töne aus': t(lambda: r['fxMuted1'] and r['fxMuted2'] and r['fxOnNow']),
         'echte WebAudio-Töne laufen ohne Fehler': t(lambda: r['realFx'] is True),
         'Song geschafft mit vielen „zu spät“ → trotzdem +10 % und voller Akkord': t(lambda: r['t0'] == 0.6 and r['okLate']['ok'] and r['okLate']['late'] > 1 and 'Nächstes Mal 70 %' in r['okLate']['sub'] and r['okLate']['big'] == 1 and r['t1'] == 0.7),
         '2× gestockt (v5.59) → Tempo bleibt (kein Rückfall)': t(lambda: not r['fail1'] and r['t2'] == 0.7 and r['t3'] == 0.7),
         'Leiter 70 → 80 → 90 → 100 %, danach bleibt der Song spielbar (v5.59)': t(lambda: r['ladder'][:4] == [0.7, 0.8, 0.9, 1] and r['songLvl'] == 3 and r['pickEnd'] is not None and r['pickEnd']['k'] == -1),
         'v5.62: Song sitzt, Fehlschlag hinten → kein Absprung, nächster Versuch wieder ab Griff 1': t(lambda: not r['r1']['ok'] and r['p2']['from'] is None and r['p2']['a'] == 0 and 'von vorn' in r['r1']['sub']),
         'Rest sauber → Song geschafft, nächstes Mal wieder ab Griff 1': t(lambda: r['p2']['ok'] and r['p2']['bc'] is None and 'from' not in r['p3'] and r['p3']['k'] == -1),
         'v5.62: der nächste ganze Durchgang geschafft → Akkord und +10 % (70 %)': t(lambda: r['p2']['ok'] and r['p2']['big'] == 1 and r['p2']['ts'] == 7 and 'Nächstes Mal 70 %' in r['p2']['sub'] and r['p3t'] == 0.7 and r['p3a'] == 0),
         'danach wieder geschafft → +10 % (80 %)': t(lambda: r['p3ok'] and 'Nächstes Mal 80 %' in r['p3sub'] and r['p4t'] == 0.8),
         'v5.62: A mitten im Song (Song sitzt) → neuer Anlauf von vorn, kein Sprung zur Stelle': t(lambda: not r['ab']['from'] and r['ab']['a'] == 0 and r['ab']['log']['abort'] == 1),
         'nach dem Neuansatz: A 2× schnell = sofort selbst dran': t(lambda: r['ab']['dbl']),
         'kurzer Song (≤ 40 Griffe) → immer ab Griff 1': t(lambda: r['shortN'] <= 40 and r['shortFrom'] == 0),
         'Version 5.77': t(lambda: r['ver'].startswith('Version 5.77')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
