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
        print(json.dumps(r,ensure_ascii=False)); print('pageerrors',errs); await br.close()
asyncio.run(main())
