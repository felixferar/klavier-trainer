"""v5.59 „Durchgespielt“: der ganze Song aus dem Kopf gilt als geschafft, wenn er ohne langes Stocken (> 2,5 s länger als das Lied dort dauert; 1 Stocker je 40 Griffe ist erlaubt)
bis zum Ende gespielt wurde. Falsche Töne werden gezeigt und gezählt, entscheiden aber nicht mehr. Zeilen und Stücke bleiben unverändert.
usage: python3 tools/bench/durchtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""async (SG)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.fxKnock=()=>{};window.fxLine=()=>{};window.fxBig=()=>{};
 const o={};
 const mk=(id,ns)=>({id,type:'midi',title:id,artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))});
 const it=mk('fly_me',SG.fly_me);LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,z=()=>zlState();
 const press=j=>{for(const m of gs[j].mids)memPress(m,'kb')};
 /* gap[j] = Sekunden, die vor Griff j vergehen (sonst 0,5 s – so schnell spielt Felix); bad[j] = falsche Tasten vor Griff j */
 const play=(r,bad,gap)=>{bad=bad||{};gap=gap||{};{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}
   for(let j=r.pos;j<=r.b;j++){if(j>r.a){const g=gap[j]!=null?gap[j]:0.5;for(let t=0;t<g;t+=0.02)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}};
 const reset=(song,ts)=>{const y=z();y.st=[4,4,4,4,4,4,4,4];y.song=song;y.ts=ts;y.tf={};y.tu={};y.bc={};y.lf={};y.lw={};y.nj={};y.nq=null;y.rep=null;for(let q=1;q<8;q++)y.nd[q]=1;for(const bb of zlBlocks(8))y.bd[zlBK(bb)]=1;y.bh={s0:1};memSaveAll()};
 const last=()=>(load('kt_v8log')||[]).slice(-1)[0];
 const cuts=z().cuts.slice();o.cuts=cuts;
 /* längster Ton im Lied (bei Fly Me 2,64 s vor Griff 13) */
 let lj=1;for(let j=2;j<gs.length;j++)if(gs[j].start-gs[j-1].start>gs[lj].start-gs[lj-1].start)lj=j;o.longGap=gs[lj].start-gs[lj-1].start;
 /* 1. viele falsche Töne (jeder 4. Griff), aber flüssig → geschafft, +10 % */
 reset(1,6);const many={};for(let j=3;j<89;j+=4)many[j]=1;
 let r=zlStart(zlPick(z()));play(r,many);o.a={ok:r.res.ok,wrong:r.wrong,tol:zlTol(r),msg:r.res.msg,sub:r.res.sub,stars:r.res.stars,stall:last().stall,ts:z().ts,song:z().song};memStop();
 /* 2. fehlerfrei und flüssig → 3 Sterne */
 reset(1,6);r=zlStart(zlPick(z()));play(r);o.b={ok:r.res.ok,stars:r.res.stars,msg:r.res.msg};memStop();
 /* 3. langer Ton wird ausgehalten (Original-Pause + 2 s) → kein Stocken */
 reset(1,6);r=zlStart(zlPick(z()));play(r,{},{[lj]:o.longGap/0.6+2});o.c={ok:r.res.ok,stall:last().stall};memStop();
 /* 4a. einmal 4 s gestockt (mitten in Zeile 3) → trotzdem geschafft (2 Stocker sind bei 89 Griffen erlaubt), die Zeile wird genannt */
 const sg=q=>{const j=cuts[q]+3;return [j,4+(gs[j].start-gs[j-1].start)/0.6]};
 reset(1,6);r=zlStart(zlPick(z()));o.max=Math.max(1,Math.round((r.b-r.la+1)/ZL.stallPer));play(r,{},Object.fromEntries([sg(2)]));o.d0={ok:r.res.ok,msg:r.res.msg,stars:r.res.stars,stall:last().stall,ts:z().ts};memStop();
 /* 4b. 4× gestockt (Zeilen 3, 5, 6, 7) → nicht geschafft, Tempo bleibt, nächster Anlauf vor der ersten gestockten Zeile */
 reset(1,6);r=zlStart(zlPick(z()));play(r,{},Object.fromEntries([sg(2),sg(4),sg(5),sg(6)]));
 o.d={ok:r.res.ok,msg:r.res.msg,sub:r.res.sub,stall:last().stall,ts:z().ts,bc:(z().bc.s1||[]).slice().sort()};memStop();
 const p=zlPick(z());o.d.from=p.from;r=zlStart(p);play(r,many);o.d2={ok:r.res.ok,ts:z().ts};memStop();
 /* 5. Hilfe (B) geholt → zählt wie Stocken */
 reset(1,6);r=zlStart(zlPick(z()));{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}for(let j=r.pos;j<=r.b;j++){for(let t=0;t<0.5;t+=0.02)zlTick(r,0.02);if(j===20)memPress(AW.helpKey,'kb');press(j)}o.e={ok:r.res.ok,stall:last().stall};memStop();
 /* 6. Stück „Zeilen 1–2 am Stück“ bleibt streng: viele falsche Töne → nicht geschafft */
 reset(0,null);{const y=z();y.bd={};y.bh={'b0-1':1};memSaveAll()}
 const pb=zlPick(z());o.f={blk:pb.blk,stage:pb.stage};r=zlStart(pb);const mb={};for(let j=r.la;j<=r.b;j+=2)mb[j]=1;play(r,mb);o.f.ok=r.res.ok;memStop();
 /* 7. bei 100 % bleibt der Song spielbar */
 reset(3,10);const pe=zlPick(z());o.g={k:pe&&pe.k,blk:pe&&pe.blk,tempo:pe?zlTempoFor(z(),pe):null};
 o.ver=$('#verTxt').textContent;return o}"""
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
    c = {'22 falsche Töne (weit über der alten Toleranz), aber flüssig → geschafft': t(lambda: r['a']['ok'] and r['a']['wrong'] > r['a']['tol'] and r['a']['stall'] == 0),
         'falsche Töne werden weiter angezeigt (Überschrift), 2 Sterne': t(lambda: 'Durchgespielt' in r['a']['msg'] and 'daneben' in r['a']['msg'] and r['a']['stars'] == 2),
         'geschafft ab Griff 1 → Tempo +10 % (60 → 70 %)': t(lambda: r['a']['ts'] == 7 and 'Nächstes Mal 70 %' in r['a']['sub']),
         'fehlerfrei und flüssig → 3 Sterne': t(lambda: r['b']['ok'] and r['b']['stars'] == 3),
         'langer Ton im Lied bei 60 % ausgehalten (+2 s) → kein Stocken': t(lambda: r['longGap'] > 2 and r['c']['ok'] and r['c']['stall'] == 0),
         '1× 4 s gestockt → geschafft (2 Stocker erlaubt bei 89 Griffen), Zeile wird genannt, 2 Sterne, +10 %': t(lambda: r['max'] == 2 and r['d0']['ok'] and '1× gestockt (Zeile 3)' in r['d0']['msg'] and r['d0']['stars'] == 2 and r['d0']['stall'] == 1 and r['d0']['ts'] == 7),
         '4× gestockt → nicht geschafft, Zeilen 3, 5, 6, 7 genannt, Tempo bleibt': t(lambda: not r['d']['ok'] and '4× gestockt (Zeile 3, 5, 6, 7)' in r['d']['msg'] and 'erlaubt sind 2' in r['d']['msg'] and r['d']['stall'] == 4 and r['d']['ts'] == 6),
         'v5.62: Song sitzt → nach dem Fehlschlag kein Absprung, wieder ab Griff 1': t(lambda: not r['d'].get('from')),
         'nächster ganzer Durchgang ohne Stocken (auch mit falschen Tönen) → geschafft, +10 %': t(lambda: r['d2']['ok'] and r['d2']['ts'] == 7),
         'Hilfe (B) geholt → zählt als 1 Stocker': t(lambda: r['e']['ok'] and r['e']['stall'] == 1),
         'Stück „am Stück“ unverändert streng (Toleranz)': t(lambda: r['f']['blk'] is not None and r['f']['stage'] == 4 and not r['f']['ok']),
         'bei 100 % bleibt der ganze Song spielbar': t(lambda: r['g']['k'] == -1 and r['g']['blk'] is None and r['g']['tempo'] == 1),
         'Version 5.71': t(lambda: r['ver'].startswith('Version 5.71')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
