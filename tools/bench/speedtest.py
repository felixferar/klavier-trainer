"""v4.40: Messung der Fallgeschwindigkeit der Balken im Video (JS-Fassung) an echten Frames der Prüfstand-Videos: Abweichung zur wahren Geschwindigkeit; bei uneinigen Messungen kein Ergebnis.
usage: speedtest.py APP.html FRAMEDIR (FRAMEDIR/meta.json + N_{0,1}{a,b}.jpg, 1280x720)"""
import sys,asyncio,json,os,base64
from playwright.async_api import async_playwright
fd=sys.argv[2];meta=json.load(open(os.path.join(fd,'meta.json')))
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500)
        out={};bad=[]
        for n,m in meta.items():
            imgs={k:base64.b64encode(open(os.path.join(fd,f'{n}_{k}.jpg'),'rb').read()).decode() for k in ['0a','0b','1a','1b']}
            r=await pg.evaluate("""async([imgs,yT])=>{const load=b=>new Promise(res=>{const i=new Image();i.onload=()=>{const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);res(x.getImageData(0,0,c.width,c.height))};i.src='data:image/jpeg;base64,'+b});
              const A0=await load(imgs['0a']),B0=await load(imgs['0b']),A1=await load(imgs['1a']),B1=await load(imgs['1b']);
              const g={ar:16/9,yT:yT[0]/720};return cmpSpeedFrom([{a:A0,b:B0,dt:0.4},{a:A1,b:B1,dt:0.4}],g,1280,720)}""",[imgs,m['yT']])
            v=None if r is None else round(r*720)
            out[n]=(m['pps'],v)
            if v is not None and abs(v/m['pps']-1)>0.03:bad.append(n)
            print(n,'wahr',m['pps'],'gemessen',v,flush=True)
        ok=not bad and not errs and sum(1 for a,b in out.values() if b is None)<=1
        print('pageerrors',errs,'zu ungenau',bad,'ERGEBNIS','OK' if ok else 'FEHLER');await br.close()
asyncio.run(main())
