// Akkorde: Grundfälle, Folgen, gehaltene Töne, zu weite Griffe, schnelle Wechsel, gleiche Akkorde.
// Aufruf: node test/t-akkorde.js
'use strict';
const F = require('../fingering.js');
let ok = 0, bad = 0;
const check = (name, cond, info) => { if (cond) ok++; else bad++; console.log(`${cond ? 'OK  ' : 'FEHL'} ${name}${info ? ' – ' + info : ''}`); };
// Hilfen: Folge von Griffen [[midis], dauer]; liefert Noten + Finger je Griff (tief→hoch)
function seq(items, gap = 0) {
  let t = 0; const notes = [];
  for (const [ms, d] of items) { for (const m of [].concat(ms)) notes.push({ midi: m, start: t, dur: d * 0.95 }); t += d + gap; }
  return notes;
}
function grips(notes, r) {
  const by = new Map();
  notes.forEach((n, i) => { const k = n.start.toFixed(3); if (!by.has(k)) by.set(k, []); by.get(k).push([n.midi, r.fingers[i]]); });
  return [...by.values()].map(g => g.sort((a, b) => a[0] - b[0]).map(x => x[1]).join(''));
}
const run = (items, hand, opts = {}) => { const notes = seq(items); const r = F.computeHand(notes, Object.assign({ hand }, opts)); return { notes, r, g: grips(notes, r) }; };
const any = (got, list) => list.split('|').includes(got);

// 1) Dreiklänge Grundstellung, alle 24, beide Hände: 1-3-5 rechts / 5-3-1 links (tief→hoch)
for (const hand of ['R', 'L']) {
  let good = 0; const dev = [];
  for (let t = 0; t < 12; t++) for (const third of [4, 3]) {
    const root = (hand === 'R' ? 60 : 48) + t, { g, r } = run([[[root, root + third, root + 7], 1]], hand);
    if (g[0] === (hand === 'R' ? '135' : '531') && !r.violations.length) good++; else dev.push(`${t}/${third}:${g[0]}`);
  }
  check(`Dreiklänge Grundstellung ${hand} (24)`, good === 24, dev.join(' '));
}
// 2) Umkehrungen + Vierklänge
check('1. Umkehrung R E-G-C = 125', run([[[64, 67, 72], 1]], 'R').g[0] === '125');
check('2. Umkehrung R G-C-E = 135', run([[[67, 72, 76], 1]], 'R').g[0] === '135');
check('1. Umkehrung L E-G-C = 531', run([[[52, 55, 60], 1]], 'L').g[0] === '531');
check('2. Umkehrung L G-C-E = 521', run([[[43, 48, 52], 1]], 'L').g[0] === '521');
check('Vierklang R C-E-G-C = 1235|1245', any(run([[[60, 64, 67, 72], 1]], 'R').g[0], '1235|1245'), run([[[60, 64, 67, 72], 1]], 'R').g[0]);
check('Vierklang L C-E-G-C = 5321|5421', any(run([[[48, 52, 55, 60], 1]], 'L').g[0], '5321|5421'), run([[[48, 52, 55, 60], 1]], 'L').g[0]);
check('Septakkord R G-H-D-F = 1235', run([[[67, 71, 74, 77], 1]], 'R').g[0] === '1235', run([[[67, 71, 74, 77], 1]], 'R').g[0]);
// 3) Kadenz eng: C-E-G, C-F-A, H-D-G, C-E-G (rechts) – Daumen bleibt unten, 0 Verstöße
{
  const { g, r } = run([[[60, 64, 67], 1], [[60, 65, 69], 1], [[59, 62, 67], 1], [[60, 64, 67], 1]], 'R');
  check('Kadenz eng rechts', g[0] === '135' && any(g[1], '135|125|124') && any(g[2], '125|124|135') && g[3] === '135' && !r.violations.length, g.join(' '));
}
{ // links: C3-E3-G3 / C3-F3-A3 / H2-D3-G3 / C3-E3-G3
  const { g, r } = run([[[48, 52, 55], 1], [[48, 53, 57], 1], [[47, 50, 55], 1], [[48, 52, 55], 1]], 'L');
  check('Kadenz eng links', g[0] === '531' && any(g[1], '521|531') && any(g[2], '531|521|421') && g[3] === '531' && !r.violations.length, g.join(' '));
}
// 4) Gehaltener Basston links + Begleitung: C3 (ganze Note) dazu G3 E3 G3
{
  const notes = [{ midi: 48, start: 0, dur: 1.9 }, { midi: 55, start: 0.5, dur: 0.45 }, { midi: 52, start: 1.0, dur: 0.45 }, { midi: 55, start: 1.5, dur: 0.45 }];
  const r = F.computeHand(notes, { hand: 'L' });
  check('gehaltener Bass links 5 + 1-3-1|1-2-1', r.fingers[0] === 5 && any(r.fingers.slice(1).join(''), '131|121') && !r.violations.length, r.fingers.join(''));
}
// 5) Zu weit: Dezime C4–E5 für die kleine Hand → gebrochen gemeldet, kein Absturz
{
  const { r } = run([[[60, 76], 1]], 'R', { profile: F.PROFILES.klein });
  check('Dezime kleine Hand → "brechen"', r.rolled.length === 1 && F.unavoidableHand(seq([[[60, 76], 1]]), F.PROFILES.klein, 'R').length === 1, r.explain(0));
  const r2 = run([[[60, 76], 1]], 'R').r;
  check('Dezime deine Hand (max 14) → auch zu weit', r2.rolled.length === 1);
  const r3 = run([[[60, 74], 1]], 'R').r;
  check('None C4–D5 deine Hand → greifbar (1-5)', r3.rolled.length === 0 && r3.fingers.join('') === '15', r3.fingers.join(''));
}
// 6) Schneller Griffwechsel: C-E-G → D-F-A in 0,08 s ist mit keinem Griff machbar → als unvermeidbar gemeldet
{
  const notes = seq([[[60, 64, 67], 0.08], [[62, 65, 69], 0.5]]);
  const un = F.unavoidableHand(notes, F.PROFILES.meine, 'R');
  check('Akkordwechsel 0,08 s → unvermeidbar gemeldet', un.length === 1);
  const notes2 = seq([[[60, 64, 67], 0.3], [[62, 65, 69], 0.5]]);
  const r = F.computeHand(notes2, { hand: 'R' });
  check('Akkordwechsel 0,3 s → spielbar', !r.violations.length, grips(notes2, r).join(' '));
}
// 7) Gleiche Akkorde gleich gegriffen: C–G–a–F je mit Melodie dazwischen, 4×
{
  const prog = [[[60, 64, 67], 0.5], [69, 0.25], [67, 0.25], [[59, 62, 67], 0.5], [65, 0.25], [64, 0.25], [[60, 64, 69], 0.5], [72, 0.25], [71, 0.25], [[60, 65, 69], 0.5], [67, 0.25], [65, 0.25]];
  const items = [].concat(prog, prog, prog, prog);
  const { notes, r, g } = run(items, 'R');
  const byChord = {};
  items.forEach(([ms], k) => { if (Array.isArray(ms)) { const key = ms.join(','); (byChord[key] = byChord[key] || new Set()).add(g[k]); } });
  const allSame = Object.values(byChord).every(s => s.size === 1);
  check('gleiche Akkorde = gleicher Griff (4 Durchgänge)', allSame && !r.violations.length, Object.entries(byChord).map(([k, s]) => k + ':' + [...s].join('/')).join('  '));
}
// 8) Tonleiter vor und nach einem Akkord: Lehrbuch-Muster bleibt erhalten
{
  const items = [[60, 0.15], [62, 0.15], [64, 0.15], [65, 0.15], [67, 0.15], [69, 0.15], [71, 0.15], [72, 0.15], [[60, 64, 67], 0.6], [72, 0.15], [71, 0.15], [69, 0.15], [67, 0.15], [65, 0.15], [64, 0.15], [62, 0.15], [60, 0.15]];
  const { r, g } = run(items, 'R');
  check('C-Dur auf, Akkord, C-Dur ab: Muster + 0 Verstöße', r.patterns.length >= 2 && !r.violations.length && g.slice(0, 8).join('') === '12312345', g.join(' '));
}
// 9) Gebrochener Akkord (nacheinander) wie Arpeggio-Grundfall, gehalten mit Pedal-Überlappung
{
  const notes = [60, 64, 67, 72].map((m, i) => ({ midi: m, start: i * 0.25, dur: 1.2 - i * 0.25 }));
  const r = F.computeHand(notes, { hand: 'R' });
  check('gebrochen + gehalten C-E-G-C → 1-2-3-5', r.fingers.join('') === '1235' && !r.violations.length, r.fingers.join(''));
}
// 10) Deine Vorgabe in einem Akkord geht vor
{
  const notes = seq([[[60, 64, 67], 1]]);
  const r = F.computeHand(notes, { hand: 'R', fixed: { 2: 4 } });
  check('Vorgabe G mit 4 → 1-2-4|1-3-4', any(grips(notes, r)[0], '124|134') && r.status[2] === 'fest', grips(notes, r)[0]);
}
console.log(`\n${ok} OK, ${bad} fehlgeschlagen`);
process.exitCode = bad ? 1 : 0;
