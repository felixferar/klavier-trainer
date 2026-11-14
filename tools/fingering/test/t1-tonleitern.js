// T1 – Tonleitern und Arpeggien, rechte Hand, 2 Oktaven.
// Aufruf: node test/t1-tonleitern.js [--profile meine|standard|klein] [--ioi 0.15] [--pure] [--quiet]
'use strict';
const F = require('../fingering.js');

const args = process.argv.slice(2);
const arg = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const PROFILE = F.PROFILES[arg('--profile', 'meine')];
const IOI = parseFloat(arg('--ioi', '0.15'));
const PURE = args.includes('--pure');       // ohne Muster-Schicht (nur Kostenmodell)
const QUIET = args.includes('--quiet');
const HAND = arg('--hand', 'R') === 'L' ? 'L' : 'R';

// ---------------------------------------------------------------
// Lehrbuch-Fingersätze rechte Hand (Hanon/ABRSM), 2 Oktaven aufwärts, 15 Töne.
// Abwärts = dieselbe Folge rückwärts. "alt" = anerkannte Alternative.
// ---------------------------------------------------------------
const STD = '123123412312345';
const F_PAT = '123412312341234';
const BOOK_DUR = {
  0: { name: 'C-Dur', main: STD }, 7: { name: 'G-Dur', main: STD }, 2: { name: 'D-Dur', main: STD },
  9: { name: 'A-Dur', main: STD }, 4: { name: 'E-Dur', main: STD }, 11: { name: 'H-Dur', main: STD },
  6: { name: 'Fis/Ges-Dur', main: '234123123412312' },
  1: { name: 'Des-Dur', main: '231234123123412' },
  8: { name: 'As-Dur', main: '341231234123123', alt: ['231231234123123'] },
  3: { name: 'Es-Dur', main: '312341231234123', alt: ['212341231234123'] },
  10: { name: 'B-Dur', main: '212312341231234', alt: ['412312341231234'] },
  5: { name: 'F-Dur', main: F_PAT },
};
const BOOK_MOLL = {
  9: { name: 'a', main: STD }, 4: { name: 'e', main: STD }, 11: { name: 'h', main: STD },
  2: { name: 'd', main: STD }, 7: { name: 'g', main: STD }, 0: { name: 'c', main: STD },
  5: { name: 'f', main: F_PAT },
  6: { name: 'fis', main: '341231234123123' }, 1: { name: 'cis', main: '341231234123123' },
  8: { name: 'gis', main: '341231234123123' },
  3: { name: 'es', main: '312341231234123', alt: ['212341231234123'] },
  10: { name: 'b', main: '212312341231234', alt: ['412312341231234'] },
};
// Arpeggien Grundstellung, 2 Oktaven aufwärts, 7 Töne
const AW = '1231235', AB = '2124124', AS = '2312312';
const ARP_DUR = { 0: AW, 7: AW, 5: AW, 2: AW, 9: AW, 4: AW, 11: AW, 6: AW, 1: AB, 3: AB, 8: AB, 10: AB };
const ARP_MOLL = { 9: AW, 4: AW, 2: AW, 7: AW, 0: AW, 11: AW, 5: AW, 3: AW, 6: AB, 1: AB, 8: AB, 10: AS };
// Melodisch Moll (nur Zusatzbericht): Referenz nur, wo das Buch in beide Richtungen gleich fingert
const MEL_REF = { 9: STD, 4: STD, 11: STD, 2: STD, 7: STD, 0: STD, 5: F_PAT };

// Linke Hand (ABRSM/Hanon), 2 Oktaven aufwärts ab dem Grundton, 15 Töne. Abwärts = rückwärts.
const LSTD = '543213214321321', LH4 = '432143213214321', LFIS = '432132143213214', LB = '321432132143213';
const BOOK_DUR_L = {
  0: { name: 'C-Dur', main: LSTD }, 7: { name: 'G-Dur', main: LSTD }, 2: { name: 'D-Dur', main: LSTD },
  9: { name: 'A-Dur', main: LSTD }, 4: { name: 'E-Dur', main: LSTD }, 5: { name: 'F-Dur', main: LSTD },
  11: { name: 'H-Dur', main: LH4 }, 6: { name: 'Fis/Ges-Dur', main: LFIS },
  1: { name: 'Des-Dur', main: LB }, 3: { name: 'Es-Dur', main: LB }, 8: { name: 'As-Dur', main: LB }, 10: { name: 'B-Dur', main: LB },
};
const BOOK_MOLL_L = {
  9: { name: 'a', main: LSTD }, 4: { name: 'e', main: LSTD }, 2: { name: 'd', main: LSTD },
  7: { name: 'g', main: LSTD }, 0: { name: 'c', main: LSTD }, 5: { name: 'f', main: LSTD },
  11: { name: 'h', main: LH4 }, 6: { name: 'fis', main: LFIS }, 1: { name: 'cis', main: LB }, 8: { name: 'gis', main: LB },
  3: { name: 'es', main: '214321321432132' }, 10: { name: 'b', main: '213214321321432' },
};
const ALW = '5421421', AL3 = '2142142', AL5 = '3213213';
const ARP_DUR_L = { 0: ALW, 7: ALW, 5: ALW, 2: ALW, 9: ALW, 4: ALW, 11: ALW, 6: ALW, 1: AL3, 3: AL3, 8: AL3, 10: AL5 };
const ARP_MOLL_L = { 9: ALW, 4: ALW, 2: ALW, 7: ALW, 0: ALW, 11: ALW, 5: ALW, 3: ALW, 6: AL3, 1: AL3, 8: AL3, 10: AL5 };
const MEL_REF_L = { 9: LSTD, 4: LSTD, 2: LSTD, 7: LSTD, 0: LSTD, 5: LSTD };
const BD = HAND === 'L' ? BOOK_DUR_L : BOOK_DUR, BM = HAND === 'L' ? BOOK_MOLL_L : BOOK_MOLL;
const AD = HAND === 'L' ? ARP_DUR_L : ARP_DUR, AM = HAND === 'L' ? ARP_MOLL_L : ARP_MOLL, MR = HAND === 'L' ? MEL_REF_L : MEL_REF;

const STEPS = { dur: [0, 2, 4, 5, 7, 9, 11], harm: [0, 2, 3, 5, 7, 8, 11], nat: [0, 2, 3, 5, 7, 8, 10], melUp: [0, 2, 3, 5, 7, 9, 11] };
const DUR_NAMES = ['C', 'Des', 'D', 'Es', 'E', 'F', 'Fis/Ges', 'G', 'As', 'A', 'B', 'H'];
const MOLL_NAMES = ['c', 'cis', 'd', 'es', 'e', 'f', 'fis', 'g', 'gis', 'a', 'b', 'h'];
const NN = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'As', 'A', 'B', 'H'];

const root = t => (HAND === 'L' ? 48 : 60) + t;
function scaleMidi(t, steps, octaves = 2) {
  const out = [];
  for (let o = 0; o < octaves; o++) for (const s of steps) out.push(root(t) + 12 * o + s);
  out.push(root(t) + 12 * octaves);
  return out;
}
function arpMidi(t, third) { const out = []; for (let o = 0; o < 2; o++) out.push(root(t) + 12 * o, root(t) + 12 * o + third, root(t) + 12 * o + 7); out.push(root(t) + 24); return out; }
const toNotes = midis => midis.map((m, i) => ({ midi: m, start: i * IOI, dur: IOI * 0.95 }));
const variants = up => {
  const down = up.slice().reverse();
  return { auf: up, ab: down, aufab: up.concat(down.slice(1)) };
};
const seqVariants = s => {
  const up = s.split('').map(Number), down = up.slice().reverse();
  return { auf: up, ab: down, aufab: up.concat(down.slice(1)) };
};

function score(got, mainS, alts) {
  const refs = [mainS].concat(alts || []).map(seqVariants);
  const res = {};
  for (const v of ['auf', 'ab', 'aufab']) {
    const m = refs[0][v];
    const exact = got[v].filter((x, i) => x === m[i]).length;
    let bestOk = -1, bestRef = 0;
    refs.forEach((r, k) => { const ok = got[v].filter((x, i) => x === r[v][i]).length; if (ok > bestOk) { bestOk = ok; bestRef = k; } });
    res[v] = { n: m.length, exact, ok: bestOk, ref: bestRef, ref_seq: refs[bestRef][v] };
  }
  return res;
}

function run(midis) {
  const V = variants(midis), got = {}, viol = {}, open = {};
  for (const v of ['auf', 'ab', 'aufab']) {
    const notes = toNotes(V[v]);
    const r = F.computeFingering(notes, { profile: PROFILE, patterns: !PURE, repeats: !PURE, hand: HAND });
    got[v] = r.fingers; viol[v] = r.violations.length; open[v] = r.open.filter(Boolean).length;
  }
  return { got, viol, open, V };
}

const rows = [], devs = [];
let totN = 0, totOk = 0, totExact = 0, totViol = 0, totOpen = 0;
function test(group, name, midis, mainS, alts, counts = true) {
  const r = run(midis);
  const s = mainS ? score(r.got, mainS, alts) : null;
  const viol = r.viol.auf + r.viol.ab + r.viol.aufab, open = r.open.auf + r.open.ab + r.open.aufab;
  if (s) {
    const n = s.auf.n + s.ab.n + s.aufab.n, ok = s.auf.ok + s.ab.ok + s.aufab.ok, ex = s.auf.exact + s.ab.exact + s.aufab.exact;
    rows.push({ group, name, pct: 100 * ok / n, exactPct: 100 * ex / n, viol, open });
    if (counts) { totN += n; totOk += ok; totExact += ex; totViol += viol; totOpen += open; }
    for (const v of ['auf', 'ab', 'aufab']) {
      if (s[v].ok < s[v].n) {
        const ref = s[v].ref_seq, g = r.got[v];
        const where = g.map((x, i) => x !== ref[i] ? `${NN[r.V[v][i] % 12]}${Math.floor(r.V[v][i] / 12) - 1}: ${x} statt ${ref[i]}` : null).filter(Boolean);
        devs.push(`${group} ${name} ${v}: App ${g.join('')} | Buch ${ref.join('')} | ${where.join(', ')}`);
      }
    }
  } else {
    rows.push({ group, name, pct: null, exactPct: null, viol, open, got: r.got.aufab.join('') });
    if (viol) devs.push(`${group} ${name}: ${viol} unspielbare Stellen!`);
  }
}

for (let t = 0; t < 12; t++) { const b = BD[t]; test('Dur', b.name, scaleMidi(t, STEPS.dur), b.main, b.alt); }
for (let t = 0; t < 12; t++) { const b = BM[t]; test('Moll harm.', b.name + '-Moll', scaleMidi(t, STEPS.harm), b.main, b.alt); }
for (let t = 0; t < 12; t++) { const b = BM[t]; test('Moll nat.', b.name + '-Moll', scaleMidi(t, STEPS.nat), b.main, b.alt); }
for (let t = 0; t < 12; t++) test('Arp. Dur', DUR_NAMES[t] + '-Dur', arpMidi(t, 4), AD[t]);
for (let t = 0; t < 12; t++) test('Arp. Moll', MOLL_NAMES[t] + '-Moll', arpMidi(t, 3), AM[t]);

// Melodisch Moll: aufwärts melodisch, abwärts natürlich – nur Zusatzbericht
const melRows = [];
for (let t = 0; t < 12; t++) {
  const up = scaleMidi(t, STEPS.melUp), downNat = scaleMidi(t, STEPS.nat).reverse();
  const midis = up.concat(downNat.slice(1));
  const notes = toNotes(midis);
  const r = F.computeFingering(notes, { profile: PROFILE, patterns: !PURE, repeats: !PURE, hand: HAND });
  let match = null;
  if (MR[t]) {
    const ref = seqVariants(MR[t]).aufab;
    match = 100 * r.fingers.filter((x, i) => x === ref[i]).length / ref.length;
  }
  melRows.push({ name: MOLL_NAMES[t] + '-Moll mel.', got: r.fingers.join(''), match, viol: r.violations.length });
}

// T1b: Ausschnitte (8 Töne), Einstieg mitten in der Tonleiter.
// Bestanden, wenn die Töne 2–7 einem Lehrbuch-Muster folgen (dieser Tonart oder einer
// Tonart mit denselben Tönen) und der Schlusston Muster oder "Schluss ohne Untersatz" ist.
const allBooks = [];
for (const [kind, book] of [['dur', BD], ['harm', BM], ['nat', BM]])
  for (let t = 0; t < 12; t++) {
    const seq = book[t].main.split('').map(Number), mids = scaleMidi(t, STEPS[kind]);
    const map = {}; for (let k = 7; k < 14; k++) map[mids[k] % 12] = seq[k];
    allBooks.push({ name: `${kind}${t}`, map });
  }
let exN = 0, exOk = 0; const exDevs = [];
for (const [kind, names] of [['dur', DUR_NAMES], ['harm', MOLL_NAMES], ['nat', MOLL_NAMES]])
  for (let t = 0; t < 12; t++) {
    const mids = scaleMidi(t, STEPS[kind]);
    for (const dir of [1, -1]) for (let s = 1; s <= 6; s++) {
      let ex = mids.slice(s, s + 8);
      if (dir < 0) ex = mids.slice(14 - s - 7, 14 - s + 1).reverse();
      const r = F.computeFingering(toNotes(ex), { profile: PROFILE, patterns: !PURE, repeats: !PURE, hand: HAND });
      const g = r.fingers;
      const ok = allBooks.some(B => {
        if (!ex.every(m => (m % 12) in B.map)) return false;
        for (let k = 1; k < 7; k++) if (g[k] !== B.map[ex[k] % 12]) return false;
        const p = B.map[ex[7] % 12], prevP = B.map[ex[6] % 12];
        const md = HAND === 'L' ? -dir : dir;   // links gespiegelt: Schlussregel gilt in Spielrichtung der Hand
        return g[7] === p || (md > 0 && p === 1 && g[7] > prevP) || (md < 0 && prevP === 1 && g[7] === 2);
      }) && r.violations.length === 0;
      exN++; if (ok) exOk++;
      else exDevs.push(`${kind} ${names[t]} ${dir > 0 ? 'auf' : 'ab'} ab Ton ${s + 1}: ${ex.map(m => NN[m % 12]).join(' ')} → ${g.join('')}`);
    }
  }

// ---------------- Ausgabe ----------------
const pct = x => x === null ? '  –  ' : (x.toFixed(1) + '%').padStart(6);
console.log(`T1 ${HAND === 'L' ? 'linke' : 'rechte'} Hand | Hand: ${PROFILE.name} | Tempo: ${IOI}s pro Ton | ${PURE ? 'NUR KOSTENMODELL (ohne Muster)' : 'mit Muster-Schicht'}`);
if (!QUIET) {
  console.log('\nGruppe      Tonleiter          Treffer  exakt Haupttab.  unspielbar  offen');
  for (const r of rows) console.log(`${r.group.padEnd(11)} ${r.name.padEnd(18)} ${pct(r.pct)}   ${pct(r.exactPct)}          ${String(r.viol).padStart(3)}     ${String(r.open).padStart(3)}`);
  console.log('\nMelodisch Moll (Zusatz, kein Bestehenskriterium):');
  for (const r of melRows) console.log(`  ${r.name.padEnd(16)} ${r.got}  ${r.match === null ? 'keine feste Referenz' : 'Treffer ' + r.match.toFixed(1) + '%'}  unspielbar: ${r.viol}`);
}
console.log(`\nGESAMT (Dur, Moll harm., Moll nat., Arpeggien): ${totOk}/${totN} = ${(100 * totOk / totN).toFixed(2)}%  | davon exakt Haupttabelle ${(100 * totExact / totN).toFixed(2)}%  | unspielbar ${totViol} | offen ${totOpen}`);
const pflicht = rows.filter(r => ['Dur', 'Moll harm.', 'Arp. Dur', 'Arp. Moll'].includes(r.group));
console.log(`PFLICHT (Dur + harm. Moll + Arpeggien): ${pflicht.every(r => r.pct === 100) ? 'BESTANDEN 100%' : 'NICHT bestanden'}`);
console.log(`T1b Ausschnitte (Einstieg mitten drin): ${exOk}/${exN} = ${(100 * exOk / exN).toFixed(1)}%`);
if (devs.length) { console.log('\nAbweichungen:'); devs.forEach(d => console.log('  ' + d)); }
if (exDevs.length && !QUIET) { console.log('\nT1b-Abweichungen:'); exDevs.slice(0, 40).forEach(d => console.log('  ' + d)); if (exDevs.length > 40) console.log(`  … und ${exDevs.length - 40} weitere`); }
process.exitCode = pflicht.every(r => r.pct === 100) ? 0 : 1;
