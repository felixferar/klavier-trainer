// Stellen, die der Nutzer am Klavier mit ⚑ als komisch markiert hat – müssen im Stil "einfach" (App-Standard) natürlich sein.
// Aufruf: node test/t-flaggen.js
'use strict';
const F = require('../fingering.js');
let ok = 0, bad = 0;
const check = (name, cond, info) => { if (cond) ok++; else bad++; console.log(`${cond ? 'OK  ' : 'FEHL'} ${name}${info ? ' – ' + info : ''}`); };
const NN = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'As', 'A', 'B', 'H'];

// Fly Me To The Moon (EASY Piano Tutorial Wa8fAoJmjQA), ganze Umwandlung vom Handy, 15.11.2026, Flaggen bei 8,7/11,1/34/36,1/51,3/53,1 s
const m = require('./flaggen/fly-me-to-the-moon-ganz.json');
const R = m.notes.filter(x => x[3] === 'R').map(x => ({ midi: x[0], start: x[1], dur: x[2] }));
const find = names => { const out = []; for (let i = 0; i + names.length <= R.length; i++) if (names.every((nm, k) => NN[R[i + k].midi % 12] === nm)) out.push(i); return out; };
const r = F.computeHand(R, { hand: 'R', style: 'einfach' });
const fs = (i, L) => r.fingers.slice(i, i + L).join('');
// Flaggen v5.03 (8,7/11,1/34/36,1/51,3/53,1) und v5.04 (19,2/20,5/22,7/35,4/36,7), Stil einfach
// 1) "H A G F E(lang)" am Phrasenende: weder 3 über den Daumen auf E (v5.03) noch Daumen rutscht F→E (v5.04) – E mit 2 übersetzt
for (const i of find(['H', 'A', 'G', 'F', 'E', 'A'])) check(`Fly: H-A-G-F-E (lang) bei ${R[i].start.toFixed(1)} s`, r.fingers[i + 3] === 1 && r.fingers[i + 4] === 2, fs(i, 5));
// 2) "A G F E D E F A" (2. Phrase) in einer Handlage, ohne Versetzen
for (const i of find(['A', 'G', 'F', 'E', 'D', 'E', 'F', 'A'])) check(`Fly: A-G-F-E-D-E-F-A bei ${R[i].start.toFixed(1)} s`, fs(i, 8) === '54321235', fs(i, 8));
// 3) "C D F F A" (v5.03: 2-3-1-1 untergesetzt; v5.04: F4 F4 A4 – Finger 4 rutscht nach dem langen F auf A)
for (const i of find(['C', 'D', 'F', 'F', 'A'])) { const f = r.fingers.slice(i, i + 5); check(`Fly: C-D-F-F-A bei ${R[i].start.toFixed(1)} s`, f[0] < f[1] && f[1] < f[2] && f[3] !== f[4], fs(i, 5)); }
// 4) "As F E D C" (v5.04: D1→C1 Daumen rutscht)
for (const i of find(['As', 'F', 'E', 'D', 'C'])) { const f = r.fingers.slice(i, i + 5); check(`Fly: As-F-E-D-C bei ${R[i].start.toFixed(1)} s ohne Rutschen`, f.every((x, k) => k === 0 || x !== f[k - 1]), fs(i, 5)); }
// 5) im ganzen Song: kein Finger spielt zwei Nachbartasten (≤ 4 Halbtöne) direkt nacheinander
{ let bad = []; for (let i = 1; i < R.length; i++) { const d = Math.abs(R[i].midi - R[i - 1].midi); if (d > 0 && d <= 4 && r.fingers[i] === r.fingers[i - 1]) bad.push(NN[R[i - 1].midi % 12] + r.fingers[i - 1] + '→' + NN[R[i].midi % 12] + r.fingers[i] + '@' + R[i].start.toFixed(1)); }
  check('Fly: kein Rutschen mit demselben Finger im ganzen Song', !bad.length, bad.join(' ')); }
check('Fly: spielbar (beide Stile)', !r.violations.length && !F.computeHand(R, { hand: 'R' }).violations.length);
// 6) "Nur Orientierung": deutlich weniger Zahlen, und keine Zahl innerhalb einer ruhigen Handlage
{ const vis = r.cue.filter(Boolean).length; check('Fly: Orientierungs-Zahlen höchstens 35 % der Töne', vis <= 0.35 * R.length, `${vis}/${R.length}`);
  const i = find(['A', 'G', 'F', 'E', 'D', 'E', 'F', 'A'])[0]; check('Fly: in der Handlage A-G-F-E-D-E-F-A nur die erste Zahl (falls nötig)', r.cue.slice(i + 1, i + 8).every(c => !c), JSON.stringify(r.cue.slice(i, i + 8))); }
console.log(`\n${ok} OK, ${bad} fehlgeschlagen`);
process.exitCode = bad ? 1 : 0;
