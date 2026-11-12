"""v4.71: Ziel und nächster Schritt sichtbar; Karte entscheidet (Sauber zählt, Zögern zählt mit); gehaltene Note bleibt markiert"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};window.__instantEnd=true;
 const notes=[];let t=0;for(let i=0;i<10;i++){notes.push({m:60+(i%5)*2,start:t,dur:.4,hand:'R'});t+=.5}
 const it={id:'zl',type:'midi',title:'Z',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 const play=(hes)=>{memStart(0,false);const R=MEM.run;let T=1000;performance.now=()=>T;while(!R.done){R.vt=Math.max(R.vt,MEM.gs[R.pos].start);T+=(hes&&(R.pos===R.a+3||R.pos===R.a+6))?3000:500;for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}return R};
 memStart(0,false);o.goal0=$('#memGoal').textContent;
 let R=play(false);o.msg1=$('#memMsg').textContent;o.next1=$('#memNext').textContent;o.goal1=$('#memGoal').innerHTML.split('class="on"').length-1;
 R=play(true);o.cat2=R.ev.cat;o.lvlAfterHes=MEM.rec.secs[0].lvl;o.msg2=$('#memMsg').textContent;o.again2=getComputedStyle($('#memAgain')).display;
 play(false);R=play(false);o.lvlUp=MEM.rec.secs[0].lvl;o.msg3=$('#memMsg').textContent;o.next3=$('#memNext').textContent;
 // gehaltene Note
 performance.now=()=>Date.now();MEM.rec.secs[0].lvl=1;memStart(0,false);R=MEM.run;R.vt=MEM.gs[R.a].start;const m0=[...MEM.gs[R.a].mids][0];KB.held.add(m0);memPress(m0,'kb');
 const strokes=[];const proto=CanvasRenderingContext2D.prototype,sr=proto.strokeRect;proto.strokeRect=function(...a){strokes.push(this.strokeStyle);return sr.apply(this,a)};memDraw();o.heldStroke=strokes.slice();
 KB.held.delete(m0);strokes.length=0;memDraw();o.relStroke=strokes.slice();proto.strokeRect=sr;return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'Sicherheit sichtbar':'Sicherheit Stufe 1: 60 %' in r['goal0'] and 'Stufe 2' in r['goal0'] and 'noch ca. 2' in r['goal0'],
           'nach 1× sauber steigt':'76 %' in r['msg1'] and r['next1']=='Nächster Durchgang',
           'Zögern: nicht sauber, kein Aufstieg':r['cat2']!='s' and r['lvlAfterHes']==1 and r['again2']=='none',
           'Stufe 2 nach genug Sicherheit':r['lvlUp']==2,
           'gehalten grün':'#3bb273' in [x.lower() for x in r['heldStroke']] and '#ffffff' not in [x.lower() for x in r['heldStroke']],
           'losgelassen weiß':'#ffffff' in [x.lower() for x in r['relStroke']],'keine Fehler':not errs}
        print(c);ok=all(c.values());print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
