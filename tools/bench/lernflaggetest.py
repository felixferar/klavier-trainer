"""v5.60: 🚩 „Hier stimmt was nicht“ im Auswendig-Modus – Stelle wird gemerkt (kt_lflags) und nach diag/flags/…_lern.json hochgeladen.
usage: python3 tools/bench/lernflaggetest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""async (SG)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};const o={},ups=[];
 const it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',fromYT:'abcdefghijk',video:{first:3},data:b64FromBuf(writeMidi(SG.fly_me.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};
 openMem(it);const gs=MEM.gs;zlState().st=[4,4,4,4,4,4,4,4];memSaveAll();
 /* ohne Schlüssel: nur merken */
 let r=zlStart({k:2,stage:4});for(const m of gs[r.a].mids)memPress(m,'kb');for(const m of gs[r.a+1].mids)memPress(m,'kb');
 o.btn=!!$('#zlFlag')&&getComputedStyle($('#zlFlag')).display!=='none';$('#zlFlag').click();
 const L=load('kt_lflags')||[];o.n1=L.length;o.f=L[0];o.posT=gs[r.a+2].start;o.runAlive=MEM.run===r&&!r.done&&r.pos===r.a+2;
 /* mit Schlüssel: Upload, danach leer */
 save('kt_ghtok','x');window.ghUpload=async(p,b,m)=>{ups.push([p,JSON.parse(decodeURIComponent(escape(atob(b))))]);return {ok:true}};
 await zlFlagSync();await new Promise(z=>setTimeout(z,50));o.ups=ups.map(u=>u[0]);o.up0=ups[0]&&ups[0][1].kind;o.n2=(load('kt_lflags')||[]).length;
 /* beim Vorspielen: Zeit des Vorspielens */
 memStop();r=zlStart({k:1,stage:4});zlDemo(r,false);for(let t=0;t<1.5;t+=0.02)zlTick(r,0.02);const dt=r.demo.t;$('#zlFlag').click();await new Promise(z=>setTimeout(z,50));
 o.demoF=ups[1]&&ups[1][1];o.dt=dt;o.stillDemo=!!r.demo;
 /* Upload scheitert → bleibt gemerkt */
 window.ghUpload=async()=>({ok:false});$('#zlFlag').click();await new Promise(z=>setTimeout(z,50));o.n3=(load('kt_lflags')||[]).length;memStop();return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 800, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        try: r = await pg.evaluate(JS, SONGS)
        except Exception as e: r = {'crash': str(e)[:400]}
        await br.close()
    print(json.dumps(r, ensure_ascii=False)[:1500])
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'🚩-Knopf im Übungsbildschirm sichtbar': t(lambda: r['btn']),
         'Tippen merkt die Stelle (Zeit des aktuellen Griffs, Video-Zeit, Noten drumherum)': t(lambda: r['n1'] == 1 and r['f']['kind'] == 'lernflag' and abs(r['f']['T'] - r['posT']) < 0.02 and abs(r['f']['video'] - (r['f']['T'] + 2)) < 0.02 and len(r['f']['near']) >= 3 and r['f']['videoId'] == 'abcdefghijk'),
         'der Durchgang läuft ungestört weiter': t(lambda: r['runAlive']),
         'mit Schlüssel: Upload nach diag/flags/…_lern.json, Merkliste danach leer': t(lambda: r['ups'][0].startswith('diag/flags/') and r['ups'][0].endswith('_abcdefghijk_lern.json') and r['up0'] == 'lernflag' and r['n2'] == 0),
         'beim Vorspielen: Stelle = Vorspiel-Zeit': t(lambda: r['demoF']['demo'] == 1 and abs(r['demoF']['T'] - (r['dt'] - 0.3)) < 0.05 and r['stillDemo']),
         'Upload scheitert → bleibt gemerkt (wird nachgeholt)': t(lambda: r['n3'] == 1),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
