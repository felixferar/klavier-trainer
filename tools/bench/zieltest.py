"""v4.71: Ziel und nächster Schritt sichtbar; Karte entscheidet (Sauber zählt, Zögern zählt mit); gehaltene Note bleibt markiert"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{window.MEM_V8=false;window.FLOW_FIND=false;FL.start=0.8; /* v4.92: Nebel-Logik ohne Kennenlern-Runde prüfen */ const o={};window.playTone=()=>{};window.__instantEnd=true;
 const notes=[];let t=0;for(let i=0;i<10;i++){notes.push({m:60+(i%5)*2,start:t,dur:.4,hand:'R'});t+=.5}
 const it={id:'zl',type:'midi',title:'Z',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 const play=(hes)=>{memStart(0,false);const R=MEM.run;let T=1000;performance.now=()=>T;while(!R.done){R.vt=Math.max(R.vt,MEM.gs[R.pos].start);T+=(hes&&(R.pos===R.a+3||R.pos===R.a+6))?3000:500;for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}return R};
 memStart(0,false);o.goal0=$('#memGoal').textContent;
 let R=play(false);o.msg1=$('#memMsg').textContent;o.next1=$('#memNext').textContent;o.goal1=$('#memGoal').innerHTML.split('class="on"').length-1;
 R=play(true);o.cat2=R.ev.cat;o.lvlAfterHes=MEM.rec.secs[0].lvl;o.msg2=$('#memMsg').textContent;o.again2=getComputedStyle($('#memAgain')).display;
 play(false);play(false);R=play(false);o.lvlUp=MEM.rec.secs[0].lvl;o.msg3=$('#memMsg').textContent;o.next3=$('#memNext').textContent;
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
        c={'Ziel sichtbar (v4.81: Schritt 1 Kennenlernen)':'Schritt 1 von 3' in r['goal0'] and 'Kennenlernen' in r['goal0'],
           'nach 1 Durchgang kennengelernt':r['msg1'].startswith('Kennengelernt') and r['next1']=='Weiter: Verblassen',
           'Zögern: nicht sauber, aber „Fast“ bringt weiter':r['cat2']=='f' and r['lvlAfterHes']==2 and 'mehr Noten' in r['msg2'],
           'danach Aus dem Kopf':r['lvlUp']==3 and 'aus dem Kopf' in r['msg3'],
           'gehalten grün':'#3bb273' in [x.lower() for x in r['heldStroke']] and '#ffffff' not in [x.lower() for x in r['heldStroke']],
           'losgelassen weiß':'#ffffff' in [x.lower() for x in r['relStroke']],'keine Fehler':not errs}
        print(c);ok=all(c.values());print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
