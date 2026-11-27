"""Test 'Alle Songs löschen': zwei Bestätigungen, Zeitablauf setzt zurück, gesperrt bei Umwandlung, Profil/Statistik bleiben."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(400)
        r=await pg.evaluate("""async()=>{const o={},sl=ms=>new Promise(r=>setTimeout(r,ms)),b=document.getElementById('delSongs');
          const seed=()=>{LIB=[{id:'a',type:'midi',title:'A',fromYT:'x'},{id:'b',type:'midi',title:'B'},{id:'c',type:'midi',title:'C'}];save('kt_lib',LIB)};
          ST.bestStreak=7;save('kt_stats',ST);
          seed();b.click();o.nach1=b.textContent;b.click();o.nach2=b.textContent;o.libZwischen=LIB.length;b.click();o.libEnde=LIB.length;o.gespeichert=JSON.parse(localStorage.getItem('kt_lib')).length;o.btn=b.textContent;o.statsBleiben=ST.bestStreak;
          seed();b.click();await sl(4300);o.nachZeit={txt:b.textContent,lib:LIB.length};
          seed();b.click();b.click();await sl(4300);o.zeit2={txt:b.textContent,lib:LIB.length};
          seed();SCAN.on=true;b.click();o.gesperrt={lib:LIB.length,txt:b.textContent};SCAN.on=false;
          LIB=[];b.click();o.leer={txt:b.textContent};return o}""")
        globals().__setitem__('_R',r);print(json.dumps(r,ensure_ascii=False)); globals().__setitem__('_E',errs);print('pageerrors',errs); await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'erste Bestätigung nennt die Zahl der Songs':'Wirklich alle 3' in r['nach1'],'zweite Bestätigung':'Letzte Chance' in r['nach2'],'vor dem dritten Tippen ist nichts gelöscht':r['libZwischen']==3,'danach ist alles gelöscht und gespeichert':r['libEnde']==0 and r['gespeichert']==0 and r['btn']=='Löschen','Statistik bleibt':r['statsBleiben']>0,'Zeitablauf setzt zurück, nichts gelöscht':r['nachZeit']=={'txt':'Löschen','lib':3} and r['zeit2']['lib']==3,'während einer Umwandlung gesperrt':r['gesperrt']['lib']==3,'leere Bibliothek: Knopf bleibt ruhig':r['leer']['txt']=='Löschen'}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
