/* Lernen v6 (Prototyp) – der schlanke Auswendig-Modus.
   Kennt kein DOM, kein localStorage, keinen Klang: alles kommt von außen. Läuft deshalb auch in Node (tools/v6/test.js).

   Drei Bausteine:
     modell(roh, stand)      Song → Griffe, Abschnitte (A B C …), Taktraster, Akkordnamen, Hände-Prüfung
     lauf(modell, auftrag)   ein Durchgang: Stufe 1 Zeigen · 2 Aus dem Kopf · 3 Im Takt
     abschluss / los         Lernstand fortschreiben, nächsten Schritt wählen, Wiederholung nach Tagen

   Eine Erfolgsregel: geschafft = bis zum Ende mit höchstens 1 Stocker je 40 Griffe. Falsche Töne werden gezählt, entscheiden nichts.
   Lernstand je Song (7 Felder): {cuts, wie, pos, tempo, ivl, due, stern}. */
(function (root, factory) { if (typeof module === 'object' && module.exports) module.exports = factory(); else root.Lernen = factory(); })(this, function () {
'use strict';

const K = {
  hilfeNach: 1.5,     // Aus dem Kopf: so lange Stillstand, dann leuchtet der aktuelle Griff
  ersterGriff: 3,     // … beim allerersten Griff etwas mehr Zeit
  stockPer: 40,       // 1 Stocker je 40 Griffe ist erlaubt (geeicht an 27 echten Durchgängen, v5.59)
  fenster: 0.5,       // Im Takt: ein Griff zählt bis ± ½ Schlag um seine Zeit
  stockSchlag: 1,     // Im Takt: länger als 1 Schlag draußen = Stocker
  meister: 0.125,     // Meisterprüfung: jeder Griff ± ⅛ Schlag
  meisterFalsch: 2,
  abschnittMax: 24,   // längere Abschnitte werden geteilt
  raster: 0.5,        // Griffe liegen auf Achteln (½ Schlag)
  rasterOk: 0.85,     // Anteil der Griffe, der aufs Raster passen muss
  tempoMin: 5, tempoMax: 10,
  leiter: [1, 3, 7, 14, 30],
  pauseMin: 12, pauseFehl: 3,
  // feste Schrittfolge je Abschnitt: nr = Wert von stand.pos, wenn der Schritt geschafft ist
  schritte: [
    { nr: 1, stufe: 1, hand: 'L' }, { nr: 2, stufe: 1, hand: 'R' }, { nr: 3, stufe: 1, hand: 'LR' },
    { nr: 4, stufe: 2, hand: 'LR' },
    { nr: 5, stufe: 3, hand: 'R' }, { nr: 6, stufe: 3, hand: 'LR' }],
  stufen: ['', 'Zeigen', 'Aus dem Kopf', 'Im Takt'],
  haende: { L: 'linke Hand', R: 'rechte Hand', LR: 'beide Hände' }
};
const TON = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'As', 'A', 'B', 'H']; // deutsche Namen: B = b, H = h
const median = a => { if (!a.length) return 0; const s = a.slice().sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const erlaubt = n => Math.max(1, Math.round(n / K.stockPer));

/* ---------- 1. Song-Modell ---------- */

/* roh = { griffe:[{t, n:[[midi, hand, dauer], …]}],  takt:{beat, S:[Taktanfänge in s]} | null,
           zeilen:[{a, b}], formen:[{s, e}] }   (zeilen/formen = Vorschlag für die Abschnitte, aus dem bestehenden Takt-Schnitt)
   stand  = gespeicherter Lernstand oder null – seine cuts/wie gelten, damit ein neuer Schnitt nichts verschiebt */
function modell(roh, stand) {
  const G = roh.griffe.map(g => ({ t: g.t, toene: g.n.map(x => ({ m: x[0], h: x[1] === 'L' ? 'L' : 'R', d: x[2] })) }));
  const N = G.length, M = { griffe: G, n: N };
  haende(M);
  raster(M, roh.takt);
  const cuts = stand && stand.cuts && stand.cuts.length && stand.cuts[0] === 0 && stand.cuts.every(c => c < N) ? stand.cuts.slice() : schnitt(M, roh);
  M.abschnitte = cuts.map((a, k) => ({ a, b: (k + 1 < cuts.length ? cuts[k + 1] : N) - 1 }));
  const sig = s => { const x = []; for (let j = s.a; j <= s.b; j++) x.push(G[j].toene.map(t => t.m).sort((p, q) => p - q).join('.')); return x.join('|'); };
  const sigs = M.abschnitte.map(sig); let buchst = 0;
  M.abschnitte.forEach((s, k) => {
    const w = stand && stand.wie && stand.wie.length === cuts.length ? stand.wie[k] : sigs.indexOf(sigs[k]);
    s.wie = w >= 0 && w < k ? w : -1;
    s.name = s.wie >= 0 ? M.abschnitte[s.wie].name : String.fromCharCode(65 + buchst % 26) + (buchst >= 26 ? Math.floor(buchst / 26) + 1 : ''); if (s.wie < 0) buchst++;
    // Überlappung: 1 Takt früher beginnen (ohne Raster: 3 Griffe), nie vor dem Anfang des vorigen Abschnitts
    let a0 = s.a; if (k > 0) { const lim = M.abschnitte[k - 1].a, ab = G[s.a].q - M.bpb - 1e-6; while (a0 > lim && (M.rasterOk ? G[a0 - 1].q >= ab : s.a - a0 < 3)) a0--; }
    s.a0 = a0;
    s.einhand = !hat(G, a0, s.b, 'L') || !hat(G, a0, s.b, 'R');
  });
  M.akkorde = akkorde(M);
  return M;
}
function hat(G, a, b, h) { for (let j = a; j <= b; j++) if (G[j].toene.some(t => t.h === h)) return true; return false; }

/* Hände: Sind die Farben des Videos wirklich die Hände? Wenn „rechts“ tief unter „links“ greift oder eine Hand > 2 Oktaven auf einmal spannt → nach Lage trennen. */
function haende(M) {
  const L = [], R = []; let weit = 0;
  for (const g of M.griffe) for (const h of ['L', 'R']) { const p = g.toene.filter(t => t.h === h).map(t => t.m); if (!p.length) continue; (h === 'L' ? L : R).push(...p); if (Math.max(...p) - Math.min(...p) > 24) weit++; }
  M.haendeOk = true; if (!L.length || !R.length) return;
  const rs = R.slice().sort((a, b) => a - b), ls = L.slice().sort((a, b) => a - b), tief = rs[Math.floor(rs.length * 0.05)], hoch = ls[Math.floor(ls.length * 0.95)];
  if (tief >= median(L) && hoch <= median(R) && weit <= M.griffe.length * 0.02) return;
  M.haendeOk = false;
  // Trennlinie: die leerste Stelle zwischen C3 und F♯4
  const alle = L.concat(R); let best = 60, leer = Infinity;
  for (let s = 48; s <= 66; s++) { const c = alle.filter(m => Math.abs(m - s + 0.5) <= 2.5).length + Math.abs(s - 60) * 0.01; if (c < leer) { leer = c; best = s; } }
  for (const g of M.griffe) for (const t of g.toene) t.h = t.m < best ? 'L' : 'R';
  M.trennung = best;
}

/* Taktraster: jede Griffzeit als Schlag-Zahl q, aufs Achtel gezogen. Ohne brauchbaren Takt: Original-Zeiten in „Schlägen“ des mittleren Abstands. */
function raster(M, takt) {
  const G = M.griffe;
  if (takt && takt.beat > 0 && takt.S && takt.S.length >= 2) {
    const S = takt.S.slice().sort((a, b) => a - b), d = []; for (let i = 1; i < S.length; i++) d.push(S[i] - S[i - 1]);
    const bpb = Math.max(1, Math.round(median(d) / takt.beat)); let pass = 0;
    for (const g of G) {
      let i = 0; while (i + 1 < S.length && S[i + 1] <= g.t + takt.beat * 0.25) i++;
      const len = i + 1 < S.length ? S[i + 1] - S[i] : median(d), roh = (g.t - S[i]) / (len / bpb), q = Math.round(roh / K.raster) * K.raster;
      if (Math.abs(roh - q) <= 0.2) pass++;
      g.q = i * bpb + q;
    }
    if (pass >= G.length * K.rasterOk) { M.rasterOk = true; M.bpb = bpb; M.schlag = median(d) / bpb; const q0 = Math.floor(G[0].q / bpb) * bpb; for (const g of G) g.q -= q0; mono(G); return; }
  }
  const io = []; for (let j = 1; j < G.length; j++) io.push(G[j].t - G[j - 1].t);
  const kurz = io.filter(x => x > 0.05).sort((a, b) => a - b), schlag = kurz.length ? kurz[Math.floor(kurz.length * 0.3)] : 0.5;
  M.rasterOk = false; M.bpb = 4; M.schlag = schlag; for (const g of G) g.q = (g.t - G[0].t) / schlag;
}
function mono(G) { for (let j = 1; j < G.length; j++) if (G[j].q <= G[j - 1].q) G[j].q = G[j - 1].q + K.raster / 2; } // zwei Griffe nie auf demselben Punkt

/* Abschnitte: Formteile aus dem Takt-Schnitt; zu lange werden an einer Zeilengrenze (sonst am Takt) geteilt. */
function schnitt(M, roh) {
  const N = M.n, Z = (roh.zeilen || []).filter(z => z.a < N), cuts = [];
  const F = roh.formen && roh.formen.length && Z.length ? roh.formen.map(f => ({ a: Z[f.s].a, b: Z[Math.min(f.e, Z.length - 1)].b, zs: Z.slice(f.s, f.e + 1).map(z => z.a) })) : [{ a: 0, b: N - 1, zs: Z.map(z => z.a) }];
  const teile = (a, b, zs) => {
    if (b - a + 1 <= K.abschnittMax) { cuts.push(a); return; }
    const mitte = (a + b + 1) / 2, kand = zs.filter(x => x > a + 3 && x <= b - 3); let c = -1;
    if (kand.length) c = kand.reduce((p, x) => Math.abs(x - mitte) < Math.abs(p - mitte) ? x : p);
    else for (let j = a + 4; j <= b - 3; j++) if (Math.abs(M.griffe[j].q % M.bpb) < 1e-6 && (c < 0 || Math.abs(j - mitte) < Math.abs(c - mitte))) c = j;
    if (c < 0) c = Math.round(mitte);
    teile(a, c - 1, zs); teile(c, b, zs);
  };
  for (const f of F) teile(f.a, Math.min(f.b, N - 1), f.zs);
  if (cuts[0] !== 0) cuts.unshift(0);
  return cuts.filter((c, i) => i === 0 || c > cuts[i - 1]);
}

/* Akkordnamen über dem Bass: Grundton = tiefster Ton der linken Hand; Moll/Dur/7 aus allen Tönen bis zum nächsten Basswechsel. */
function akkorde(M) {
  const G = M.griffe, seg = [];
  for (let j = 0; j < G.length; j++) { const l = G[j].toene.filter(t => t.h === 'L'); if (!l.length) continue; const pc = Math.min(...l.map(t => t.m)) % 12; if (!seg.length || seg[seg.length - 1].pc !== pc) seg.push({ g: j, pc }); }
  seg.forEach((s, i) => {
    const bis = i + 1 < seg.length ? seg[i + 1].g : G.length, w = new Array(12).fill(0);
    for (let j = s.g; j < bis; j++) for (const t of G[j].toene) w[(t.m - s.pc + 120) % 12] += Math.max(0.1, t.d || 0.1);
    const klein = w[3], gross = w[4], dim = w[6] > 0 && klein > 0 && w[7] === 0;
    let name = TON[s.pc];
    if (dim) name += '°'; else { if (klein > gross) name += 'm'; if (!klein && !gross) { s.name = name; return; } if (w[10] > 0) name += '7'; else if (w[11] > 0 && gross >= klein) name += 'maj7'; }
    s.name = name;
  });
  return seg.map(s => ({ g: s.g, name: s.name, bass: TON[s.pc] }));
}
function akkordBei(M, j) { let r = null; for (const a of M.akkorde) { if (a.g <= j) r = a; else break; } return r; }

/* ---------- 2. Lernstand ---------- */

function neu(M) { return { cuts: M.abschnitte.map(s => s.a), wie: M.abschnitte.map(s => s.wie), pos: M.abschnitte.map(() => 0), tempo: null, ivl: 0, due: null, stern: 0 }; }

/* Einen Abschnitt gezielt üben (angetippt): sein nächster offener Schritt, sonst „Im Takt, beide Hände“. */
function abschnittUeben(M, st, k) { if (M.abschnitte[k].wie >= 0) k = M.abschnitte[k].wie; const sch = schritteVon(M, k), s = sch.find(x => x.nr > st.pos[k]) || sch[sch.length - 1]; return Object.assign({ k, tempo: tempoVon(st) }, s); }

/* Übernahme aus dem alten Zeilen-Modus: Abschnitt, dessen Zeilen alle „sitzen“ (Stufe 4) → Zeigen und Aus dem Kopf sind erledigt, weiter mit Im Takt. */
function uebernahme(M, alt) {
  const st = neu(M); if (!alt || !alt.cuts || !alt.st) return st;
  if (alt.song >= 1) { st.pos = st.pos.map(() => 6); if (alt.tempo) st.tempo = alt.tempo; return st; } // der ganze Song sitzt schon → direkt der ganze Song im Takt, kein Abschnitt wird neu gelernt
  M.abschnitte.forEach((s, k) => { let alle = true, eine = false; alt.cuts.forEach((c, q) => { const e = (q + 1 < alt.cuts.length ? alt.cuts[q + 1] : M.n) - 1; if (c <= s.b && e >= s.a) { eine = true; if ((alt.st[q] || 0) < 4) alle = false; } }); if (eine && alle) st.pos[k] = 4; });
  return st;
}

function schritteVon(M, k) { const s = M.abschnitte[k]; return s.einhand ? K.schritte.filter(x => x.hand === 'LR') : K.schritte; }
function posVon(M, st, k) { const s = M.abschnitte[k]; return s.wie >= 0 ? st.pos[s.wie] : st.pos[k]; }

/* Was ist als Nächstes dran?  → {k, nr, stufe, hand, tempo} · {k:-1, stufe:3, hand:'LR', tempo} (ganzer Song) · null (Song fertig) */
function naechstes(M, st) {
  for (let k = 0; k < M.abschnitte.length; k++) { if (M.abschnitte[k].wie >= 0) continue; const s = schritteVon(M, k).find(x => x.nr > st.pos[k]); if (s) return Object.assign({ k, tempo: tempoVon(st) }, s); }
  return st.ivl > 0 ? null : ganzerSong(st);
}
function ganzerSong(st) { return { k: -1, nr: 0, stufe: 3, hand: 'LR', tempo: tempoVon(st) }; }
function tempoVon(st) { return Math.min(K.tempoMax, Math.max(K.tempoMin, st.tempo || 6)) / 10; }
function fortschritt(M, st) { const eig = M.abschnitte.map((s, k) => k).filter(k => M.abschnitte[k].wie < 0), ges = eig.length * 6 + 1; return { fertig: st.ivl > 0, teil: (eig.reduce((a, k) => a + Math.min(6, st.pos[k]), 0) + (st.ivl > 0 ? 1 : 0)) / ges, abschnitte: M.abschnitte.map((s, k) => ({ name: s.name, pos: posVon(M, st, k), wie: s.wie })) }; }
function titel(M, A) { const wo = A.k < 0 ? 'Ganzer Song' : 'Abschnitt ' + M.abschnitte[A.k].name; return wo + ' · ' + K.stufen[A.stufe] + (A.stufe === 3 ? ' · ' + Math.round(A.tempo * 100) + ' %' : '') + (A.k >= 0 && !M.abschnitte[A.k].einhand ? ' · ' + (A.stufe === 3 && A.hand === 'R' ? 'rechts, die App spielt links' : K.haende[A.hand]) : ''); }

/* ---------- 3. Ein Durchgang ---------- */

/* außen = { ton(midi, dauerSek, laut), puls(betont) }  – beide optional.
   Rückgabe: { taste(midi), tick(dt), bild(), fertig, ergebnis } */
function lauf(M, A, aussen) {
  aussen = aussen || {}; const G = M.griffe, sec = A.k >= 0 ? M.abschnitte[A.k] : null, a = sec ? sec.a0 : 0, b = sec ? sec.b : M.n - 1;
  const meine = t => A.hand === 'LR' || t.h === A.hand;
  // E = die Griffe, die der Spieler greift (nur seine Hand); B = Töne, die die App im Takt dazu spielt
  const E = [], B = [];
  for (let j = a; j <= b; j++) { const m = G[j].toene.filter(meine), o = G[j].toene.filter(t => !meine(t)); if (m.length) E.push({ j, q: G[j].q, t: G[j].t, mids: m.map(t => t.m), hit: new Set(), st: 0 }); for (const t of o) B.push({ q: G[j].q, m: t.m, d: t.d || 0.4 }); }
  const L = { M, A, E, a, b, pos: 0, uhr: 0, falsch: 0, stocker: 0, wo: [], fertig: false, ergebnis: null, rot: null, rotBis: 0 };
  const ende = () => {
    const n = E.length, max = erlaubt(n), ok = A.stufe === 1 || L.stocker <= max, r = { ok, stocker: L.stocker, erlaubt: max, falsch: L.falsch, n, wo: L.wo.slice(), dauer: L.uhr, eigenTempo: null, meister: false, abw: null };
    if (A.stufe < 3) { const v = []; for (let i = 1; i < n; i++) { const soll = E[i].t - E[i - 1].t; if (soll > 0.05 && E[i].wait > 0) v.push(soll / E[i].wait); } if (v.length >= 4) r.eigenTempo = median(v); }
    else { const dq = E.filter(e => e.st === 1).map(e => Math.abs(e.dq)); r.abw = dq.length ? median(dq) : null; r.treffer = dq.length;
      r.meister = A.k < 0 && A.tempo >= 1 && L.stocker === 0 && dq.length === n && L.falsch <= K.meisterFalsch && dq.every(x => x <= K.meister); }
    L.fertig = true; L.ergebnis = r;
  };
  const falschTon = m => { const e = E[Math.min(L.pos, E.length - 1)]; if (e && !e.f) { e.f = 1; L.falsch++; } L.rot = m; L.rotBis = L.uhr + 0.4; };

  if (A.stufe < 3) {                                   /* --- Stufe 1 und 2: die App wartet --- */
    L.seit = 0; L.hilfe = false;
    L.taste = m => {
      if (L.fertig || !E.length) return; const e = E[L.pos];
      if (e.mids.includes(m)) { e.hit.add(m); if (e.hit.size === e.mids.length) { e.wait = L.pos ? L.uhr - L.letzt : 0; L.letzt = L.uhr; e.st = 1; L.pos++; L.seit = 0; L.hilfe = false; if (L.pos >= E.length) ende(); } return; }
      const v = E[L.pos - 1]; if (v && v.mids.includes(m) && L.uhr - L.letzt < 0.3) return; // später Ton des Akkords davor
      falschTon(m);
    };
    L.tick = dt => {
      if (L.fertig) return; L.uhr += dt; L.seit += dt; if (A.stufe !== 2 || L.hilfe || L.pos >= E.length) return;
      // Hilfe erst nach 1,5 s Stillstand – ein langer Ton im Lied ist kein Stillstand: was über 1 Schlag hinausgeht, kommt dazu
      const lang = L.pos ? Math.max(0, E[L.pos].t - E[L.pos - 1].t - M.schlag) : K.ersterGriff - K.hilfeNach;
      if (L.seit >= K.hilfeNach + lang) { L.hilfe = true; L.stocker++; L.wo.push(E[L.pos].j); }
    };
  } else {                                             /* --- Stufe 3: Im Takt – nichts wartet --- */
    const q0 = Math.floor((E.length ? E[0].q : 0) / M.bpb) * M.bpb, qEnd = (E.length ? E[E.length - 1].q : 0) + 1;
    L.q = q0 - M.bpb; L.bi = 0; L.np = Math.ceil(L.q); L.aus = null; // aus = Schlag-Zeit, seit der der Spieler „draußen“ ist
    const sps = () => A.tempo / M.schlag;               // Schläge je Sekunde
    L.taste = m => {
      if (L.fertig) return; let best = null;
      for (let i = L.pos; i < E.length && E[i].q <= L.q + K.fenster; i++) { const e = E[i]; if (e.st !== 2 && e.mids.includes(m) && !e.hit.has(m) && Math.abs(e.q - L.q) <= K.fenster && (!best || Math.abs(e.q - L.q) < Math.abs(best.q - L.q))) best = e; }
      if (!best) { if (!E.some(e => Math.abs(e.q - L.q) <= K.fenster && e.mids.includes(m))) falschTon(m); return; }
      best.hit.add(m); if (best.st === 0) { best.st = 1; best.dq = L.q - best.q; L.aus = null; }
    };
    L.tick = dt => {
      if (L.fertig) return; L.uhr += dt; L.q += dt * sps();
      while (L.np <= L.q) { const imTakt = ((L.np - q0) % M.bpb + M.bpb) % M.bpb === 0; if (aussen.puls && (L.np < q0 || A.hand === 'LR')) aussen.puls(imTakt, L.np < q0); L.np++; } // Einzählen immer, danach Puls nur, wenn beide Hände selbst spielen
      while (L.bi < B.length && B[L.bi].q <= L.q) { if (aussen.ton && B[L.bi].q >= q0) aussen.ton(B[L.bi].m, B[L.bi].d / A.tempo, 0.5); L.bi++; }
      while (L.pos < E.length && E[L.pos].q + K.fenster < L.q) { const e = E[L.pos]; if (e.st === 0) { e.st = 2; if (L.aus == null) { L.aus = e.q; L.ausN = 0; } if (++L.ausN > 1 && L.ausN % 4 === 1 && L.gez === L.aus) { L.stocker++; L.wo.push(e.j); } } L.pos++; } // wer lange draußen bleibt: je 4 weitere verpasste Griffe noch ein Stocker
      // draußen seit mehr als 1 Schlag → ein Stocker (einmal je Aussetzer)
      if (L.aus != null && L.aus !== L.gez && L.q - K.fenster - L.aus > K.stockSchlag) { L.gez = L.aus; L.stocker++; L.wo.push(E[Math.max(0, L.pos - 1)].j); }
      if (L.q >= qEnd + K.fenster) ende();
    };
  }
  /* Was die Oberfläche zeigen soll */
  L.bild = () => {
    const e = E[Math.min(L.pos, E.length - 1)], zeig = A.stufe === 1 || (A.stufe === 2 && L.hilfe), ak = e ? akkordBei(M, e.j) : null;
    return { titel: titel(M, A), stufe: A.stufe, hand: A.hand, leuchten: zeig && e && !L.fertig ? e.mids.filter(m => !e.hit.has(m)) : [], akkord: ak && A.stufe === 1 ? ak.name : '', hilfe: !!L.hilfe,
      rot: L.uhr < L.rotBis ? L.rot : null, griff: Math.min(L.pos, E.length), von: E.length, einzaehlen: A.stufe === 3 && E.length && L.q < Math.floor(E[0].q / M.bpb) * M.bpb ? Math.ceil(Math.floor(E[0].q / M.bpb) * M.bpb - L.q) : 0,
      stocker: L.stocker, falsch: L.falsch, fertig: L.fertig };
  };
  if (!E.length) ende();
  return L;
}

/* Vorspielen: liefert die Töne eines Auftrags als Liste [{nach: Sekunden, m, d}] – die Oberfläche spielt sie ab. */
function vorspiel(M, A, tempo) { const sec = A.k >= 0 ? M.abschnitte[A.k] : null, a = sec ? sec.a0 : 0, b = sec ? sec.b : M.n - 1, t0 = M.griffe[a].t, out = []; for (let j = a; j <= b; j++) for (const t of M.griffe[j].toene) if (A.hand === 'LR' || t.h === A.hand) out.push({ nach: (M.griffe[j].t - t0) / tempo, m: t.m, d: (t.d || 0.4) / tempo }); return out; }

/* ---------- 4. Nach dem Durchgang: Lernstand fortschreiben ---------- */

const tagPlus = (tag, n) => { const d = new Date(tag + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
function abschnittVon(M, j) { let k = 0; for (let i = 0; i < M.abschnitte.length; i++) if (M.abschnitte[i].a <= j) k = i; return k; }

/* heute = 'JJJJ-MM-TT'. Ändert stand. Rückgabe: {text, zurueck:k|null}  (text = ein Satz für die Anzeige) */
function abschluss(M, st, A, r, heute, sitz) {
  let text, zurueck = null; const fehl = sitz ? (sitz.reihe = r.ok ? 0 : (sitz.reihe || 0) + 1) : 0;
  const neben = r.falsch ? ` · ${r.falsch === 1 ? '1 Griff' : r.falsch + ' Griffe'} daneben` : '', sto = r.stocker ? `${r.stocker}× gestockt` : 'ohne Stocken';
  if (A.k >= 0) {
    const name = M.abschnitte[A.k].name;
    if (r.ok) {
      st.pos[A.k] = Math.max(st.pos[A.k], A.nr);
      if (A.stufe === 2 && st.tempo == null && r.eigenTempo) st.tempo = Math.min(K.tempoMax, Math.max(K.tempoMin, Math.floor(r.eigenTempo * 10))); // Start-Tempo = so schnell, wie er von sich aus spielt
      text = A.stufe === 1 ? `Abschnitt ${name}: ${K.haende[A.hand]} gezeigt` : A.nr === 6 ? `Abschnitt ${name} sitzt im Takt (${sto})` : `Abschnitt ${name} · ${K.stufen[A.stufe]}: geschafft (${sto})`;
    } else {
      text = `${sto} – erlaubt ${r.erlaubt === 1 ? 'ist 1' : 'sind ' + r.erlaubt}. Gleich noch mal`;
      if (A.stufe === 3 && fehl >= 2 && (st.tempo || 6) > K.tempoMin) { st.tempo = (st.tempo || 6) - 1; sitz.reihe = 0; text += ` · etwas langsamer (${st.tempo * 10} %)`; } // 2× hintereinander nicht im Takt → −10 %
    }
  } else {
    const wdh = st.ivl > 0 && st.due && st.due <= heute;
    if (r.ok) {
      if (st.ivl === 0) { st.ivl = K.leiter[0]; st.due = tagPlus(heute, st.ivl); text = 'Der ganze Song sitzt im Takt'; }
      else if (wdh) { const i = K.leiter.indexOf(st.ivl); st.ivl = K.leiter[Math.min(K.leiter.length - 1, i + 1)]; st.due = tagPlus(heute, st.ivl); text = `Sitzt noch – wieder in ${st.ivl} Tagen`; }
      else text = 'Durchgespielt';
      text += ` (${sto})`;
      if ((st.tempo || 6) < K.tempoMax) { st.tempo = (st.tempo || 6) + 1; text += ` · nächstes Mal ${st.tempo * 10} %`; }
      if (r.meister && !st.stern) { st.stern = 1; text += ' · Meisterprüfung bestanden'; }
    } else {
      // Kein Absprung zu einem Abschnitt (Felix 27.11.: das zerstört den Fluss) – der ganze Song kommt einfach wieder. zurueck = wo es am meisten hakte, nur als Hinweis; gezielt üben kann er per Antippen.
      const z = {}; for (const j of r.wo) { const k = abschnittVon(M, j); z[k] = (z[k] || 0) + 1; }
      let bk = -1; for (const k in z) if (bk < 0 || z[k] > z[bk]) bk = +k; zurueck = bk >= 0 ? bk : null;
      if (wdh) { const i = K.leiter.indexOf(st.ivl); st.ivl = K.leiter[Math.max(0, i - 1)]; st.due = tagPlus(heute, 1); }
      text = `${sto} – erlaubt sind ${r.erlaubt}. Gleich noch einmal`;
      if (fehl >= 2 && (st.tempo || 6) > K.tempoMin) { st.tempo = (st.tempo || 6) - 1; sitz.reihe = 0; text += ` · nächstes Mal ${st.tempo * 10} %`; }
    }
  }
  if (sitz) { sitz.laeufe = (sitz.laeufe || 0) + 1; if (r.ok) sitz.ok = (sitz.ok || 0) + 1; if (A.stufe > 1) { if (sitz.stErst == null) sitz.stErst = r.stocker; sitz.stLetzt = r.stocker; } if (r.ok) sitz.letztes = text; }
  return { text: text + (A.stufe > 1 && r.ok ? neben : ''), zurueck };
}

/* ---------- 5. „Los“: was kommt heute dran? ---------- */

/* songs = [{id, stand}] (stand darf fehlen = noch nie geübt) · app = {aktuell: id, wdhTag: 'JJJJ-MM-TT'} (ein kleiner Merkzettel für die ganze App)
   → {id, art: 'wdh' | 'weiter' | 'frei'} oder null (nichts in der Bibliothek) */
function los(songs, app, heute) {
  app = app || {};
  if (app.wdhTag !== heute) {                           // höchstens 1 Wiederholung am Tag, der am längsten fällige Song zuerst
    const f = songs.filter(s => s.stand && s.stand.ivl > 0 && s.stand.due && s.stand.due <= heute).sort((x, y) => x.stand.due < y.stand.due ? -1 : x.stand.due > y.stand.due ? 1 : 0);
    if (f.length) return { id: f[0].id, art: 'wdh' };
  }
  const offen = s => !s.stand || !(s.stand.ivl > 0), akt = songs.find(s => s.id === app.aktuell);
  if (akt && offen(akt)) return { id: akt.id, art: 'weiter' };
  const angef = songs.find(s => s.stand && offen(s) && s.stand.pos.some(p => p > 0)); if (angef) return { id: angef.id, art: 'weiter' };
  const neuer = songs.find(offen); if (neuer) return { id: neuer.id, art: 'weiter' };
  return akt ? { id: akt.id, art: 'frei' } : songs.length ? { id: songs[0].id, art: 'frei' } : null;
}

/* Sitzung: nur im Arbeitsspeicher. sitz = {start: Sekunden, reihe, laeufe, ok, stErst, stLetzt, gesagt} */
function sitzung(jetzt) { return { start: jetzt, reihe: 0, laeufe: 0, ok: 0, stErst: null, stLetzt: null, gesagt: false, letztes: '' }; }
/* Einmal je Sitzung: nach 12 Minuten oder 3 nicht geschafften Durchgängen in Folge → Text, sonst null */
function aufhoeren(sitz, jetzt) {
  if (sitz.gesagt) return null; const min = (jetzt - sitz.start) / 60;
  if (min < K.pauseMin && sitz.reihe < K.pauseFehl) return null;
  sitz.gesagt = true; const t = [];
  if (sitz.letztes) t.push(sitz.letztes + '.');
  t.push(`Heute ${sitz.laeufe} ${sitz.laeufe === 1 ? 'Durchgang' : 'Durchgänge'}, ${sitz.ok} geschafft.`);
  if (sitz.stErst != null && sitz.stLetzt != null && sitz.stLetzt < sitz.stErst) t.push(`Am Anfang ${sitz.stErst} Stocker, zuletzt ${sitz.stLetzt}.`);
  return { titel: 'Gute Stelle zum Aufhören', text: t.join(' '), grund: min >= K.pauseMin ? 'zeit' : 'fehl' };
}

return { K, modell, neu, uebernahme, abschnittUeben, naechstes, ganzerSong, schritteVon, fortschritt, titel, lauf, vorspiel, abschluss, los, sitzung, aufhoeren, erlaubt, akkordBei, tagPlus, TON };
});
