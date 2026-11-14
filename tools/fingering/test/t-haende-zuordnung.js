// Hand-Zuordnung: gemessen an den 15 Testvideos mit bekannter Hand (kt-test-301…315).
// Vergleich: "ab C4 = rechts" (bisher) gegen assignHands.
'use strict';
const fs = require('fs'), path = require('path');
const F = require('../fingering.js');
const datei = require('./daten.js');
const D = path.join(__dirname, 'daten');
let n = 0, okNew = 0, okOld = 0; const rows = [];
for (let s = 301; s <= 315; s++) {
  const y = JSON.parse(fs.readFileSync(datei(s + '.json')));
  const notes = y.notes.map(x => ({ midi: x.m, start: x.s, dur: x.d, hand: x.h }));
  const h = F.assignHands(notes);
  let a = 0, b = 0; notes.forEach((x, i) => { if (h[i] === x.hand) a++; if ((x.midi >= 60 ? 'R' : 'L') === x.hand) b++; });
  n += notes.length; okNew += a; okOld += b;
  rows.push(`kt-test-${s}: neu ${(100 * a / notes.length).toFixed(1)} %  | ab C4 ${(100 * b / notes.length).toFixed(1)} %`);
}
rows.forEach(r => console.log(r));
console.log(`\nGESAMT ${n} Töne: Hand-Zuordnung ${(100 * okNew / n).toFixed(1)} %  | "ab C4 = rechts" ${(100 * okOld / n).toFixed(1)} %`);
// Embers: Daten-Hand ist fast überall "R" – wie viele Töne würden einer Hand Griffe über der Grenze geben?
const e = JSON.parse(fs.readFileSync(datei('embers-notes.json'))).map(x => ({ midi: x[0], start: x[1], dur: x[2] }));
const he = F.assignHands(e);
console.log(`Embers: ${he.filter(x => x === 'L').length} Töne links, ${he.filter(x => x === 'R').length} rechts (Daten-Angabe: 5 links)`);
process.exitCode = okNew >= okOld ? 0 : 1;
