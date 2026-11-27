"""Test convShowTitle: Titel im Umwandlungs-Panel, mit (n/N) in der Warteschlange, Rückfall ohne Titel (kein alter Titel bleibt stehen)."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(400)
        r=await pg.evaluate("""()=>{const o={},t=()=>document.getElementById('convTitle').textContent;
          convShowTitle({title:'Secret Garden – Piano'});o.einzeln=t();
          Q.on=true;Q.i=1;Q.n=3;convShowTitle({title:'Fly'});o.queue=t();Q.i=0;convShowTitle({title:'Erster'});o.queueErster=t();Q.i=1;
          convShowTitle({title:'YouTube-Video'});o.ohneTitel=t();
          convShowTitle(null);o.nullItem=t();Q.on=false;
          document.getElementById('yt').classList.add('convL');document.body.classList.add('convL');const el=document.getElementById('convTitle');o.querformat={sichtbar:getComputedStyle(el).display!=='none',nowrap:getComputedStyle(el).whiteSpace};
          return o}""")
        globals().__setitem__('_R',r);print(json.dumps(r,ensure_ascii=False)); globals().__setitem__('_E',errs);print('pageerrors',errs); await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'einzeln: Titel im Panel':r['einzeln'].endswith('Secret Garden – Piano'),'Warteschlange: Zähler und Titel':r['queue']=='1 von 3 fertig · Fly' and r['queueErster']=='0 von 3 fertig · Erster','ohne Titel bleibt kein alter Titel stehen':r['ohneTitel'].endswith('Song wird erstellt …') and r['nullItem'].endswith('Song wird erstellt …'),'im Querformat sichtbar, einzeilig':r['querformat']=={'sichtbar':True,'nowrap':'nowrap'}}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
