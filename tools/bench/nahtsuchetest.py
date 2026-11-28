"""v5.76: Songerkennung – Tonwiederholungen, Namensschilder, Bildwechsel, Kamera-Zoom.
Felix 27.11.: „immer die gleichen Fehler, vor allem mehrere Töne hintereinander, die als ein langer Ton gezählt werden“.
Der Test baut ein Synthesia-Bild selbst (Tastatur, fallende Balken, 7 Lesezeilen wie am Handy) und schickt es durch scanCore/finishScan – ohne Video, ohne Handy.
 1. Tonwiederholungen: zwischen zwei Balken derselben Taste liegt nur eine dünne dunkle Linie (0,8 Pixel). Alle 30 Töne müssen einzeln da sein.   (v5.70: 25 von 30 → rot)
 2. Namensschilder: jeder Balken trägt unten ein dunkles Kästchen mit farbiger Schrift. Das Kästchen ist keine Lücke – kein Ton darf dazukommen,
    und das Video muss als Schild-Video erkannt sein.   (Zwischenstand von v5.76 ohne Schild-Erkennung: 28 erfundene Töne)
 3. Bildwechsel: nach 9 s zeigt das Video eine andere Tastatur (um eine halbe Taste versetzt, z. B. zweiter Song oder fremder Abspann). Dort endet der Song –
    es darf kein Ton mehr dazukommen.   (v5.70: 5 falsche Töne → rot)
 4. Kamera-Zoom: das Bild wird über 8 s langsam 6 % größer (echte Hände, Kamera fährt). Das ist KEIN Bildwechsel – der Song wird bis zum Ende gelesen.
Wichtig: Das Bild ist gebaut. Ob die Erkennung an echten Videos stimmt, zeigt nur die Messung an den Aufnahmen mit Vergleichs-MIDI (tools/bench/MESSBASIS.md).
usage: python3 tools/bench/nahtsuchetest.py $PWD/web/index.html"""
import sys, os, asyncio
from playwright.async_api import async_playwright
app = 'file://' + os.path.abspath(sys.argv[1])
JS = r"""async()=>{
// Gebautes Synthesia-Bild für scanCore: 7 Pixelzeilen je Bild (0 = schwarze Tasten, 1 = weiße Tasten, 2 = knapp über der Tastatur, 3–6 = vier Bahn-Zeilen).
// Läuft im Browser (Test) und in Node (Entwicklung). synth(opts) → {W, keys, kw, fps, frames:[Uint8Array(W*7*3)], times:[]}
function synth(o) {
  const W = o.W || 960, fps = o.fps || 44, v = o.v || 160, dur = o.dur, notes = o.notes, gap = o.gap == null ? 1.5 : o.gap;
  const WPC = [0, 2, 4, 5, 7, 9, 11], OFF = {1: -0.12, 3: 0.12, 6: -0.14, 8: 0, 10: 0.14}, lo = 48, hi = 72;
  const whites = []; for (let m = lo; m <= hi; m++) if (WPC.includes(m % 12)) whites.push(m); const ww = W / whites.length;
  const geo = shift => { const ks = []; let wi = 0; for (let m = lo; m <= hi; m++) { if (WPC.includes(m % 12)) { ks.push({m, c: wi * ww + ww / 2 + shift, hw: ww * 0.5, bw: ww * 0.42, black: false}); wi++; } else ks.push({m, c: wi * ww + ww * OFF[m % 12] + shift, hw: ww * 0.29, bw: ww * 0.26, black: true}); } return ks; };
  const G0 = geo(0), G1 = geo(ww * 0.5);                      // G1 = „andere Tastatur“ (um eine halbe Taste versetzt)
  const keys = G0.map(k => ({m: k.m, x: k.c / (W - 1), black: k.black, rest: k.black ? [18, 18, 20] : [235, 235, 228]}));
  const BG = [22, 22, 26], WHITE = [235, 235, 228], BLACK = [18, 18, 20], SEP = [60, 60, 60], HAND = {R: [70, 170, 255], L: [120, 230, 90]};
  const H = o.rows || [112.5, 110, 107.5, 105], HC = 3, AP = [-1, -0.5, 0, 0.5, 1], NR = 3 + H.length;
  const byKey = new Map(); for (const n of notes) { if (!byKey.has(n.m)) byKey.set(n.m, []); byKey.get(n.m).push(n); }
  for (const L of byKey.values()) { L.sort((a, b) => a.s - b.s); for (let i = 0; i < L.length; i++) L[i].top = (i + 1 < L.length && L[i + 1].s - L[i].e < 0.02) ? gap : 0; }
  const lab = o.label || null;                                 // {from:2, h:10, text:[3,8]} = Kästchen 2…12 px über dem Balkenende, Schrift in 5…10 px
  // Farbe an Bildstelle (x, y über der Tastatur) zur Zeit t; G = Tastenlage dieses Bildes
  const colAt = (G, xi, y, t) => { let res = BG; for (let pass = 0; pass < 2; pass++) for (const k of G) { if (k.black !== (pass === 1)) continue; if (Math.abs(xi - k.c) > k.bw) continue; const L = byKey.get(k.m); if (!L) continue;
      for (const n of L) { const bot = (n.s - t) * v, top = (n.e - t) * v - n.top; if (y < bot || y >= top) continue; const c = HAND[n.h || 'R'];
        if (lab && y - bot >= lab.from && y - bot < lab.from + lab.h && Math.abs(xi - k.c) <= k.bw * 0.8) { const ty = y - bot - lab.from, inText = ty >= lab.text[0] && ty < lab.text[1];
          res = inText && Math.abs(xi - k.c) <= k.bw * 0.6 && (Math.round(xi - k.c) & 3) < 2 ? (lab.ink || [245, 245, 245]) : [c[0] * 0.35, c[1] * 0.35, c[2] * 0.35]; } else res = c; } } return res; };
  const sounding = (m, t) => { const L = byKey.get(m); if (!L) return null; for (const n of L) if (t >= n.s && t < n.e - 0.012) return n; return null; };
  const frames = [], times = [], nF = Math.round(dur * fps);
  for (let f = 0; f < nF; f++) { const t = f / fps, px = new Uint8Array(W * NR * 3), other = o.switchAt != null && t >= o.switchAt, G = other ? G1 : G0;
    const z = o.zoom ? 1 + o.zoom.by * Math.min(1, Math.max(0, (t - o.zoom.from) / (o.zoom.to - o.zoom.from))) : 1, src = x => W / 2 + (x - W / 2) / z;
    const set = (r, x, c) => { const i = (r * W + x) * 3; px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2]; };
    for (let x = 0; x < W; x++) { const xs = src(x);
      // Tastenzeilen
      let wk = null, bk = null; for (const k of G) { if (!k.black && Math.abs(xs - k.c) <= k.hw) wk = k; if (k.black && Math.abs(xs - k.c) <= k.hw) bk = k; }
      const edge = wk && Math.abs(Math.abs(xs - wk.c) - wk.hw) < 0.7, nw = wk && sounding(wk.m, t), nb = bk && sounding(bk.m, t);
      set(0, x, bk ? (nb ? HAND[nb.h || 'R'].map(c => c * 0.8) : BLACK) : (wk ? (nw ? HAND[nw.h || 'R'] : WHITE) : BLACK));
      set(1, x, edge ? SEP : (wk ? (nw ? HAND[nw.h || 'R'] : WHITE) : BLACK));
      // Zeile knapp über der Tastatur und die vier Bahn-Zeilen: Mittel über die Höhe eines Aufnahme-Pixels
      for (let r = 2; r < NR; r++) { const h = r === 2 ? HC : H[r - 3]; let a = 0, b = 0, c = 0; for (const d of AP) { const q = colAt(G, xs, h + d, t); a += q[0]; b += q[1]; c += q[2]; } set(r, x, [a / 5, b / 5, c / 5]); } }
    frames.push(px); times.push(t); }
  return {W, keys, kw: ww / (W - 1), fps, frames, times, n: NR};
}
// Lied mit Tonwiederholungen: [Taste, Beginn, Dauer]
function song() { const n = []; let t = 1.5; const add = (m, d, h) => { n.push({m, s: t, e: t + d, h: h || 'R'}); t += d; }, rest = d => { t += d; };
  for (let i = 0; i < 4; i++) add(60, 0.4); rest(0.3); for (let i = 0; i < 3; i++) add(64, 0.3); rest(0.3); add(67, 1.2); rest(0.3);
  for (let i = 0; i < 4; i++) add(61, 0.25); rest(0.4); add(62, 0.5); add(64, 0.5); add(65, 0.5); rest(0.3); for (let i = 0; i < 6; i++) add(66, 0.2); rest(0.4);
  for (let i = 0; i < 2; i++) add(69, 0.6); rest(0.3); add(72, 0.8);
  // linke Hand: lange Töne und zwei Wiederholungen
  let u = 1.5; const addL = (m, d) => { n.push({m, s: u, e: u + d, h: 'L'}); u += d; }; addL(48, 1.6); addL(48, 1.6); u += 0.3; addL(52, 2.0); u += 0.5; addL(50, 1.5); addL(50, 1.5); u += 0.4; addL(55, 2.0);
  return {notes: n, end: Math.max(t, u)}; }

 const S=song(),base={notes:S.notes,dur:S.end+2.5};
 const run=opt=>{const V=synth(Object.assign({},base,opt));
   Object.assign(SCAN,{oddR:[],normF:0,gapMin:null,lrow:null,fi:0,laneGap:null,laneBg:null,laneBgN:null,wov:null,keyPx:null,barDelay:null,kw:V.kw,fromFile:true,hole:false,lastF:null,on:true,keys:V.keys.map(k=>({...k})),rest:null,state:null,lane:null,events:[],frames:0,vtMap:[],lastVt:0,scene:0,cut:null,okF:0,okT:null,oneColor:false,start:0});
   for(let i=0;i<V.frames.length;i++){const p=V.frames[i],W=V.W;scanCore((r,x)=>{const j=(r*W+x)*3;return [p[j],p[j+1],p[j+2]]},W,V.n,V.times[i])}
   SCAN.on=false;const g=finishScan().map(n=>[n.m,n.start,n.dur]).sort((a,b)=>a[1]-b[1]),exp=S.notes.map(n=>[n.m,n.s]).sort((a,b)=>a[1]-b[1]);
   // Vergleich: gleiche Taste, Beginn höchstens 80 ms daneben (der gemeinsame Versatz wird ausgeglichen: die App legt den ersten Ton auf 1 s)
   const off=g.length?g[0][1]-exp[0][1]:0,used=new Set(),miss=[];let hit=0;
   for(const e of exp){let b=-1;g.forEach((x,i)=>{if(!used.has(i)&&x[0]===e[0]&&Math.abs(x[1]-off-e[1])<=0.08&&(b<0||Math.abs(x[1]-off-e[1])<Math.abs(g[b][1]-off-e[1])))b=i});if(b>=0){used.add(b);hit++}else miss.push(e[0]+'@'+e[1].toFixed(2))}
   const extra=g.filter((x,i)=>!used.has(i)).map(x=>[x[0],+(x[1]-off).toFixed(2)]);
   return {soll:exp.length,ist:g.length,hit,miss,extra,cut:SCAN.cut==null?null:+SCAN.cut.toFixed(2),lab:SCAN.seamLab||null,last:g.length?+(g[g.length-1][1]-off).toFixed(2):null}};
 const o={};
 o.wdh=run({gap:0.8,v:200,fps:44});
 o.schild=run({gap:0.8,v:120,fps:30,label:{from:2,h:11,text:[3,8],ink:[170,210,255]}});
 o.wechsel=run({gap:0.8,v:200,fps:44,switchAt:9.0});
 o.zoom=run({gap:0.8,v:200,fps:44,zoom:{from:3,to:11,by:0.06}});
 o.ver=document.querySelector('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(app); await pg.wait_for_timeout(500)
        r = await pg.evaluate(JS); await b.close()
    w, s, x, z = r['wdh'], r['schild'], r['wechsel'], r['zoom']
    c = {'Tonwiederholungen: alle 30 Töne einzeln erkannt': w['hit'] == 30,
         'Tonwiederholungen: kein Ton zu viel': not w['extra'],
         'Namensschilder: als Schild-Video erkannt': bool(s['lab'] and s['lab'].get('on')),
         'Namensschilder: kein erfundener Ton durch die Kästchen': not s['extra'],
         'Bildwechsel: der Song endet am Wechsel (Schnitt zwischen 8 und 9,5 s)': x['cut'] is not None and 8 <= x['cut'] <= 9.5,
         'Bildwechsel: kein Ton von der anderen Tastatur': not [e for e in x['extra']],
         'Bildwechsel: die Töne davor sind alle da': not [m for m in x['miss'] if float(m.split('@')[1]) < 8.6],
         'Kamera-Zoom: kein Schnitt, der Song wird bis zum Ende gelesen': z['cut'] is None and z['last'] is not None and z['last'] > 12,
         'Kamera-Zoom: mindestens 28 von 30 Tönen': z['hit'] >= 28,
         'Version 5.78': r['ver'].startswith('Version 5.78'),
         'keine JS-Fehler': not errs}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    if not all(c.values()): print({k: {a: v[a] for a in ('soll', 'ist', 'hit', 'miss', 'extra', 'cut', 'lab', 'last')} for k, v in r.items() if isinstance(v, dict)}, errs)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
