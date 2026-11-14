"""v4.93: Balken-Zeilen – jeder Balken gehört seiner eigenen Taste, und ein Balken, der schon im ersten Bild in der Lesezeile steht, wird nicht zum 'Hintergrund'.
usage: python3 tools/bench/balkentest.py [APP.html]   (Standard: web/index.html)
Prüft laneBars direkt mit gebauten Pixelzeilen (keine Videos nötig):
 1. Weißer Balken allein (C), daneben eine nach innen versetzte schwarze Taste (C#): nur C ist belegt.       (v4.90: C# bekam den Balken mit → rot)
 2. C und C# gleichzeitig (C#-Balken ragt rechts über C hinaus): beide belegt.
 3. Balken mit Buchstabe (dunkles Pixel + helle Schrift mitten im Balken): weiße Taste belegt, schwarze Nachbartaste nicht.
 4. Erstes Bild: Balken steht schon in der Zeile. Danach dunkler Hintergrund, dann derselbe Balken neu: wird erkannt.   (v4.90: nie → rot)
 5. Lernen des Überstands: nach 20 einzelnen weißen Balken reicht ein kleiner Überstand von 4 px für die schwarze Taste.
"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
APP = 'file://' + os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'web', 'index.html'))
JS = r"""()=>{
 const W=600,WPC=[0,2,4,5,7,9,11],OFF={1:-0.15,3:0.15,6:-0.15,8:0,10:0.15};
 const whites=[];for(let m=48;m<=72;m++)if(WPC.includes(m%12))whites.push(m);const ww=W/whites.length;
 const keys=[];let wi=0;for(let m=48;m<=72;m++){if(WPC.includes(m%12)){keys.push({m,x:(wi*ww+ww/2)/(W-1),black:false});wi++}else keys.push({m,x:(wi*ww+ww*OFF[m%12])/(W-1),black:true})}
 const reset=()=>Object.assign(SCAN,{keys,kw:ww/(W-1),laneBg:null,laneBgN:null,keyPx:null,wov:null});
 const BG=[10,12,16],BAR=[120,90,240];
 const row=(spans)=>{const a=[];for(let x=0;x<W;x++)a.push(BG);for(const [x0,x1,c] of spans)for(let x=Math.max(0,Math.round(x0));x<=Math.min(W-1,Math.round(x1));x++)a[x]=c||BAR;return a};
 const run=(r)=>laneBars((rr,x)=>r[x],W,0,0);
 const K=m=>keys.findIndex(k=>k.m===m),cx=m=>keys[K(m)].x*(W-1),res={};
 const C=60,Cs=61,D=62;const cL=cx(C)-ww/2,cR=cx(C)+ww/2;
 // 1
 reset();run(row([]));let o=run(row([[cL+2,cR-2]]));res.t1={C:o[K(C)],Cs:o[K(Cs)],ok:o[K(C)]&&!o[K(Cs)]};
 // 2: C# bar (width 0.6 ww around its centre) on top of the C bar
 reset();run(row([]));o=run(row([[cL+2,cR-2],[cx(Cs)-ww*0.3,cx(Cs)+ww*0.3]]));res.t2={C:o[K(C)],Cs:o[K(Cs)],D:o[K(D)],ok:o[K(C)]&&o[K(Cs)]&&!o[K(D)]};
 // 3: letter: dark pixel, two bright pixels, dark pixel inside the C bar, right of the middle
 reset();run(row([]));const lx=Math.round(cx(C)+2);o=run(row([[cL+2,cR-2],[lx,lx,BG],[lx+1,lx+2,[250,250,250]],[lx+3,lx+3,BG]]));res.t3={C:o[K(C)],Cs:o[K(Cs)],B:o[K(59)],ok:o[K(C)]&&!o[K(Cs)]&&!o[K(59)]};
 // 4: first frame already shows the D bar; then 6 frames background; then the D bar again
 reset();const dL=cx(D)-ww/2,dR=cx(D)+ww/2;run(row([[dL+2,dR-2]]));for(let i=0;i<6;i++)run(row([]));o=run(row([[dL+2,dR-2]]));res.t4={D:o[K(D)],ok:!!o[K(D)]};
 // 5: 20 single white bars teach the overhang (−2 px); then C + a C# bar sticking out only 4 px past C's right edge
 reset();run(row([]));for(let i=0;i<22;i++){run(row([[cx(64)-ww/2+2,cx(64)+ww/2-2]]));run(row([]))}
 o=run(row([[cL+2,cR+4]]));res.t5={C:o[K(C)],Cs:o[K(Cs)],ok:o[K(C)]&&o[K(Cs)]};
 return res}"""


async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(400)
        r = await pg.evaluate(JS); bad = [k for k, v in r.items() if not v['ok']]
        for k, v in r.items(): print(k, 'OK ' if v['ok'] else 'FEHLER', json.dumps({a: b for a, b in v.items() if a != 'ok'}))
        print('pageerrors', errs)
        print('balkentest', 'OK' if not bad and not errs else 'FEHLER ' + ','.join(bad))
        await br.close()
        sys.exit(1 if bad or errs else 0)
asyncio.run(main())
