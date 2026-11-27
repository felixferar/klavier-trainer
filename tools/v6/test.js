/* Tests für den Kern (tools/v6/lernen.js) – ohne Browser:  node tools/v6/test.js */
const L = require('./lernen.js'), fs = require('fs'), path = require('path');
const SG = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'songs.json'))), FELIX = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'felix_fly_me.json')));
let rot = 0; const ok = (name, c, info) => { console.log((c ? 'OK   ' : 'FEHL ') + name + (c || info === undefined ? '' : '  → ' + JSON.stringify(info))); if (!c) rot++; };
const M = L.modell(SG.fly_me.roh, null), G = M.griffe;

/* ---------- E1: Song-Modell ---------- */
console.log('— E1 Song-Modell');
ok('Fly Me: Abschnitte A B C A B D', M.abschnitte.map(s => s.name).join(' ') === 'A B C A B D', M.abschnitte.map(s => s.name));
ok('Wiederholungen erkannt (4. = 1., 5. = 2.)', M.abschnitte.map(s => s.wie).join() === '-1,-1,-1,0,1,-1', M.abschnitte.map(s => s.wie));
ok('Grenzen 0 · 13 · 26 · 46 · 59 · 72', M.abschnitte.map(s => s.a).join() === '0,13,26,46,59,72', M.abschnitte.map(s => s.a));
ok('Taktraster passt, 4 Schläge je Takt', M.rasterOk && M.bpb === 4, [M.rasterOk, M.bpb]);
ok('alle Griffe auf Achteln, Zeiten steigen', G.every((g, j) => Math.abs(g.q * 2 - Math.round(g.q * 2)) < 1e-6 && (!j || g.q > G[j - 1].q)));
ok('Überlappung: Abschnitt 2 beginnt 1 Takt früher', M.abschnitte[1].a0 < M.abschnitte[1].a && G[M.abschnitte[1].a].q - G[M.abschnitte[1].a0].q <= 4, [M.abschnitte[1].a0, M.abschnitte[1].a]);
ok('Akkorde über dem Bass: A D G C F H E A', M.akkorde.slice(0, 8).map(a => a.bass).join(' ') === 'A D G C F H E A', M.akkorde.slice(0, 8).map(a => a.bass));
ok('Akkordnamen: Am7 Dm7 G7 C…', /^Am7? Dm7? G7? C/.test(M.akkorde.slice(0, 4).map(a => a.name).join(' ')), M.akkorde.slice(0, 8).map(a => a.name));
ok('Hände plausibel (Fly Me)', M.haendeOk === true);
const RW = L.modell(SG.runaway.roh, null);
ok('Runaway: Farbe ≠ Hand erkannt, nach Lage getrennt', RW.haendeOk === false && RW.griffe.every(g => g.toene.every(t => (t.m < RW.trennung) === (t.h === 'L'))), [RW.haendeOk, RW.trennung]);
for (const id of Object.keys(SG)) { const m = L.modell(SG[id].roh, null); ok(`${id}: kein Abschnitt über 24 Griffe, Schnitt lückenlos (${m.abschnitte.length} Abschnitte, ${m.abschnitte.filter(s => s.wie < 0).length} neu)`, m.abschnitte.every((s, k) => s.b - s.a + 1 <= 24 && s.b >= s.a && (k === 0 ? s.a === 0 : s.a === m.abschnitte[k - 1].b + 1)) && m.abschnitte[m.abschnitte.length - 1].b === m.n - 1, m.abschnitte.map(s => s.b - s.a + 1)); }
{ const st = L.neu(M); st.cuts = [0, 10, 30, 60]; st.wie = [-1, -1, -1, -1]; st.pos = [0, 0, 0, 0]; const m2 = L.modell(SG.fly_me.roh, st); ok('gespeicherter Schnitt gilt (ein neuer Algorithmus verschiebt nichts)', m2.abschnitte.map(s => s.a).join() === '0,10,30,60'); }

/* ---------- Hilfen ---------- */
const spiele = (R, opt) => { opt = opt || {}; let n = 0; while (!R.fertig && n++ < 5000) { const e = R.E[R.pos]; if (!e) break; const w = opt.warte ? opt.warte(R.pos, e) : 0.4; for (let t = 0; t < w; t += 0.02) R.tick(0.02); if (opt.falsch && opt.falsch(R.pos)) R.taste(30); for (const m of e.mids) R.taste(m); } return R.ergebnis; };
/* Im Takt: Tasten zu festen Schlag-Zeiten; plan(e, i) → Abweichung in Schlägen oder null = Griff auslassen */
const imTakt = (R, plan, aussen) => { const ev = []; R.E.forEach((e, i) => { const d = plan ? plan(e, i) : 0; if (d != null) ev.push({ q: e.q + d, e }); }); ev.sort((a, b) => a.q - b.q); let i = 0, n = 0; while (!R.fertig && n++ < 200000) { R.tick(0.005); while (i < ev.length && ev[i].q <= R.q) { for (const m of ev[i].e.mids) R.taste(m); i++; } } return R.ergebnis; };

/* ---------- E2: Zeigen und Aus dem Kopf ---------- */
console.log('— E2 Zeigen · Aus dem Kopf');
{ const R = L.lauf(M, { k: 0, nr: 1, stufe: 1, hand: 'L', tempo: 0.6 }); const b = R.bild();
  ok('Zeigen links: nur die linke Hand ist dran, Taste leuchtet, Akkordname steht da', R.E.every(e => e.mids.every(m => G[e.j].toene.find(t => t.m === m).h === 'L')) && b.leuchten.length === 1 && b.akkord.startsWith('A'), [b.leuchten, b.akkord]);
  R.taste(30); R.taste(31); const r = spiele(R); ok('Zeigen: falsche Töne zählen, aber einmal durch = weiter', r.ok && r.falsch === 1 && r.stocker === 0, r); }
{ const R = L.lauf(M, { k: 1, nr: 4, stufe: 2, hand: 'LR', tempo: 0.6 }); for (const m of R.E[0].mids) R.taste(m); for (const m of R.E[1].mids) R.taste(m);
  ok('Abschnitt 2 beginnt mit dem letzten Takt von Abschnitt 1', R.E[0].j === M.abschnitte[1].a0 && R.E[0].j < 13);
  for (let t = 0; t < 1.4; t += 0.02) R.tick(0.02); const vor = R.bild().leuchten.length; for (let t = 0; t < 0.2; t += 0.02) R.tick(0.02); const b = R.bild();
  ok('Aus dem Kopf: dunkel; nach 1,5 s Stillstand leuchtet genau der aktuelle Griff', vor === 0 && b.leuchten.length === R.E[2].mids.length && b.leuchten.every(m => R.E[2].mids.includes(m)) && R.stocker === 1, [vor, b.leuchten]);
  for (const m of R.E[2].mids) R.taste(m); ok('nach dem Griff ist es wieder dunkel', R.bild().leuchten.length === 0); }
{ const lang = (i, e) => { const d = i ? e.t - M.griffe[e.j - 1].t : 0; return d > 1 ? d + 0.3 : 0.4; }; const R = L.lauf(M, { k: -1, stufe: 2, hand: 'LR', tempo: 0.6 }); const r = spiele(R, { warte: lang });
  ok('lange Töne im Lied voll ausgehalten (+0,3 s) → keine Hilfe, kein Stocker', r.stocker === 0, r.wo); }
{ const R = L.lauf(M, { k: 0, nr: 4, stufe: 2, hand: 'LR', tempo: 0.6 }); const r = spiele(R, { warte: i => i === 5 || i === 9 ? 2.5 : 0.4 });
  ok('13 Griffe, 2× Hilfe gebraucht → nicht geschafft (erlaubt ist 1)', !r.ok && r.stocker === 2 && r.erlaubt === 1, r); }
{ const R = L.lauf(M, { k: 0, nr: 4, stufe: 2, hand: 'LR', tempo: 0.6 }); const r = spiele(R, { warte: () => 0.5, falsch: i => i % 3 === 0 });
  ok('viele falsche Töne, aber flüssig → geschafft; Eigentempo gemessen (0,67-s-Töne in 0,5 s ≈ 130 %)', r.ok && r.falsch >= 4 && r.eigenTempo > 1.2 && r.eigenTempo < 1.45, r); }

/* ---------- E3: Im Takt ---------- */
console.log('— E3 Im Takt');
{ const toene = [], puls = []; const A = { k: -1, stufe: 3, hand: 'LR', tempo: 1 }, R = L.lauf(M, A, { ton: (m) => toene.push(m), puls: (b, vor) => puls.push([b, vor]) }); const b0 = R.bild(); const r = imTakt(R);
  ok('ganzer Song, genau im Takt → geschafft, 0 Stocker, Meisterprüfung bestanden', r.ok && r.stocker === 0 && r.treffer === r.n && r.meister, r);
  ok('1 Takt Einzählen (4 Schläge, die Eins betont), danach leiser Puls', b0.einzaehlen === 4 && puls.filter(p => p[1]).length === 4 && puls[0][0] === true && puls.filter(p => !p[1]).length > 100, [b0.einzaehlen, puls.length]);
  ok('beide Hände selbst → die App spielt keine Töne dazu', toene.length === 0);
  ok('Dauer = Dauer des Lieds (nichts wartet)', Math.abs(r.dauer - (G[G.length - 1].q + 1.5 + 4) * M.schlag) < 1, r.dauer); }
{ const toene = []; const R = L.lauf(M, { k: 0, nr: 5, stufe: 3, hand: 'R', tempo: 0.8 }, { ton: m => toene.push(m) }); const r = imTakt(R);
  const links = []; for (let j = 0; j <= 12; j++) for (const t of G[j].toene) if (t.h === 'L') links.push(t.m);
  ok('rechts allein: die App spielt die linke Hand dazu', r.ok && toene.join() === links.join() && R.E.every(e => e.mids.every(m => m >= 55)), [toene.length, links.length]); }
{ const R = L.lauf(M, { k: -1, stufe: 3, hand: 'LR', tempo: 1 }); let n = 0; while (!R.fertig && n++ < 200000) R.tick(0.005);
  ok('gar nicht gespielt → der Durchgang läuft trotzdem zu Ende (nichts wartet), nicht geschafft', R.fertig && !R.ergebnis.ok && R.ergebnis.stocker > 10, R.ergebnis.stocker); }
{ const r = imTakt(L.lauf(M, { k: -1, stufe: 3, hand: 'LR', tempo: 1 }), (e, i) => i === 5 ? null : 0); ok('1 Griff ausgelassen (1 Schlag) → kein Stocker', r.ok && r.stocker === 0 && r.treffer === r.n - 1, r); }
{ const r = imTakt(L.lauf(M, { k: -1, stufe: 3, hand: 'LR', tempo: 1 }), (e, i) => i === 5 || i === 6 ? null : 0); ok('2 Griffe hintereinander ausgelassen (> 1 Schlag draußen) → 1 Stocker, trotzdem geschafft (2 erlaubt)', r.ok && r.stocker === 1 && r.erlaubt === 2, r); }
{ const aus = new Set([5, 6, 30, 31, 60, 61]); const r = imTakt(L.lauf(M, { k: -1, stufe: 3, hand: 'LR', tempo: 1 }), (e, i) => aus.has(i) ? null : 0); ok('3 Aussetzer → nicht geschafft', !r.ok && r.stocker === 3, r); }
{ const r = imTakt(L.lauf(M, { k: -1, stufe: 3, hand: 'LR', tempo: 1 }), (e, i) => (i % 2 ? 0.3 : -0.3)); ok('ungenau (± 0,3 Schlag), aber im Puls → geschafft, keine Meisterprüfung', r.ok && r.stocker === 0 && !r.meister && r.abw > 0.25, r); }
{ const R = L.lauf(M, { k: -1, stufe: 3, hand: 'LR', tempo: 1 }); const ev = R.E.map(e => e); let i = 0, n = 0; while (!R.fertig && n++ < 200000) { R.tick(0.005); while (i < ev.length && ev[i].q <= R.q) { if (i % 4 === 0) R.taste(30); for (const m of ev[i].mids) R.taste(m); i++; } }
  ok('23 falsche Töne dazwischen → geschafft, werden nur gezählt', R.ergebnis.ok && R.ergebnis.falsch >= 20 && R.ergebnis.stocker === 0, R.ergebnis); }
/* Felix' echte ganze Durchgänge (Warte-Modus, 25./26.11.) so nachgespielt, als wären sie „Im Takt“ bei 100 % gelaufen */
{ const zeile = []; for (const tempo of [0.8, 1.0]) { let gut = 0; const st = [];
    for (const f of FELIX) { const R = L.lauf(M, { k: -1, stufe: 3, hand: 'LR', tempo }); const zeit = []; let t = 4 * M.schlag / tempo; f.waits.forEach((w, i) => { t += i ? w : 0; zeit.push(t); });
      let i = 0, n = 0, uhr = 0; while (!R.fertig && n++ < 400000) { R.tick(0.005); uhr += 0.005; while (i < zeit.length && zeit[i] <= uhr) { for (const m of R.E[i].mids) R.taste(m); i++; } } st.push(R.ergebnis.stocker); if (R.ergebnis.ok) gut++; }
    zeile.push(`${tempo * 100} %: ${gut} von ${FELIX.length} geschafft, Stocker im Mittel ${(st.reduce((a, b) => a + b, 0) / st.length).toFixed(1)}`); }
  console.log('INFO Felix’ 27 echte Durchgänge, als „Im Takt“ gewertet → ' + zeile.join(' · '));
  ok('Probe mit echten Durchgängen läuft durch', true); }

/* ---------- E4: Lernstand, Los, Wiederholung ---------- */
console.log('— E4 Lernstand · Los · Wiederholung');
{ const st = L.neu(M), sitz = L.sitzung(0), folge = []; let n = 0, A;
  while ((A = L.naechstes(M, st)) && n++ < 100) { folge.push((A.k < 0 ? 'Song' : M.abschnitte[A.k].name) + A.stufe + A.hand); const R = L.lauf(M, A); const r = A.stufe === 3 ? imTakt(R) : spiele(R, { warte: () => 0.5 }); L.abschluss(M, st, A, r, '2026-12-01', sitz); }
  ok('neuer Song, alles geschafft: 4 Abschnitte × 6 Schritte + ganzer Song = 25 Durchgänge', folge.length === 25 && folge[0] === 'A1L' && folge[5] === 'A3LR' && folge[24] === 'Song3LR', folge);
  ok('Schrittfolge je Abschnitt: links · rechts · zusammen · Kopf · Takt rechts · Takt zusammen', folge.slice(0, 6).join(' ') === 'A1L A1R A1LR A2LR A3R A3LR', folge.slice(0, 6));
  ok('wiederholte Abschnitte werden nicht noch einmal gelernt', !folge.slice(18, 24).some(x => x[0] !== 'D'), folge.slice(12));
  ok('Start-Tempo = gemessenes Eigentempo (hier 100 %), Song fertig → morgen fällig', st.ivl === 1 && st.due === '2026-12-02' && st.tempo === 10, st);
  ok('Lernstand hat genau 7 Felder', Object.keys(st).sort().join() === 'cuts,due,ivl,pos,stern,tempo,wie', Object.keys(st));
  ok('fertig → nichts mehr offen', L.naechstes(M, st) === null); }
{ const st = L.uebernahme(M, { cuts: SG.fly_me.altCuts, st: [4, 4, 4, 4, 4, 4, 4, 4], song: 1 }), A = L.naechstes(M, st);
  ok('Übernahme: Felix’ Fly Me (Song sitzt) → direkt der ganze Song im Takt, kein Abschnitt wird neu gelernt', st.pos.join() === '6,6,6,6,6,6' && A.k === -1 && A.stufe === 3 && A.hand === 'LR', [st.pos, A]);
  { const s1 = L.uebernahme(M, { cuts: SG.fly_me.altCuts, st: [4, 4, 4, 4, 4, 4, 4, 4], song: 0 }), A1 = L.naechstes(M, s1); ok('Übernahme: alle Zeilen sitzen, Song noch nie geschafft → Abschnitt A im Takt', s1.pos.join() === '4,4,4,4,4,4' && A1.k === 0 && A1.stufe === 3 && A1.hand === 'R', [s1.pos, A1]); }
  { const s2 = L.neu(M); s2.pos = [6, 6, 2, 0, 0, 0]; const a = L.abschnittUeben(M, s2, 3), b = L.abschnittUeben(M, s2, 2); ok('Abschnitt antippen: fertiger Abschnitt → Im Takt, beide Hände (Wiederholung zeigt aufs Original); offener → sein nächster Schritt', a.k === 0 && a.nr === 6 && b.k === 2 && b.nr === 3, [a, b]); }
  const st2 = L.uebernahme(M, { cuts: SG.fly_me.altCuts, st: [4, 4, 4, 2, 0, 0, 0, 0] }); ok('Übernahme teilweise: A und B sitzen, C (Zeilen 3–4, eine noch offen) und D beginnen vorn', st2.pos.join() === '4,4,0,0,0,0' && L.naechstes(M, st2).k === 0 && L.naechstes(M, st2).stufe === 3, st2.pos); }
{ const st = L.neu(M); st.pos = [6, 6, 6, 0, 0, 6]; st.tempo = 8; const sitz = L.sitzung(0), A = L.naechstes(M, st); ok('alle Abschnitte durch → ganzer Song im Takt', A.k === -1 && A.stufe === 3 && A.tempo === 0.8, A);
  const aus = new Set([30, 31, 34, 35, 40, 41]); const r = imTakt(L.lauf(M, A), (e, i) => aus.has(i) ? null : 0), x = L.abschluss(M, st, A, r, '2026-12-01', sitz), B = L.naechstes(M, st);
  { const s9 = Object.assign(L.neu(M), { pos: [4, 0, 0, 0, 0, 0], tempo: 9 }), z9 = L.sitzung(0), A9 = L.naechstes(M, s9), leer = { ok: false, stocker: 5, erlaubt: 1, falsch: 0, wo: [3], n: 13 }; L.abschluss(M, s9, A9, leer, '2026-12-01', z9); const t1 = s9.tempo; const y = L.abschluss(M, s9, A9, leer, '2026-12-01', z9);
    ok('Abschnitt im Takt 2× hintereinander nicht geschafft → 10 % langsamer (90 → 80 %)', t1 === 9 && s9.tempo === 8 && /langsamer/.test(y.text), [t1, s9.tempo, y.text]); }
  ok('im Song 3× gestockt → kein Absprung zu einem Abschnitt: der ganze Song kommt wieder, der Stand bleibt', !r.ok && st.pos.join() === '6,6,6,0,0,6' && B.k === -1 && st.ivl === 0 && /noch einmal/.test(x.text), [r.stocker, st.pos, x]); }
{ /* Kalender: 3 fertige Songs, 60 Tage, jeden Tag einmal „Los“ – Wiederholung gelingt immer */
  const songs = ['a', 'b', 'c'].map((id, i) => ({ id, stand: Object.assign(L.neu(M), { pos: [6, 6, 6, 0, 0, 6], ivl: 1, due: L.tagPlus('2026-12-01', i === 2 ? 1 : 0), tempo: 10 }) })), app = {}; let tag = '2026-12-01', max = 0, wdh = 0; const abst = { a: [], b: [], c: [] };
  for (let d = 0; d < 60; d++) { let heute = 0; for (let k = 0; k < 4; k++) { const p = L.los(songs, app, tag); if (!p || p.art !== 'wdh') break; const s = songs.find(x => x.id === p.id), A = L.ganzerSong(s.stand); L.abschluss(M, s.stand, A, { ok: true, stocker: 0, erlaubt: 2, falsch: 0, wo: [] }, tag, null); app.wdhTag = tag; abst[p.id].push(s.stand.ivl); heute++; wdh++; } max = Math.max(max, heute); tag = L.tagPlus(tag, 1); }
  ok('60 Tage, 3 Songs: nie mehr als 1 Wiederholung am Tag', max === 1 && wdh >= 12, [max, wdh]);
  ok('Abstände wachsen 3 → 7 → 14 → 30 Tage und bleiben bei 30', abst.a.slice(0, 4).join() === '3,7,14,30' && abst.a.every(x => x <= 30), abst); }
{ const st = Object.assign(L.neu(M), { pos: [6, 6, 6, 0, 0, 6], ivl: 14, due: '2026-12-01', tempo: 10 }), A = L.ganzerSong(st); const x = L.abschluss(M, st, A, { ok: false, stocker: 4, erlaubt: 2, falsch: 0, wo: [50, 51, 52, 20] }, '2026-12-03', null);
  ok('Wiederholung gestockt → Abstand eine Stufe zurück (14 → 7), morgen wieder, kein Abschnitt wird zurückgestuft', st.ivl === 7 && st.due === '2026-12-04' && st.pos[0] === 6, [st, x]); }
{ const songs = [{ id: 'x', stand: Object.assign(L.neu(M), { ivl: 3, due: '2026-12-10' }) }, { id: 'y', stand: L.neu(M) }, { id: 'z' }];
  ok('nichts fällig → weiter am aktuellen Song; ohne aktuellen: der erste offene', L.los(songs, { aktuell: 'z' }, '2026-12-01').id === 'z' && L.los(songs, {}, '2026-12-01').id === 'y' && L.los(songs, { aktuell: 'z' }, '2026-12-10').art === 'wdh'); }
{ const s = L.sitzung(0); ok('Aufhören: nach 5 Minuten ohne Fehlserie kein Hinweis', L.aufhoeren(s, 300) === null);
  s.laeufe = 9; s.ok = 6; s.stErst = 5; s.stLetzt = 2; s.letztes = 'Abschnitt B sitzt im Takt (ohne Stocken)'; const h = L.aufhoeren(s, 12 * 60 + 1);
  ok('nach 12 Minuten: einmal, mit Fortschritt in Worten', h && h.titel === 'Gute Stelle zum Aufhören' && /Abschnitt B sitzt/.test(h.text) && /5 Stocker, zuletzt 2/.test(h.text) && L.aufhoeren(s, 800) === null, h);
  const s2 = L.sitzung(0); s2.reihe = 3; ok('nach 3 nicht geschafften Durchgängen in Folge: Hinweis', (L.aufhoeren(s2, 60) || {}).grund === 'fehl'); }

const zeilen = fs.readFileSync(path.join(__dirname, 'lernen.js'), 'utf8').split('\n').length;
ok(`Kern bleibt unter 700 Zeilen (${zeilen})`, zeilen < 700);
console.log(rot ? `\n${rot} FEHLER` : '\nalles grün'); process.exit(rot ? 1 : 0);
