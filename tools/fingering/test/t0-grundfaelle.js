// T0 – Lehrbuch-Grundfälle (Fünftonlage, kurze Figuren), rechte Hand.
// Mehrere Lösungen durch "|" getrennt = alle gelten als richtig.
'use strict';
const F = require('../fingering.js');
const mk = (arr, ioi) => arr.map((m, i) => ({ midi: m, start: i * ioi, dur: ioi * 0.95 }));
const CASES = [
  ['C D E F G', [60, 62, 64, 65, 67], '12345'],
  ['G F E D C', [67, 65, 64, 62, 60], '54321'],
  ['C–G–C hin und zurück', [60, 62, 64, 65, 67, 65, 64, 62, 60], '123454321'],
  ['C D E D C', [60, 62, 64, 62, 60], '12321'],
  ['D-Dur Fünftonlage', [62, 64, 66, 67, 69], '12345'],
  ['E D C D E E E (Tonwiederholung)', [64, 62, 60, 62, 64, 64, 64], '3212333|3212321'],
  ['G-Dur Fünftonlage', [67, 69, 71, 72, 74], '12345'],
  ['C E G E C (gebrochen)', [60, 64, 67, 64, 60], '13531|12421'],
  ['C–G mit Doppel-G', [60, 62, 64, 65, 67, 67, 65, 64, 62, 60], '1234554321'],
  ['a-Moll Fünftonlage', [69, 71, 72, 74, 76], '12345'],
  ['F-Dur Fünftonlage', [65, 67, 69, 70, 72], '12345'],
  ['C D E C E D C', [60, 62, 64, 60, 64, 62, 60], '1231321'],
];
let ok = 0, n = 0;
const fails = [];
for (const [name, m, ref] of CASES) for (const ioi of [0.15, 0.4]) {
  const r = F.computeFingering(mk(m, ioi), {});
  const got = r.fingers.join('');
  n++;
  if (ref.split('|').includes(got) && r.violations.length === 0) ok++;
  else fails.push(`${name} (${ioi}s): App ${got}, Buch ${ref}`);
}
console.log(`T0 Grundfälle: ${ok}/${n}`);
fails.forEach(f => console.log('  ' + f));
module.exports = { ok, n, fails };
