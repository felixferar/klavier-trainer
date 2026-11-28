// Spielt eine Diagnose-Aufnahme (.ktd.gz) durch scanCore/finishScan aus einer App-Datei (index.html) – ohne Browser.
// usage: node replay_node.js APP.html AUFNAHME.ktd.gz OUT.json [--dbg EXPR] [--set NAME=VALUE ...]
const fs = require('fs'), zlib = require('zlib');
function loadApp(appPath, flags) {
  const html = fs.readFileSync(appPath, 'utf8');
  const a = html.indexOf('/* ================= Video → Noten (Synthesia-Videos)');
  const b = html.indexOf('// --- MIDI writer');
  if (a < 0 || b < 0) throw new Error('Marken nicht gefunden');
  let code = html.slice(a, b);
  // zweites Stück: Tastatursuche wie am Handy (tryKeyboard, restColors, cropBars) – für das Nachspielen mit der AKTUELLEN Tastaturerkennung
  const c = html.indexOf('// a row well above the keyboard where only the falling bars are'), d = html.indexOf('// "blocked" = practically no bright pixel');
  const has2 = c > 0 && d > c; if (has2) code += '\n' + html.slice(c, d);
  const win = Object.assign({}, flags || {});
  if (typeof globalThis.ImageData === 'undefined') globalThis.ImageData = class { constructor(w, h) { this.width = w; this.height = h; this.data = new Uint8ClampedArray(w * h * 4); } };
  const fn = new Function('window', 'scanRows', 'scanDet', 'scanFrames', 'ytp', 'toast', 'performance',
    code + '\n;return {SCAN,scanCore,finishScan,finishCore,rgb2hsv,lum,laneBars,detectKeys,findKeyboardRows,keyLayout,hueDist' + (has2 ? ',tryKeyboard,restColors,cropBars,KB_RES_MAX' : '') + '};');
  const api = fn(win, {yA: 0.8, yB: 0.92}, null, null, null, () => {}, {now: () => Date.now()});
  api.window = win; return api;
}
function loadKtd(path) {
  let raw = fs.readFileSync(path);
  if (raw.slice(0, 7).toString() === 'KTDIAG1') raw = Buffer.from(raw.slice(raw.indexOf(10) + 1).toString().trim(), 'base64');
  if (raw[0] === 0x1f && raw[1] === 0x8b) raw = zlib.gunzipSync(raw, {maxOutputLength: 2 ** 31 - 1});
  if (raw.slice(0, 4).toString() !== 'KTD1') throw new Error('keine Diagnose-Datei');
  const hl = raw.readUInt32LE(4), meta = JSON.parse(raw.slice(8, 8 + hl).toString('utf8'));
  const fsz = 32 + meta.w * meta.n * 3, frames = [];
  for (let p = 8 + hl; p + fsz <= raw.length; p += fsz) {
    const f = raw.readDoubleLE(p + 16);
    frames.push({t: raw.readDoubleLE(p), vt: raw.readDoubleLE(p + 8), f, st: raw.readDoubleLE(p + 24), o: p + 32});
  }
  return {meta, frames, raw};
}
// Tastatur mit der Erkennung der App-Datei neu aus dem Fundbild bestimmen (wie am Handy: tryKeyboard → keyLayout → restColors mit Fundbild + letzten 5 Suchbildern).
// Die Ruhefarben werden an den AUFGENOMMENEN Zeilen gelesen (die Pixelzeilen der Aufnahme liegen dort).
function relayout(api, rec, dir) {
  if (!api.tryKeyboard || !fs.existsSync(dir + '/raw/index.json')) return null;
  const idx = JSON.parse(fs.readFileSync(dir + '/raw/index.json', 'utf8')), imgs = {};
  for (const it of idx) { const im = new ImageData(it.w, it.h); im.data.set(fs.readFileSync(`${dir}/raw/${it.name}.rgba`)); im.t = it.t; imgs[it.name] = im; }
  if (!imgs.still) return null;
  const t = api.tryKeyboard(imgs.still); if (!t || !t.det || t.n > 87 || t.det.res > api.KB_RES_MAX) return null;
  const keys = api.keyLayout(t.det, 0); if (!keys.length) return null;
  const rows = rec.meta.scanRows || t.rows, fr = idx.filter(i => i.name !== 'still').map(i => imgs[i.name]);
  api.restColors(keys, [imgs.still, ...fr.slice(-5)], rows);
  return {keys, kw: t.det.w / t.det.W, rowsNew: t.rows, n: keys.length, res: t.det.res};
}
function replay(api, rec, opt) {
  opt = opt || {};
  const {SCAN, scanCore, finishScan} = api, M = rec.meta, w = M.w, raw = rec.raw;
  if (opt.layout) { M.keys = opt.layout.keys; M.kw = opt.layout.kw; }
  const keys = M.keys.map(k => ({...k}));
  Object.assign(SCAN, {oddR: [], normF: 0, gapMin: null, lrow: null, fi: 0, laneGap: null, laneBg: null, laneBgN: null, wov: null, keyPx: null, barDelay: null, kw: M.kw, fromFile: true, hole: false, lastF: null, on: true, keys, rest: null, state: null, lane: null, events: [], frames: 0, vtMap: [], lastVt: 0, scene: 0, cut: null, okF: 0, okT: null, oneColor: false, start: M.start || 0,
    stab: null, recal: 0, recalK: null, octV: null, dbg: null, laneBgc: null, sceneT: null, okS: null, adopted: null, preGhost: null, dbgZones: null, dbgChordAdd: null, dbgChordFix: null, dbgPreAdd: null, dK: null, handFix: null, firstNote: null, _zbg: null});
  if (opt.reset) opt.reset(SCAN);
  for (const fr of rec.frames) {
    if (Number.isNaN(fr.f)) continue; if (!SCAN.on) break;
    const o = fr.o;
    scanCore((r, x) => { const i = o + (r * w + x) * 3; return [raw[i], raw[i + 1], raw[i + 2]]; }, w, M.n, fr.f);
  }
  SCAN.on = false;
  const notes = finishScan();
  return notes.map(n => [n.m, n.start, n.dur, n.hand]);
}
module.exports = {loadApp, loadKtd, replay, relayout};
if (require.main === module) {
  const a = process.argv.slice(2), flags = {}; let dbg = null, lay = null;
  for (let i = a.length - 1; i >= 0; i--) { if (a[i] === '--set') { const [k, v] = a[i + 1].split('='); flags[k] = JSON.parse(v); a.splice(i, 2); } else if (a[i] === '--dbg') { dbg = a[i + 1]; a.splice(i, 2); } else if (a[i] === '--relayout') { lay = a[i + 1]; a.splice(i, 2); } }
  const api = loadApp(a[0], flags), rec = loadKtd(a[1]);
  const oldN = rec.meta.keys.length, L = lay ? relayout(api, rec, lay) : null;
  const t0 = Date.now(), notes = replay(api, rec, {layout: L});
  const out = {notes, barDelay: api.SCAN.barDelay, okT: api.SCAN.okT, start: api.SCAN.start, firstNote: api.SCAN.firstNote, frames: rec.frames.length, ms: Date.now() - t0, keysOld: oldN, keysNew: L ? L.n : null, kbRes: L ? L.res : null, keyLo: api.SCAN.keys[0].m};
  if (dbg) out.dbg = (new Function('SCAN', 'api', 'return (' + dbg + ')'))(api.SCAN, api);
  fs.writeFileSync(a[2], JSON.stringify(out));
}
