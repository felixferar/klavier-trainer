"""v4.40: Messung der Fallgeschwindigkeit der Balken im Video (JS-Fassung) an echten Frames der Prüfstand-Videos: Abweichung zur wahren Geschwindigkeit; bei uneinigen Messungen kein Ergebnis.
usage: speedtest.py APP.html FRAMEDIR (FRAMEDIR/meta.json + N_{0,1}{a,b}.jpg, 1280x720)"""
import sys,asyncio,json,os,base64
from playwright.async_api import async_playwright
# Ohne FRAMEDIR: die Bilder im Repo (fixtures/spd1_*.jpg, wahre Geschwindigkeit 183 px/s bei 720 px Höhe wie in cmptest.py). Die Bilder der übrigen
# Prüfstand-Videos lagen nie im Repo; bis 27.11.2026 startete der Test deshalb gar nicht.
if len(sys.argv)>2: fd=sys.argv[2];meta=json.load(open(os.path.join(fd,'meta.json')))
else: fd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures');meta={'spd1':{'pps':183,'yT':[602]}}
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
        ok=ok and any(b is not None for a,b in out.values())   # mindestens eine echte Messung
        print('pageerrors',errs,'zu ungenau',bad,'ERGEBNIS','OK' if ok else 'FEHLER');await br.close();return 0 if ok else 1
sys.exit(asyncio.run(main()))
