"""v4.44: Kalibrierung pausiert -> keine Karte auf der Startseite, kein Eintrag in den Einstellungen, Einfuehrung ohne Kalibrierungsseite"""
import sys,asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500)
        r=await pg.evaluate("""()=>{const o={};CAL={};KB.saved=null;renderHome();o.card=$('#calCard').classList.contains('hidden');
          renderSettings();const li=$('#calStat2').closest('.li');o.row=li.classList.contains('hidden');
          let called=0;const oc=openCal;openCal=()=>{called++};openOnb();o.pages=ONB.length;o.noCalPage=!ONB.some(x=>x.h==='Kalibrierung');
          while(onbI<ONB.length-1)$('#onbNext').click();o.lastBtn=$('#onbNext').textContent;o.skipHidden=$('#onbSkip').classList.contains('hidden');
          $('#onbNext').click();o.home=!$('#home').classList.contains('hidden');o.called=called;o.onbSaved=localStorage.getItem('kt_onb');
          openCal=oc;return o}""")
        print(r,errs)
        ok=r['card'] and r['row'] and r['pages']==4 and r['noCalPage'] and r['lastBtn']=="Los geht's" and r['skipHidden'] and r['home'] and r['called']==0 and not errs
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
