"""v4.36 Vergleichsansicht: (1) Abbildung Bruchteile→Pixel (gleiche Fläche = Identität, 16:9-Fläche = Videorand), (2) Overlay-Rechtecke sitzen auf den im Embers-Bild roten Tasten (Pixelmitten 572/636/785 bei 1280 px, direkt im Bild gemessen),
(3) Songmenü-Knopf nur für Songs aus Video, Song ohne Geometrie -> Hinweis statt Ansicht, (4) Ansicht mit Stub-Player: Text + Rechteck zur richtigen Zeit, Zurück räumt auf."""
import sys,asyncio,json,os,base64
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures')
meta=json.load(open(os.path.join(H,'embers_v434_meta.json')))
keys=meta['keys'];lo=keys[0]['m'];hi=keys[-1]['m'];rows=meta['scanRows']
geo={'x':[keys[0]['x'],keys[-1]['x']],'kw':meta['kw'],'yT':rows['yT'],'yA':rows['yA'],'yB':rows['yB'],'yC':rows['yC'],'sh':0,'kx':[round(k['x'],4) for k in keys],'ar':round(753/320,4)}
# direkt im Bild gemessene rote Tastenmitten (Zeile 320 von 544) – unabhängig vom App-Raster
im=np.array(Image.open(os.path.join(H,'embers_mid1.jpg')).convert('RGB')).astype(int)
row=im[320];red=(row[:,0]>190)&(row[:,1]<110)&(row[:,2]<100);xs=np.where(red)[0];g=[]
for x in xs:
    if g and x-g[-1][-1]<=2:g[-1].append(x)
    else:g.append([x])
measured=[int(np.mean(q)) for q in g if len(q)>=4]
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""async([geo,lo,measured])=>{const o={};
          let P=cmpPx(geo,1280,544);o.ident=[0,0.25,0.5,1].map(f=>Math.round(P.X(f)-f*1280)); // gleiche Flaeche: Abbildung = Identitaet
          P=cmpPx(geo,800,450);const ar=geo.ar,cw=Math.min(ar,16/9),leftF=(ar-cw)/2/ar,rightF=1-leftF;o.rand=[Math.round(P.X(leftF)),Math.round(P.X(rightF))]; // 16:9-Flaeche: Videorand 0..800
          P=cmpPx(geo,1280,544);o.sitz=measured.map(px=>{let best=null;for(let m=lo;m<lo+geo.kx.length;m++){const x=P.X(geo.kx[m-lo]);if(best==null||Math.abs(x-px)<Math.abs(best.x-px))best={m,x}}return [px,best.m,Math.round(best.x)]});
          o.kw=Math.round(P.kw*10)/10;
          // Songmenue + Hinweis
          const mk=(id,fromYT,withGeo)=>({id,type:'midi',title:'T'+id,data:b64FromBuf(writeMidi([{m:60,start:1,dur:2,hand:'R'},{m:64,start:5,dur:1,hand:'R'},{m:72,start:9,dur:2,hand:'R'}])),fromYT,video:{v:2,src:'yt',start:0,first:3,keys:[lo,lo+geo.kx.length-1],geo:withGeo?geo:undefined}});
          const a=mk('a','abcdefghijk',true),b=mk('b','abcdefghijk',false),c=mk('c',null,false);LIB=[a,b,c];
          openSongMenu(c);o.menuOhneYT=$('#smCmp').classList.contains('hidden');openSongMenu(a);o.menuYT=$('#smCmp').classList.contains('hidden');
          openSongMenu(b);openCompare(b);o.ohneGeoCMP=CMP===null;o.ohneGeoToast=!!document.querySelector('.toast');closeSheets();
          // Ansicht mit Stub-Player
          let call=null;window.openYT=(it,auto,cmp)=>{call=[it.videoId,auto,cmp,it.start];$('#yScan').classList.toggle('hidden',!!CMP);$('#cmpBar').classList.toggle('hidden',!CMP);$('#cmpCv').classList.toggle('hidden',!CMP);show('yt')};
          let vt=0,paused=false,seek=null;ytp={getCurrentTime:()=>vt,pauseVideo(){paused=true},seekTo(t){seek=t;vt=t}};
          openCompare(a);o.cmp=!!CMP;o.call=call;o.off=CMP&&CMP.off;
          vt=1+2+0.5; // Notenzeit 1.5 -> Note 60 klingt (1..3)
          await new Promise(z=>setTimeout(z,300));cmpDraw();o.txt=$('#cmpTxt').textContent;
          const cv=$('#cmpCv'),ctx=cv.getContext('2d'),d=cv.getBoundingClientRect(),dpr=window.devicePixelRatio||1,Pp=cmpPx(geo,d.width,d.height),x60=Pp.X(geo.kx[60-lo]),yMid=(Pp.Y(geo.yT)+Pp.Y(geo.yB))/2;
          o.pixel60=ctx.getImageData(Math.round(x60*dpr),Math.round(yMid*dpr),1,1).data[3]>0;
          o.pixelDanebenLeer=ctx.getImageData(Math.round((x60+Pp.kw*3)*dpr),Math.round(yMid*dpr),1,1).data[3]===0;
          vt=2+4.5;cmpDraw();o.txtStille=$('#cmpTxt').textContent; // Notenzeit 4.5: nichts klingt
          $('#cmpNextN').click();o.nextSeek=seek;  // naechste Note nach 4.5 beginnt bei 5 -> Videozeit 5+2=7
          $('#yBack').click();o.nachZurueck={cmp:CMP===null,bar:$('#cmpBar').classList.contains('hidden'),cv:$('#cmpCv').classList.contains('hidden'),scan:$('#yScan').classList.contains('hidden')};
          return o}""",[geo,lo,measured])
        print(json.dumps(r,ensure_ascii=False,indent=1));print('gemessen',measured)
        kwpx=r['kw']
        ok=(all(abs(v)<=1 for v in r['ident']) and abs(r['rand'][0])<=1 and abs(r['rand'][1]-800)<=1
            and all(abs(a-b)<=kwpx/2 for a,b,c in [(x[0],x[2],0) for x in r['sitz']]) and len(r['sitz'])>=3
            and r['menuOhneYT'] and not r['menuYT'] and r['ohneGeoCMP'] and r['ohneGeoToast']
            and r['cmp'] and r['call'][2] is True and r['call'][1] is False and r['off']==2
            and r['txt'].startswith('App: ') and 'C4' in r['txt'] and r['pixel60'] and r['pixelDanebenLeer']
            and r['txtStille'].startswith('App: –') and abs(r['nextSeek']-7)<0.01
            and r['nachZurueck']['cmp'] and r['nachZurueck']['bar'] and r['nachZurueck']['cv'] and not r['nachZurueck']['scan'])
        print('pageerrors',errs,'ERGEBNIS','OK' if ok and not errs else 'FEHLER');await br.close()
asyncio.run(main())
