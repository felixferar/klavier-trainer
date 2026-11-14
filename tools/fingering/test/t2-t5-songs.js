// T2 (0 unmögliche Griffe) und T5 (gleiche Stelle = gleicher Fingersatz)
// an Testmelodien und Song-Daten aus dem Repo, mit 3 Handgrößen.
// Aufruf: node test/t2-t5-songs.js [--detail]
'use strict';
const fs = require('fs'), path = require('path');
const F = require('../fingering.js');
const datei = require('./daten.js');
const DETAIL = process.argv.includes('--detail');
const D = path.join(__dirname, 'daten');

// ---------------- Quellen ----------------
const songs = [];
const mel = (name, midis, durs, art = 0.9) => {   // durs: Dauer je Ton in Sekunden (Zahl oder Liste)
  let t = 0; const notes = [];
  midis.forEach((m, i) => { const d = Array.isArray(durs) ? durs[i % durs.length] : durs; if (m !== null) notes.push({ midi: m, start: t, dur: d * art }); t += d; });
  songs.push({ group: 'erfunden', name, notes });
};
const rep = (arr, k) => [].concat(...Array(k).fill(arr));

// 1) Sprünge: Oktaven, Sexten, Dezimen
mel('Sprünge', [60, 72, 67, 64, 76, 72, 79, 67, 60, 69, 65, 77, 74, 62, 71, 83, 79, 67, 72], [0.4, 0.4, 0.2, 0.2]);
// 2) Akkordbrechung auf/ab über 2 Oktaven, Dur/Moll/schwarze Tasten, schnell
mel('Akkordbrechungen', [60, 64, 67, 72, 76, 79, 84, 79, 76, 72, 67, 64, 61, 65, 68, 73, 77, 80, 85, 80, 77, 73, 68, 65, 62, 66, 69, 74, 78, 81, 86], 0.14);
// 3) Alberti-Figuren
mel('Alberti', rep([60, 67, 64, 67], 3).concat(rep([59, 67, 62, 67], 2), rep([60, 69, 65, 69], 2), rep([60, 67, 64, 67], 2)), 0.15);
// 4) Wiederholung exakt + fast gleich (eine Note anders)
const motA = [67, 69, 71, 72, 74, 72, 71, 69, 67, 64], motB = [65, 64, 62, 60, 62, 64];
const motA2 = motA.slice(); motA2[6] = 70;
mel('Wiederholung + fast gleich', motA.concat(motB, motA, motB, motA2, motB, motA), 0.25);
// 5) Schnelle Tonwiederholungen + Sprung
mel('Tonwiederholung schnell', [64, 64, 64, 64, 67, 67, 67, 67, 72, 72, 71, 71, 69, 69, 67, 67, 76, 76, 76, 72], 0.12);
// 6) Schwarze Tasten / Pentatonik
mel('Pentatonik schwarz', [66, 68, 70, 73, 75, 78, 75, 73, 70, 68, 66, 63, 61, 63, 66, 70, 73, 78, 82, 78, 73], 0.18);
// 7) Chromatisch
mel('Chromatik', [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60], 0.13);
// 8) Weite Sprünge sehr schnell (Grenzfall)
mel('Sprünge schnell', [60, 74, 62, 76, 64, 77, 65, 79, 67, 81, 69, 83, 71, 84], 0.12);
// 9) Pop-Melodie mit Sequenzen und Pausen (wiederkehrender Refrain)
const ref = [69, 69, 72, 71, 69, 67, null, 64, 67, 69, 69, 67, 64, 62, null, 64];
mel('Pop-Refrain', ref.concat([60, 62, 64, 67, 64, 62, 60, null], ref, [72, 71, 69, 67, 69, null, null, null], ref), [0.3, 0.3, 0.3, 0.6]);

// 2) Repo: Embers (echter Song, mit Hand), Oberstimme der rechten Hand
{
  const e = JSON.parse(fs.readFileSync(datei('embers-notes.json')));
  const R = e.filter(x => x[3] === 'R').map(x => ({ midi: x[0], start: x[1], dur: x[2] }));
  songs.push({ group: 'Repo echt', name: 'Embers (R, Oberstimme)', notes: F.toMelody(R) });
}
// 3) Repo: 15 erzeugte Testvideos (exakte Noten, mit Hand)
for (let s = 301; s <= 315; s++) {
  const y = JSON.parse(fs.readFileSync(datei(s + '.json')));
  const R = y.notes.filter(x => x.h === 'R').map(x => ({ midi: x.m, start: x.s, dur: x.d }));
  songs.push({ group: 'Repo Testvideo', name: 'kt-test-' + s, notes: F.toMelody(R) });
}
// 4) Repo: echte YouTube-Aufnahmen (ohne Hand-Angabe → rechte Hand = ab C4, Oberstimme)
const AUF = { 'golden hour': '14-21-25_D4COOEBwBjk_done.json', 'Wake Me Up': '16-04-51_41Z7W_0dJu8_done.json', 'SpongeBob': '2026-11-09_SG_cv29mAsA_spongebob.json',
  'GUnDodr9GLo': '14-49-51_GUnDodr9GLo_done.json', '163bCfINABY': '15-01-34_163bCfINABY_done.json', 'mu6gef4lM80': '16-43-39_mu6gef4lM80_done.json' };
for (const [name, file] of Object.entries(AUF)) {
  const r = JSON.parse(fs.readFileSync(datei(file)));
  const R = r.events.filter(e => e[0] >= 60).map(e => ({ midi: e[0], start: e[1], dur: Math.max(0.02, e[2] - e[1]) }));
  songs.push({ group: 'Repo Aufnahme', name, notes: F.toMelody(R) });
}

// ---------------- T5 unabhängig gemessen ----------------
// Alle Fenster aus 6 Tönen mit gleichen Tonhöhen und ungefähr gleichem Rhythmus vergleichen.
function t5(notes, fingers, status) {
  const W = 6, n = notes.length, key = i => notes.slice(i, i + W).map(x => x.midi).join(',');
  const ioi = i => notes[i + 1].start - notes[i].start;
  const same = (i, j) => { for (let k = 0; k < W - 1; k++) { const a = ioi(i + k), b = ioi(j + k); if (Math.abs(a - b) > Math.max(0.06, 0.25 * Math.max(a, b))) return false; } return true; };
  const byKey = new Map();
  for (let i = 0; i + W <= n; i++) { const k = key(i); if (!byKey.has(k)) byKey.set(k, []); byKey.get(k).push(i); }
  let pairs = 0, equal = 0, exc = 0; const diffs = [];
  for (const list of byKey.values()) {
    for (let a = 0; a < list.length; a++) for (let b = a + 1; b < list.length; b++) {
      const i = list[a], j = list[b];
      if (j < i + W || !same(i, j)) continue;
      const fi = fingers.slice(i, i + W).join(''), fj = fingers.slice(j, j + W).join('');
      const isExc = status.slice(j, j + W).includes('ausnahme') || status.slice(i, i + W).includes('ausnahme');
      if (isExc) { exc++; continue; }
      pairs++; if (fi === fj) equal++; else if (diffs.length < 5) diffs.push(`Ton ${i} ${fi} ↔ Ton ${j} ${fj}`);
    }
  }
  return { pairs, equal, exc, diffs };
}

// "Unvermeidbar": Stellen, an denen KEIN Fingersatz die Grenzen schafft (Eingabe selbst unspielbar).
// Gerechnet über die ganze Kette (bester Weg ohne jede Vorgabe).
function unavoidable(notes, profile) { const where = F.unavoidable(notes, profile); return { c: where.length, where }; }

// ---------------- Lauf ----------------
const profiles = ['meine', 'standard', 'klein'];
const rows = [];
let tot = { notes: 0, viol: 0, unav: 0, pairs: 0, equal: 0, exc: 0, open: 0 };
const totP = {}; profiles.forEach(p => { totP[p] = { viol: 0, unav: 0, notes: 0 }; });
const violDetails = [];
for (const s of songs) {
  for (const pName of profiles) {
    const prof = F.PROFILES[pName];
    const t0 = Date.now();
    const r = F.computeFingering(s.notes, { profile: prof });
    const ms = Date.now() - t0;
    const u = unavoidable(s.notes, prof);
    // Verstöße an Stellen, die ohnehin unmöglich sind, zählen nicht gegen den Fingersatz
    const v = r.violations.filter(x => !u.where.includes(x.index));
    const k = t5(s.notes, r.fingers, r.status);
    const open = r.open.filter(Boolean).length;
    let regions = 0; for (let i = 0; i < r.open.length; i++) if (r.open[i] && !(i > 0 && r.open[i - 1])) regions++;
    const ausnU = r.repeats.reduce((a, g) => a + g.reasons.filter(x => x === 'unspielbar').length, 0), ausnB = r.repeats.reduce((a, g) => a + g.reasons.filter(x => x === 'belegt').length, 0);
    rows.push({ group: s.group, name: s.name, p: pName, n: s.notes.length, viol: v.length, unav: u.c, t5: k, open, ms, muster: r.patterns.length, wdh: r.repeats.length, ausn: ausnU + '+' + ausnB });
    if (pName === 'meine') { tot.ausnU = (tot.ausnU || 0) + ausnU; tot.ausnB = (tot.ausnB || 0) + ausnB; }
    totP[pName].viol += v.length; totP[pName].unav += u.c; totP[pName].notes += s.notes.length;
    if (pName === 'meine') { tot.regions = (tot.regions || 0) + regions; tot.notes += s.notes.length; tot.pairs += k.pairs; tot.equal += k.equal; tot.exc += k.exc; tot.open += open; }
    v.forEach(x => violDetails.push(`${s.name} [${pName}] Ton ${x.index}: ${x.text}`));
  }
}

// ---------------- Ausgabe ----------------
console.log('T2/T5 rechte Hand (Oberstimme) | Fingersatz-Kern v' + F.VERSION);
console.log('\nQuelle            Stück                      Töne | unmögl. meine/std/klein | unvermeidb. | T5 gleich        | offen | Muster Wdh. Ausn. | ms');
for (let i = 0; i < rows.length; i += 3) {
  const a = rows[i], b = rows[i + 1], c = rows[i + 2];
  const t5s = a.t5.pairs ? `${a.t5.equal}/${a.t5.pairs}` : '–';
  console.log(`${a.group.padEnd(17)} ${a.name.padEnd(26)} ${String(a.n).padStart(4)} | ${String(a.viol).padStart(3)} / ${String(b.viol).padStart(3)} / ${String(c.viol).padStart(3)}         | ${String(a.unav).padStart(4)}        | ${t5s.padEnd(16)} | ${(100 * a.open / a.n).toFixed(0).padStart(3)} % | ${String(a.muster).padStart(4)} ${String(a.wdh).padStart(4)} ${String(a.ausn).padStart(5)} | ${a.ms}`);
  if (DETAIL && a.t5.diffs.length) a.t5.diffs.forEach(d => console.log('     T5-Abweichung: ' + d));
}
console.log('\nT2 – unmögliche Griffe (ohne Stellen, die mit keinem Finger gehen):');
for (const p of profiles) console.log(`  ${F.PROFILES[p].name.padEnd(12)} ${totP[p].viol} bei ${totP[p].notes} Tönen   (unvermeidbar in der Eingabe: ${totP[p].unav})`);
console.log(`T5 – wiederholte 6-Ton-Stellen gleich gefingert: ${tot.equal}/${tot.pairs} = ${(100 * tot.equal / Math.max(1, tot.pairs)).toFixed(1)} %  (bewusste Ausnahmen "nur hier": ${tot.exc})`);
console.log(`Ausnahmen "nur hier" (Vorkommen): ${tot.ausnU} weil unspielbar, ${tot.ausnB} weil Überschneidung mit anderer Wiederholung`);
console.log(`Offen markiert (meine Werte): ${tot.open}/${tot.notes} Töne = ${(100 * tot.open / tot.notes).toFixed(1)} %, das sind ${tot.regions} Entscheidungsstellen = ${(100 * tot.regions / tot.notes).toFixed(1)} je 100 Töne`);
if (violDetails.length) { console.log('\nVerstöße:'); violDetails.slice(0, 30).forEach(d => console.log('  ' + d)); }
module.exports = { rows, totP, tot };
