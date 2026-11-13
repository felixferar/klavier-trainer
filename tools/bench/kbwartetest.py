"""v4.75: Solange das Klavier nach dem Öffnen noch nicht geantwortet hat, zeigt die App „Verbinde … ist das Klavier eingeschaltet?“ – nie „verbunden“."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""()=>{const o={};
 window.nat=()=>Promise.resolve(null);kbConnectTo('41:88','GZUT-MIDI'); /* v4.75: Nutzer hat selbst „verbinden“ gedrückt */
 kbMsg({cmd:'kbState',state:'connecting',name:'GZUT-MIDI',addr:'41:88',saved:'41:88'});
 kbMsg({cmd:'kbLog',line:'Ausgang geöffnet: true'});kbMsg({cmd:'kbLog',line:'Warte auf Antwort vom Klavier …'});
 o.chip=kbInfo().label;o.big=($('#kbBig')||{textContent:''}).textContent;
 kbMsg({cmd:'kbState',state:'waiting',name:'GZUT-MIDI',addr:'41:88',saved:'41:88',msg:'Klavier nicht gefunden – ist es eingeschaltet? Ich versuche es weiter.'});
 o.chip2=kbInfo().label;o.big2=($('#kbBig')||{textContent:''}).textContent;
 kbMsg({cmd:'kbLog',line:'Klavier antwortet – verbunden'});kbMsg({cmd:'kbState',state:'on',name:'GZUT-MIDI',addr:'41:88',saved:'41:88'});
 o.chip3=kbInfo().label;return o}"""
async def main(url):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':400,'height':780});errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+url);await pg.wait_for_timeout(800)
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'beim Warten nicht verbunden':r['chip']!='Klavier verbunden' and 'eingeschaltet' in r['big'],
           'nicht gefunden: Hinweis einschalten':r['chip2']!='Klavier verbunden' and 'eingeschaltet' in r['big2'],
           'nach Antwort verbunden':r['chip3']=='Klavier verbunden','keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await b.close()
asyncio.run(main(sys.argv[1]))
