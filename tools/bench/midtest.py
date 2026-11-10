"""Test diagMidTick: 4 Standbilder (25/50/75 %, dur-5 s), je einmal, ohne Auswirkung bei Datei-Scan / Diagnose aus / Fehlern."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(400)
        r=await pg.evaluate("""async()=>{const out={};let calls=0,fail=false;
          grabVideo=()=>{calls++;return new Promise((res,rej)=>setTimeout(()=>fail?rej(new Error('x')):res({}),50))};imgJpeg=()=>'data:image/jpeg;base64,AAAA';
          const run=async(dur)=>{for(let vt=0;vt<=dur;vt+=0.3){diagMidTick(vt,dur);await new Promise(r=>setTimeout(r,0))}await new Promise(r=>setTimeout(r,200))};
          DIAG.on=true;DIAG.meta={};SCAN.fromFile=false;calls=0;await run(200);out.normal={calls,t:DIAG.meta.midStills.map(x=>x.t)};
          DIAG.meta={};calls=0;SCAN.fromFile=true;await run(200);out.datei={calls,has:!!DIAG.meta.midStills};
          SCAN.fromFile=false;DIAG.on=false;DIAG.meta={};calls=0;await run(200);out.diagAus={calls};
          DIAG.on=true;DIAG.meta={};calls=0;fail=true;await run(200);out.fehler={calls,n:(DIAG.meta.midStills||[]).length};
          fail=false;DIAG.meta={};calls=0;await run(15);out.kurz={calls};
          DIAG.meta={};calls=0;(async()=>{for(let vt=0;vt<=60;vt+=0.3){diagMidTick(vt,200);if(vt>=50)DIAG.meta=null;await new Promise(r=>setTimeout(r,0))}})();await new Promise(r=>setTimeout(r,600));out.metaNull='ok';
          return out}""")
        print(json.dumps(r)); print('pageerrors',errs); await br.close()
asyncio.run(main())
