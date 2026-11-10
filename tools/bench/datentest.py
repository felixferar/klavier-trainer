import sys, asyncio, json
from playwright.async_api import async_playwright
APP = 'file://' + sys.argv[1]
NOTES = "Array.from({length:40},(_,i)=>({m:60+i%12,start:1+i*0.5,dur:0.4,hand:i%2?'L':'R',hue:i%2?100:300}))"
PRE = """()=>{window.__notes=%s;SCAN.keys=[{m:48},{m:84}];SCAN.start=0;SCAN.frames=10;SCAN.lastVt=10;SCAN.fromFile=false;
 window.__toasts=[];const t0=window.toast;window.toast=(m,ms)=>{window.__toasts.push(m);return t0&&t0(m,ms)};
 window.__sh=[];const e0=window.showConvError;window.showConvError=(m,t)=>{window.__sh.push(m);try{return e0(m,t)}catch(e){}}}""" % NOTES
async def newpage(br):
    pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(APP); await pg.wait_for_timeout(500)
    await pg.evaluate("localStorage.clear();sessionStorage.clear()")
    await pg.evaluate(PRE); return pg, errs
async def fill(pg, free):
    return await pg.evaluate("""(free)=>{let n=0,chunk='x'.repeat(100000);
      try{while(true){localStorage.setItem('b'+n,chunk);n++}}catch(e){}
      localStorage.removeItem('b'+(n-1)); let s=1000;
      while(s>=1){try{localStorage.setItem('c'+s+'_'+n,'y'.repeat(s));n++}catch(e){s=s>>1}}
      /* now nearly full: free a defined amount */
      const k=Object.keys(localStorage).filter(k=>k[0]=='c').sort((a,b)=>localStorage.getItem(a).length-localStorage.getItem(b).length); let freed=0; for(const x of k){ if(freed>=free)break; freed+=localStorage.getItem(x).length+x.length; localStorage.removeItem(x)} return freed}""", free)
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        res = {}
        # T1: storage full, manual save
        pg, errs = await newpage(br)
        await fill(pg, 100)
        r = await pg.evaluate("""()=>{const before=LIB.length,raw=localStorage.getItem('kt_lib');SCAN.result=window.__notes;scanSave(false);
          return {libBefore:before,libAfter:LIB.length,persistedSame:localStorage.getItem('kt_lib')===raw,resultKept:!!SCAN.result,toasts:window.__toasts,dialogOpen:document.querySelector('#scanDone').classList.contains('on')}}""")
        res['T1 Speicher voll (manuell)'] = r
        # T2: storage full inside queue
        pg, errs = await newpage(br)
        await fill(pg, 100)
        r = await pg.evaluate("""()=>{Q.on=true;Q.cancel=false;let got=null;Q.res=x=>{got=x};SCAN.result=window.__notes;scanSave(true);
          const o={queueResult:got,cancel:Q.cancel,libAfter:LIB.length};Q.on=false;return o}""")
        res['T2 Speicher voll (Warteschlange)'] = r
        # T3: update while result is waiting
        pg, errs = await newpage(br)
        await pg.evaluate('''window.fetch=async()=>({text:async()=>'<span id="verTxt">Version 99.9</span>'})''')
        r = await pg.evaluate("""async()=>{window.__rl=0;doReload=()=>{window.__rl++};SCAN.on=false;SCAN.result=window.__notes;try{sessionStorage.clear()}catch(e){}
          await updCheck();return {reloads:window.__rl}}""")
        res['T3 Update bei offenem Ergebnis'] = r
        # T3b: update with nothing pending must still reload
        r = await pg.evaluate("""async()=>{window.__rl=0;SCAN.result=null;try{sessionStorage.clear()}catch(e){}await updCheck();return {reloads:window.__rl}}""")
        res['T3b Update ohne offenes Ergebnis (soll laden)'] = r
        # T5: cancel in the 500 ms window
        pg, errs = await newpage(br)
        r = await pg.evaluate("""async()=>{finishScan=()=>window.__notes;diagSave=()=>{};SCAN.on=true;SCAN.fromFile=true;ytAuto=true;
          const n0=LIB.length;scanStop();await new Promise(r=>setTimeout(r,200));convCancelled();await new Promise(r=>setTimeout(r,800));
          return {libAdded:LIB.length-n0,msgs:window.__sh,resultLeft:!!SCAN.result}}""")
        res['T5 Abbrechen im 500-ms-Fenster'] = r
        # T10: normal auto save still works
        pg, errs = await newpage(br)
        r = await pg.evaluate("""async()=>{finishScan=()=>window.__notes;diagSave=()=>{};SCAN.on=true;SCAN.fromFile=true;ytAuto=true;
          const n0=LIB.length;scanStop();await new Promise(r=>setTimeout(r,900));
          return {libAdded:LIB.length-n0,persisted:JSON.parse(localStorage.getItem('kt_lib')||'[]').length,resultLeft:!!SCAN.result}}""")
        res['T10 normaler Auto-Pfad (soll 1 Song)'] = r
        res['pageerrors'] = errs
        print(json.dumps(res, ensure_ascii=False, indent=1))
        await br.close()
asyncio.run(main())
