"""v5.70: Im Auswendig-Modus bleibt eine Taste auf der App-Klaviatur gefärbt, solange sie am Klavier gehalten wird.
Felix 27.11.: „wenn ich Tasten gedrückt halte, dass die noch wirklich gedrückt sind auf der App – grün oder rot“.
Vorher: richtige Taste blitzte 0,35 s grün, falsche 0,6 s rot, auch wenn der Finger liegen blieb.
Prüft die Farbe der Taste auf der gezeichneten Klaviatur: gehalten nach 1,2 s noch grün bzw. rot; losgelassen klingt es kurz nach und ist dann weg;
erneutes Drücken nach dem Loslassen zählt neu; ohne Klavier (kein KB.held) bleibt das kurze Aufblitzen.
usage: python3 tools/bench/gehaltentest.py $PWD/web/index.html"""
import sys, os, asyncio
from playwright.async_api import async_playwright
app = 'file://' + os.path.abspath(sys.argv[1])
JS = r"""async()=>{const o={};const ns=[];let t=1.5;for(let r=0;r<6;r++){for(const m of [60,64,67])ns.push({m,start:t,dur:1.3,hand:'R'});t+=1.7;ns.push({m:62,start:t,dur:0.8,hand:'R'});t+=1.2}
 const it={id:'gh',type:'midi',title:'T',artist:'x',data:b64FromBuf(writeMidi(ns)),video:{v:2}};LIB=[it];S.fingers=false;window.AW_NOLOOP=1;
 openMem(it);zlStart({k:0,stage:1,t:0});const R=MEM.run;if(R.demo)zlDemoEnd(R);
 const cv=document.querySelector('#zlCv');
 // Farbe der Taste m: beim Zeichnen mitschreiben, womit die Tastenfläche gefüllt wird
 const keyCol=()=>{const c=cv.getContext('2d'),fr=c.fillRect.bind(c);const seen=[];let last='';const desc=Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype,'fillStyle');
   c.fillRect=(x,y,w,h)=>{seen.push([String(c.fillStyle).toLowerCase(),x,y,w,h]);return fr(x,y,w,h)};zlDraw();c.fillRect=fr;
   const ok=ZL.col.ok.toLowerCase(),bad=ZL.col.bad.toLowerCase();return {ok:seen.filter(s=>s[0]===ok).length,bad:seen.filter(s=>s[0]===bad&&s[4]<200&&s[3]<80).length}};
 const real=performance.now.bind(performance);let off=0;performance.now=()=>real()+off;
 const down=m=>{KB.held.add(m);zlPress(m)},up=m=>{KB.held.delete(m);KB.rel.set(m,performance.now())};
 // 0) v5.79: D einmal falsch (vor dem Akkord) – kommt später richtig dran
 down(62);off+=50;up(62);off+=1000;
 // 1) richtige Taste (C des ersten Akkords) gehalten
 down(60);o.g0=keyCol().ok;off+=1200;o.gHeld=keyCol().ok;up(60);off+=100;o.gAfter100=keyCol().ok;off+=400;o.gAfter500=keyCol().ok;
 // 2) falsche Taste gehalten
 down(61);o.b0=keyCol().bad;off+=1500;o.bHeld=keyCol().bad;up(61);off+=100;o.bAfter200=keyCol().bad;off+=700;o.bAfter800=keyCol().bad;
 // 3) ohne Klavier (Mikrofon): KB.held kennt die Taste nicht → nur kurzes Aufblitzen wie bisher
 zlPress(64);o.m0=keyCol().ok;off+=1200;o.mLater=keyCol().ok;
 // 4) Taste gehalten, obwohl ihr Treffer VOR dem letzten Loslassen lag (alter Treffer zählt nicht als gehalten)
 down(67);off+=50;up(67);off+=600;KB.held.add(67);o.old=keyCol().ok;KB.held.delete(67);
 // 5) v5.79: jetzt ist D dran – richtig gedrückt, gehalten, losgelassen: klingt GRÜN nach, nicht rot (der Fehlgriff von vorhin zählt nicht mehr)
 o.pos=MEM.gs[R.pos].mids.has(62);down(62);off+=800;o.dHeld=keyCol();up(62);off+=80;o.dAfter=keyCol();
 o.ver=document.querySelector('#verTxt').textContent;performance.now=real;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(app); await pg.wait_for_timeout(400); r = await pg.evaluate(JS); await br.close()
    c = {'richtige Taste wird grün': r['g0'] >= 1,
         'richtige Taste bleibt grün, solange sie gehalten wird (1,2 s)': r['gHeld'] >= 1,
         'nach dem Loslassen klingt Grün kurz nach und ist nach 0,5 s weg': r['gAfter100'] >= 1 and r['gAfter500'] == 0,
         'falsche Taste wird rot und bleibt rot, solange sie gehalten wird (1,5 s)': r['b0'] >= 1 and r['bHeld'] >= 1,
         'nach dem Loslassen klingt Rot kurz nach (0,1 s) und ist nach 0,8 s weg': r['bAfter200'] >= 1 and r['bAfter800'] == 0,
         'ohne Klavier-Verbindung: kurzes Aufblitzen wie bisher': r['m0'] >= 1 and r['mLater'] == 0,
         'ein alter Treffer färbt eine neu gehaltene Taste nicht': r['old'] == 0,
         'v5.79: Taste früher einmal falsch, jetzt richtig gehalten → grün, auch beim Loslassen kein Rot': r['pos'] and r['dHeld']['bad'] == 0 and r['dAfter']['bad'] == 0 and r['dAfter']['ok'] >= 1,
         'Version 5.81': r['ver'].startswith('Version 5.81'),
         'keine JS-Fehler': not errs}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    if not all(c.values()): print(r, errs)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
