"""v4.71: Tastenfarbe nur so lange wie gedrückt (+0,12 s); falscher Ton im Akkord: nur diese Taste rot, losgelassene Akkordtöne müssen neu gespielt werden, gehaltene zählen weiter"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};window.playTone=()=>{};window.__instantEnd=true;
 const notes=[{m:60,start:0,dur:.5,hand:'R'},{m:64,start:0,dur:.5,hand:'R'},{m:67,start:0,dur:.5,hand:'R'}];let t=1;for(let i=0;i<9;i++){notes.push({m:62+(i%3),start:t,dur:.3,hand:'R'});t+=.5}
 const it={id:'ht',type:'midi',title:'H',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 memStart(0,false);const R=MEM.run;R.vt=MEM.gs[R.a].start;
 const cols={};const orig=drawKeys;const grab=()=>{window.drawKeys=function(c,lo,hi,W,h,fn,l){for(const m of [60,64,65,67])cols[m]=fn(m,false);return orig(c,lo,hi,W,h,fn,l)};memDraw();window.drawKeys=orig;return {...cols}};
 const dn=m=>kbEvent(0x90,m-KB.shift,90),up=m=>kbEvent(0x80,m-KB.shift,0);
 dn(60);dn(64);o.c1=grab();dn(65);o.c2=grab();o.hitHeld=[...R.hit].sort();up(60);up(64);up(65);await w(200);o.c3=grab();
 // nach Fehler und Loslassen: Akkord muss komplett neu
 dn(60);dn(64);dn(65);up(60);up(64);up(65);o.hitAfter=[...R.hit];dn(67);o.posAfter67=R.pos-R.a;dn(60);dn(64);o.posAfterAll=R.pos-R.a;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r),errs)
        G='#3BB273';Rd='#E5484D'
        c={'grün beim Halten':r['c1']['60']==G and r['c1']['64']==G,'nur falsche rot':r['c2']['65']==Rd and r['c2']['60']==G and r['c2']['64']==G,
           'gehaltene zählen':r['hitHeld']==[60,64],'nach Loslassen aus':r['c3']['60']!=G and r['c3']['65']!=Rd,
           'losgelassen zählt nicht':r['hitAfter']==[] and r['posAfter67']==0,'ganzer Akkord → weiter':r['posAfterAll']==1,'keine Fehler':not errs}
        print(c);ok=all(c.values());print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
