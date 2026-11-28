"""v5.77: Songerkennung – blasse Balkenfarbe und Vor-Leuchten.
 1. Blasse Farbe (Malve, Sättigung 0,18 – echte Videos Kg8z, Sdij): die linke Hand spielt auf schwarzen Tasten erst einen langen Ton (2,5 s), kurz danach Wiederholungen.
    Bis v5.76 hielt die App die lange blass leuchtende Taste für „Taste in Ruhe“ – danach war die Taste taub, die Wiederholungen fehlten. Und blasse Balken sah sie in der
    Bahn gar nicht. Jetzt müssen alle Töne da sein, und kein Ton darf dazukommen.
 2. Vor-Leuchten (Videos mit Leuchteffekt, Lh8A): eine schwarze Taste leuchtet schon 0,3 s vor dem Anschlag schwach. Der Ton muss am Balken beginnen, nicht am Vor-Leuchten.
Das Bild ist gebaut (Bildbau aus nahtsuchetest.py). Ob die Erkennung an echten Videos stimmt, zeigt nur die Messung mit Vergleichs-MIDI (tools/bench/MESSBASIS.md).
usage: python3 tools/bench/blasstest.py $PWD/web/index.html"""
import sys, os, asyncio
from playwright.async_api import async_playwright
app = 'file://' + os.path.abspath(sys.argv[1])
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nahtsuchetest.py'), encoding='utf8').read()
synth = src[src.index('function synth(o) {'):src.index('// Lied mit Tonwiederholungen')]
for a, b in (("HAND = {R: [70, 170, 255], L: [120, 230, 90]}", "HAND = o.hand || {R: [70, 170, 255], L: [120, 230, 90]}"),
             ("set(0, x, bk ? (nb ? HAND[nb.h || 'R'].map(c => c * 0.8) : BLACK)", "const pgl = bk && !nb && o.pre ? sounding(bk.m, t + o.pre.lead) : null; set(0, x, bk ? (nb ? HAND[nb.h || 'R'].map(c => c * (o.bf || 0.8)) : pgl ? HAND[pgl.h || 'R'].map(c => c * 0.8 * o.pre.f) : BLACK)")):
    assert a in synth, a; synth = synth.replace(a, b)
JS = "async()=>{\n" + synth + r"""
 const mk=(L,R)=>{const n=[];let t=1.5;for(const [m,d,p] of R){if(m)n.push({m,s:t,e:t+d,h:'R'});t+=d+(p||0)}let u=1.5;for(const [m,d,p] of L){if(m)n.push({m,s:u,e:u+d,h:'L'});u+=d+(p||0)}return {notes:n,end:Math.max(t,u)}};
 const run=(S,opt)=>{const V=synth(Object.assign({notes:S.notes,dur:S.end+2.5,gap:0.8,v:200,fps:44},opt));
   Object.assign(SCAN,{oddR:[],normF:0,gapMin:null,lrow:null,fi:0,laneGap:null,laneBg:null,laneBgN:null,wov:null,keyPx:null,barDelay:null,kw:V.kw,fromFile:true,hole:false,lastF:null,on:true,keys:V.keys.map(k=>({...k})),rest:null,state:null,lane:null,events:[],frames:0,vtMap:[],lastVt:0,scene:0,cut:null,okF:0,okT:null,oneColor:false,start:0});
   for(let i=0;i<V.frames.length;i++){const p=V.frames[i],W=V.W;scanCore((r,x)=>{const j=(r*W+x)*3;return [p[j],p[j+1],p[j+2]]},W,V.n,V.times[i])}
   SCAN.on=false;const g=finishScan().map(n=>[n.m,n.start,n.dur]).sort((a,b)=>a[1]-b[1]),exp=S.notes.map(n=>[n.m,n.s]).sort((a,b)=>a[1]-b[1]);
   const off=g.length?g[0][1]-exp[0][1]:0,used=new Set(),miss=[];let hit=0;
   for(const e of exp){let b=-1;g.forEach((x,i)=>{if(!used.has(i)&&x[0]===e[0]&&Math.abs(x[1]-off-e[1])<=0.08&&(b<0||Math.abs(x[1]-off-e[1])<Math.abs(g[b][1]-off-e[1])))b=i});if(b>=0){used.add(b);hit++}else miss.push(e[0]+'@'+e[1].toFixed(2))}
   return {soll:exp.length,ist:g.length,hit,miss,extra:g.filter((x,i)=>!used.has(i)).map(x=>[x[0],+(x[1]-off).toFixed(2)])}};
 const o={};
 /* 1. Malve auf schwarzen Tasten: langer Ton, 0,25 s Pause, vier Wiederholungen; dasselbe noch einmal auf einer zweiten Taste. Rechte Hand (blau) spielt dazu weiße Tasten. */
 const A=mk([[61,2.5,0.25],[61,0.3],[61,0.3],[61,0.3],[61,0.3,0.4],[54,2.5,0.25],[54,0.3],[54,0.3],[54,0.3,0.4],[58,0.6],[58,0.6]],[[60,0.5],[64,0.5],[67,0.5,0.3],[65,0.8],[62,0.8,0.3],[60,0.5],[64,0.5],[67,1.0,0.5],[72,0.6],[69,0.6],[65,1.2]]);
 o.blass=run(A,{hand:{R:[70,170,255],L:[141,117,142]},bf:1});
 /* 2. Vor-Leuchten: schwarze Tasten leuchten 0,3 s vorher mit 0,4 der Kraft (6 schwarze Töne zwischen 13 weißen – der Balken-Verzug wird an den weißen gemessen) */
 const B=mk([[48,1.2,0.6],[52,1.2,0.6],[54,1.2,0.6],[55,1.2,0.6],[50,1.2,0.6],[56,1.2,0.6]],[[60,0.5,0.4],[62,0.5,0.4],[61,0.5,0.7],[64,0.5,0.4],[65,0.5,0.4],[66,0.6,0.7],[67,0.6,0.4],[69,0.5,0.4],[70,0.5,0.7],[72,0.5,0.4],[60,0.5,0.4],[64,0.5,0.4],[63,0.5]]);
 o.vor=run(B,{pre:{lead:0.3,f:0.4}});
 o.ver=document.querySelector('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(app); await pg.wait_for_timeout(500)
        r = await pg.evaluate(JS); await b.close()
    a, v = r['blass'], r['vor']
    c = {f"Blasse Farbe: alle {a['soll']} Töne erkannt (auch die Wiederholungen nach dem langen Ton)": a['hit'] == a['soll'],
         'Blasse Farbe: kein Ton zu viel': not a['extra'],
         f"Vor-Leuchten: alle {v['soll']} Töne beginnen am Balken (± 80 ms)": v['hit'] == v['soll'],
         'Vor-Leuchten: kein Ton zu viel': not v['extra'],
         'Version 5.77': r['ver'].startswith('Version 5.77'),
         'keine JS-Fehler': not errs}
    for k, x in c.items(): print(('OK   ' if x else 'FEHL ') + k)
    if not all(c.values()): print({k: x for k, x in r.items() if isinstance(x, dict)}, errs)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
