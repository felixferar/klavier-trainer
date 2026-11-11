"""v4.46 Doppelbild: Video und Noten gleich gross, gleiche Spalten (gleiche x-Lage), hoch: untereinander + Leiste unten, quer: links untereinander + Leiste rechts, alles im Bild"""
import sys,asyncio,json
sys.argv.append('')
from playwright.async_api import async_playwright
exec(open('/tmp/dshot.py').read().split("async def main")[0].replace("import sys,asyncio,json,os",""))
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']);res={}
        for name,vp in (('hoch',{'width':400,'height':780}),('quer',{'width':800,'height':360}),('klein',{'width':360,'height':640})):
            pg=await br.new_page(viewport=vp);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500)
            await pg.evaluate(JS,[geo,lo]);await pg.wait_for_timeout(300)
            res[name]=await pg.evaluate("""([W,H])=>{const r=s=>{const b=$(s).getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height,r:b.right,b:b.bottom}};const v=r('#ytBox'),c=r('#cmpScene'),bar=r('#cmpBar');
              return {same:Math.abs(v.w-c.w)<1&&Math.abs(v.h-c.h)<1&&Math.abs(v.x-c.x)<1,ratio:Math.round(v.w/v.h*100)/100,stacked:c.y>=v.b-1,inside:v.r<=W+1&&c.b<=H+1&&bar.b<=H+1&&bar.r<=W+1,barSide:bar.x>=v.r-1,barBelow:bar.y>=c.b-1,vw:Math.round(v.w),vh:Math.round(v.h),textHidden:getComputedStyle($('#cmpTxt')).display==='none'}}""",[vp['width'],vp['height']]);res[name]['err']=errs
        print(json.dumps(res));h,q,k=res['hoch'],res['quer'],res['klein']
        ok=all(x['same'] and abs(x['ratio']-1.78)<0.02 and x['stacked'] and x['inside'] and x['textHidden'] and not x['err'] for x in (h,q,k)) and h['barBelow'] and k['barBelow'] and q['barSide'] and q['vw']>=300
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
