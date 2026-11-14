// 10 schwierige Stellen für den unabhängigen Prüfer
'use strict';
const fs = require('fs'), path = require('path');
const F = require('../fingering.js');
const datei = require('./daten.js');
const D = path.join(__dirname, 'daten');
const N = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'As', 'A', 'B', 'H'];
const nm = m => N[m % 12] + (Math.floor(m / 12) - 1);
const seq = (midis, durs) => { let t = 0; return midis.map((m, i) => { const d = Array.isArray(durs) ? durs[i % durs.length] : durs; const x = { midi: m, start: t, dur: d * 0.9 }; t += d; return x; }); };
const song = (file, isRec) => { const r = JSON.parse(fs.readFileSync(datei(file))); return F.toMelody(isRec ? r.events.filter(e => e[0] >= 60).map(e => ({ midi: e[0], start: e[1], dur: Math.max(0.02, e[2] - e[1]) })) : r.filter(x => x[3] === 'R').map(x => ({ midi: x[0], start: x[1], dur: x[2] }))); };
const cut = (notes, a, b) => { const s = notes.slice(a, b), t0 = s[0].start; return s.map(x => ({ midi: x.midi, start: +(x.start - t0).toFixed(3), dur: +x.dur.toFixed(3) })); };
const wake = song('aufnahmen/16-04-51_41Z7W_0dJu8_done.json', true), gund = song('aufnahmen/14-49-51_GUnDodr9GLo_done.json', true), golden = song('aufnahmen/14-21-25_D4COOEBwBjk_done.json', true), embers = song('embers-notes.json', false);
const STELLEN = [
  ['Sprünge (Oktaven, Sexten)', seq([60, 72, 67, 64, 76, 72, 79, 67, 60, 69, 65, 77], [0.4, 0.4, 0.2, 0.2])],
  ['Akkordbrechung Des-Dur schnell', seq([61, 65, 68, 73, 77, 80, 85, 80, 77, 73, 68, 65], 0.14)],
  ['Schnelle Tonwiederholung + Sprung', seq([64, 64, 64, 64, 67, 67, 67, 67, 72, 72, 71, 71, 69, 69, 67, 67], 0.12)],
  ['Pentatonik schwarze Tasten', seq([66, 68, 70, 73, 75, 78, 75, 73, 70, 68, 66, 63, 61, 63, 66], 0.18)],
  ['Chromatik auf und ab', seq([60, 61, 62, 63, 64, 65, 66, 67, 68, 67, 66, 65, 64, 63, 62, 61, 60], 0.13)],
  ['Wechselsprünge schnell', seq([60, 74, 62, 76, 64, 77, 65, 79, 67, 81], 0.12)],
  ['Wake Me Up (Ausschnitt)', cut(wake, 60, 78)],
  ['GUnDodr9GLo (Ausschnitt)', cut(gund, 0, 14)],
  ['golden hour (Ausschnitt)', cut(golden, 40, 56)],
  ['Embers (Ausschnitt)', cut(embers, 40, 56)],
];
const txt = STELLEN.map(([name, notes], k) => {
  const rows = notes.map((x, i) => { const next = notes[i + 1]; const gap = next ? (next.start - x.start).toFixed(2) + ' s bis zum nächsten Ton' : 'letzter Ton'; const held = next && x.start + x.dur - next.start > 0.15 && x.start + x.dur - next.start > 0.5 * (next.start - x.start) ? ', klingt beim nächsten Ton noch (gehalten)' : ''; return `${i + 1}. ${nm(x.midi)} (${gap}${held})`; });
  return `Stelle ${k + 1}: ${name}\n` + rows.join('\n');
}).join('\n\n');
module.exports = { STELLEN, txt, nm };
if (require.main === module) {
  console.log(txt);
  const mine = STELLEN.map(([name, notes]) => { const r = F.computeFingering(notes); return { name, fingers: r.fingers, open: r.open, alt: r.alt, viol: r.violations.length, explain: notes.map((_, i) => r.explain(i)) }; });
  fs.writeFileSync(path.join(__dirname, 'stellen-app.json'), JSON.stringify(mine, null, 1));
  mine.forEach((m, k) => console.error(`App Stelle ${k + 1}: ${m.fingers.join(' ')}  offen: ${m.open.map((o, i) => o ? (i + 1) + '→' + m.alt[i] : '').filter(Boolean).join(' ') || '–'}  Verstöße ${m.viol}`));
}
