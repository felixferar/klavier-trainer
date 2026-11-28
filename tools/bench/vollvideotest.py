"""v5.81 Vergleich zeigt das ganze Video: Start bei 0:00 (nicht beim Lesestart), Zeitleiste von Video 0:00 bis Videoende, Bereich vor dem Lesestart grau,
Zurück vor der ersten Note springt an den Videoanfang."""
import sys,asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""async()=>{const o={};const lo=48,n=36;const kx=[];for(let i=0;i<n;i++)kx.push(0.05+i*0.9/n);
          const geo={x:[kx[0],kx[n-1]],kw:0.02,yT:0.2,yA:0.3,yB:0.6,yC:0.7,sh:0,kx,ar:2.35};
          const notes=[];for(let i=0;i<40;i++)notes.push({m:60+i%12,start:1+i*0.5,dur:0.4,hand:'R'});
          /* Lesen begann bei Video 12 s (Tastatur erst da gefunden), erste Note bei 14 s, Video 60 s lang */
          const it={id:'t1',type:'midi',title:'T',data:b64FromBuf(writeMidi(notes)),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:12,first:14,keys:[lo,lo+n-1],geo}};LIB=[it];
          let opened=null;window.openYT=(it,a,c)=>{opened=it;cmpMode(!!CMP);show('yt')};let vt=0,seek=null;
          ytp={getCurrentTime:()=>vt,getDuration:()=>60,pauseVideo(){},seekTo(t){seek=t;vt=t},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2};
          openCompare(it);o.start=opened&&opened.start;o.off=CMP.off;
          const R=tlRange();o.a=R.a;o.b=R.b;o.r=R.r;
          vt=0;tlDraw();o.t0=$('#tlT').textContent;
          const tr=$('#tlTrack'),bx=tr.getBoundingClientRect(),ev=(t,x)=>new PointerEvent(t,{clientX:x,clientY:bx.top+5,pointerId:1,bubbles:true});tr.setPointerCapture=()=>{};
          tr.dispatchEvent(ev('pointerdown',bx.left+1));tr.dispatchEvent(ev('pointerup',bx.left+1));o.seekLeft=seek;
          tr.dispatchEvent(ev('pointerdown',bx.right-1));tr.dispatchEvent(ev('pointerup',bx.right-1));o.seekRight=seek;
          await new Promise(z=>setTimeout(z,300));
          vt=13.5;seek=null;$('#cmpPrevN').click();await new Promise(z=>setTimeout(z,300));o.prev=seek;
          vt=0;$('#cmpNextN').click();await new Promise(z=>setTimeout(z,300));o.next=seek;
          return o}""")
        print(r,errs)
        ok=(r['start']==0 and abs(r['off']-13)<1e-6 and abs(r['a']+13)<1e-6 and abs(r['b']-47)<1e-6 and abs(r['r']+1)<1e-6
            and r['t0']=='0:00,0' and r['seekLeft']<0.5 and abs(r['seekRight']-60)<0.5 and r['prev']==0 and abs(r['next']-14)<0.05 and not errs)
        print('OK' if ok else 'FAIL');sys.exit(0 if ok else 1)
asyncio.run(main())
