import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(400)
        r=await pg.evaluate("""async()=>{ytAuto=true;const log=[];let t0=performance.now(),vt=0,rate=1,state=3,last=performance.now();
          // fake player: ad for 1 s (state 3), then the main video plays with the current rate
          ytp={getPlayerState:()=>{const n=performance.now();if(state===1){vt+=(n-last)/1000*rate}last=n;if(n-t0>1000)state=1;return state},getCurrentTime:()=>vt,
               setPlaybackRate:x=>{rate=x;log.push(['rate',x,Math.round(performance.now()-t0)])},playVideo:()=>{},pauseVideo:()=>{},mute:()=>{},unMute:()=>{}};
          const t1=performance.now();const ok=await waitMainVideo(20000);
          return {ok,videoTimeAtReturn:+vt.toFixed(2),realMs:Math.round(performance.now()-t1),log}}""")
        globals().__setitem__('_R',r);print(json.dumps(r)); globals().__setitem__('_E',errs);print('pageerrors',errs); await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'wartet erfolgreich':r['ok'] is True,'Video steht danach am Anfang':r['videoTimeAtReturn']<0.5,'dauert etwa eine Sekunde':500<r['realMs']<6000,'Tempo wurde zum Warten gedrosselt':any(x[0]=='rate' for x in r['log'])}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
