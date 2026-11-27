// Hand-Simulation (Kern): macht aus Noten + Fingersatz eine Handbahn und sucht Stellen, die für die Hand eng werden.
// Läuft in Node (require) und im Browser (window.HandSim). Einheit: w = Breite einer weißen Taste (23,5 mm).
(function (root, factory) { if (typeof module === 'object' && module.exports) module.exports = factory(); else root.HandSim = factory(); }(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const BLK = m => [1, 3, 6, 8, 10].includes(((m % 12) + 12) % 12);
  // x-Lage einer Taste in w: weiße Taste = Mitte, schwarze Taste = auf der Fuge
  const keyX = m => { let w = 0; for (let k = 21; k < m; k++) if (!BLK(k)) w++; return BLK(m) ? w : w + 0.5; };
  const MM = 23.5, ST = 164.5 / 12 / MM;   // ein Halbton im Schnitt in w (Oktave = 7 weiße Tasten)
  // Spannen je Fingerpaar in Halbtönen: [bequem, sicher maximal]. Gilt für beide Hände (Felix 27.11.2026: „geht bei beiden Händen gleich“). gemessen = von Felix am Klavier (14.11.2026), sonst geschätzt (Parncutt, an 1–5 skaliert).
  // 27.11.2026 nachgemessen (erster Finger auf C, zweiter auf der weitesten Taste): 2–3 bequem G / gerade so A; 3–4 nur F (G verkrampft, nicht sauber);
  // 4–5 locker F / gerade so G; 2–5 locker H / gerade so C. 2–4 und 3–5 daraus abgeleitet (zwischen den Nachbarwerten).
  const HAND = { '1-2': [7, 11, 'gemessen'], '1-3': [9, 12, 'geschätzt'], '1-4': [11, 13, 'geschätzt'], '1-5': [12, 14, 'gemessen'], '2-3': [7, 9, 'gemessen'], '2-4': [9, 11, 'abgeleitet'], '2-5': [11, 12, 'gemessen'],
    '3-4': [5, 5, 'gemessen'], '3-5': [7, 9, 'abgeleitet'], '4-5': [5, 7, 'gemessen'] };
  // so weit geht jeder Finger bequem zur Seite, gemessen von seiner Ruhelage in w: [zur Daumenseite, zur Kleinfingerseite] (Daumen kann untersetzen, kleiner Finger abspreizen)
  const REACH = { 1: [-2.2, 2.5], 2: [-1.0, 1.2], 3: [-0.7, 0.7], 4: [-0.7, 0.7], 5: [-0.6, 1.5] };
  const T = { GRIFF: 0.05, LAGE: 1.0, SPRUNG: 2.5, ZEIT0: 0.15, ZEIT_W: 0.035 };   // ab 1 w = Hand versetzt, ab 2,5 w = Sprung; Zeit, die ein Weg braucht
  function simHand(notes, hand) {   // notes: [{midi,start,dur,fing,mark}] einer Hand
    const s = hand === 'L' ? -1 : 1, ns = notes.slice().sort((a, b) => a.start - b.start || a.midi - b.midi), G = [];
    // Handfläche als „faule Hand“: Jeder gedrückte Finger erlaubt der Handfläche einen Bereich (so weit er sich bequem zur Seite strecken kann).
    // Die Hand bleibt liegen, solange sie darf, und rückt sonst nur so weit wie nötig. So zählt ein gestreckter Daumen nicht als Handbewegung.
    let prev = null;
    for (let i = 0; i < ns.length;) { let j = i; while (j < ns.length && ns[j].start - ns[i].start <= T.GRIFF) j++; const g = ns.slice(i, j);
      let lo = -1e9, hi = 1e9; const withF = g.filter(n => n.fing >= 1);
      for (const n of withF) { const x = keyX(n.midi), r = REACH[n.fing], a = s > 0 ? x - (n.fing - 3) - r[1] : x + (n.fing - 3) + r[0], b2 = s > 0 ? x - (n.fing - 3) - r[0] : x + (n.fing - 3) + r[1]; lo = Math.max(lo, a); hi = Math.min(hi, b2); }
      let c; if (!withF.length) c = g.reduce((t, n) => t + keyX(n.midi), 0) / g.length; else if (lo > hi) c = (lo + hi) / 2; else c = prev == null ? (lo + hi) / 2 : Math.min(hi, Math.max(lo, prev));
      prev = c; G.push({ start: g[0].start, end: Math.max(...g.map(n => n.start + n.dur)), notes: g, c, flags: [] }); i = j; }
    const st = { griffe: G.length, lagen: 0, spruenge: 0, eng: 0, weit: 0, zuWeit: 0, daumenSchwarz: 0, weg: 0, marken: 0 };
    G.forEach((g, i) => {
      // Griff: äußere Finger gegen die Spanne
      const f = g.notes.filter(n => n.fing >= 1).sort((a, b) => a.midi - b.midi);
      for (let a = 0; a < f.length; a++) for (let b = a + 1; b < f.length; b++) { const lo = Math.min(f[a].fing, f[b].fing), hi = Math.max(f[a].fing, f[b].fing), sp = HAND[lo + '-' + hi]; if (!sp) continue; const d = f[b].midi - f[a].midi;
        if (d > sp[1] && !g.flags.some(x => x.k === 'zuWeit')) { g.flags.push({ k: 'zuWeit', t: `Finger ${lo} und ${hi} müssten ${d} Halbtöne spannen, sicher gehen ${sp[1]} (${sp[2]})` }); st.zuWeit++; }
        else if (d > sp[0] && !g.flags.some(x => x.k === 'weit' || x.k === 'zuWeit')) { g.flags.push({ k: 'weit', t: `weiter Griff: Finger ${lo} und ${hi} spannen ${d} Halbtöne, bequem sind ${sp[0]} (${sp[2]})` }); st.weit++; } }
      if (g.notes.some(n => n.fing === 1 && BLK(n.midi))) st.daumenSchwarz++;
      if (g.notes.some(n => n.mark)) { st.marken++; g.flags.push({ k: 'marke', t: 'App-Marke: ' + [...new Set(g.notes.map(n => n.mark).filter(Boolean))].join(', ') }); }
      if (!i) return;
      const p = G[i - 1], move = Math.abs(g.c - p.c), dt = g.start - p.start; g.move = move; g.dir = Math.sign(g.c - p.c); st.weg += move;
      if (move >= T.LAGE) st.lagen++;
      if (move >= T.SPRUNG) { st.spruenge++; const need = T.ZEIT0 + T.ZEIT_W * move;
        if (dt < need) { st.eng++; g.flags.push({ k: 'eng', t: `Sprung über ${move.toFixed(1)} Tasten in ${dt.toFixed(2)} s – dafür bräuchte die Hand etwa ${need.toFixed(2)} s` }); }
        else g.flags.push({ k: 'sprung', t: `Hand springt ${move.toFixed(1)} Tasten ${g.dir > 0 ? 'nach rechts' : 'nach links'} (Zeit: ${dt.toFixed(2)} s)` }); }
    });
    st.wegCm = st.weg * MM / 10; return { hand, G, st };
  }
  function simSong(notes) {   // notes mit .hand 'L'/'R'
    const out = {}; for (const H of ['L', 'R']) { const ns = notes.filter(n => n.hand === H); if (ns.length) out[H] = simHand(ns, H); } return out;
  }
  return { simHand, simSong, keyX, BLK, HAND, REACH, T, MM };
}));
