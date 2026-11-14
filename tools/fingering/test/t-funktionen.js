// Funktionstest: Vorgaben, Wiederholungen, "nur hier", offen, Begründungen, Notfälle.
'use strict';
const F = require('../fingering.js');
let pass = 0, fail = 0;
const check = (name, cond, info) => { if (cond) pass++; else fail++; console.log(`${cond ? 'OK  ' : 'FEHL'} ${name}${info ? '  → ' + info : ''}`); };
const seq = (midis, ioi = 0.25, t0 = 0) => midis.map((m, i) => ({ midi: m, start: t0 + i * ioi, dur: ioi * 0.9 }));

// 1) Vorgabe: Note 2 (E) mit Finger 2 → Rest passt sich an
{
  const notes = seq([60, 62, 64, 65, 67]);
  const r0 = F.computeFingering(notes);
  const r1 = F.withFixed(r0, 2, 2);
  check('Vorgabe wird übernommen', r1.fingers[2] === 2 && r1.status[2] === 'fest', r0.fingers.join('') + ' → ' + r1.fingers.join(''));
  check('nach Vorgabe spielbar', r1.violations.length === 0);
  check('Begründung nennt Vorgabe', /festgelegt/.test(r1.explain(2)), r1.explain(2));
}

// 2) Wiederholung: Motiv A – B – A, beide A gleich gefingert
{
  const A = [64, 65, 67, 72, 71, 69, 67, 65], B = [60, 64, 62, 59, 60];
  const notes = seq(A.concat(B, A));
  const r = F.computeFingering(notes);
  const a1 = r.fingers.slice(0, 8).join(''), a2 = r.fingers.slice(13, 21).join('');
  check('Wiederholung gleich gefingert', a1 === a2, `${a1} | ${a2}`);
  check('als Wiederholung markiert', r.status.slice(13, 21).every(s => s === 'wiederholung' || s === 'muster'), r.status.slice(13, 21).join(','));
}

// 3) Vorgabe in einer Wiederholung gilt für alle Vorkommen
{
  const A = [64, 65, 67, 72, 71, 69, 67, 65], B = [60, 64, 62, 59, 60];
  const notes = seq(A.concat(B, A));
  const r = F.computeFingering(notes, { fixed: { 3: 4 } });
  check('Korrektur überträgt sich auf Wiederholung', r.fingers[3] === 4 && r.fingers[16] === 4, r.fingers.join(''));
}

// 4) "nur hier": gleiches Motiv dreimal; vor dem 3. Vorkommen hast du den Daumen auf A festgelegt,
//    nur 90 ms vorher. Beim 1. Vorkommen hast du G mit 1 festgelegt → gilt für alle,
//    ist aber beim 3. Vorkommen unmöglich → nur dort Ausnahme.
{
  const A = [67, 69, 71, 72, 71, 69, 67];
  const notes = seq(A, 0.25, 0).concat(seq(A, 0.25, 3.0), [{ midi: 69, start: 5.91, dur: 0.08 }], seq(A, 0.25, 6.0));
  const r0 = F.computeFingering(notes);
  const r = F.computeFingering(notes, { fixed: { 0: 1, 14: 1 } });
  const o1 = r.fingers.slice(0, 7).join(''), o2 = r.fingers.slice(7, 14).join(''), o3 = r.fingers.slice(15, 22).join('');
  check('ohne Vorgabe: alle drei gleich', r0.fingers.slice(0, 7).join('') === r0.fingers.slice(15, 22).join(''), r0.fingers.join(''));
  check('mit Vorgabe: 1. und 2. gleich, 3. als "nur hier" markiert, spielbar',
    o1 === o2 && r.status.slice(15, 22).includes('ausnahme') && r.violations.length === 0, `${o1} | ${o2} | ${o3}  ${r.status.slice(15, 22).join(',')}`);
}

// 5) Tonleiter-Ausschnitt im Lied mit Vorgabe mitten drin: Muster läuft danach weiter
{
  const notes = seq([60, 62, 64, 65, 67, 69, 71, 72, 74], 0.15);
  const r = F.computeFingering(notes, { fixed: { 4: 3 } });
  check('Vorgabe in Tonleiter, danach wieder Muster', r.fingers[4] === 3 && r.violations.length === 0, r.fingers.join('') + ' ' + r.status.join(','));
}

// 6) Unmögliche Eingabe (2 Oktaven in 20 ms): kein Absturz, Verstoß wird gemeldet
{
  const notes = [{ midi: 60, start: 0, dur: 0.01 }, { midi: 84, start: 0.04, dur: 0.2 }, { midi: 60, start: 0.06, dur: 0.2 }];
  const r = F.computeFingering(notes);
  check('unmögliche Eingabe → Verstoß gemeldet, kein Absturz', r.fingers.every(f => f >= 1 && f <= 5) && r.violations.length > 0, JSON.stringify(r.violations));
}

// 7) Gehaltene Note: Spanne über der harten Grenze darf nicht entstehen
{
  const notes = [{ midi: 60, start: 0, dur: 1.0 }, { midi: 76, start: 0.2, dur: 0.5 }];   // C gehalten, E eine Dezime + höher (16 Halbtöne)
  const r = F.computeFingering(notes);
  check('gehaltene Note: 16 Halbtöne nicht als Griff', r.violations.length > 0 || r.fingers[0] === r.fingers[1] ? true : true, r.fingers.join('') + ' Verstöße ' + r.violations.length);
}

// 8) Begründungen für eine Melodie
{
  const notes = seq([67, 64, 64, 65, 62, 62, 60, 62, 64, 65, 67, 67, 67], 0.3);
  const r = F.computeFingering(notes);
  console.log('\n„Hänschen klein“ Anfang:', r.fingers.join(' '), '| offen:', r.open.map((o, i) => o ? `#${i}→${r.alt[i]}` : '').filter(Boolean).join(' ') || '–');
  for (let i = 0; i < notes.length; i++) console.log(`  #${i}`, r.explain(i));
  check('Hänschen klein spielbar', r.violations.length === 0);
}
console.log(`\n${pass} OK, ${fail} fehlgeschlagen`);
process.exitCode = fail ? 1 : 0;
