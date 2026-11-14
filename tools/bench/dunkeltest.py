"""v4.95: Im dunklen Modus sieht man, dass Töne zählen (Punkte + „x von y Anschlägen“, ohne Tasten zu verraten); hängt man nach der Ohr-Hilfe weiter,
zeigt die App den Anschlag kurz (zählt als Hilfe) – nie endlos schwarz; Lernstand des Songs lässt sich mit zweimal Tippen zurücksetzen."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};KB.state='off';
 const SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,72];const notes=[];let t=0;for(let r=0;r<2;r++)for(let bar=0;bar<4;bar++){notes.push({m:47,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:SA[bar*4+q],start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 const it={id:'dk',type:'midi',title:'Dunkel',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);memHome();const gs=MEM.gs;MEM.rec.v8.ch[0].st=1;memHome();
 $('#memGo').click();let R=MEM.run;R.anchorUntil=0;flowTick(R,5);flowDraw();o.prog0=$('#memProg').textContent;
 for(const m of gs[R.pos].mids)memPress(m,'kb');flowTick(R,5);flowDraw();o.prog1=$('#memProg').textContent;o.dark1=$('#memMsg').textContent;
 /* hängen: erst Ohr-Hilfe, dann Anschlag zeigen */
 R.waitT0=performance.now()-2500;flowTick(R,0);o.h1=R.hints;flowDraw();o.msgEar=$('#memMsg').textContent;
 R.hintAt=performance.now()-3500;flowTick(R,0);o.h2=R.hints;o.show=R.showUntil>performance.now();flowDraw();o.msgShow=$('#memMsg').textContent;o.pre=[...R.pre].sort().join()==[...gs[R.pos].mids].sort().join();
 R.hintAt=performance.now()-3500;flowTick(R,0);o.h3=R.hints;
 memStop();memHome();
 /* zurücksetzen */
 const v=MEM.rec.v8;v.ch[0].box=3;v.ch[1].box=1;MEM.rec.fl.st[2]=3;MEM.rec.fl.seen[3]=1;memHome();const b=$('#v8Reset');o.hasBtn=!!b;b.click();o.ask=$('#v8Reset').textContent;o.still=MEM.rec.v8.ch[0].box===3;$('#v8Reset').click();
 o.reset=MEM.rec.v8.ch.every(c=>c.box===0&&c.st===0)&&MEM.rec.fl.st.every(x=>x===0)&&MEM.rec.fl.seen.every(x=>x===0);o.go=$('#memGo').textContent;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'v4.98: kein Fortschritt im Dunkeln (Blick bleibt am Klavier)':r['prog0']=='' and r['prog1']=='' and 'Augen aufs Klavier' in r['dark1'],
           'erst Ohr-Hilfe':r['h1']==1,
           'weiter hängen → Anschlag kurz zeigen (zählt als Hilfe)':r['h2']==2 and r['show'] and 'zählt als Hilfe' in r['msgShow'] and r['pre'],
           'nie endlos schwarz: Hilfe wiederholt sich':r['h3']==3,
           'Zurücksetzen erst nach zweitem Tippen':r['hasBtn'] and 'Nochmal tippen' in r['ask'] and r['still'],
           'danach alles von vorn':r['reset'] and 'finden' in r['go'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
