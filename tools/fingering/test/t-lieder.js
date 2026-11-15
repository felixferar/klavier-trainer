// Echte Melodien mit festem Lehrbuch-Fingersatz (Anfänger-Ausgaben, Fünftonlage bzw. Tonleiter), rechts und links.
// Aufruf: node test/t-lieder.js
'use strict';
const F = require('../fingering.js');
const STIL = process.argv.includes('--einfach') ? 'einfach' : 'lehrbuch';   // --einfach: Stil der App
let ok = 0, bad = 0, tones = 0, same = 0;
const N = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, H: 11, B: 10 };
// "E4 Dis5 …" → MIDI
const midi = s => { const m = s.match(/^([A-H])(is|es)?(-?\d)$/); return 12 * (+m[3] + 1) + N[m[1]] + (m[2] === 'is' ? 1 : m[2] === 'es' ? -1 : 0); };
function song(name, hand, tonesStr, beats, beat, book, alts = []) {
  const ms = tonesStr.trim().split(/\s+/).map(midi), notes = []; let t = 0;
  ms.forEach((m, i) => { const d = beats[i % beats.length] * beat; notes.push({ midi: m, start: t, dur: d * 0.9 }); t += d; });
  const r = F.computeHand(notes, { hand, style: STIL });
  const got = r.fingers.join(''), refs = [book].concat(alts);
  const best = refs.map(x => [...x].filter((c, i) => +c === r.fingers[i]).length).reduce((a, b) => Math.max(a, b), 0);
  tones += ms.length; same += best;
  const pass = refs.includes(got) && !r.violations.length;
  if (pass) ok++; else bad++;
  console.log(`${pass ? 'OK  ' : 'ABW '} ${(name + ' (' + hand + ')').padEnd(34)} App ${got}${pass ? '' : '\n       Buch ' + book + `   (${best}/${ms.length} gleich)`}`);
}
const q = [1], hb = 0.5;
// Ode an die Freude (C-Dur, Fünftonlage C–G)
const ode1 = 'E4 E4 F4 G4 G4 F4 E4 D4 C4 C4 D4 E4 E4 D4 D4', ode2 = 'E4 E4 F4 G4 G4 F4 E4 D4 C4 C4 D4 E4 D4 C4 C4';
const odeR = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 0.5, 2];
song('Ode an die Freude, Teil 1', 'R', ode1, odeR, hb, '334554321123322');
song('Ode an die Freude, Teil 2', 'R', ode2, odeR, hb, '334554321123211');
const down = s => s.replace(/(\d)/g, d => String(+d - 1));
song('Ode an die Freude, Teil 1', 'L', down(ode1), odeR, hb, '332112345543344');
song('Ode an die Freude, Teil 2', 'L', down(ode2), odeR, hb, '332112345543455');
// Hänschen klein (C-Dur, C–G)
const hk = 'G4 E4 E4 F4 D4 D4 C4 D4 E4 F4 G4 G4 G4';
song('Hänschen klein', 'R', hk, [1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2], hb, '5334221234555');
song('Hänschen klein', 'L', down(hk), [1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2], hb, '1332445432111');
// Freue dich, Welt / Joy to the World: absteigende C-Dur-Tonleiter
const joy = 'C5 H4 A4 G4 F4 E4 D4 C4';
song('Freue dich, Welt (Anfang)', 'R', joy, [1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 2], 0.4, '54321321');
song('Freue dich, Welt (Anfang)', 'L', down(joy), [1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 2], 0.4, '12312345');
// Für Elise, Anfang (rechts): E Dis E Dis E H D C A
song('Für Elise (Anfang)', 'R', 'E5 Dis5 E5 Dis5 E5 H4 D5 C5 A4', [1, 1, 1, 1, 1, 1, 1, 1, 3], 0.2, '545452431');
// Alle meine Entchen in der Fünftonlage auf G-Dur? → bewusst in C-Dur bis A: Anfänger-Ausgabe 1 2 3 4 5 5 / 5? (keine feste Referenz) – ausgelassen
console.log(`\n${ok} OK, ${bad} mit Abweichung | Töne gleich wie im Buch: ${same}/${tones} = ${(100 * same / tones).toFixed(1)} %`);
process.exitCode = bad ? 1 : 0;
