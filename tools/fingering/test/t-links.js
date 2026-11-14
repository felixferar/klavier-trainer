// Linke Hand: Spiegeltest + chromatische Tonleiter + T2 links an Song-Daten.
// Aufruf: node test/t-links.js
'use strict';
const fs = require('fs'), path = require('path');
const F = require('../fingering.js');
const datei = require('./daten.js');
let ok = 0, bad = 0;
const check = (name, cond, info) => { if (cond) ok++; else bad++; console.log(`${cond ? 'OK  ' : 'FEHL'} ${name}${info ? ' – ' + info : ''}`); };
const mk = (midis, ioi = 0.25) => midis.map((m, i) => ({ midi: m, start: i * ioi, dur: ioi * 0.9 }));

// 1) Spiegeltest: Kostenmodell (ohne Muster) links an D gespiegelt = rechts. 300 Zufallsmelodien.
let seed = 7; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
let same = 0, tot = 0;
for (let k = 0; k < 300; k++) {
  let m = 55 + Math.floor(rnd() * 20); const mids = [];
  for (let i = 0; i < 16; i++) { mids.push(m); m += [-7, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 7, 12][Math.floor(rnd() * 13)]; m = Math.max(40, Math.min(90, m)); }
  const ioi = [0.12, 0.2, 0.35][k % 3];
  const r = F.computeFingering(mk(mids, ioi), { patterns: false });
  const l = F.computeFingering(mk(mids.map(x => 124 - x), ioi), { patterns: false, hand: 'L' });
  tot++; if (r.fingers.join('') === l.fingers.join('')) same++;
}
check('Spiegeltest 300 Melodien (ohne Muster)', same === tot, `${same}/${tot} gleich`);

// 2) (entfällt: gespiegelt beginnt C-Dur auf E, Muster ist dann a-Moll)
if (0)
{
  const up = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84];
  const r = F.computeFingering(mk(up, 0.15));
  const l = F.computeFingering(mk(up.map(x => 124 - x), 0.15), { hand: 'L' });
  check('C-Dur links = gespiegelt rechts (mit Muster)', r.fingers.join('') === l.fingers.join(''), l.fingers.join(''));
}
// 3) Chromatisch links: Daumen weiß, 3 schwarz, E und H mit 2 (Spiegel von F und C)
{
  const ch = []; for (let m = 48; m <= 60; m++) ch.push(m);
  const l = F.computeFingering(mk(ch, 0.13), { hand: 'L' });
  const exp = ch.map((m, i) => [1, 3, 1, 3, 2, 1, 3, 1, 3, 1, 3, 2][m % 12]);
  // Ränder: Anfang/Ende frei (Start 1 auf C ok)
  const mism = l.fingers.filter((f, i) => i > 0 && i < ch.length - 1 && f !== exp[i]).length;
  check('Chromatik links aufwärts', mism === 0, l.fingers.join(''));
}
// 4) Fünftonlage links: C D E F G = 5 4 3 2 1, abwärts 1 2 3 4 5
{
  const a = F.computeFingering(mk([48, 50, 52, 53, 55, 53, 52, 50, 48], 0.3), { hand: 'L' });
  check('Fünftonlage links', a.fingers.join('') === '543212345', a.fingers.join(''));
  const b = F.computeFingering(mk([48, 55, 52, 55, 48, 55, 52, 55], 0.15), { hand: 'L' });
  check('Alberti links C-G-E-G', b.fingers.join('') === '51315131', b.fingers.join(''));
  const c = F.computeFingering(mk([36, 48, 43, 48, 36, 48, 43, 48], 0.3), { hand: 'L' });
  check('Oktav-Bass links C2-C3-G2-C3 (5-1-2-1)', c.fingers.join('') === '51215121', c.fingers.join(''));
}

// 5) T2 links an Song-Daten mit Hand-Angabe (Unterstimme der linken Hand), 3 Handgrößen
const D = path.join(__dirname, 'daten'), songs = [];
{ const e = JSON.parse(fs.readFileSync(datei('embers-notes.json'))); songs.push(['Embers L', e.filter(x => x[3] === 'L').map(x => ({ midi: x[0], start: x[1], dur: x[2] }))]); }
for (let s = 301; s <= 315; s++) { const y = JSON.parse(fs.readFileSync(datei(s + '.json'))); songs.push(['kt-test-' + s + ' L', y.notes.filter(x => x.h === 'L').map(x => ({ midi: x.m, start: x.s, dur: x.d }))]); }
for (const pr of ['meine', 'standard', 'klein']) {
  let v = 0, un = 0, n = 0;
  for (const [, ns] of songs) {
    const mel = F.toMelody(ns, 'L'); n += mel.length;
    const r = F.computeFingering(mel, { profile: F.PROFILES[pr], hand: 'L' });
    v += r.violations.length; un += F.unavoidable(mel, F.PROFILES[pr], 'L').length;
  }
  check(`T2 links (${F.PROFILES[pr].name}), ${n} Töne`, v === 0, `${v} unmögliche Griffe, unvermeidbar in der Eingabe: ${un}`);
}
console.log(`\n${ok} OK, ${bad} fehlgeschlagen`);
process.exitCode = bad ? 1 : 0;
