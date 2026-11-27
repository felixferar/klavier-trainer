// Hand-Simulation über alle Songs des Prüfstands. Aufruf: node tools/handsim/lauf.js [--daten DATEI.json  (Sing + Fly Me für die Ansicht)]
'use strict';
const fs = require('fs'), path = require('path');
const F = require('../fingering/fingering.js'), S = require('./kern.js'), { loadSongs } = require('../bench/fingerpruef.js');
const A = process.argv.slice(2), P = F.PROFILES.meine;
function finger(song) { const out = [];
  for (const H of ['L', 'R']) { const ns = song.notes.filter(n => n.hand === H); if (!ns.length) continue;
    const r = F.computeHand(ns.map(n => ({ midi: n.midi, start: n.start, dur: n.dur })), { hand: H, profile: P, style: 'einfach' });
    ns.forEach((n, i) => out.push({ midi: n.midi, start: +n.start.toFixed(3), dur: +n.dur.toFixed(3), hand: H, fing: r.fingers[i] || 0, mark: r.mark[i] || '' })); }
  return out.sort((a, b) => a.start - b.start || a.midi - b.midi); }
const songs = loadSongs(), rows = [], T = {};
for (const s of songs) { const ns = finger(s), sim = S.simSong(ns), dur = Math.max(...ns.map(n => n.start + n.dur)) - Math.min(...ns.map(n => n.start));
  const r = { name: s.name, set: s.set, min: dur / 60 };
  for (const H of ['L', 'R']) if (sim[H]) { r[H] = sim[H].st; for (const k in sim[H].st) T[k] = (T[k] || 0) + sim[H].st[k]; }
  rows.push(r); }
const fmt = st => st ? `Lagen ${String(st.lagen).padStart(4)} Sprünge ${String(st.spruenge).padStart(4)} eng ${String(st.eng).padStart(3)} weit ${String(st.weit).padStart(3)} zu weit ${String(st.zuWeit).padStart(3)} Weg ${(st.wegCm / 100).toFixed(1).padStart(5)} m` : '–';
if (A.includes('--detail')) rows.forEach(r => console.log(r.name.padEnd(40), 'R:', fmt(r.R), '| L:', fmt(r.L)));
for (const id of ['RgMoK2SUEyw', 'Wa8fAoJmjQA']) { const r = rows.find(x => x.name.includes(id)); if (r) console.log(r.name.padEnd(20), 'R:', fmt(r.R), '| L:', fmt(r.L)); }
console.log(`\n${rows.length} Songs: Griffe ${T.griffe}, Hand versetzt ${T.lagen} (${(100 * T.lagen / T.griffe).toFixed(1)} %), Sprünge ${T.spruenge}, davon zu eng in der Zeit ${T.eng}, weite Griffe ${T.weit}, zu weite Griffe ${T.zuWeit}, Daumen auf Schwarz ${T.daumenSchwarz}`);
const hard = rows.map(r => ({ n: r.name, e: ((r.R ? r.R.eng + r.R.zuWeit : 0) + (r.L ? r.L.eng + r.L.zuWeit : 0)), g: (r.R ? r.R.griffe : 0) + (r.L ? r.L.griffe : 0) }));
const clean = hard.filter(x => x.e === 0).length; console.log(`Songs ohne eine einzige harte Stelle (zu eng oder zu weit): ${clean} von ${rows.length}`);
if (A.includes('--daten')) { const out = {}; for (const [id, title] of [['RgMoK2SUEyw', "Sing – I'm Still Standing"], ['Wa8fAoJmjQA', 'Fly Me to the Moon']]) { const s = songs.find(x => x.name === 'handy:' + id); if (s) out[id] = { title, notes: finger(s).map(n => [n.midi, n.start, n.dur, n.hand, n.fing, n.mark]) }; }
  fs.writeFileSync(A[A.indexOf('--daten') + 1], JSON.stringify(out)); }
