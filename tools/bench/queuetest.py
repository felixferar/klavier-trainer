import sys, asyncio, json
from playwright.async_api import async_playwright
APP='file://'+sys.argv[1]
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(500)
        await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""async()=>{NAT.ok=true;window.__opened=[];window.__sh=[];
          openYT=(it,a)=>{window.__opened.push(it.videoId);setTimeout(()=>Q.finish(true,it.videoId),30)};
          const e0=showConvError;showConvError=(m,t)=>{window.__sh.push(m)};
          LIB.push({id:'m1',type:'midi',title:'a',fromYT:'AAAAAAAAAAA',data:''});
          await qStart('https://youtu.be/AAAAAAAAAAA https://youtu.be/BBBBBBBBBBB https://youtu.be/BBBBBBBBBBB https://youtu.be/CCCCCCCCCCC');
          const o1={opened:window.__opened.slice(),msg:window.__sh.slice()};
          window.__opened=[];window.__sh=[];
          await qStart('https://youtu.be/AAAAAAAAAAA');
          return {run1:o1,allSkipped:{opened:window.__opened,msg:window.__sh,qOn:Q.on}}}""")
        globals().__setitem__('_R',r);print(json.dumps(r,ensure_ascii=False,indent=1)); globals().__setitem__('_E',errs);print('pageerrors',errs); await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'vorhandene Songs werden übersprungen, die anderen erstellt':r['run1']['opened']==['BBBBBBBBBBB','CCCCCCCCCCC'] and '2 von 2 Songs erstellt' in r['run1']['msg'][0] and 'übersprungen' in r['run1']['msg'][0],'alle schon vorhanden: nichts zu tun, Warteschlange aus':r['allSkipped']['opened']==[] and 'nichts zu tun' in r['allSkipped']['msg'][0] and r['allSkipped']['qOn'] is False}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
