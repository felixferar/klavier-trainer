"""v4.75: drei klare Zustände – verbunden / nicht verbunden (Hintergrund-Versuche unsichtbar) / verbinde … (nur wenn der Nutzer selbst verbinden gedrückt hat)."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""()=>{const o={};window.nat=()=>Promise.resolve(null);const st=(s,x)=>kbMsg(Object.assign({cmd:'kbState',state:s,name:'GZUT-MIDI',addr:'41:88',saved:'41:88'},x||{}));
 st('on');o.on=kbInfo().label;
 st('lost',{msg:'Verbindung zum Keyboard verloren – verbinde neu …'});o.lost=kbInfo().label;o.lostBig=($('#kbBig')||{textContent:''}).textContent;
 st('connecting');o.bgConn=kbInfo().label;st('waiting');o.bgWait=kbInfo().label;st('connecting');o.bgConn2=kbInfo().label;
 kbConnectTo('41:88','GZUT-MIDI');o.manual=kbInfo().label;o.manualBig=($('#kbBig')||{textContent:''}).textContent;
 st('waiting',{msg:'Klavier nicht gefunden – ist es eingeschaltet? Ich versuche es weiter.'});o.manualWait=($('#kbBig')||{textContent:''}).textContent;
 st('on');o.on2=kbInfo().label;st('connecting');o.after=kbInfo().label;return o}"""
async def main(url):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':400,'height':780});errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+url);await pg.wait_for_timeout(800)
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'verbunden':r['on']=='Klavier verbunden' and r['on2']=='Klavier verbunden',
           'aus → nicht verbunden':r['lost']=='Nicht verbunden' and 'Nicht verbunden' in r['lostBig'],
           'Hintergrund-Versuche ruhig':r['bgConn']=='Nicht verbunden' and r['bgWait']=='Nicht verbunden' and r['bgConn2']=='Nicht verbunden',
           'selbst verbinden → Verbinde':r['manual'].startswith('Verbinde') and 'Verbinde' in r['manualBig'],
           'selbst, nicht gefunden → Hinweis':'eingeschaltet' in r['manualWait'],
           'nach Verbindung wieder ruhig':r['after']=='Nicht verbunden','keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await b.close()
asyncio.run(main(sys.argv[1]))
