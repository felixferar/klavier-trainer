"""v4.34: zwei gestapelte Tastaturen (virtuell mit Balken oben + gefilmte echte mit Händen darunter, gleiche Tastenpositionen):
die OBERE wird gewählt. usage: python3 stacktest.py APP.html  (Fixtures: Embers-Standbild mit Pausen-Overlay und freies Bild)"""
import sys,asyncio,json,base64,os
from playwright.async_api import async_playwright
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures')
JS="""async(b)=>{const im=new Image();im.src='data:image/jpeg;base64,'+b;await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;c.getContext('2d').drawImage(im,0,0);return findKeyboardRows(c.getContext('2d').getImageData(0,0,c.width,c.height))}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);ok=True
        for f in ('embers_still.jpg','embers_mid.jpg'):
            r=await pg.evaluate(JS,base64.b64encode(open(os.path.join(H,f),'rb').read()).decode())
            good=bool(r) and r['yA']<0.6 and r['yB']<0.7;ok&=good  # virtuelle Tastatur: Pixelzeile ~290 von 544 (yA≈0.53), nicht die echte (~397, yA≈0.73)
            print(f,json.dumps(r),'OK' if good else 'FALSCH')
        print('pageerrors',errs,'ERGEBNIS','OK' if ok and not errs else 'FEHLER');await br.close()
asyncio.run(main())
