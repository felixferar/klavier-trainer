"""Test: Eingabefeld der Warteschlange wird nach dem Durchlauf geleert; bei Abbruch bleibt der Text; Fehler bei Vorbereitung lassen Text stehen."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(500); await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""async()=>{NAT.ok=true;const o={};showConvError=()=>{};const T='https://youtu.be/AAAAAAAAAAA https://youtu.be/BBBBBBBBBBB';
          openYT=(it,a)=>{setTimeout(()=>Q.finish(true,it.videoId),20)};
          $('#ytMulti').value=T;await qStart($('#ytMulti').value);o.fertig={feld:$('#ytMulti').value,gespeichert:load('kt_lastq')};
          $('#ytMulti').value=T;openYT=(it,a)=>{setTimeout(()=>{Q.cancel=true;Q.finish(false,'abgebrochen')},20)};await qStart($('#ytMulti').value);o.abbruch={feld:$('#ytMulti').value,gespeichert:load('kt_lastq')};
          LIB.push({id:'m1',type:'midi',title:'a',fromYT:'AAAAAAAAAAA',data:''});LIB.push({id:'m2',type:'midi',title:'b',fromYT:'BBBBBBBBBBB',data:''});
          $('#ytMulti').value=T;save('kt_lastq',T);await qStart(T);o.alleVorhanden={feld:$('#ytMulti').value,gespeichert:load('kt_lastq')};
          $('#ytMulti').value='kein link';await qStart('kein link');o.keinLink={feld:$('#ytMulti').value};
          return o}""")
        globals().__setitem__('_R',r);print(json.dumps(r,ensure_ascii=False)); globals().__setitem__('_E',errs);print('pageerrors',errs); await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'nach dem Durchlauf ist das Feld leer':r['fertig']=={'feld':'','gespeichert':''},'bei Abbruch bleibt der Text':'AAAAAAAAAAA' in r['abbruch']['feld'] and r['abbruch']['feld']==r['abbruch']['gespeichert'],'alle schon vorhanden: Feld leer':r['alleVorhanden']=={'feld':'','gespeichert':''},'ohne Link bleibt der Text stehen':r['keinLink']['feld']=='kein link'}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
