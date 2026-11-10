"""v4.28: pickKb lehnt schlechte Tastaturpassung ab (res > 0.16): Intro-Grafik von rYglC8WAm5g (res 0.172) wird NICHT als Tastatur genommen, echte Tastatur (mid still, res ~0.11) schon."""
import sys,asyncio,json,base64
from playwright.async_api import async_playwright
async def main():
    app,intro,real=sys.argv[1:4]
    b=lambda f:base64.b64encode(open(f,'rb').read()).decode()
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+app);await pg.wait_for_timeout(500)
        r=await pg.evaluate("""async(bs)=>{const o={};const get=async b=>{const im=new Image();im.src='data:image/jpeg;base64,'+b;await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const x=c.getContext('2d');x.drawImage(im,0,0);return x.getImageData(0,0,c.width,c.height)};
          for(const [k,b] of Object.entries(bs)){const img=await get(b);const t=tryKeyboard(img);const pk=pickKb([t]);o[k]={tryKeyboard:t?{res:+t.det.res.toFixed(3),nb:t.det.nb,w:+t.det.w.toFixed(1)}:null,pickKb:!!pk}}return o}""",{'intro':b(intro),'real':b(real)})
        print(json.dumps(r));print('pageerrors',errs);await br.close()
asyncio.run(main())
