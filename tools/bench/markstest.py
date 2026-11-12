"""v4.48: Markierungen aus: kein Bild vom Video gemacht, nichts gemessen, keine rot/gruen/gestrichelt-Markierung, Statuszeile leer, Weiter/Zurueck springen weiter"""
import sys,asyncio,json
from playwright.async_api import async_playwright
exec(open('/tmp/dshot.py').read().split("async def main")[0].replace("import sys,asyncio,json,os",""))
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':400,'height':780});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500)
        r=await pg.evaluate("""async([geo,lo])=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));o.flag=CMP_MARKS;let grabs=0;NAT.ok=true;grabVideo=async()=>{grabs++;return null};
          const notes=[];for(let i=0;i<10;i++)notes.push({m:lo+30,start:1+i,dur:0.5,hand:'R'});
          const a={id:'a',type:'midi',title:'T',artist:'x',data:b64FromBuf(writeMidi(notes)),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:2,first:3,fps:25,keys:[lo,lo+geo.kx.length-1],geo}};LIB=[a];
          window.openYT=()=>{cmpMode(!!CMP);show('yt')};let vt=3.2,seeks=[];ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(t){vt=t;seeks.push(t)},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2,destroy(){}};
          openCompare(a);await wait(300);vt=3.4;$('#cmpNextN').click();await wait(500);cmpDraw();
          o.seeks=seeks.length;o.grabs=grabs;o.lit=CMP.lit;o.step=CMP.step;o.busy=CMP.busy;o.status=$('#cmpDiff').textContent.trim();o.noBadStatus=!/Unterschied|passt|verdeckt|Messe|Prüfe|messbar/.test($('#cmpDiff').textContent);
          const cls=cmpCls(cmpSounding(CMP.notes,vt-CMP.off),CMP.litT&&CMP.lit);o.cls=[...cls.values()];
          return o}""",[geo,lo]);print(json.dumps(r,ensure_ascii=False),errs)
        ok=(r['flag'] is False and r['seeks']>=1 and r['grabs']==0 and r['lit'] is None and r['step'] and not r['busy'] and r['noBadStatus'] and all(c=='play' for c in r['cls']) and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
