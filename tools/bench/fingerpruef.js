// Prüfstand Fingersatz (v5.68): misst über ALLE Songs, ob der Fingersatz zum Auswendiglernen taugt.
// Rangfolge der Regeln: spielbar → gleich → fest → bequem.
// Songs: fixtures/finger_handy.json (neuester Handy-Scan je Video, genau das, was die App bekommt; lokal erzeugt mit fingerhandy.py),
//        fixtures/echte_songs.json, refs/echt/*.mid (Kanal-MIDIs, volle Arrangements).
// Aufruf: node tools/bench/fingerpruef.js [--stabil] [--nur handy|midi|echt] [--song TEIL] [--detail] [--json DATEI] [--ziel]
//   --stabil : zusätzlich Zeit-Rauschen / fehlender Ton / halber Song (dauert länger)
//   --ziel   : Ende mit Fehler, wenn die Ziele aus dem Bauplan nicht erreicht sind
'use strict';
const fs = require('fs'), path = require('path');
const F = require('../fingering/fingering.js');
const A = process.argv.slice(2), has = k => A.includes(k), val = k => (A.includes(k) ? A[A.indexOf(k) + 1] : null);
const P = F.PROFILES.meine, STIL = 'einfach';

function parseMidi(buf) {
  let p = 0; const r32 = () => { const v = buf.readUInt32BE(p); p += 4; return v; }, r16 = () => { const v = buf.readUInt16BE(p); p += 2; return v; };
  p = 4; r32(); r16(); const ntr = r16(), div = r16(); const tracks = [], tempos = [];
  for (let t = 0; t < ntr; t++) {
    p += 4; const len = r32(), end = p + len; let tick = 0, run = 0; const ev = [];
    while (p < end) {
      let d = 0, b; do { b = buf[p++]; d = (d << 7) | (b & 127); } while (b & 128); tick += d;
      let st = buf[p]; if (st & 128) { p++; if (st < 0xF0) run = st; } else st = run;
      if (st === 0xFF) { const ty = buf[p++]; let l = 0; do { b = buf[p++]; l = (l << 7) | (b & 127); } while (b & 128); if (ty === 0x51) tempos.push([tick, (buf[p] << 16) | (buf[p + 1] << 8) | buf[p + 2]]); p += l; }
      else if (st === 0xF0 || st === 0xF7) { let l = 0; do { b = buf[p++]; l = (l << 7) | (b & 127); } while (b & 128); p += l; }
      else { const hi = st & 0xF0; if (hi === 0xC0 || hi === 0xD0) p++; else { const a = buf[p++], v = buf[p++]; if (hi === 0x90 && v > 0) ev.push([tick, a, 1]); else if (hi === 0x80 || hi === 0x90) ev.push([tick, a, 0]); } }
    }
    p = end; tracks.push(ev);
  }
  tempos.sort((a, b) => a[0] - b[0]); if (!tempos.length || tempos[0][0] > 0) tempos.unshift([0, 500000]);
  const sec = tk => { let s = 0, last = 0, us = 500000; for (const [t, u] of tempos) { if (t >= tk) break; s += (t - last) * us / div / 1e6; last = t; us = u; } return s + (tk - last) * us / div / 1e6; };
  const out = []; tracks.forEach((ev, ti) => { const on = {}; for (const [t, m, o] of ev) { if (o) on[m] = t; else if (on[m] != null) { out.push({ midi: m, start: sec(on[m]), dur: Math.max(0.03, sec(t) - sec(on[m])), tr: ti }); delete on[m]; } } });
  return out.sort((a, b) => a.start - b.start || a.midi - b.midi);
}
// Hände wie in der App (fingSong): einfarbig und weiter als 14 Halbtöne → Hand-Zuordnung des Moduls
function appHands(ns) {
  const one = ns.every(n => n.hand === ns[0].hand), lo = Math.min(...ns.map(n => n.midi)), hi = Math.max(...ns.map(n => n.midi));
  if (one && hi - lo > 14) { const h = F.assignHands(ns.map(n => ({ midi: n.midi, start: n.start, dur: n.dur }))); ns.forEach((n, i) => { n.hand = h[i]; }); }
}
function loadSongs() {
  const songs = [], B = __dirname;
  const hp = path.join(B, 'fixtures', 'finger_handy.json');   // lokal, aus dem privaten Diagnose-Archiv: python3 tools/bench/fingerhandy.py
  if (!fs.existsSync(hp)) console.log('HINWEIS: fixtures/finger_handy.json fehlt (python3 tools/bench/fingerhandy.py) – es laufen nur Fly Me, Für Elise und die Kanal-MIDIs.');
  const H = fs.existsSync(hp) ? JSON.parse(fs.readFileSync(hp)) : {};
  for (const [k, v] of Object.entries(H)) { const ns = v.notes.map(x => ({ midi: x[0], start: x[1], dur: x[2], hand: x[3] === 'L' ? 'L' : 'R' })); appHands(ns); songs.push({ name: 'handy:' + k, set: 'handy', notes: ns }); }
  const E = JSON.parse(fs.readFileSync(path.join(B, 'fixtures', 'echte_songs.json')));
  for (const k of ['fly_me', 'fuer_elise']) { const ns = E[k].map(x => ({ midi: x[0], start: x[1], dur: x[2], hand: x[3] === 'L' ? 'L' : 'R' })); appHands(ns); songs.push({ name: 'echt:' + k, set: 'echt', notes: ns }); }
  const dir = path.join(B, 'refs', 'echt');
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.mid')).sort()) {
    const ns = parseMidi(fs.readFileSync(path.join(dir, f))), trs = [...new Set(ns.map(n => n.tr))];
    if (trs.length === 2) { const mean = t => { const a = ns.filter(n => n.tr === t); return a.reduce((s, n) => s + n.midi, 0) / a.length; }; const hiT = mean(trs[0]) > mean(trs[1]) ? trs[0] : trs[1]; ns.forEach(n => { n.hand = n.tr === hiT ? 'R' : 'L'; }); }
    else { ns.forEach(n => { n.hand = 'R'; }); appHands(ns); }
    songs.push({ name: 'midi:' + f.replace('.mid', ''), set: 'midi', notes: ns });
  }
  return songs;
}
// Griffe unabhängig vom Modul bilden (gleichzeitig = Anschläge höchstens 50 ms auseinander)
function grips(ns) {
  const G = []; let i = 0;
  while (i < ns.length) { let j = i; const g = []; while (j < ns.length && ns[j].start - ns[i].start <= 0.05) { if (!g.some(q => ns[q].midi === ns[j].midi)) g.push(j); j++; } g.sort((a, b) => ns[a].midi - ns[b].midi); G.push(g); i = j; }
  return G;
}
const W = 4, W_LANG = 8;   // 4 = streng (auch kurze Bruchstücke), 8 = „dieselbe Stelle“ (ab hier setzt das Modul die Marke 'anders')
// gleich: gleiche Folge von 4 Griffen (nur Tonhöhen) → gleiche Finger? Abweichung = Vorkommen, die nicht den häufigsten Fingersatz haben.
function gleich(ns, G, f, mark, W_) {
  const W = W_ || 4;
  const key = g => g.map(i => ns[i].midi).join('.'), fk = g => g.map(i => f[i]).join('');
  const seq = {}; for (let i = 0; i + W <= G.length; i++) { const k = G.slice(i, i + W).map(key).join('|'); (seq[k] = seq[k] || []).push(i); }
  let sq = 0, bad = 0, badUnmarked = 0;
  for (const k in seq) {
    const L = seq[k]; if (L.length < 2) continue; const c = {}; const fs_ = L.map(i => G.slice(i, i + W).map(fk).join('|')); fs_.forEach(x => { c[x] = (c[x] || 0) + 1; });
    const top = Object.keys(c).sort((a, b) => c[b] - c[a])[0]; sq += L.length;
    L.forEach((i, q) => { if (fs_[q] === top) return; bad++; if (!mark || !G.slice(i, i + W).some(g => g.some(n => mark[n]))) badUnmarked++; });
  }
  const by = {}; for (const g of G) { if (g.length < 2) continue; (by[key(g)] = by[key(g)] || new Set()).add(fk(g)); }
  let kinds = 0, multi = 0; for (const k in by) { kinds++; if (by[k].size > 1) multi++; }
  return { sq, bad, badUnmarked, kinds, multi };
}
const MEHR = val('--mehr');
function run(ns, hand, extra) { return F.computeHand(ns, Object.assign({ hand, profile: P, style: STIL }, MEHR == null ? {} : { gleichMehr: +MEHR }, has('--ohnegleich') ? { gleich: false } : {}, extra || {})); }
let seed = 7; const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };

function main() {
  let songs = loadSongs();
  if (val('--nur')) songs = songs.filter(s => s.set === val('--nur'));
  if (val('--song')) songs = songs.filter(s => s.name.includes(val('--song')));
  const T = {}, add = (k, v) => { T[k] = (T[k] || 0) + v; }, rows = [], per = {};
  const t0 = Date.now();
  for (const s of songs) for (const hand of ['R', 'L']) {
    const ns = s.notes.filter(n => n.hand === hand).map(n => ({ midi: n.midi, start: n.start, dur: n.dur })); if (ns.length < 8) continue;
    add('stimmen', 1); add('toene', ns.length);
    let r; try { r = run(ns, hand); } catch (e) { add('abbruch', 1); rows.push(`${s.name} ${hand}: ABBRUCH ${e.message}`); (per[s.name] = per[s.name] || {})[hand] = { abbruch: true }; continue; }
    const G = grips(ns), un = new Set(F.unavoidableHand(ns, P, hand));
    const viol = r.violations.filter(x => !un.has(x.index)).length;
    add('unmoeglichOhneMarke', r.violations.filter(x => !un.has(x.index) && !(r.mark && r.mark[x.index])).length);
    const mark = r.mark || null, anders = mark ? mark.filter(x => x === 'anders').length : 0, ehrlich = mark ? mark.filter(x => x && x !== 'anders').length : 0;
    const g = gleich(ns, G, r.fingers, mark && mark.map(x => !!x)), g8 = gleich(ns, G, r.fingers, mark && mark.map(x => !!x), W_LANG);
    add('lang', g8.sq); add('langAnders', g8.bad); add('langAndersOhneMarke', g8.badUnmarked);
    const ohneFinger = r.fingers.filter((x, i) => !(x >= 1 && x <= 5) && !(mark && mark[i])).length;
    add('griffe', G.length); add('unmoeglich', viol); add('eingabeUngreifbar', un.size); add('zuWeit', r.rolled.length); add('folgen', g.sq); add('folgenAnders', g.bad); add('folgenAndersOhneMarke', g.badUnmarked);
    add('akkArten', g.kinds); add('akkMehrdeutig', g.multi); add('markeAnders', anders); add('markeEhrlich', ehrlich); add('ohneFinger', ohneFinger);
    add('ausnahme', r.status.filter(x => x === 'ausnahme').length); add('offen', r.open.filter(Boolean).length);
    if (g.bad) add('stimmenMitFolgenAnders', 1);
    (per[s.name] = per[s.name] || {})[hand] = { toene: ns.length, unmoeglich: viol, folgen: g.sq, folgenAnders: g.bad, lang: g8.sq, langAnders: g8.bad, akkMehrdeutig: g.multi, anders };
    rows.push(`${(s.name + ' ' + hand).padEnd(46)} ${String(ns.length).padStart(5)} Töne | unmöglich ${viol} | Folgen anders ${g.bad}/${g.sq} (ohne Marke ${g.badUnmarked}) | Akkord mehrdeutig ${g.multi}/${g.kinds} | „hier anders“ ${anders}`);
    if (has('--stabil') && ns.length >= 30 && ns.length <= 1500) {
      const base = r.fingers, cmp = (f, map) => { let c = 0; f.forEach((x, i) => { if (x !== base[map ? map(i) : i]) c++; }); return c; };
      const st = (k, c, n) => { add(k + 'Anders', c); add(k + 'Toene', n); add(k + 'Stimmen', 1); if (c) add(k + 'Betroffen', 1); };
      { const j = ns.map(n => ({ ...n })); let i = 0; while (i < j.length) { let k = i; const d = (rnd() - 0.5) * 0.05; while (k < j.length && ns[k].start - ns[i].start <= 0.03) { j[k].start = Math.max(0, ns[k].start + d); j[k].dur = ns[k].dur * (0.85 + rnd() * 0.3); k++; } i = k; }
        try { st('rauschen', cmp(run(j, hand).fingers), ns.length); } catch (e) { add('stabilAbbruch', 1); } }
      { const m = Math.floor(ns.length / 2), j = ns.filter((n, i) => i !== m); try { st('tonFehlt', cmp(run(j, hand).fingers, i => (i < m ? i : i + 1)), j.length); } catch (e) { add('stabilAbbruch', 1); } }
      { const h = Math.floor(ns.length / 2); try { st('halb', cmp(run(ns.slice(0, h), hand).fingers), h); } catch (e) { add('stabilAbbruch', 1); } }
    }
  }
  if (has('--detail')) rows.forEach(r => console.log(r)); else rows.filter(r => r.includes('ABBRUCH')).forEach(r => console.log(r));
  const pc = (a, b) => (b ? (100 * a / b).toFixed(2) + ' %' : '–');
  const Z = k => T[k] || 0;
  console.log(`\n${songs.length} Songs, ${Z('stimmen')} Hand-Stimmen, ${Z('toene')} Töne, ${Z('griffe')} Griffe | Modul ${F.VERSION} | ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  console.log(`Abbrüche:                                ${Z('abbruch')}`);
  console.log(`unmögliche Griffe (vom Fingersatz):      ${Z('unmoeglich')}`);
  console.log(`  davon ohne Marke:                      ${Z('unmoeglichOhneMarke')}`);
  console.log(`Töne ohne Finger und ohne Marke:         ${Z('ohneFinger')}`);
  console.log(`gleiche Folge (4 Griffe), andere Finger:  ${Z('folgenAnders')} / ${Z('folgen')} = ${pc(Z('folgenAnders'), Z('folgen'))}  (in ${Z('stimmenMitFolgenAnders')} Stimmen)`);
  console.log(`  davon ohne Marke:                      ${Z('folgenAndersOhneMarke')}`);
  console.log(`gleiche Stelle (8 Griffe), andere Finger: ${Z('langAnders')} / ${Z('lang')} = ${pc(Z('langAnders'), Z('lang'))}`);
  console.log(`  davon ohne Marke:                      ${Z('langAndersOhneMarke')}`);
  console.log(`Akkord-Arten mit mehreren Griffen:       ${Z('akkMehrdeutig')} / ${Z('akkArten')}`);
  console.log(`Marke „hier anders“:                     ${Z('markeAnders')} Töne = ${pc(Z('markeAnders'), Z('toene'))}`);
  console.log(`Marke springen/brechen/zu viel:          ${Z('markeEhrlich')} Töne`);
  console.log(`(alt) Status „nur hier“:                 ${Z('ausnahme')} Töne = ${pc(Z('ausnahme'), Z('toene'))} | offen ${Z('offen')}`);
  console.log(`Eingabe selbst ungreifbar:               ${Z('eingabeUngreifbar')} Stellen, ${Z('zuWeit')} Griffe zu weit`);
  if (has('--stabil')) for (const [k, n] of [['rauschen', 'Zeit-Rauschen (±25 ms, Länge ±15 %)'], ['tonFehlt', 'ein Ton fehlt'], ['halb', 'nur erste Hälfte']])
    console.log(`Stabil – ${n.padEnd(36)} ${Z(k + 'Anders')} / ${Z(k + 'Toene')} = ${pc(Z(k + 'Anders'), Z(k + 'Toene'))}  (in ${Z(k + 'Betroffen')} von ${Z(k + 'Stimmen')} Stimmen)`);
  if (val('--json')) fs.writeFileSync(val('--json'), JSON.stringify({ modul: F.VERSION, songs: songs.length, summe: T, je: per }, null, 1));
  if (has('--ziel')) {
    const ok = Z('abbruch') === 0 && Z('unmoeglichOhneMarke') === 0 && Z('ohneFinger') === 0 && Z('langAndersOhneMarke') === 0;
    console.log(ok ? 'ZIEL erreicht (harte Ziele)' : 'ZIEL NICHT erreicht'); process.exitCode = ok ? 0 : 1;
  }
}
module.exports = { loadSongs, grips, gleich, parseMidi };
if (require.main === module) main();
