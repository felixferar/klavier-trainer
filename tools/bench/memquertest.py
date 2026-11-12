"""v4.68: Auswendig quer (753×360 wie das Handy des Nutzers): Notenbahn, Klaviatur, Rückmeldung und Knöpfe ohne Scrollen sichtbar; Noten fließen im Takt und warten am nächsten Ton"""
import sys,asyncio,json
from playwright.async_api import async_playwright
SETUP=r"""()=>{window.__mp||(window.__mp=memPress,memPress=function(m,src){const R=MEM.run;if(R&&!R.watch&&R.vt!=null&&R.lvl<=2&&!window.__strict)R.vt=Math.max(R.vt,MEM.gs[R.pos].start);return window.__mp(m,src)}); /* Test: wie Warten, bis der Balken unten ist */const notes=[];let t=0;for(let i=0;i<20;i++){notes.push({m:64+[0,2,4,5,7][i%5],start:t,dur:i%3===0?0.9:0.3,hand:'R'});if(i%4===0)notes.push({m:48+(i%3)*2,start:t,dur:1.4,hand:'L'});t+=i%3===0?0.9:0.3}
 const it={id:'q1',type:'midi',title:'Q',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];window.playTone=()=>{};
 openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});memStart(0,false);return {vt0:MEM.run.vt,g0:MEM.gs[0].start}}"""
FLOW=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));const R=MEM.run,o={};o.a=R.vt;await w(400);o.b=R.vt;await w(1500);o.c=R.vt;o.target=MEM.gs[R.pos].start;
 for(const m of MEM.gs[R.pos].mids)memPress(m,'kb');o.pos=R.pos;await w(150);o.d=R.vt;o.next=MEM.gs[R.pos].start;return o}"""
FIN=r"""()=>{const R=MEM.run;while(!R.done){for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}const vis=id=>{const e=$(id);if(!e)return null;const r=e.getBoundingClientRect();return {top:Math.round(r.top),bottom:Math.round(r.bottom),h:Math.round(r.height),w:Math.round(r.width)}};
 return {cv:vis('#memCv'),next:vis('#memNext'),ev:vis('#memEv'),msg:vis('#memMsg'),topbar:getComputedStyle($('#mem .topbar')).display,H:innerHeight,scroll:$('#mem .scroll').scrollHeight-$('#mem .scroll').clientHeight}}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        s=await pg.evaluate(SETUP);f=await pg.evaluate(FLOW);await pg.screenshot(path='/tmp/quer_run.png')
        r=await pg.evaluate(FIN);await pg.wait_for_timeout(200);await pg.screenshot(path='/tmp/quer_done.png')
        print(json.dumps({'setup':s,'flow':f,'fin':r}),errs)
        c={'Vorlauf':s['vt0']<s['g0'],
           'fliesst':f['b']>f['a']+0.2,
           'wartet am Ton':abs(f['c']-f['target'])<1e-6,
           'weiter nach Spielen':f['d']>f['c'] and f['d']<=f['next']+1e-6,
           'Kopfzeile weg':r['fin']['topbar']=='none' if 'fin' in r else r['topbar']=='none',
           'Weiter sichtbar':r['next']['h']>0 and r['next']['bottom']<=r['H'],
           'Rueckmeldung sichtbar':r['ev']['h']>0 and r['ev']['bottom']<=r['H'],
           'Notenbahn hoch':r['cv']['h']>=r['H']-20,
           'kein Scrollen':r['scroll']<=1,
           'keine Fehler':not errs}
        print(c);ok=all(c.values());print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
