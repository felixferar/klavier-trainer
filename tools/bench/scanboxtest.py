"""v4.37: scanBox (-> geo.ar) wird auch im automatischen Weg (scanRun) gesetzt, nicht nur im manuellen scanStart-Weg. Rot vor Fix: scanBox bleibt null."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500)
        o=await pg.evaluate("""async()=>{NAT.ok=true;scanBox=null;
          ytp={getCurrentTime:()=>5,pauseVideo(){},setPlaybackRate(){},getDuration:()=>100};
          scanDet={w:1,W:1};scanRows={yA:0.8,yB:0.92};scanImg={width:10,height:10,data:[]};keyLayout=()=>[{m:48,x:0.1}];restColors=()=>{};laneHigh=()=>[];
          nat=async()=>({ok:false});
          try{await scanRun(true)}catch(e){return {err:String(e).slice(0,80),box:scanBox}}
          return {box:scanBox}}""")
        print(json.dumps(o),errs);await br.close()
asyncio.run(main())
