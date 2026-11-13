"""v4.79, ab v4.81 in Schritt 2 „Verblassen“ (Etappen 100/60/30 %, Schritt 3 ohne Noten): Stufe 3 – Noten verblassen nach und nach: je höher die Sicherheit, desto weniger Noten sind sichtbar.
Sicherheit 60 % (Start von Stufe 3) → etwa die Hälfte der Anschläge sichtbar; 85 % → keine; darunter mehr.
Immer dieselben Noten verschwinden zuerst (wer bei 70 % sichtbar ist, war es auch bei 60 %); der erste Anschlag bleibt am längsten.
Die Bahn zeigt in Stufe 3 wirklich Balken (Pixel), bei 85 % keine."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};window.playTone=()=>{};window.__instantEnd=true;
 const notes=[];let t=0;for(let i=0;i<16;i++){notes.push({m:60+(i%7),start:t,dur:0.4,hand:'R'});t+=0.5}
 const it={id:'vb',type:'midi',title:'Vb',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});
 const r0=MEM.rec.secs[0];
 const vis=fe=>{if(fe>2){r0.lvl=3;r0.fe=2}else{r0.lvl=2;r0.fe=fe}memStart(0,false);const R=MEM.run;const s=(typeof memFadeSet==='function')?memFadeSet(R):null;const n=R.b-R.a+1;const out={n,set:s?[...s].sort((a,b)=>a-b):null,a:R.a};
   /* Pixel in der Notenbahn zählen */
   R.vt=MEM.gs[R.a].start-0.5;memDraw();const cv=$('#memCv'),k=cv.height/cv.clientHeight,h=Math.floor((MEM.hn-6)*k);const d=cv.getContext('2d').getImageData(0,0,cv.width,Math.max(1,h)).data;let px=0;for(let i=3;i<d.length;i+=4)if(d[i]>20)px++;out.px=px;
   memStop();return out};
 o.s35=vis(0);o.s60=vis(1);o.s70=vis(2);o.s85=vis(3);o.s95=vis(3);
 /* Stufe 1 unverändert: alle Noten sichtbar */
 r0.lvl=1;r0.sk=60;memStart(0,false);o.l1=typeof memFadeSet==='function'?null:null;R=MEM.run;R.vt=MEM.gs[R.a].start-0.5;memDraw();{const cv=$('#memCv'),k=cv.height/cv.clientHeight,h=Math.floor((MEM.hn-6)*k);const d=cv.getContext('2d').getImageData(0,0,cv.width,h).data;let px=0;for(let i=3;i<d.length;i+=4)if(d[i]>20)px++;o.l1px=px}
 memStop();return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        ok=lambda x:x['set'] is not None
        L=lambda x:len(x['set']) if ok(x) else -1
        c={'Funktion da':ok(r['s60']),
           'Etappe 1 → alle sichtbar':L(r['s35'])==r['s35']['n'],
           'Etappe 2 → 60 %':ok(r['s60']) and L(r['s60'])==round(0.6*r['s60']['n']),
           'Schritt 3 → keine':L(r['s85'])==0 and L(r['s95'])==0,
           'weniger bei mehr Sicherheit':L(r['s35'])>=L(r['s60'])>=L(r['s70'])>=L(r['s85']),
           'immer dieselben verschwinden':ok(r['s70']) and set(r['s70']['set'])<=set(r['s60']['set']),
           'erster Anschlag bleibt am längsten':ok(r['s70']) and (L(r['s70'])==0 or r['s70']['a'] in r['s70']['set']),
           'Bahn zeigt Balken in Etappe 2':r['s60']['px']>200,
           'Bahn leer in Schritt 3':r['s85']['px']<50,
           'Stufe 1 unverändert':r['l1px']>=r['s60']['px'],
           'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
