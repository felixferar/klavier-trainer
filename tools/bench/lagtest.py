"""v5.05: Abtastung alle 22 ms; kommt die App nicht hinterher (Bilder > 0,25 s verspätet, 10× in Folge), schaltet sie auf 40 ms zurück.
usage: python3 tools/bench/lagtest.py $PWD/web/index.html"""
import sys, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(1500)
        src = await pg.evaluate("()=>{const a=document.documentElement.innerHTML;return {i22:/interval:22/.test(a),fb:/SCAN\\.slow=true/.test(a)}}")
        r = await pg.evaluate("""()=>{const sent=[];window.nat=(c,x)=>{sent.push([c,x&&x.interval]);return Promise.resolve({ok:true})};
          window.scanCore=()=>{};window.diagFrame=()=>{};window.ytp={getPlayerState:()=>1,getCurrentTime:()=>0};
          Object.assign(SCAN,{on:true,keys:[{}],vtMap:[],natArgs:{interval:22},lagMin:null,lagN:0,slow:false});
          const d=btoa('x'),t0=performance.now();
          for(let i=0;i<30;i++)scanFrame({t:performance.now()-5,d,w:1,n:1}); const okFast=!SCAN.slow&&sent.length===0;
          for(let i=0;i<9;i++)scanFrame({t:performance.now()-400,d,w:1,n:1}); const not9=!SCAN.slow;
          scanFrame({t:performance.now()-400,d,w:1,n:1}); const slow=SCAN.slow&&sent.length===1&&sent[0][0]==='scanStart'&&sent[0][1]===40;
          for(let i=0;i<20;i++)scanFrame({t:performance.now()-400,d,w:1,n:1}); const once=sent.length===1;
          return {okFast,not9,slow,once}}""")
        await br.close()
    ok = True
    for k, v in [('Code: Intervall 22 ms', src['i22']), ('Code: Rückschaltung vorhanden', src['fb']), ('pünktliche Bilder: bleibt schnell', r['okFast']),
                 ('9 verspätete Bilder: noch schnell', r['not9']), ('10 verspätete Bilder: zurück auf 40 ms', r['slow']), ('nur einmal umschalten', r['once']), ('keine Seitenfehler', not errs)]:
        print(('OK  ' if v else 'FEHLER ') + k); ok &= bool(v)
    print('ALLES OK' if ok else 'FEHLGESCHLAGEN'); sys.exit(0 if ok else 1)
asyncio.run(main())
