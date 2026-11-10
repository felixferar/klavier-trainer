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
        print(json.dumps(r)); print('pageerrors',errs); await br.close()
asyncio.run(main())
