// T2 + T5 mit beiden Händen und ALLEN Tönen (Akkorde, gehaltene Töne), 3 Handgrößen.
// Songs mit bekannter Hand: Embers + kt-test-301…315. Aufnahmen ohne Hand: Hand-Zuordnung der App (assignHands).
// Aufruf: node test/t-haende-songs.js [--detail]
'use strict';
const fs = require('fs'), path = require('path');
const F = require('../fingering.js');
const STIL = process.argv.includes('--einfach') ? 'einfach' : 'lehrbuch';   // --einfach: Stil der App
const datei = require('./daten.js');
const DETAIL = process.argv.includes('--detail');
const D = path.join(__dirname, 'daten');
const songs = [];
{ // Embers: Hand-Angabe in den Daten ist fast überall "R" (auch die Bässe) → Hand-Zuordnung
  const e = JSON.parse(fs.readFileSync(datei('embers-notes.json'))).map(x => ({ midi: x[0], start: x[1], dur: x[2] }));
  const h = F.assignHands(e); e.forEach((n, i) => { n.hand = h[i]; }); songs.push({ name: 'Embers (Hand-Zuordnung)', notes: e }); }
for (let s = 301; s <= 315; s++) { const y = JSON.parse(fs.readFileSync(datei(s + '.json'))); songs.push({ name: 'kt-test-' + s, notes: y.notes.map(x => ({ midi: x.m, start: x.s, dur: x.d, hand: x.h })) }); }
const AUF = { 'golden hour': '14-21-25_D4COOEBwBjk_done.json', 'Wake Me Up': '16-04-51_41Z7W_0dJu8_done.json', 'SpongeBob': '2026-11-09_SG_cv29mAsA_spongebob.json',
  'GUnDodr9GLo': '14-49-51_GUnDodr9GLo_done.json', '163bCfINABY': '15-01-34_163bCfINABY_done.json', 'mu6gef4lM80': '16-43-39_mu6gef4lM80_done.json' };
if (F.assignHands) for (const [name, file] of Object.entries(AUF)) {
  const r = JSON.parse(fs.readFileSync(datei(file)));
  const notes = r.events.map(e => ({ midi: e[0], start: e[1], dur: Math.max(0.02, e[2] - e[1]) }));
  const h = F.assignHands(notes); notes.forEach((n, i) => { n.hand = h[i]; });
  songs.push({ name: name + ' (Aufnahme)', notes });
}

// T5 für Griffe: gleiche Folge von 4 Griffen (Tonhöhen) mit ungefähr gleichem Rhythmus → gleiche Finger?
function t5(notes, fingers, hand, status) {
  const gs = F.groupNotes(notes, hand).map(g => ({ key: g.notes.map(x => x.o).join('.'), f: g.notes.map(x => fingers[x.src]).join(''), start: g.start, exc: g.notes.some(x => status[x.src] === 'ausnahme') }));
  const W = 4, by = new Map(); let pairs = 0, eq = 0, chordPairs = 0, chordEq = 0, excl = 0;
  for (let i = 0; i + W <= gs.length; i++) { const k = gs.slice(i, i + W).map(x => x.key).join('|'); if (!by.has(k)) by.set(k, []); by.get(k).push(i); }
  const ioi = i => (gs[i + 1] ? gs[i + 1].start - gs[i].start : 0);
  for (const list of by.values()) for (let a = 0; a < list.length; a++) for (let b = a + 1; b < list.length; b++) {
    const i = list[a], j = list[b]; if (j < i + W) continue;
    let same = true; for (let k = 0; k < W - 1; k++) { const x = ioi(i + k), y = ioi(j + k); if (Math.abs(x - y) > Math.max(0.06, 0.25 * Math.max(x, y))) same = false; }
    if (!same) continue;
    if (gs.slice(i, i + W).some(x => x.exc) || gs.slice(j, j + W).some(x => x.exc)) { excl++; continue; }
    const fa = gs.slice(i, i + W).map(x => x.f).join('|'), fb = gs.slice(j, j + W).map(x => x.f).join('|');
    pairs++; if (fa === fb) eq++; else if (diffs.length < 40) diffs.push(`${gs.slice(i, i + W).map(x => x.key).join(' ')}: ${fa} ↔ ${fb} (Griff ${i}/${j})`);
    if (gs.slice(i, i + W).some(x => x.key.includes('.'))) { chordPairs++; if (fa === fb) chordEq++; }
  }
  return { pairs, eq, chordPairs, chordEq, excl };
}

const sum = {}, diffs = [];
let t5x = 0, tN = 0, tChord = 0, tMs = 0, t5p = 0, t5e = 0, t5cp = 0, t5ce = 0, rolled = 0;
const lines = [];
for (const pr of ['meine', 'standard', 'klein']) {
  let v = 0, un = 0;
  for (const s of songs) for (const hand of ['R', 'L']) {
    const ns = s.notes.filter(n => n.hand === hand).map(n => ({ midi: n.midi, start: n.start, dur: n.dur }));
    if (!ns.length) continue;
    const t0 = Date.now();
    const r = F.computeHand(ns, { profile: F.PROFILES[pr], hand, style: STIL });
    const ms = Date.now() - t0;
    const u = F.unavoidableHand(ns, F.PROFILES[pr], hand);
    // Verstöße an Stellen, die mit keinem Griff gehen, zählen nicht (Eingabe unspielbar)
    const uSet = new Set(u), real = r.violations.filter(x => !uSet.has(x.index));
    v += real.length; un += u.length;
    if (pr === 'meine') {
      tN += ns.length; tChord += r.chords.reduce((a, c) => a + c.notes.length, 0); tMs += ms; rolled += r.rolled.length;
      const q = t5(ns, r.fingers, hand, r.status); t5x += q.excl; t5p += q.pairs; t5e += q.eq; t5cp += q.chordPairs; t5ce += q.chordEq;
      lines.push(`${(s.name + ' ' + hand).padEnd(30)} ${String(ns.length).padStart(5)} Töne, ${String(r.chords.length).padStart(4)} Griffe | Verstöße ${real.length} | unvermeidbar ${u.length} | gebrochen ${r.rolled.length} | T5 ${q.eq}/${q.pairs} | ${ms} ms`);
      if (DETAIL && real.length) real.slice(0, 5).forEach(x => lines.push(`     ${x.index}: ${x.text} – ${r.explain(x.index)}`));
    }
  }
  sum[pr] = { v, un };
}
lines.forEach(l => console.log(l));
console.log(`\nZusammen (deine Werte): ${tN} Töne, davon ${tChord} in Akkorden; ${(tMs / 1000).toFixed(1)} s Rechenzeit; ${rolled} Griffe zu weit (gebrochen)`);
console.log('T2 – unmögliche Griffe (ohne Stellen, die mit keinem Griff gehen):');
for (const pr of Object.keys(sum)) console.log(`  ${F.PROFILES[pr].name.padEnd(12)} ${sum[pr].v}   (unvermeidbar in der Eingabe: ${sum[pr].un})`);
console.log(`T5 – gleiche 4-Griff-Folgen gleich gefingert: ${t5e}/${t5p} = ${(100 * t5e / t5p).toFixed(1)} %  | davon mit Akkorden: ${t5ce}/${t5cp} = ${(100 * t5ce / Math.max(1, t5cp)).toFixed(1)} %  | bewusste Ausnahmen "nur hier" (nicht mitgezählt): ${t5x}`);
if (DETAIL) diffs.slice(0, 12).forEach(d => console.log('   ' + d));
process.exitCode = Object.values(sum).every(x => x.v === 0) ? 0 : 1;
