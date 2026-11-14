// Vergleich App ↔ unabhängiger Prüfer: Kosten beider Lösungen im Modell, Unterschiede je Stelle
'use strict';
const F = require('../fingering.js');
const { STELLEN, nm } = require('./stellen.js');
const P = require('./pruefer.json');
function costOf(notes, fingers) {   // Gesamtkosten eines vorgegebenen Fingersatzes im Modell
  const fixed = {}; fingers.forEach((f, i) => { fixed[i] = f; });
  const r = F.computeFingering(notes, { fixed, patterns: false, repeats: false });
  return { cost: r.totalCost, viol: F.checkPlayable(notes, fingers).length };
}
let same = 0, tot = 0;
STELLEN.forEach(([name, notes], k) => {
  const app = F.computeFingering(notes), a = app.fingers, p = P[k];
  const ca = costOf(notes, a), cp = costOf(notes, p);
  const diff = a.map((f, i) => f !== p[i] ? `${i + 1}:${nm(notes[i].midi)} App ${f}/Prüfer ${p[i]}${app.open[i] ? ' (App: offen→' + app.alt[i] + ')' : ''}` : null).filter(Boolean);
  tot += a.length; same += a.length - diff.length;
  console.log(`Stelle ${k + 1} ${name}: ${diff.length ? diff.length + ' Abweichungen' : 'identisch'} | Kosten App ${ca.cost.toFixed(1)} (unspielbar ${ca.viol}) / Prüfer ${cp.cost.toFixed(1)} (unspielbar ${cp.viol})`);
  if (diff.length) { console.log('   App    ' + a.join(' ')); console.log('   Prüfer ' + p.join(' ')); console.log('   ' + diff.join(' | ')); }
});
console.log(`\nÜbereinstimmung je Ton: ${same}/${tot} = ${(100 * same / tot).toFixed(0)} %`);
