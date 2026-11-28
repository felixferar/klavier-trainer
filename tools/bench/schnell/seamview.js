// Neue Nähte ansehen: je Naht die vier Bahn-Zeilen um die Taste, Zeit nach unten. usage: node seamview.js VIDEOID OUT.png [ANZAHL=12] [SEED=1] [APP]
const fs = require('fs'), zlib = require('zlib'), {loadApp, loadKtd, replay} = require('./replay_node.js');
const a = process.argv.slice(2), DIAG = (process.env.KLAVIER_DIAG || '/home/claude/klavier-diagnose') + '/diag', f = fs.readdirSync(DIAG).filter(x => x.includes('_' + a[0]) && x.endsWith('_done.ktd.gz')).sort().pop();
const N = +(a[2] || 12), seed = +(a[3] || 1), api = loadApp(a[4] || require('path').join(__dirname, '..', '..', '..', 'web', 'index.html'), {}), rec = loadKtd(DIAG + '/' + f);
const notes = replay(api, rec), S = api.SCAN, M = rec.meta, w = M.w, raw = rec.raw, start = M.start || 0, rd = S.seamRd || [0, 0, 0, 0], off = S.seamOff || 0;
const fr = rec.frames.filter(x => !Number.isNaN(x.f)), ft = fr.map(x => x.f - start);
const app = (S.seams || []).filter(s => { const L = S.lane[s.k]; return L && L.ons.some(o => Math.abs(o - (s.t + off)) < 1e-6); });
console.log(f, '| Noten', notes.length, '| Nähte gefunden', (S.seams || []).length, 'eingefügt', app.length, '| rd', rd.map(x => +x.toFixed(3)).join(','), 'off', +off.toFixed(3), '| kw px', +((S.kw || 0) * (w - 1)).toFixed(1));
let r0 = seed; const rnd = () => (r0 = (r0 * 1103515245 + 12345) % 2147483648) / 2147483648;
const pick = app.map(s => [rnd(), s]).sort((p, q) => p[0] - q[0]).slice(0, N).map(x => x[1]).sort((p, q) => p.t - q.t);
const kwp = Math.max(6, (S.kw || 0.02) * (w - 1)), hw = Math.round(kwp * 1.1), cw = 2 * hw + 1, SX = kwp > 20 ? 1 : 2, SY = 5, HALF = 0.4, gap = 6;
const fps = fr.length / (ft[ft.length - 1] - ft[0]), nf = Math.round(HALF * fps), ch = 2 * nf + 1, cellW = (cw * SX + 2) * 4 + gap * 2, cellH = ch * SY + gap * 2, cols = Math.max(1, Math.floor(1500 / cellW));
const rowsN = Math.ceil(pick.length / cols), W = cols * cellW, H = rowsN * cellH, img = Buffer.alloc(W * H * 3, 40);
const idxAt = t => { let lo = 0, hi = ft.length - 1; while (lo < hi) { const m = (lo + hi) >> 1; if (ft[m] < t) lo = m + 1; else hi = m; } return lo; };
pick.forEach((s, n) => { const cx = (n % cols) * cellW + gap, cy = Math.floor(n / cols) * cellH + gap, kx = Math.round(S.keys[s.k].x * (w - 1));
  for (let r = 0; r < 4; r++) { const i0 = idxAt(s.t + rd[r]);
    for (let d = -nf; d <= nf; d++) { const i = i0 + d; if (i < 0 || i >= fr.length) continue; const o = fr[i].o + (3 + r) * w * 3;
      for (let x = -hw; x <= hw; x++) { const X = kx + x; if (X < 0 || X >= w) continue; const p = o + X * 3;
        for (let yy = 0; yy < SY; yy++) for (let xx = 0; xx < SX; xx++) { const q = ((cy + (d + nf) * SY + yy) * W + cx + r * (cw * SX + 2) + (x + hw) * SX + xx) * 3; img[q] = raw[p]; img[q + 1] = raw[p + 1]; img[q + 2] = raw[p + 2]; } }
      if (d === 0) for (let xx = 0; xx < 2; xx++) for (let yy = 0; yy < SY; yy++) { const q = ((cy + nf * SY + yy) * W + cx + r * (cw * SX + 2) + cw * SX + xx) * 3; img[q] = 255; img[q + 1] = 255; img[q + 2] = 0; } } }
  console.log(`#${n + 1} Taste ${S.keys[s.k].midi || S.keys[s.k].m || s.k} t ${(s.t + off).toFixed(2)} Zeilen ${s.n} q ${s.q.toFixed(2)}`); });
// PNG schreiben
const crcT = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
const crc = b => { let c = 0xffffffff; for (const x of b) c = crcT[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (t, d) => { const l = Buffer.alloc(4); l.writeUInt32BE(d.length); const td = Buffer.concat([Buffer.from(t), d]), c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); };
const ih = Buffer.alloc(13); ih.writeUInt32BE(W, 0); ih.writeUInt32BE(H, 4); ih[8] = 8; ih[9] = 2;
const sc = Buffer.alloc((W * 3 + 1) * H); for (let y = 0; y < H; y++) img.copy(sc, y * (W * 3 + 1) + 1, y * W * 3, (y + 1) * W * 3);
fs.writeFileSync(a[1], Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ih), chunk('IDAT', zlib.deflateSync(sc)), chunk('IEND', Buffer.alloc(0))]));
console.log('Bild', W, 'x', H, '| Zelle: 4 Zeilen (oben→unten nah an der Tastatur?), Zeit nach unten, gelber Strich = Naht');
