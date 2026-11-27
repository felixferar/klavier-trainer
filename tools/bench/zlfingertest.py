"""v5.67: Auswendig-Modus zeigt Fingerzahlen und unterscheidet schwarze von weißen Tasten.
Felix 27.11.: „Ich weiß nicht, wo meine Hände hin müssen“ und „es wird B angezeigt, ich drücke B – gemeint war die schwarze Taste“.
Prüft: Namen wie in den Videos (B = weiße Taste, Bb = schwarze), Schild hinter den Namen schwarzer Tasten, Fingerzahl im Balken und auf der Zieltaste,
Fingersatz für jeden Ton, Akkord ohne doppelten oder überkreuzten Finger, gleiche Griffe = gleiche Finger, Schalter aus = keine Zahlen.
usage: python3 tools/bench/zlfingertest.py $PWD/web/index.html"""
import sys, os, asyncio
from playwright.async_api import async_playwright
app = 'file://' + os.path.abspath(sys.argv[1])
JS = r"""async()=>{const o={};const ns=[];let t=1.5;
 for(let r=0;r<6;r++){for(const m of [70,73,77])ns.push({m,start:t,dur:1.3,hand:'R'});for(let i=0;i<4;i++)ns.push({m:58,start:t+i*0.42,dur:0.18,hand:'L'});t+=1.7;
   for(const m of [69,72,77])ns.push({m,start:t,dur:1.3,hand:'R'});for(let i=0;i<4;i++)ns.push({m:59,start:t+i*0.42,dur:0.18,hand:'L'});t+=1.7}
 const it={id:'zf',type:'midi',title:'T',artist:'x',data:b64FromBuf(writeMidi(ns)),video:{v:2}};LIB=[it];
 o.names=[NAMES[10],NAMES[11],NAMES[1],NAMES[6],zlName(70),zlName(71)];o.fingDefault=S.fingers;
 const run=on=>{S.fingers=on;openMem(it);zlStart({k:0,stage:2,t:0});const R=MEM.run;if(R&&R.demo)R.demo=null;
   const cv=document.querySelector('#zlCv'),c=cv.getContext('2d'),log=[],ft=c.fillText.bind(c),rr=c.roundRect&&c.roundRect.bind(c);let boxes=0;
   c.fillText=(s,x,y)=>{log.push(String(s));return ft(s,x,y)};if(rr)c.roundRect=(...a)=>{if(a[3]<24&&a[2]<60)boxes++;return rr(...a)};zlDraw();c.fillText=ft;if(rr)c.roundRect=rr;return {log,boxes}};
 const a=run(true);o.on=a.log;o.boxes=a.boxes;o.all=MEM.notes.every(n=>n.fing>=1&&n.fing<=5);
 const ch=MEM.notes.filter(n=>n.hand==='R'&&Math.abs(n.start-MEM.notes.find(q=>q.hand==='R').start)<0.05).sort((p,q)=>p.midi-q.midi).map(n=>n.fing);o.chord=ch;
 const by={};for(const g of MEM.gs){const r=[...g.mids].filter(m=>m>60).sort((p,q)=>p-q);if(r.length<2)continue;const k=r.join(),f=r.map(m=>MEM.notes.find(q=>q.midi===m&&Math.abs(q.start-g.start)<0.2).fing).join();(by[k]=by[k]||new Set()).add(f)}
 o.same=Object.values(by).every(s=>s.size===1);o.kinds=Object.keys(by).length;
 const b=run(false);o.off=b.log;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(app); await pg.wait_for_timeout(400); r = await pg.evaluate(JS); await br.close()
    num = lambda L: [x for x in L if x in '12345']
    c = {'Namen: schwarze Taste „Bb“, weiße Taste „B“ (nicht mehr deutsch B/H); Db und F# wie in den Videos': r['names'] == ['Bb', 'B', 'Db', 'F#', 'Bb', 'B'],
         'Fingersatz ist nach dem Update eingeschaltet': r['fingDefault'] is True,
         'jeder Ton hat einen Finger 1–5': r['all'],
         'Akkord Bb–Db–F rechts: aufsteigend, kein Finger doppelt': r['chord'] == sorted(set(r['chord'])) and len(r['chord']) == 3,
         'gleiche Griffe haben überall dieselben Finger': r['same'] and r['kinds'] >= 2,
         'Balken zeigen Namen und Fingerzahlen': 'Bb' in r['on'] and 'F' in r['on'] and len(num(r['on'])) >= 4,
         'Namen schwarzer Tasten stehen auf einem Schild': r['boxes'] >= 2,
         'Schalter aus: keine Fingerzahlen, Namen bleiben': not num(r['off']) and 'Bb' in r['off'],
         'keine JS-Fehler': not errs}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    if not all(c.values()): print(r, errs)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
