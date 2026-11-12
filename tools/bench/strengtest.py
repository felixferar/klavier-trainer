"""v4.69: Stufe 1/2 streng im Rhythmus: zu früh gedrückt zählt nicht und wird gezählt; die Songuhr springt nicht vor; keine Tasten-Hilfe in Stufe 1; Hilfe in Stufe 2 erst nach Warten an der Linie"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};window.playTone=()=>{};
 const notes=[];let t=0;for(let i=0;i<20;i++){notes.push({m:60+(i%5)*2,start:t,dur:0.4,hand:'R'});t+=0.6}
 const it={id:'st',type:'midi',title:'St',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 memStart(0,false);let R=MEM.run;const g0=[...MEM.gs[R.a].mids][0];
 memPress(g0,'kb');o.earlyRejected=R.pos===R.a&&memG(R,R.a).early===1&&R.errors===0;o.msg=$('#memMsg').textContent;
 o.hintLvl1=memHintOn();
 // warten bis der Balken unten ist, dann spielen
 await w(1400);o.arrived=R.vt>=MEM.gs[R.a].start-1e-6;memPress(g0,'kb');o.accepted=R.pos===R.a+1;
 // nächster Ton 0,1 s vor Ankunft (innerhalb Fenster) → angenommen, Uhr springt NICHT
 while(MEM.gs[R.pos].start-R.vt>0.1)await w(16);const vtBefore=R.vt;memPress([...MEM.gs[R.pos].mids][0],'kb');o.inWindow=R.pos===R.a+2;o.noJump=R.vt-vtBefore<0.05;
 // Stufe 2: Hilfe erst 2,5 s nach Ankunft
 memStop();MEM.rec.secs[0].lvl=2;memStart(0,false);R=MEM.run;o.hint2early=memHintOn();await w(1400);const at=R.arrAt;o.arr2=at!=null;R.arrAt=memNow()-3000;o.hint2late=memHintOn();
 // Auswertung zählt "zu früh"
 memStop();MEM.rec.secs[0].lvl=1;memStart(0,false);R=MEM.run;memPress(g0,'kb');R.vt=MEM.gs[R.pos].start;while(!R.done){R.vt=Math.max(R.vt,MEM.gs[R.pos].start);for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}
 o.evEarly=R.ev.early;o.evText=R.ev.text;
 // Beschriftung: schwarze Tasten und Balken (Text wird gezeichnet)
 let txt=[];const cx=$('#memCv').getContext('2d'),ft=cx.fillText.bind(cx);CanvasRenderingContext2D.prototype._ft=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(s,...a){txt.push(s);return this._ft(s,...a)};
 memStop();memStart(0,false);R=MEM.run;R.vt=MEM.gs[R.a].start;memDraw();o.labels=[...new Set(txt)].slice(0,30);o.blackLab=txt.includes('Cis')||txt.includes('Dis');o.barLab=txt.filter(x=>x==='C').length>=2;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={k:r[k] for k in ['earlyRejected','arrived','accepted','inWindow','noJump','arr2','hint2late','blackLab','barLab']}
        c['keine Hilfe Stufe1']=not r['hintLvl1'];c['keine Hilfe vor Ankunft']=not r['hint2early'];c['zu früh gezählt']=r['evEarly']==1 and 'früh' in r['evText'];c['Hinweis']='früh' in r['msg'];c['keine Fehler']=not errs
        print(c);ok=all(c.values());print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
