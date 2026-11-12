"""v4.41: YouTube-Karte ueber den Tasten -> 'verdeckt' statt Fehler. Rot-vor-Fix: ohne Schutz meldet cmpLit viele Tasten."""
import sys,os,json,base64,io
from PIL import Image,ImageDraw
from playwright.async_api import async_playwright
import asyncio
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures')
meta=json.load(open(os.path.join(H,'embers_v434_meta.json')));keys=meta['keys'];rows=meta['scanRows']
geo={'x':[keys[0]['x'],keys[-1]['x']],'kw':meta['kw'],'yT':rows['yT'],'yA':rows['yA'],'yB':rows['yB'],'yC':rows['yC'],'sh':0,'kx':[round(k['x'],4) for k in keys],'ar':meta.get('ar',1280/544)}
lo=keys[0]['m']
def img(cover):
    im=Image.open(os.path.join(H,'embers_mid1_16x9.jpg')).convert('RGB')
    if cover:
        d=ImageDraw.Draw(im);w,h=im.size
        for i in range(40):d.rectangle([i*w/40,h*0.5,(i+0.5)*w/40,h],fill=(220,40+i*4,30))
    b=io.BytesIO();im.save(b,'JPEG');return base64.b64encode(b.getvalue()).decode()
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500)
        r=await pg.evaluate("""async([geo,lo,a,b])=>{const out={};
          const load=async s=>{const i=new Image();i.src='data:image/jpeg;base64,'+s;await i.decode();const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);return x.getImageData(0,0,c.width,c.height)};
          window.ytp={getCurrentTime:()=>5};NAT.ok=true;$('#ytBox').getBoundingClientRect=()=>({width:1280,height:720});
          for(const [k,s] of [['clean',a],['cover',b]]){const im=await load(s);window.grabVideo=async()=>im;
            CMP_MARKS=true;CMP={g:geo,lo,off:0,notes:[],gen:0};await cmpMeasure();out[k]={cover:!!CMP.cover,lit:CMP.lit?CMP.lit.size:null}}
          return out}""",[geo,lo,img(False),img(True)])
        print(json.dumps(r),errs)
        ok=(not r['clean']['cover'] and r['clean']['lit'] is not None and r['cover']['cover'] and r['cover']['lit'] is None and not errs)
        print('OK' if ok else 'FAIL');sys.exit(0 if ok else 1)
asyncio.run(main())
