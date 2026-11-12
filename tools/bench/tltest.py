"""v4.64 Zeitleiste im Vergleichsmodus: sichtbar, Song-/Videozeit, Tippen springt, Markieren/Entfernen, Flags im Shot-Info."""
import sys,asyncio,json,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""async()=>{const o={};const lo=48,n=36;const kx=[];for(let i=0;i<n;i++)kx.push(0.05+i*0.9/n);
          const geo={x:[kx[0],kx[n-1]],kw:0.02,yT:0.2,yA:0.3,yB:0.6,yC:0.7,sh:0,kx,ar:2.35};
          const notes=[];for(let i=0;i<40;i++)notes.push({m:60+i%12,start:1+i*0.5,dur:0.4,hand:'R'});
          const it={id:'t1',type:'midi',title:'T',data:b64FromBuf(writeMidi(notes)),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:0,first:3,keys:[lo,lo+n-1],geo}};LIB=[it];
          window.openYT=(it,a,c)=>{cmpMode(!!CMP);show('yt')};let vt=0,seek=null;ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(t){seek=t;vt=t},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2};
          CMP_MARKS=true;openCompare(it);o.cmp=!!CMP;o.off=CMP&&CMP.off;
          vt=10+CMP.off;await new Promise(z=>setTimeout(z,300));tlDraw();
          o.vis=$('#tlTrack').getBoundingClientRect().height>20;o.t=$('#tlT').textContent;o.v=$('#tlV').textContent;
          const r=$('#tlTrack').getBoundingClientRect(),ev=(t,x)=>new PointerEvent(t,{clientX:x,clientY:r.top+5,pointerId:1,bubbles:true});
          const tr=$('#tlTrack');tr.setPointerCapture=()=>{};tr.dispatchEvent(ev('pointerdown',r.left+r.width/2));tr.dispatchEvent(ev('pointerup',r.left+r.width/2));
          o.seek=seek;o.expect=tlDur()/2+CMP.off;
          $('#tlFlag').click();o.f1=tlFlags().length;vt=seek;tlDraw();$('#tlFlag').click();o.f2=tlFlags().length;
          vt=3+CMP.off;$('#tlFlag').click();o.f3=tlFlags().length;
          return o}""")
        print(r,errs)
        ok=r['cmp'] and r['vis'] and r['t']=='0:10,0' and 'Video' in r['v'] and abs(r['seek']-r['expect'])<0.5 and r['f1']==1 and r['f2']==0 and r['f3']==1 and not errs
        print('OK' if ok else 'FAIL');sys.exit(0 if ok else 1)
asyncio.run(main())
