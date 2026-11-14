"""v5.02: Oktave aus dem Bild – viele Tutorials markieren das mittlere C (dunklere „C4“-Beschriftung oder ein Punkt).
Echte Handy-Bilder (3 Bilder beim Abspielen je Video, aus klavier-diagnose) in refs/oktave/: 3 Videos, bei denen die App eine Oktave zu hoch lag
(im Bild nachgezählt), 14 richtige (müssen richtig bleiben), 11 ohne eindeutige Markierung (keine Entscheidung → alte Regel bleibt).
Dazu: Entscheidungsregel (≥ 2 gleiche Bilder, kein Widerspruch, höchstens eine Oktave) und Anwenden auf Noten/Tasten.

usage: python3 tools/bench/oktavtest.py $PWD/web/index.html"""
import sys, os, json, base64, asyncio
from playwright.async_api import async_playwright
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'refs', 'oktave')

JS = r"""async(cases)=>{
 const load=src=>new Promise(res=>{const im=new Image();im.onload=()=>{const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const x=c.getContext('2d');x.drawImage(im,0,0);res(x.getImageData(0,0,c.width,c.height))};im.src=src});
 const out=[];
 for(const c of cases){const votes=[];for(const s of c.imgs){const img=await load(s);votes.push(midCMark(img,c.keys,c.rows))}
   out.push({vid:c.vid,want:c.want,votes,dec:octFromMarks(votes)})}
 const o={cases:out};
 /* Regel */
 o.r1=JSON.stringify(octFromMarks([72,72,null]))===JSON.stringify({d:-12,sure:true});
 o.r2=octFromMarks([72,null,null]).sure===false;         /* ein Bild allein reicht nicht */
 o.r3=octFromMarks([72,60,72]).sure===false;             /* Widerspruch → nichts */
 o.r4=octFromMarks([84,84,84]).sure===false;             /* zwei Oktaven: unplausibel → nichts */
 o.r5=JSON.stringify(octFromMarks([60,60,60]))===JSON.stringify({d:0,sure:true});
 /* Anwenden */
 const keys0=[{m:60,x:.1},{m:72,x:.5}];SCAN.keys=keys0.map(k=>({...k}));scanDet={shift:0,octEst:true};SCAN.octV=[72,72,72];
 const notes=[{m:64,start:0,dur:1},{m:76,start:1,dur:1}];const a=octFixApply(notes);
 o.apply=a.d===-12&&notes[0].m===52&&notes[1].m===64&&SCAN.keys[0].m===48&&scanDet.shift===-12;
 SCAN.keys=keys0.map(k=>({...k}));scanDet={shift:0,octEst:true};SCAN.octV=[48,48,48];const n2=[{m:100,start:0,dur:1}];octFixApply(n2);
 o.range=n2[0].m===100&&SCAN.octFix.sure===false;        /* würde über die Klaviatur hinausgehen → nichts */
 return o}"""

async def main():
    cases = json.load(open(os.path.join(D, 'faelle.json')))
    for c in cases:
        c['imgs'] = ['data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(D, f), 'rb').read()).decode() for f in c['imgs']]
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(3000)
        r = await pg.evaluate(JS, cases); await br.close()
    ok = True; nf = nk = nn = 0
    for c in r['cases']:
        d = c['dec']; w = c['want']
        good = (d['sure'] is False) if w is None else (d['sure'] and d['d'] == w)
        ok &= good
        if w is None: nn += good
        elif w: nf += good
        else: nk += good
        print(f"{c['vid']:12} soll={w!s:5} Bilder={c['votes']} → {d} {'OK' if good else 'FALSCH'}")
    print(f"korrigiert {nf}/3, richtig geblieben {nk}/14, keine Entscheidung {nn}/11")
    checks = {k: v for k, v in r.items() if k != 'cases'}; checks['keine Fehler'] = not errs
    print(checks, errs)
    ok &= all(checks.values())
    print('OK' if ok else 'FEHLER')

asyncio.run(main())
