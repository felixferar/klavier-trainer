"""v5.53: Tempo wächst mit (Konzept 24.11.) + tiefes A: vorspielen · halten = schneller · 2× schnell = selbst dran.
usage: python3 tools/bench/tempotest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""async (S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={},sl=ms=>new Promise(r=>setTimeout(r,ms));
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,bad,slow)=>{bad=bad||{};{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}for(let j=r.pos;j<=r.b;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}if(slow&&slow[j]){for(let i=0;i<50;i++)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 /* Lernstufen immer 60 % */
 let r=zlStart({k:0,stage:2});o.noten=r.tempo;memStop();r=zlStart({k:0,stage:3});o.blass=r.tempo;memStop();
 /* Kopf: flüssig → +10 %, Pfeil */
 const zz=z();zz.st=[3,0,0,0,0,0,0,0];zz.kc=[0,0,0,0,0,0,0,0];memSaveAll();
 r=zlStart({k:0,stage:4});o.k1={t:r.tempo,up:r.tup};play(r);o.k1.sub=r.res.sub;o.k1.tp=z().tp[0];tick(4);r=R();
 zlUI(r);o.k2={k:r.k,t:r.tempo,up:r.tup,foot:$('#zlTempo').textContent};
 /* stockend geschafft (Lied wartet an 3 Stellen) → bleibt */
 play(r,{},{3:1,6:1,9:1});o.k2.sub=r.res.sub;o.k2.ok=r.res.ok;o.k2.tp=z().tp[0];memStop();
 /* 2× nicht geschafft → −10 % */
 z().st[0]=4;z().tp[0]=8;memSaveAll();r=zlStart({k:0,stage:4,rep:1});play(r,{2:1,5:1,8:1});o.f1={tp:z().tp[0],sub:r.res.sub};memStop();
 r=zlStart({k:0,stage:4,rep:1});play(r,{2:1,5:1,8:1});o.f2={tp:z().tp[0],sub:r.res.sub};memStop();
 r=zlStart({k:0,stage:4,rep:1});z().tp[0]=6;memStop();r=zlStart({k:0,stage:4,rep:1});play(r,{2:1,5:1,8:1});memStop();r=zlStart({k:0,stage:4,rep:1});play(r,{2:1,5:1,8:1});o.floor=z().tp[0];memStop();
 /* Stück: langsamste Zeile; flüssig → Zeilen mind. so schnell */
 z().st=[4,4,4,4,4,4,4,4];z().tp=[8,7,9,9,6,6,6,6];z().tb={};memSaveAll();r=zlStart({k:-1,blk:'0-1',stage:4,t:0});o.blk={t:r.tempo};play(r);o.blk.tb=z().tb['0-1'];o.blk.tp=z().tp.slice(0,2);memStop();
 r=zlStart({k:-1,blk:'0-1',stage:3,t:0});o.blkBlass=r.tempo;memStop();
 /* tiefes A */
 r=zlStart({k:1,stage:4});memPress(AW.restart,'kb');memRelease(AW.restart);o.a={demo:!!r.demo};tick(1);const v0=r.demo.t;tick(1);const n1=r.demo.t-v0;
 await sl(500);memPress(AW.restart,'kb');tick(0.4);const v1=r.demo.t;tick(1);const n2=r.demo.t-v1;zlUI(r);o.a.ffbar=$('#zlStat').textContent;o.a.ratio=n2/n1;o.a.stillDemo=!!r.demo;
 memRelease(AW.restart);const v2=r.demo.t;tick(1);o.a.back=(r.demo.t-v2)/n1;
 await sl(500);memPress(AW.restart,'kb');memRelease(AW.restart);memPress(AW.restart,'kb');memRelease(AW.restart);o.a.dbl=!r.demo&&r.pos===r.a;press(r.a);o.a.start=r.pos>r.a;memStop();
 /* außerhalb des Vorspielens: 2× schnell = Neustart ohne Vorspielen */
 r=zlStart({k:1,stage:4});press(r.a);press(r.a+1);await sl(500);memPress(AW.restart,'kb');memRelease(AW.restart);memPress(AW.restart,'kb');memRelease(AW.restart);o.a.restart=!r.demo&&r.pos===r.a;memStop();
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
    c = {'Lernstufen (Mit Noten, Verblassen, Stück blass) immer 60 %': t(lambda: r['noten'] == 0.6 and r['blass'] == 0.6 and r['blkBlass'] == 0.6),
         'aus dem Kopf flüssig → nächstes Mal 70 %, angesagt': t(lambda: r['k1']['t'] == 0.6 and not r['k1']['up'] and 'Nächstes Mal 70 %' in r['k1']['sub'] and r['k1']['tp'] == 7),
         'nächster Durchgang 70 % mit ↑': t(lambda: r['k2']['k'] == 0 and r['k2']['t'] == 0.7 and r['k2']['up'] and r['k2']['foot'] == 'Tempo 70 % ↑'),
         'geschafft, aber stockend → Tempo bleibt': t(lambda: r['k2']['ok'] and r['k2']['tp'] == 7 and 'flüssiger' in r['k2']['sub']),
         '2× nicht geschafft → −10 %, nie unter 60 %': t(lambda: r['f1']['tp'] == 8 and r['f2']['tp'] == 7 and 'langsamer: 70 %' in r['f2']['sub'] and r['floor'] == 6),
         'Stück startet mit der langsamsten Zeile, flüssig → +10 %, Zeilen mind. so schnell': t(lambda: r['blk']['t'] == 0.7 and r['blk']['tb'] == 8 and r['blk']['tp'] == [8, 7]),
         'tiefes A startet Vorspielen': t(lambda: r['a']['demo']),
         'A gehalten → ca. 3× schneller, Leiste sagt es': t(lambda: 2.5 < r['a']['ratio'] < 3.5 and r['a']['stillDemo'] and 'schneller' in r['a']['ffbar']),
         'A loslassen → normal weiter': t(lambda: 0.9 < r['a']['back'] < 1.1),
         'A 2× schnell → sofort selbst dran': t(lambda: r['a']['dbl'] and r['a']['start']),
         'A 2× schnell mitten im Durchgang → von vorne, ohne Vorspielen': t(lambda: r['a']['restart']),
         'Version 5.54': t(lambda: r['ver'].startswith('Version 5.54')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
