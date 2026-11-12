"""v4.48: Fallgeschwindigkeit aus den Noten (echte Embers-Fotos vom Handy + ein synthetisches Bild mit bekannter Geschwindigkeit)"""
import sys,os,json,base64,io,asyncio
from PIL import Image,ImageDraw
from playwright.async_api import async_playwright
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures','shots')
def b64(p):return base64.b64encode(open(p,'rb').read()).decode()
shots=[]
for ts in ('2026-11-12T12-30-19','2026-11-12T12-30-25','2026-11-12T12-30-37'):
    j=json.load(open(f'{H}/{ts}.json'));shots.append({'img':b64(f'{H}/{ts}.jpg'),'T':j['cmp']['litT']})
geo=json.load(open(f'{H}/2026-11-12T12-30-37.json'))['cmp']['geo'];lo=24
notes=[{'midi':n[0],'start':n[1],'dur':n[2],'hand':'R'} for n in json.load(open(f'{H}/embers-notes.json'))]
# synthetisch: 640x360, Tasten ab yT, Balken faellt mit 0.2 Boxhoehen/s, Noten 0.8 s lang
def synth(v,T,notes_s):
    W,Hh=640,360;im=Image.new('RGB',(W,Hh),(20,20,20));d=ImageDraw.Draw(im);yT=geo['yT']*Hh
    d.rectangle([0,yT,W,Hh],fill=(230,230,230))
    ar=geo['ar'];cw=min(ar,16/9)
    X=lambda f:((f*ar-(ar-cw)/2)/cw)*W
    for n in notes_s:
        if n['start']<=T<n['start']+n['dur']+3:
            x=X(geo['kx'][n['midi']-lo]);bot=yT-(n['start']-T)*v*Hh;top=yT-(n['start']+n['dur']-T)*v*Hh
            d.rectangle([x-4,max(0,top),x+4,min(yT-1,bot)],fill=(200,40,40))
    b=io.BytesIO();im.save(b,'PNG');return base64.b64encode(b.getvalue()).decode()
sn=[{'midi':24+30+i*2,'start':1.0,'dur':0.8,'hand':'R'} for i in range(7)]
syn=[{'img':synth(0.2,1.2,sn),'T':1.2},{'img':synth(0.2,1.3,sn),'T':1.3}]
JS="""async([shots,geo,lo,notes,syn,sn])=>{const ld=b=>new Promise(res=>{const i=new Image();i.onload=()=>{const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);res({im:x.getImageData(0,0,c.width,c.height),w:i.width,h:i.height})};i.src=(b.startsWith('iVBOR')?'data:image/png;base64,':'data:image/jpeg;base64,')+b});
  const o={};const fr=[];for(const s of shots){const l=await ld(s.img);fr.push({im:l.im,T:s.T,w:l.w,h:l.h})}
  // jedes Foto hat seine eigene Boxgroesse: pro Foto einzeln auswerten und gemeinsam
  o.each=fr.map(f=>cmpSpeedNotes([f],notes,lo,geo,f.w,f.h));
  const same=fr.filter(f=>f.w===612);o.joint=cmpSpeedNotes(same.concat(same),notes,lo,geo,612,344);
  const sf=[];for(const s of syn){const l=await ld(s.img);sf.push({im:l.im,T:s.T})}
  o.synth=cmpSpeedNotes(sf,sn,lo,geo,640,360);
  // zu wenig Noten -> keine Antwort
  o.few=cmpSpeedNotes([sf[0]],sn.slice(0,1),lo,geo,640,360);
  // leeres Bild (nichts sichtbar) -> keine Antwort
  const blank=new ImageData(640,360);for(let i=0;i<blank.data.length;i+=4){blank.data[i]=blank.data[i+1]=blank.data[i+2]=30;blank.data[i+3]=255}
  o.blank=cmpSpeedNotes([{im:blank,T:1.2},{im:blank,T:1.3}],sn,lo,geo,640,360);
  return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(1500)
        r=await pg.evaluate(JS,[shots,geo,lo,notes,syn,sn]);print(json.dumps(r),errs)
        ok=(r['synth'] is not None and abs(r['synth']/0.2-1)<0.05 and r['few'] is None and r['blank'] is None and r['joint'] is not None and 0.12<=r['joint']<=0.18 and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
