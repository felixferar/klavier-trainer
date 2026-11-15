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
// 1) "H A G F E(lang)" am Phrasenende: kein Übersetzen auf E (vorher 3-2-1-3), E mit dem Daumen
for (const i of find(['H', 'A', 'G', 'F', 'E', 'A'])) check(`Fly: H-A-G-F-E (lang) bei ${R[i].start.toFixed(1)} s`, r.fingers[i + 4] === 1 && r.fingers[i + 3] === 1, fs(i, 5));
// 2) "A G F E D E F A" (2. Phrase) in einer Handlage, ohne Versetzen
for (const i of find(['A', 'G', 'F', 'E', 'D', 'E', 'F', 'A'])) check(`Fly: A-G-F-E-D-E-F-A bei ${R[i].start.toFixed(1)} s`, fs(i, 8) === '54321235', fs(i, 8));
// 3) "C D F F" (vorher 2-3-1-1, Daumen untergesetzt): aufwärts ohne Untersetzen
for (const i of find(['C', 'D', 'F', 'F', 'A'])) { const f = r.fingers.slice(i, i + 3); check(`Fly: C-D-F bei ${R[i].start.toFixed(1)} s`, f[0] < f[1] && f[1] < f[2], fs(i, 4)); }
check('Fly: spielbar (beide Stile)', !r.violations.length && !F.computeHand(R, { hand: 'R' }).violations.length);
console.log(`\n${ok} OK, ${bad} fehlgeschlagen`);
process.exitCode = bad ? 1 : 0;
