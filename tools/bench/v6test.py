"""v6-Prototyp in der App: Schalter aus = nichts ändert sich · Schalter an = „Los“ auf der Startseite, Durchgänge laufen über die echte Anbindung
(Song laden, Übernahme des alten Lernstands, Tasten, Speichern, Protokoll). Der Kern selbst wird in Node geprüft: node tools/v6/test.js
usage: python3 tools/bench/v6test.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
KERN = open(os.path.join(os.path.dirname(__file__), '..', 'v6', 'lernen.js'), encoding='utf-8').read()
JS = r"""async (SG)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};window.fxLine=()=>{};window.fxBig=()=>{};const o={},sl=ms=>new Promise(r=>setTimeout(r,ms));
 const mk=(id,ns)=>({id,type:'midi',title:id,artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))});
 const it=mk('fly_me',SG.fly_me),it2=mk('elise',SG.fuer_elise);LIB=[it,it2];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);
 /* 1. Schalter aus: kein Knopf */
 localStorage.removeItem('kt_v6on');renderHome();o.aus={on:v6On(),btn:!!$('#v6Go'),kern:typeof Lernen};
 /* alter Lernstand: Fly Me sitzt komplett */
 openMem(it);{const y=zlState();y.st=y.st.map(()=>4);y.song=0;memSaveAll()}memStop();show('home');
 /* 2. Schalter an */
 $('#v6Sw').click();o.an={on:v6On(),btn:!!$('#v6Go'),txt:$('#v6Go')&&$('#v6Go').textContent,sw:$('#v6Sw').textContent};
 /* 3. Los → Fly Me, Übernahme → Abschnitt A im Takt, rechte Hand */
 save('kt_l6',{songs:{},app:{aktuell:'fly_me'}});$('#v6Go').click();await sl(100);
 o.los={screen:!$('#v6').classList.contains('hidden'),id:V6.id,art:V6.art,A:V6.A,pos:V6.st.pos.slice(),titel:V6.run.bild().titel,namen:V6.M.abschnitte.map(s=>s.name).join(' ')};
 /* Durchgang von Hand treiben (ohne Bildschirm-Takt): genau im Takt spielen, über kbNoteOn wie das echte Klavier */
 const treibe=(plan)=>{cancelAnimationFrame(V6.raf);const R=V6.run,ev=R.E.map((e,i)=>({q:e.q,e,i}));let i=0,n=0;while(V6.run===R&&!R.fertig&&n++<200000){R.tick(0.005);while(i<ev.length&&ev[i].q<=R.q){if(!plan||plan(ev[i].i))for(const m of ev[i].e.mids)kbNoteOn(m);i++}}if(V6.run===R&&R.fertig)v6Fertig()};
 treibe();clearTimeout(V6.auto);o.d1={res:$('#v6ResT').textContent,pos:V6.st.pos.slice(),saved:(load('kt_l6').songs.fly_me||{}).pos,log:(load('kt_v8log')||[]).slice(-1)[0],next:$('#v6Next').textContent,bar:$('#v6Bar').textContent};
 $('#v6Next').click();await sl(50);o.d2={A:V6.A,titel:V6.run.bild().titel};
 /* nichts spielen → nicht geschafft, Stand bleibt */
 treibe(()=>false);clearTimeout(V6.auto);o.d3={res:$('#v6ResT').textContent,pos:V6.st.pos.slice()};
 /* 3b. Song sitzt im alten Modus → direkt der ganze Song; Abschnitt antippen → einmal gezielt, danach wieder der ganze Song; gestockt → kein Absprung */
 v6Zu();openMem(it);{const y=zlState();y.song=1;memSaveAll()}memStop();$('#v6Go').click();await sl(100);o.sitzt={A:V6.A,pos:V6.st.pos.slice(),bar:$('#v6Bar').children.length};
 $('#v6Bar').children[1].click();await sl(50);o.sitzt.wahl=Object.assign({},V6.A);treibe();clearTimeout(V6.auto);$('#v6Next').click();await sl(50);o.sitzt.danach=Object.assign({},V6.A);
 treibe(()=>false);clearTimeout(V6.auto);o.sitzt.res=$('#v6ResT').textContent;$('#v6Next').click();await sl(50);o.sitzt.nachFehl=Object.assign({},V6.A);o.sitzt.pos2=V6.st.pos.slice();
 /* 4. Warte-Stufe über die Anbindung: zweiter Song ist neu → Zeigen */
 v6Zu();save('kt_l6',Object.assign(load('kt_l6'),{app:{aktuell:'elise'}}));$('#v6Go').click();await sl(100);cancelAnimationFrame(V6.raf);
 o.neu={id:V6.id,A:V6.A,leuchten:V6.run.bild().leuchten.length,haendeOk:V6.M.haendeOk};
 {const R=V6.run;let n=0;while(!R.fertig&&n++<999){const e=R.E[R.pos];for(const m of e.mids)kbNoteOn(m)}}clearTimeout(V6.auto);o.neu.res=$('#v6ResT').textContent;o.neu.pos=V6.st.pos.slice();
 /* 5. alter Auswendig-Modus läuft daneben unverändert */
 v6Zu();openMem(it);const r=zlStart(zlPick(zlState()));o.alt={zl:!!r.zl,k:r.k,v6run:V6.run};memStop();
 o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 800, 'height': 600}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        try: r = await pg.evaluate(JS, SONGS)
        except Exception as e: r = {'crash': str(e)[:600]}
        html = await pg.content(); await br.close()
    print(json.dumps(r, ensure_ascii=False)[:3000])
    src = open(sys.argv[1], encoding='utf-8').read()
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'eingebauter Kern = tools/v6/lernen.js': KERN in src,
         'Schalter aus: kein „Los“-Knopf, Kern geladen': t(lambda: not r['aus']['on'] and not r['aus']['btn'] and r['aus']['kern'] == 'object'),
         'Schalter an: „Los“ auf der Startseite': t(lambda: r['an']['on'] and r['an']['btn'] and r['an']['txt'].startswith('Los') and r['an']['sw'] == 'An'),
         'Los → Fly Me; alter Stand übernommen → Abschnitt A · Im Takt · rechts, die App spielt links': t(lambda: r['los']['screen'] and r['los']['id'] == 'fly_me' and r['los']['art'] == 'weiter' and r['los']['pos'] == [4] * 6 and r['los']['A']['stufe'] == 3 and r['los']['A']['hand'] == 'R' and 'Abschnitt A · Im Takt' in r['los']['titel'] and 'die App spielt links' in r['los']['titel'] and r['los']['namen'] == 'A B C A B D'),
         'im Takt gespielt (über die Klavier-Eingabe) → geschafft, gespeichert, protokolliert': t(lambda: r['d1']['res'].startswith('✓') and r['d1']['pos'][0] == 5 and r['d1']['saved'][0] == 5 and r['d1']['log']['v6'] == 1 and r['d1']['log']['ok'] == 1 and r['d1']['log']['stocker'] == 0),
         '„Weiter“ → derselbe Abschnitt, beide Hände im Takt': t(lambda: r['d2']['A']['k'] == 0 and r['d2']['A']['nr'] == 6 and r['d2']['A']['hand'] == 'LR'),
         'nichts gespielt → nicht geschafft, Stand bleibt': t(lambda: not r['d3']['res'].startswith('✓') and 'gestockt' in r['d3']['res'] and r['d3']['pos'][0] == 5),
         'Song sitzt schon → direkt „Ganzer Song · Im Takt“': t(lambda: r['sitzt']['A']['k'] == -1 and r['sitzt']['pos'] == [6] * 6),
         'Abschnitt B antippen → B im Takt, danach wieder der ganze Song': t(lambda: r['sitzt']['wahl']['k'] == 1 and r['sitzt']['wahl']['stufe'] == 3 and r['sitzt']['danach']['k'] == -1),
         'ganzer Song gestockt → kein Absprung: wieder der ganze Song, Stand bleibt': t(lambda: 'gestockt' in r['sitzt']['res'] and r['sitzt']['nachFehl']['k'] == -1 and r['sitzt']['pos2'] == [6] * 6),
         'neuer Song → Abschnitt A · Zeigen · eine Hand, Taste leuchtet; durchgespielt → weiter': t(lambda: r['neu']['id'] == 'elise' and r['neu']['A']['stufe'] == 1 and r['neu']['leuchten'] >= 1 and r['neu']['res'].startswith('✓') and r['neu']['pos'][0] >= 1),
         'alter Auswendig-Modus läuft daneben unverändert': t(lambda: r['alt']['zl'] and r['alt']['v6run'] is None),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
