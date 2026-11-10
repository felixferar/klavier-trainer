"""v4.42: niedrige Videoqualitaet (<=240p) -> Warnung waehrend der Umwandlung, q im Song gespeichert, Hinweis in der Vergleichsansicht"""
import sys,asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500)
        r=await pg.evaluate("""()=>{const o={};let toasts=[];window.toast=m=>toasts.push(m);
          const run=q=>{ytp={getPlaybackQuality:()=>q};Object.assign(SCAN,{on:true,fromFile:false,frames:0,qMin:null,qWarned:false});toasts=[];scanQuality();SCAN.frames=50;scanQuality();return {qMin:SCAN.qMin,toasts:toasts.length}};
          o.tiny=run('tiny');o.hd=run('hd720');o.unknown=run('auto');
          SCAN.frames=0;ytp={getPlaybackQuality:()=>'hd720'};Object.assign(SCAN,{on:true,qMin:null,qWarned:false});scanQuality();ytp={getPlaybackQuality:()=>'small'};SCAN.frames=50;scanQuality();o.sinkt=SCAN.qMin;
          return o}""")
        print(r,errs)
        ok=(r['tiny']=={'qMin':144,'toasts':1} and r['hd']=={'qMin':720,'toasts':0} and r['unknown']['qMin'] is None and r['sinkt']==240 and not errs)
        print('OK' if ok else 'FAIL');sys.exit(0 if ok else 1)
asyncio.run(main())
