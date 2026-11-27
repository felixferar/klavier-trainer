"""v5.55: Übergänge trainieren, gleiche Zeilen erkennen, Mini-Zeilen anhängen.
- Übergang = letzte 3 Griffe der Zeile davor + erste 3 Griffe der Zeile; 2× sauber aus dem Kopf → sitzt.
- Vor jedem Stück und vor dem ganzen Song kommen die Übergänge darin, die noch nicht sitzen (gleiche Übergänge nur 1×).
- Hakt ein Stück 3× an einer Zeilengrenze (Lied wartet > 1 s länger als der Takt, oder Fehler dort), wird der Übergang nachgeübt statt der Zeile.
- Gleiche Zeile wie eine, die schon sitzt (Fly Me: 5 = 1, 6 = 2) → beginnt bei Verblassen.
Befund Testwoche 20.–26.11.: Stocker im ganzen Song fast nur an den Zeilenanfängen (Griff 13, 26, 35, 46, 59, 81).
usage: python3 tools/bench/nahttest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 openMem(it);const gs=MEM.gs,R=()=>MEM.run,z=()=>zlState(),
   tick=(sec)=>{const r0=MEM.run;for(let t=0;t<sec;t+=0.02){const r=MEM.run;if(!r||r!==r0)break;zlTick(r,0.02)}},
   press=j=>{for(const m of gs[j].mids)memPress(m,'kb')},
   play=(r,bad,slow)=>{bad=bad||{};{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}for(let j=r.pos;j<=r.b;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}if(slow&&slow[j]){for(let i=0;i<110;i++)zlTick(r,0.02)}for(let i=0;i<(bad[j]||0);i++)memPress(30,'kb');press(j)}},
   set=(st,extra)=>{const v={cv:2,n:89,cuts:[0,13,26,35,46,59,72,81],st,eh:st.map(()=>0),stars:st.map(x=>x>=4?2:0),song:0,kc:st.map(x=>x>=4?2:0)};Object.assign(v,extra||{});MEM.rec[zlKey()]=v;memSaveAll();return zlState()};
 /* 1) gleiche Zeilen und Übergänge */
 let y=set([0,0,0,0,0,0,0,0]);o.tw=y.tw.slice();o.nsig5=y.nsig[5]===y.nsig[1];o.naht1=zlNahtR(y,1);
 /* 2) gleiche Zeile wie eine, die sitzt → gleich Verblassen */
 y=set([4,4,4,4,0,0,0,0],{bd:{'0-1':1,'2-3':1,'0-3':1},nd:{1:1,2:1,3:1}});o.twin=zlPick(y);
 y.st[0]=0;o.twinNot=zlPick(y);
 /* 3) vor dem Stück 1–2: erst der Übergang 1 → 2 */
 y=set([4,4,0,0,0,0,0,0]);let p=zlPick(y);o.pre={p:{k:p.k,a:p.spot&&p.spot.a,b:p.spot&&p.spot.b,type:p.spot&&p.spot.type},name:zlPickName(p,1,y)};
 zlHome();o.pre.go=$('#zlGo').textContent;
 let r=zlStart(p);o.run1={demo:!!r.demo,tempo:r.tempo,a:r.a,la:r.la,b:r.b};zlUI(r);o.run1.chip=$('#zlChip').textContent;{let n=0;while(r.demo&&n++<5000)zlTick(r,0.02)}zlUI(r);o.run1.bar=$('#zlStat').textContent;
 o.run1.vis=[zlVis(r,r.a),zlVis(r,r.a+1),zlVis(r,r.b)];
 play(r);o.run1.res={ok:r.res.ok,sub:r.res.sub,next:r.next&&r.next.spot&&r.next.spot.ok};zlUI(r);o.run1.head=$('#zlFb .zlFbH')?.textContent;tick(4);r=R();
 o.run2={demo:!!r.demo,spot:!!r.spot};play(r);o.run2.res={ok:r.res.ok,sub:r.res.sub,next:r.next};zlUI(r);o.run2.head=$('#zlFb .zlFbH')?.textContent;o.run2.nd=z().nd[1];memStop();
 /* 4) Übergang 4× nicht geschafft → weiter zum Stück, kommt später wieder */
 y=set([4,4,0,0,0,0,0,0]);r=zlStart(zlPick(y));const fl=[];for(let i=0;i<4;i++){play(r,{[r.a+2]:1});fl.push({sv:r.spot.sv,sub:r.res.sub});tick(4);r=R()}o.fail={fl,nd:z().nd[1],next:r&&r.blk};memStop();
 /* 5) vor dem Song: gleiche Übergänge zählen als geschafft (5 → 6 = 1 → 2) */
 const all={};for(const b of zlBlocks(8))all[zlBK(b)]=1;
 y=set([4,4,4,4,4,4,4,4],{bd:all,bh:{s0:1},nd:{1:1,2:1,3:1,4:1,6:1,7:1}});o.song=zlPick(y);
 y=set([4,4,4,4,4,4,4,4],{bd:all,bh:{s0:1},nd:{1:1,2:1,3:1,5:1,6:1,7:1}});o.song4=zlPick(y).spot?.q;
 /* 5b) v5.56: Song sitzt schon → keine Übergänge vorab, gleich der Song (Bonus) */
 y=set([4,4,4,4,4,4,4,4],{bd:all,bh:{s0:1},song:1});o.songSitzt=zlPick(y);
 /* 6) Stück 1–2 hakt 3× am Übergang (Lied wartet am Griff 13) → Übergang nachüben, nicht Zeile */
 y=set([4,4,0,0,0,0,0,0],{nd:{1:1}});r=zlStart(zlPick(y));o.blk=r.blk;for(let i=0;i<3;i++){play(r,{3:1,5:1,8:1},{13:1});if(i<2){tick(4);r=R()}}
 o.stall={sub:r.res.sub,nq:z().nq,next:r.next&&r.next.spot&&r.next.spot.q,rep:z().rep};tick(4);r=R();o.stall.run=r.spot&&r.spot.type;play(r);tick(4);r=R();play(r);o.stall.back={nq:z().nq,next:r.next&&r.next.blk};memStop();
 /* 7) ohne Stocker an der Grenze → wie bisher die schwächste Zeile */
 y=set([4,4,0,0,0,0,0,0],{nd:{1:1}});r=zlStart(zlPick(y));for(let i=0;i<3;i++){play(r,{3:1,5:1,8:1});if(i<2){tick(4);r=R()}}o.noStall={nq:z().nq,rep:z().rep};memStop();
 /* 8) Mini-Zeilen */
 o.mini=awMergeMini(gs,[{a:0,b:3},{a:4,b:12},{a:13,b:25},{a:26,b:88}],99).map(h=>h.a+'-'+h.b);
 o.miniLong=awMergeMini(gs,[{a:0,b:3},{a:4,b:30},{a:31,b:88}],99).map(h=>h.a+'-'+h.b);
 /* 9) Zurücksetzen löscht die Übergänge */
 y=set([4,4,0,0,0,0,0,0],{nd:{1:1},nq:1});zlHome();$('#zlReset').click();$('#zlReset').click();o.reset={nd:Object.keys(z().nd).length,nq:z().nq};
 o.log=(load('kt_v8log')||[]).filter(e=>e.mode==='naht').map(e=>[e.ok,e.naht,e.k,e.tempo]).slice(0,3);
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
    c = {'Fly Me: Zeile 5 = 1, Zeile 6 = 2; Übergang 5→6 = 1→2': t(lambda: r['tw'] == [-1, -1, -1, -1, 0, 1, -1, -1] and r['nsig5']),
         'Übergang 1→2 = Griffe 10–15': t(lambda: r['naht1']['a'] == 10 and r['naht1']['b'] == 15),
         'gleiche Zeile wie eine, die sitzt → Verblassen; sonst Hören': t(lambda: r['twin'] == {'k': 4, 'stage': 3} and r['twinNot']['k'] == 0),
         'vor dem Stück 1–2 erst der Übergang, Knopf sagt es': t(lambda: r['pre']['p']['type'] == 'naht' and r['pre']['p']['k'] == 1 and r['pre']['p']['a'] == 10 and r['pre']['p']['b'] == 15 and r['pre']['go'] == 'Weiter: Übergang Zeile 1 → 2 · aus dem Kopf'),
         'Übergang: 1× vorspielen, 60 %, kein Anlauf, nur der erste Griff sichtbar': t(lambda: r['run1']['demo'] and r['run1']['tempo'] == 0.6 and r['run1']['la'] == r['run1']['a'] and r['run1']['vis'] == [1, 0, 0] and r['run1']['chip'] == 'Übergang' and 'nur der Übergang' in r['run1']['bar']),
         '1× sauber → „Gut! Noch 1×“, ohne erneutes Vorspielen': t(lambda: r['run1']['res']['ok'] and 'Noch 1×' in r['run1']['res']['sub'] and r['run1']['head'] == 'Gut!' and not r['run2']['demo'] and r['run2']['spot']),
         '2× sauber → „Übergang sitzt!“, weiter mit Zeilen 1–2 am Stück': t(lambda: r['run2']['head'] == 'Übergang sitzt!' and r['run2']['nd'] == 1 and r['run2']['res']['next']['blk'] == '0-1'),
         '4× nicht geschafft → Noten deutlicher, dann weiter zum Stück': t(lambda: r['fail']['fl'][1]['sv'] == 0.5 and r['fail']['fl'][2]['sv'] == 0.5 and r['fail']['nd'] == -1 and r['fail']['next'] == '0-1' and 'kommt wieder' in r['fail']['fl'][3]['sub']),
         'vor dem Song: gleicher Übergang (5→6 = 1→2) zählt als geschafft, fehlender kommt': t(lambda: r['song']['k'] == -1 and not r['song'].get('spot') and r['song4'] == 4),
         'Song sitzt schon → keine Übergänge vorab, direkt der Song': t(lambda: r['songSitzt']['k'] == -1 and not r['songSitzt'].get('spot') and r['songSitzt'].get('bonus') == 1),
         'Stück hakt 3× am Zeilenanfang → Übergang nachüben, nicht Zeile': t(lambda: r['blk'] == '0-1' and r['stall']['nq'] == 1 and r['stall']['rep'] is None and 'Übergang Zeile 1 → 2' in r['stall']['sub'] and r['stall']['next'] == 1 and r['stall']['run'] == 'naht'),
         'Übergang sitzt wieder → zurück zum Stück': t(lambda: r['stall']['back']['nq'] is None and r['stall']['back']['next'] == '0-1'),
         'ohne Stocker an der Grenze → schwächste Zeile wie bisher': t(lambda: r['noStall']['nq'] is None and r['noStall']['rep'] == 0),
         'Mini-Zeile (4 Griffe) wird angehängt, aber nicht, wenn die Zeile zu lang würde': t(lambda: r['mini'] == ['0-12', '13-25', '26-88'] and r['miniLong'][0] == '0-3'),
         'Zurücksetzen löscht die Übergänge': t(lambda: r['reset'] == {'nd': 0, 'nq': None}),
         'Protokoll: mode „naht“ mit Übergang und 60 %': t(lambda: r['log'][0][1] == 1 and r['log'][0][3] == 0.6),
         'Version 5.61': t(lambda: r['ver'].startswith('Version 5.61')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
