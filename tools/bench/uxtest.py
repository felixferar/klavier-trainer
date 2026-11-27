"""v5.49: Design-/UX-Durchsicht – Startseite und Song-Seite zeigen den Zeilen-Stand, Auswendig-Zeit zählt fürs Tagesziel,
ein Zähler für Serie/Minuten, Hauptknopf überall in der App-Farbe, „So geht's“ gegliedert mit Farblegende.
usage: python3 tools/bench/uxtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
PRE = r"""()=>{const now=Date.now();localStorage.clear();
 save('kt_v8log',[{t:now-60000,zl:1,dur:120000,song:'fly_me',k:7,mode:'kopf',ok:1},{t:now-86400000,zl:1,dur:240000,song:'fly_me',k:6,mode:'kopf',ok:1}]);save('kt_onb',1);return 1}"""
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={};
 o.backfill={today:Math.round((ST.days[dayKey()]||0)/60),streak:streak(),flag:!!load('kt_zlTime')};
 const it={id:'fly_me',type:'midi',title:'Fly Me to the Moon',artist:'Frank Sinatra',data:b64FromBuf(writeMidi(S.fly_me.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);
 openMem(it);MEM.rec[zlKey()]={cv:2,n:89,cuts:[0,13,26,35,46,59,72,81],st:[4,4,4,4,4,4,4,3],eh:[0,0,0,0,0,0,0,0],stars:[2,2,2,2,2,2,2,0],song:0,kc:[2,2,2,2,2,2,2,0]};memSaveAll();
 o.meta=(zlHome(),$('#zlMeta').textContent);o.goColor=getComputedStyle($('#zlGo')).backgroundColor;o.priColor=getComputedStyle(document.querySelector('.btn.pri')||document.body).backgroundColor;
 o.how={stages:$$('.zlHowSt span').length,legend:$$('.zlHowLeg span').length,items:$$('.zlHow li').length};
 navStack=['home'];show('home');setTab('start');renderHome();o.home=$('#vStart').innerText;
 openSongPage(it);o.sp={go:$('#spGo').textContent,way:$('#spWay').innerText,bars:$$('#spBars > div').length,full:$$('#spBars > div.full').length};
 o.state=songState(it);o.sub=memSub(it,memInfo(it));
 /* Zeit einer Auswendig-Runde zählt fürs Tagesziel */
 const before=ST.days[dayKey()]||0;openMem(it);const r=zlStart({k:7,stage:4});r.t0=Date.now()-30000;const gs=MEM.gs;
 for(let j=r.a;j<=r.b;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(const m of gs[j].mids)memPress(m,'kb')}
 o.added=Math.round((ST.days[dayKey()]||0)-before);memStop();
 /* alles geschafft */
 const z=zlState();z.st=z.st.map(()=>4);for(const b of zlBlocks(8))z.bd[zlBK(b)]=1;z.song=3;memSaveAll();o.doneSub=memSub(it,memInfo(it));o.doneState=songState(it);
 openSongPage(it);o.doneGo=$('#spGo').textContent;
 o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 800, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(1500); await pg.evaluate(PRE)
        await pg.reload(); await pg.wait_for_timeout(2500)
        try: r = await pg.evaluate(JS, SONGS)
        except Exception as e: r = {'crash': str(e)[:300]}
        await br.close()
    print(json.dumps(r, ensure_ascii=False))
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'Nachtrag: Auswendig-Zeit aus dem Protokoll zählt (heute 2 Min, Serie 2 Tage)': t(lambda: r['backfill']['today'] == 2 and r['backfill']['streak'] == 2 and r['backfill']['flag']),
         'Auswendig-Übersicht nutzt dieselben Zahlen (Serie/Minuten)': t(lambda: '2 Tage in Folge' in r['meta'] and 'Heute 2 Min' in r['meta']),
         'Startseite: „7 von 8 Zeilen sitzen“, kein „Teil 1 von 8“': t(lambda: '7 von 8 Zeilen sitzen' in r['home'] and 'Teil 1 von' not in r['home']),
         'Song-Seite: „Weiter: Zeile 8 · Aus dem Kopf“, 7 volle Balken, „Alle Zeilen“': t(lambda: r['sp']['go'] == 'Weiter: Zeile 8 · Aus dem Kopf' and r['sp']['bars'] == 8 and r['sp']['full'] == 7 and 'Alle Zeilen' in r['sp']['way']),
         'Songliste: Status „am Lernen“': t(lambda: r['state'] == 1),
         'Auswendig-Runde zählt fürs Tagesziel (≈ 30 s)': t(lambda: 25 <= r['added'] <= 40),
         'alles geschafft: Status „sitzt“, „Ganzen Song wiederholen“': t(lambda: r['doneState'] == 2 and 'alles geschafft' in r['doneSub'] and r['doneGo'] == 'Ganzen Song wiederholen'),
         'Hauptknopf im Auswendig-Bereich in der App-Farbe (wie überall)': t(lambda: r['goColor'] == r['priColor']),
         "„So geht's“: 4 Stufen-Chips, 5 Farben in der Legende, 4 Punkte": t(lambda: r['how'] == {'stages': 4, 'legend': 5, 'items': 6}),
         'Version 5.75': t(lambda: r['ver'].startswith('Version 5.75')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(1 if bad else 0)
asyncio.run(main())
