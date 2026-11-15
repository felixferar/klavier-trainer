/*
 * fingering.js – Fingersatz-Kern der Klavier-App
 * Rechte und linke Hand (links = an D gespiegelt), einstimmig; Akkorde über computeHand().
 *
 * Keine Abhängigkeiten. Läuft im Browser (window.Fingering) und in Node (require).
 *
 * Rechenweg: Regeln + Kosten + Viterbi (dynamische Programmierung, angelehnt an Parncutt 1997).
 *   - Unmögliches kostet INF (Stufe A: spielbar).
 *   - Tonleitern/Arpeggien ab einer Mindestlänge folgen dem Lehrbuch-Muster (Stufe B).
 *   - Gleiche Stellen bekommen den gleichen Fingersatz, gemeinsam optimiert (Stufe C).
 *   - Deine Vorgaben (fixed) gehen immer vor.
 * Alle Zahlen stehen als benannte Konstanten in T (Zeiten) und K (Kosten).
 *
 * Eingabe:  notes = [{midi, start, dur}, ...]  (Sekunden)
 * Ausgabe:  siehe computeFingering()
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Fingering = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const VERSION = '0.7.0';
  const INF = Infinity;

  // ===================================================================
  // 1. Zeit-Grenzen (Sekunden)
  // ===================================================================
  const T = {
    FAST_IOI: 0.20,          // Anschlagsabstand darunter = "schnelle Folge"
    REPEAT_MIN: 0.07,        // gleiche Taste, gleicher Finger: schneller ist unmöglich
    SAME_FINGER_MIN: 0.10,   // gleicher Finger auf andere Taste: Grundzeit …
    SAME_FINGER_PER_ST: 0.005, // … plus je Halbton
    NO_PAUSE: 0.3,           // v0.7: Lücke zwischen Loslassen und nächstem Anschlag, ab der die Hand neu ansetzen kann
    SHIFT_MIN: 0.15,         // Lagenwechsel (Hand springt): Grundzeit …
    SHIFT_PER_ST: 0.01,      // … plus je Halbton über der bequemen Spanne
    HELD_OVERLAP: 0.15,      // vorige Note klingt mind. so lange weiter …
    HELD_OVERLAP_REL: 0.5,   // … und mind. die halbe Zeit bis zum nächsten Ton = "gehalten" (wie gleichzeitig)
    CHORD: 0.03,             // Anschläge näher beieinander = gleichzeitig (Akkord)
    RUN_MAX_IOI: 0.8,        // größere Lücke unterbricht Tonleiter/Arpeggio
    PHRASE_GAP: 0.35,        // Pause dazwischen trennt Phrasen
  };

  // Stil "einfach" (für Selbstlerner, Standard in der App ab v5.04): Lehrbuch-Tonleiter-Fingersatz nur in schnellen Läufen;
  // bei langsamen Tönen wird die Hand versetzt (in Ruhe, während des langen Tons) statt unter-/übergesetzt.
  // Anlass: Flaggen des Nutzers in "Fly Me To The Moon" (A-G-F-E mit 3-2-1-3, C-D-F mit 2-3-1).
  const EASY = {
    RUN_MAX_IOI: 0.30,       // Tonleiter-/Arpeggio-Muster nur, wenn die Töne höchstens so weit auseinander liegen
    SLOW: 1.2,              // ab diesem Anschlagsabstand (= nach einem langen Ton) ist Zeit, die Hand in Ruhe zu versetzen
    SHIFT_SLOW: 2.0,         // Lagenwechsel mit Zeit (statt 4)
    SAME_SLOW: 2.0,          // gleicher Finger rückt auf die Nachbartaste, mit Zeit (statt 4)
    CROSS_SLOW: 3.0,         // Unter-/Übersetzen, obwohl Zeit zum Versetzen wäre: zusätzlich
    SAME_STEP: 8.0,          // v0.5: derselbe Finger auf zwei Tasten ≤ STEP_MAX auseinander, direkt nacheinander (immer, auch nach langen Tönen).
                             // Anlass: Flaggen 15.11. (F1→E1, D1→C1, F4→A4) – Rutschen soll teurer sein als sauberes Über-/Untersetzen.
    STEP_MAX: 4,
    REPEAT_CHANGE: 6.0,      // v0.7: Tonwiederholung mit Fingerwechsel (Flagge 15.11. F3→F2) – im Stil einfach bleibt man auf dem Finger
    LONG: 1.0,               // langer Ton (Sekunden)
    LAND_LONG: 0.5,          // Versetzen auf einen langen Ton ist etwas günstiger als mitten in der Phrase
  };
  const MODE = { easy: false };

  // ===================================================================
  // 2. Kosten (Punkte). Höher = schlechter.
  // ===================================================================
  const K = {
    // Spannweite (zwei Finger nacheinander, Hand bleibt liegen)
    SPAN_LARGE_THUMB: 0.5,   // je Halbton über "entspannt", Paar mit Daumen (bis "bequem" kaum Mühe)
    SPAN_LARGE: 1.0,         // je Halbton über "entspannt", Paar ohne Daumen
    SPAN_SMALL_THUMB: 0.5,   // je Halbton enger als entspannt, mit Daumen
    SPAN_SMALL: 2.0,         // je Halbton enger als entspannt, ohne Daumen
    STRETCH: 1.0,            // zusätzlich je Halbton über "bequem" (Töne nacheinander: Hand darf sich kurz öffnen)
    REACH: 0.2,              // Daumen-Paar weiter als die natürliche Lage des Fingers (1-2-3-4-5 auf C-D-E-F-G): je Halbton.
                             // Darum Quinte/Oktave lieber 1–5 als 1–4 (offener Punkt aus dem Blindtest).
    // Über-/Untersetzen (nur mit Daumen)
    CROSS_BASE: { 2: 2.5, 3: 2.25, 4: 2.75, 5: 99 },
    CROSS_PER_ST: 1.0,       // je Halbton über die bequeme Kreuzungsweite
    CROSS_LEVEL_SAME: 1.0,   // beide Tasten weiß (oder beide schwarz)
    CROSS_WHITE_TO_BLACK: 3.0, // untere Taste weiß, obere schwarz
    CROSS_NEEDLESS: 1.5,     // Unter-/Übersetzen, obwohl die Töne ringsum (±3) in eine Fünftonlage passen
    // Lagenwechsel (Hand muss springen)
    SHIFT: 4.0,
    SHIFT_PER_ST: 0.3,
    MOVE_FAST: 2.0,          // Sprung mit knapper Zeit
    TWIST: 3.0,              // verdrehte Fingerfolge (z. B. 3 dann 2 aufwärts, 5 über den Daumen): Hand muss umgreifen
    // Drei-Ton-Regeln (Parncutt): versteckter Lagenwechsel über drei Töne
    HIDDEN_SHIFT: 2.0,       // 1. und 3. Ton passen nicht mehr in eine Handlage (oder gleicher Finger auf anderer Taste)
    HIDDEN_HALF: 1.0,        // 1. und 3. Ton nur mit Dehnung in einer Handlage
    THREE_FOUR_FIVE: 0.5,    // 3, 4 und 5 direkt hintereinander (beliebige Reihenfolge)
    REPEAT_ZIGZAG: 2.0,      // Tonwiederholung mit Fingern hin und her (3-1-2 statt 3-2-1)
    // gleicher Finger
    SAME_FINGER: 4.0,        // gleicher Finger kurz hintereinander auf verschiedenen Tasten
    SAME_FINGER_PER_ST: 0.2,
    NO_PAUSE_SAME: 25.0,     // v0.7: derselbe Finger auf zwei verschiedenen Tasten OHNE Pause (Lücke < NO_PAUSE) – praktisch verboten, jeder Abstand, jeder Stil (Flagge 15.11. A3→D3)
    REPEAT_SAME_FAST: 1.0,   // schnelle Tonwiederholung mit demselben Finger
    REPEAT_CHANGE_FAST: 0.25, // Tonwiederholung mit Fingerwechsel, schnell (sinnvoll)
    REPEAT_CHANGE_SLOW: 2.0, // Tonwiederholung mit Fingerwechsel, langsam (meist unnötig)
    // schwache Finger
    WEAK: 0.25,              // Finger 4 oder 5
    WEAK_FAST: 0.0,          // Finger 4 oder 5 einzeln in schneller Folge (Wirkung steckt in den Paaren unten)
    THREE_FOUR: 0.25,        // 3 direkt gefolgt von 4
    FOUR_FIVE: 0.25,         // 4 und 5 direkt nacheinander
    WEAK_PAIR_FAST: 0.25,     // zusätzlich, wenn 3→4 oder 4↔5 schnell aufeinander folgen
    // schwarze Tasten
    THUMB_BLACK: 1.5,        // Daumen auf schwarzer Taste
    THUMB_BLACK_NB: 1.0,     // … und Nachbarton weiß
    FIVE_BLACK_NB: 1.0,      // 5 auf schwarz, Nachbarton weiß
    // Lehrbuch-Muster
    START_DEVIATION: 1.5,    // Einstiegsfinger einer Tonleiter nicht wie im Buch (mitten im Stück)
    CROSS_AT_EDGE: 2.0,
    CROSS_AT_TURN: 1.5,      // Unter-/Übersetzen in einen Wendeton hinein oder aus ihm heraus (Hand kehrt sofort um)      // Unter-/Übersetzen in den letzten oder aus dem ersten Ton einer Phrase (lohnt nicht)
    // Notfall
    CONFLICT: 50.0,          // Ersatzkosten, wenn wirklich kein spielbarer Weg existiert
    BIG: 1000.0,             // Wiederholung: gemeinsamer Fingersatz wäre hier unspielbar
  };

  // Weitere Regeln
  const R = {
    SCALE_MIN_RUN: 6,        // ab so vielen Tönen in eine Richtung gilt ein Lauf als Tonleiter
    ARP_MIN_RUN: 4,          // … als Arpeggio (4 = gebrochener Dreiklang mit Oktave, z. B. C-E-G-C = 1-2-3-5)
    RESUME_AFTER_THUMBS: 2,  // Korrektur in einer Tonleiter: so viele Daumen-Töne davor und danach sind frei, dann gilt wieder das Muster
    REPEAT_MIN_LEN: 4,       // Wiederholung ab so vielen gleichen Tönen
    RHYTHM_TOL_REL: 0.25,    // "ungefähr gleicher Rhythmus": ±25 % …
    RHYTHM_TOL_ABS: 0.06,    // … oder ±60 ms
    OPEN_REL: 0.10,          // "offen", wenn zweitbeste Lösung < 10 % teurer …
    OPEN_FLOOR: 3,         // … gemessen an den Kosten der Umgebung (mind. 5 Punkte)
    OPEN_WINDOW: 2,          // Umgebung: ±4 Töne
  };

  // ===================================================================
  // 3. Hand
  // ===================================================================
  const PROFILES = {
    meine:    { name: 'meine Werte', span15: { comf: 12, max: 14 }, span12: { comf: 7, max: 11 } },
    standard: { name: 'Standard',    span15: { comf: 12, max: 14 } },
    klein:    { name: 'kleine Hand', span15: { comf: 10, max: 12 } },
  };

  // Parncutt (1997), rechte Hand, Halbtöne:
  // [MinPrac, MinComf, MinRel, MaxRel, MaxComf, MaxPrac]
  const PARNCUTT = {
    '1-2': [-5, -3, 1, 5, 8, 10], '1-3': [-4, -2, 3, 7, 10, 12],
    '1-4': [-3, -1, 5, 9, 12, 14], '1-5': [-1, 1, 7, 10, 13, 15],
    '2-3': [1, 1, 1, 2, 3, 5], '2-4': [1, 1, 3, 4, 5, 7], '2-5': [2, 2, 5, 6, 8, 10],
    '3-4': [1, 1, 1, 2, 2, 4], '3-5': [1, 1, 3, 4, 5, 7], '4-5': [1, 1, 1, 2, 3, 5],
  };
  // Kreuzen mit dem Daumen (Daumen unter Finger k / Finger k über Daumen): bequem / maximal
  const NAT = { 2: 2, 3: 4, 4: 5, 5: 7 };   // natürliche Fünftonlage: Abstand vom Daumen in Halbtönen
  const CROSS_LIMITS = { 2: { comf: 3, max: 6 }, 3: { comf: 4, max: 6 }, 4: { comf: 2, max: 5 }, 5: { comf: 0, max: 0 } };

  // Baut die Spannen-Tabelle aus den Handwerten.
  // 1–5 und 1–2 kommen direkt aus deinen Angaben, 1–3 und 1–4 werden dazwischen
  // gelegt (Anteile wie bei Parncutt), Paare ohne Daumen mit dem Handfaktor skaliert.
  function pairTable(profile) {
    profile = profile || PROFILES.meine;
    const s15 = profile.span15;
    const r = s15.max / 15, rc = s15.comf / 13;
    const s12 = profile.span12 || { comf: Math.round(8 * rc), max: Math.round(10 * r) };
    const frac = { 2: 0, 3: 0.4, 4: 0.8, 5: 1 };
    const t = {};
    for (const key in PARNCUTT) {
      const [minPrac, minComf, minRel, maxRel0, maxComf0, maxPrac0] = PARNCUTT[key];
      const lo = +key[0], hi = +key[2];
      let maxComf, maxPrac;
      if (lo === 1) {
        maxComf = Math.round(s12.comf + frac[hi] * (s15.comf - s12.comf));
        maxPrac = Math.floor(s12.max + frac[hi] * (s15.max - s12.max) + 1e-9);
      } else {
        maxComf = Math.round(maxComf0 * rc);
        maxPrac = Math.round(maxPrac0 * r);
      }
      maxComf = Math.max(minRel, Math.min(maxComf, maxPrac));
      const maxRel = Math.max(minRel, Math.min(Math.round(maxRel0 * rc), maxComf));
      const cl = CROSS_LIMITS[hi];
      t[key] = {
        minPrac, minComf, minRel, maxRel, maxComf, maxPrac,
        crossComf: lo === 1 ? Math.round(cl.comf * r) : 0,
        crossMax: lo === 1 ? Math.round(cl.max * r) : 0,
      };
    }
    return t;
  }

  // ===================================================================
  // 4. Hilfen
  // ===================================================================
  const NAMES = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'As', 'A', 'B', 'H'];
  const BLACK = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0];
  const pcOf = m => ((m % 12) + 12) % 12;
  const isBlack = m => BLACK[pcOf(m)] === 1;
  const nameOf = m => NAMES[pcOf(m)];
  const nm = nt => NAMES[pcOf(nt.o != null ? nt.o : nt.midi)];
  // Linke Hand: Spiegelung an D (MIDI 62). Weiß bleibt weiß, schwarz bleibt schwarz, Abstände bleiben gleich.
  const MIRROR = 124;
  const mir = (m, hand) => (hand === 'L' ? MIRROR - m : m);
  const ht = n => `${n} ${Math.abs(n) === 1 ? 'Halbton' : 'Halbtöne'}`;
  const fmt = x => (Math.round(x * 10) / 10).toString().replace('.', ',');

  // ===================================================================
  // 5. Kostenfunktionen
  // ===================================================================
  // Übergang von Note a (Finger f) zu Note b (Finger g). det: optional Array für Begründungen.
  function trans(a, b, f, g, P, det) {
    const d = b.midi - a.midi, ioi = b.start - a.start;
    const held = isHeld(a, b, P);
    let c = 0;
    const add = (p, code, txt) => { c += p; if (det) det.push({ p, code, txt }); };
    const impossible = (code, txt) => { if (det) det.push({ p: INF, code, txt }); return INF; };

    if (f === g) {
      if (d === 0) {
        if (ioi < T.REPEAT_MIN) return impossible('repeat-too-fast', 'Tonwiederholung zu schnell für einen Finger');
        if (ioi < T.FAST_IOI) add(K.REPEAT_SAME_FAST, 'repeat-same', 'schnelle Tonwiederholung mit demselben Finger');
        return c;
      }
      const ad = Math.abs(d);
      if (held) return impossible('held-same', 'derselbe Finger müsste zwei Tasten gleichzeitig halten');
      const need = T.SAME_FINGER_MIN + T.SAME_FINGER_PER_ST * ad;
      if (ioi < need) return impossible('same-too-fast', `derselbe Finger schafft ${ht(ad)} nicht in ${fmt(ioi * 1000)} ms`);
      if (b.start - (a.start + a.dur) < T.NO_PAUSE) add(K.NO_PAUSE_SAME, 'same-no-pause', `Finger ${f} müsste ohne Pause von einer Taste auf die andere – nie`);
      if (MODE.easy && ioi >= EASY.SLOW) { add(EASY.SAME_SLOW + K.SAME_FINGER_PER_ST * ad, 'same-finger', `Finger ${f} rückt in Ruhe weiter (Hand versetzen)`); if (a.inPos && b.inPos) add(K.CROSS_NEEDLESS, 'shift-needless', 'Versetzen unnötig – die Töne ringsum passen in eine Handlage'); }
      else add(K.SAME_FINGER + K.SAME_FINGER_PER_ST * ad, 'same-finger', `derselbe Finger direkt nacheinander auf zwei Tasten`);
      if (MODE.easy && ad <= EASY.STEP_MAX) add(EASY.SAME_STEP, 'same-step', `Finger ${f} spielt zwei Nachbartasten direkt nacheinander – lieber über-/untersetzen`);
      if (MODE.easy && b.dur >= EASY.LONG) add(-EASY.LAND_LONG, 'land-long', 'rückt auf einen langen Ton – danach hat die Hand Ruhe');
      if (ioi < 2 * need) add(K.MOVE_FAST, 'move-fast', 'wenig Zeit für den Sprung');
      return c;
    }
    if (d === 0) {
      if (ioi < T.FAST_IOI) add(K.REPEAT_CHANGE_FAST, 'repeat-change', 'schnelle Tonwiederholung mit Fingerwechsel');
      else add(K.REPEAT_CHANGE_SLOW, 'repeat-change', 'Fingerwechsel auf derselben Taste (langsam, meist unnötig)');
      if (MODE.easy) add(EASY.REPEAT_CHANGE, 'repeat-change-easy', 'gleiche Taste nochmal – auf demselben Finger bleiben');
      return c;
    }

    const lo = Math.min(f, g), hi = Math.max(f, g), p = P[lo + '-' + hi];
    const D = f < g ? d : -d;          // Abstand vom niedrigeren zum höheren Finger
    let connected = false, crossing = false, dist = 0;
    if (lo === 1 && D < 0) {
      dist = -D;
      if (dist <= p.crossMax) { connected = true; crossing = true; }
    } else if (D >= p.minPrac && D <= p.maxPrac) connected = true;

    if (connected) {
      if (crossing) {
        const txt = g === 1 ? `Daumenuntersatz (${ht(dist)})` : `Finger ${g} setzt über den Daumen (${ht(dist)})`;
        add(K.CROSS_BASE[hi] + K.CROSS_PER_ST * Math.max(0, dist - p.crossComf), 'cross', txt);
        if (MODE.easy && ioi > EASY.RUN_MAX_IOI) add(EASY.CROSS_SLOW, 'cross-slow', 'Untersetzen bei ruhigem Tempo – Hand versetzen ist einfacher');
        const low = a.midi < b.midi ? a : b, high = a.midi < b.midi ? b : a;
        if (low.black === high.black) add(K.CROSS_LEVEL_SAME, 'cross-level', 'Untersetzen zwischen gleich hohen Tasten');
        else if (!low.black && high.black) add(K.CROSS_WHITE_TO_BLACK, 'cross-wb', 'Untersetzen von weißer auf höhere schwarze Taste');
      } else {
        const th = lo === 1;
        if (D > p.maxRel) add((th ? K.SPAN_LARGE_THUMB : K.SPAN_LARGE) * (D - p.maxRel), 'span-large', `weite Spanne ${lo}–${hi} (${ht(D)})`);
        if (D > p.maxComf) add(K.STRETCH * (D - p.maxComf), 'stretch', `Spanne ${lo}–${hi} über bequem (${D} statt höchstens ${p.maxComf})`);
        if (D < p.minRel) add((th ? K.SPAN_SMALL_THUMB : K.SPAN_SMALL) * (p.minRel - D), 'span-small', `enge Spanne ${lo}–${hi} (${ht(D)})`);
        if (th && D > NAT[hi]) add(K.REACH * (D - NAT[hi]), 'reach', `${hi} greift weiter als in der natürlichen Lage (${ht(D)})`);
      }
      if (crossing && a.inPos && b.inPos) add(K.CROSS_NEEDLESS, 'cross-needless', 'Untersetzen unnötig – die Töne ringsum passen in eine Handlage');
      if (crossing && b.turn) add(K.CROSS_AT_TURN, 'cross-turn', 'Untersetzen in einen Wendeton – die Hand kehrt gleich wieder um');
      if (crossing && a.turn) add(K.CROSS_AT_TURN, 'cross-turn', 'Übersetzen direkt nach einem Wendeton');
      if (crossing && (b.phraseEnd || a.phraseStart)) add(K.CROSS_AT_EDGE, 'cross-edge', b.phraseEnd ? 'Untersetzen in den Schlusston lohnt nicht' : 'Untersetzen gleich nach dem Anfangston lohnt nicht');
      if (f === 3 && g === 4) add(K.THREE_FOUR, '3-4', '3 gefolgt von 4');
      if (lo === 4 && hi === 5) add(K.FOUR_FIVE, '4-5', '4 und 5 direkt nacheinander');
      if (ioi < T.FAST_IOI && ((f === 3 && g === 4) || (lo === 4 && hi === 5))) add(K.WEAK_PAIR_FAST, 'weak-fast', 'schwache Finger schnell hintereinander');
      if (g === 1 && b.black && !a.black) add(K.THUMB_BLACK_NB, 'thumb-black-nb', 'Daumen geht von weißer auf schwarze Taste');
      if (f === 1 && a.black && !b.black) add(K.THUMB_BLACK_NB, 'thumb-black-nb', 'Daumen kommt von schwarzer Taste');
      if (g === 5 && b.black && !a.black) add(K.FIVE_BLACK_NB, 'five-black-nb', '5 geht auf schwarze Taste');
      if (f === 5 && a.black && !b.black) add(K.FIVE_BLACK_NB, 'five-black-nb', '5 kommt von schwarzer Taste');
      return c;
    }

    // Lagenwechsel: Hand muss springen
    let excess;
    if (lo === 1 && D < 0) excess = dist - p.crossComf;
    else if (D > p.maxPrac) excess = D - p.maxComf;
    else excess = p.minComf - D;
    excess = Math.max(1, excess);
    if (held) {
      if (D > p.maxPrac) return impossible('held-span', `Spanne ${lo}–${hi} von ${ht(D)}n über deiner Grenze ${p.maxPrac}, vorige Taste noch gehalten`);
      return impossible('held-twist', `verdrehte Fingerfolge ${f}→${g}, vorige Taste noch gehalten`);
    }
    const need = T.SHIFT_MIN + T.SHIFT_PER_ST * excess;
    if (ioi < need) return impossible('shift-too-fast', `Handsprung ${f}→${g} in ${fmt(ioi * 1000)} ms nicht machbar`);
    if (MODE.easy && ioi >= EASY.SLOW) { add(EASY.SHIFT_SLOW + K.SHIFT_PER_ST * excess, 'shift', `Hand in Ruhe versetzen (${ht(Math.abs(d))}, ${f}→${g})`); if (a.inPos && b.inPos) add(K.CROSS_NEEDLESS, 'shift-needless', 'Versetzen unnötig – die Töne ringsum passen in eine Handlage'); }
    else add(K.SHIFT + K.SHIFT_PER_ST * excess, 'shift', `Lagenwechsel: Hand springt (${ht(Math.abs(d))}, ${f}→${g})`);
    if ((lo === 1 && D < 0 && hi === 5) || (lo !== 1 && D < p.minPrac)) add(K.TWIST, 'twist', `verdrehte Fingerfolge ${f}→${g}: Hand muss umgreifen`);
    if (ioi < 2 * need) add(K.MOVE_FAST, 'move-fast', 'wenig Zeit für den Sprung');
    return c;
  }

  // Lässt sich Note a noch halten, während b angeschlagen wird? Nur wenn irgendein Fingerpaar
  // die Spanne in einer Handlage schafft. Sonst muss a vorher losgelassen werden (Pedal / andere Hand).
  function canHold(a, b, P) {
    const d = b.midi - a.midi;
    if (d === 0) return false;
    for (let f = 1; f <= 5; f++) for (let g = 1; g <= 5; g++) {
      if (f === g) continue;
      const lo = Math.min(f, g), hi = Math.max(f, g), p = P[lo + '-' + hi], D = f < g ? d : -d;
      if (lo === 1 && D < 0 ? (hi !== 5 && -D <= p.crossMax) : (D >= p.minPrac && D <= p.maxPrac)) return true;
    }
    return false;
  }
  function overlaps(a, b) {
    const ov = (a.start + a.dur) - b.start;
    return ov > T.HELD_OVERLAP && ov > T.HELD_OVERLAP_REL * (b.start - a.start);
  }
  function isHeld(a, b, P) { return overlaps(a, b) && canHold(a, b, P); }

  function isPhraseBreak(a, b) {
    return b.start - (a.start + a.dur) > T.PHRASE_GAP || b.start - a.start > T.RUN_MAX_IOI;
  }

  // Kosten einer einzelnen Note mit Finger f.
  function nodeCost(nt, f, det) {
    let c = 0;
    const add = (p, code, txt) => { c += p; if (det) det.push({ p, code, txt }); };
    if (f >= 4) {
      add(K.WEAK, 'weak', `Finger ${f} ist schwächer`);
      if (nt.fast) add(K.WEAK_FAST, 'weak-fast', `Finger ${f} in schneller Folge`);
    }
    if (f === 1 && nt.black) add(K.THUMB_BLACK, 'thumb-black', 'Daumen auf schwarzer Taste');
    return c;
  }

  // Art der Bewegung zwischen zwei Tönen (ohne Zeit): 'repeat' | 'same' | 'hand' | 'cross' | 'shift'
  function moveKind(a, b, f, g, P) {
    const d = b.midi - a.midi;
    if (d === 0) return 'repeat';
    if (f === g) return 'same';
    const lo = Math.min(f, g), hi = Math.max(f, g), p = P[lo + '-' + hi], D = f < g ? d : -d;
    if (lo === 1 && D < 0) return -D <= p.crossMax ? 'cross' : 'shift';
    return (D >= p.minPrac && D <= p.maxPrac) ? 'hand' : 'shift';
  }

  // Drei Töne n1, n2, n3 mit Fingern a, b, c. Findet Lagenwechsel, die man an
  // zwei Tönen allein nicht sieht (z. B. Daumen hüpft E→D, während 2 dazwischen liegt).
  function triCost(n1, n2, n3, a, b, c, P, det) {
    let cost = 0;
    const add = (p, code, txt) => { cost += p; if (det) det.push({ p, code, txt }); };
    if (a !== b && b !== c && a !== c && a + b + c === 12 && Math.min(a, b, c) === 3) add(K.THREE_FOUR_FIVE, '345', '3, 4 und 5 direkt hintereinander');
    if (n1.midi === n2.midi && n2.midi === n3.midi && (b - a) * (c - b) < 0) add(K.REPEAT_ZIGZAG, 'repeat-zigzag', 'Fingerwechsel auf derselben Taste hin und her');
    const k1 = moveKind(n1, n2, a, b, P), k2 = moveKind(n2, n3, b, c, P);
    // Kreuzen/Springen: schon einzeln bezahlt. Fingerwechsel auf derselben Taste als Vorbereitung (k2) ist erlaubt;
    // rückt danach aber derselbe Finger weiter (k1 = Wiederholung, k2 = Weitergehen), hat sich die Hand verschoben.
    if (!((k1 === 'hand' || k1 === 'repeat') && k2 === 'hand')) return cost;
    if (n1.midi === n3.midi) {      // hin und zurück (D–E–D): kommt ein anderer Finger auf dieselbe Taste zurück, ist die Hand gewandert
      if (a !== c && n1.start !== n3.start) add(Math.abs(a - c) >= 2 ? K.HIDDEN_SHIFT : K.HIDDEN_HALF, 'hidden-back', `${nm(n1)} erst mit ${a}, dann mit ${c}: Hand verschiebt sich`);
      return cost;
    }
    if (a === c) { add(K.HIDDEN_SHIFT, 'hidden', `Finger ${a} wechselt von ${nm(n1)} auf ${nm(n3)}: Hand verschiebt sich`); return cost; }
    const lo = Math.min(a, c), hi = Math.max(a, c), p = P[lo + '-' + hi];
    const D = a < c ? n3.midi - n1.midi : n1.midi - n3.midi;
    let inPrac, inComf;
    if (lo === 1 && D < 0) { inPrac = hi !== 5 && -D <= p.crossMax; inComf = hi !== 5 && -D <= p.crossComf; }
    else { inPrac = D >= p.minPrac && D <= p.maxPrac; inComf = D >= p.minComf && D <= p.maxComf; }
    if (!inPrac) add(K.HIDDEN_SHIFT, 'hidden', `${nm(n1)} (${a}) und ${nm(n3)} (${c}) passen nicht in eine Handlage: Hand verschiebt sich`);
    else if (!inComf) add(K.HIDDEN_HALF, 'hidden-half', `${nm(n1)} (${a}) und ${nm(n3)} (${c}) nur mit Dehnung in einer Handlage`);
    return cost;
  }

  // ===================================================================
  // 6. Modell + Viterbi
  // ===================================================================
  function buildModel(notesIn, profile, hand) {
    hand = hand === 'L' ? 'L' : 'R';
    const P = pairTable(profile);
    const order = notesIn.map((_, i) => i).sort((x, y) => (notesIn[x].start - notesIn[y].start) || (mir(notesIn[x].midi, hand) - mir(notesIn[y].midi, hand)));
    const notes = order.map(i => ({ midi: mir(notesIn[i].midi, hand), o: notesIn[i].midi, pc: pcOf(notesIn[i].midi), start: notesIn[i].start, dur: notesIn[i].dur || 0, src: i }));
    const n = notes.length;
    for (let i = 0; i < n; i++) {
      const nt = notes[i];
      nt.black = isBlack(nt.midi);
      const prev = i > 0 ? nt.start - notes[i - 1].start : INF;
      const next = i < n - 1 ? notes[i + 1].start - nt.start : INF;
      nt.fast = Math.min(prev, next) < T.FAST_IOI;
    }
    for (let i = 0; i < n - 1; i++)
      notes[i].mustRelease = overlaps(notes[i], notes[i + 1]) && notes[i + 1].midi !== notes[i].midi && !canHold(notes[i], notes[i + 1], P);
    for (let i = 0; i < n; i++) {
      notes[i].phraseStart = i === 0 || isPhraseBreak(notes[i - 1], notes[i]);
      notes[i].phraseEnd = i === n - 1 || isPhraseBreak(notes[i], notes[i + 1]);
      notes[i].turn = i > 0 && i < n - 1 && (notes[i].midi - notes[i - 1].midi) * (notes[i + 1].midi - notes[i].midi) < 0;
    }
    for (let i = 0; i < n; i++) {     // passt die Umgebung (±3 Töne) in eine Fünftonlage?
      let lo = INF, hi = -INF;
      for (let j = Math.max(0, i - 3); j <= Math.min(n - 1, i + 3); j++) { lo = Math.min(lo, notes[j].midi); hi = Math.max(hi, notes[j].midi); }
      notes[i].inPos = hi - lo <= NAT[5];
    }
    const N = new Float64Array(n * 5), Tm = new Float64Array(Math.max(0, n - 1) * 25);
    for (let i = 0; i < n; i++) for (let f = 1; f <= 5; f++) N[i * 5 + f - 1] = nodeCost(notes[i], f);
    for (let i = 0; i < n - 1; i++)
      for (let f = 1; f <= 5; f++) for (let g = 1; g <= 5; g++)
        Tm[i * 25 + (f - 1) * 5 + g - 1] = trans(notes[i], notes[i + 1], f, g, P);
    const TRI = new Float64Array(n * 125);   // Mitte i: Finger (i-1, i, i+1)
    for (let i = 1; i < n - 1; i++)
      for (let a = 1; a <= 5; a++) for (let b = 1; b <= 5; b++) for (let c = 1; c <= 5; c++)
        TRI[i * 125 + (a - 1) * 25 + (b - 1) * 5 + c - 1] = triCost(notes[i - 1], notes[i], notes[i + 1], a, b, c, P);
    const pos = new Array(n); order.forEach((src, k) => { pos[src] = k; });
    return { notes, n, N, T: Tm, TRI, P, order, pos, hand, profile: profile || PROFILES.meine };
  }

  // Viterbi 2. Ordnung: Zustand = (Finger der vorigen Note, Finger dieser Note),
  // damit Drei-Ton-Regeln exakt mitgerechnet werden.
  // mask[i]: Bitmaske erlaubter Finger (Bit 0 = Finger 1). extra: Zusatzkosten n*5.
  function viterbi(M, mask, extra) {
    const n = M.n, N = M.N, Tm = M.T, TRI = M.TRI;
    const A = new Float64Array(n * 25).fill(INF), B = new Float64Array(n * 25).fill(INF);
    const back = new Int8Array(n * 25).fill(-1);
    const relax = new Uint8Array(n);
    const marg = new Float64Array(n * 5).fill(INF);
    if (n === 0) return { A, B, path: [], total: 0, relax, marg };
    const ex = (i, f) => (extra ? extra[i * 5 + f] : 0);
    const mk = i => (mask[i] || 31);
    for (let f = 0; f < 5; f++) if (mk(0) & (1 << f)) A[f * 5 + f] = N[f] + ex(0, f);
    for (let i = 1; i < n; i++) {
      let any = false;
      for (let pass = 0; pass < 2 && !any; pass++) {
        if (pass === 1) relax[i] = 1;
        for (let a = 0; a < 5; a++) {
          if (!(mk(i - 1) & (1 << a))) continue;
          for (let b = 0; b < 5; b++) {
            if (!(mk(i) & (1 << b))) continue;
            let t = Tm[(i - 1) * 25 + a * 5 + b];
            if (t === INF) { if (!pass) continue; t = K.CONFLICT; }
            let best = INF, arg = -1;
            for (let z = 0; z < 5; z++) {
              const v0 = A[(i - 1) * 25 + z * 5 + a]; if (v0 === INF) continue;
              const v = v0 + (i >= 2 ? TRI[(i - 1) * 125 + z * 25 + a * 5 + b] : 0);
              if (v < best) { best = v; arg = z; }
            }
            if (arg >= 0) { A[i * 25 + a * 5 + b] = best + t + N[i * 5 + b] + ex(i, b); back[i * 25 + a * 5 + b] = arg; any = true; }
          }
        }
      }
    }
    for (let a = 0; a < 5; a++) for (let b = 0; b < 5; b++) {
      const st = (n - 1) * 25 + a * 5 + b;
      if (A[st] < INF || (n === 1 && a === b && (mk(0) & (1 << b)))) B[st] = 0;
    }
    for (let i = n - 2; i >= 0; i--) {
      for (let a = 0; a < 5; a++) for (let b = 0; b < 5; b++) {
        if (i === 0 ? a !== b : !(mk(i - 1) & (1 << a))) continue;
        if (!(mk(i) & (1 << b))) continue;
        let best = INF;
        for (let c = 0; c < 5; c++) {
          const bb = B[(i + 1) * 25 + b * 5 + c]; if (bb === INF) continue;
          let t = Tm[i * 25 + b * 5 + c];
          if (t === INF) { if (!relax[i + 1]) continue; t = K.CONFLICT; }
          const v = t + (i >= 1 ? TRI[i * 125 + a * 25 + b * 5 + c] : 0) + N[(i + 1) * 5 + c] + ex(i + 1, c) + bb;
          if (v < best) best = v;
        }
        B[i * 25 + a * 5 + b] = best;
      }
    }
    for (let i = 0; i < n; i++) for (let a = 0; a < 5; a++) for (let b = 0; b < 5; b++) {
      const v = A[i * 25 + a * 5 + b] + B[i * 25 + a * 5 + b];
      if (v < marg[i * 5 + b]) marg[i * 5 + b] = v;
    }
    let total = INF, lastSt = 0;
    for (let st = 0; st < 25; st++) if (A[(n - 1) * 25 + st] < total) { total = A[(n - 1) * 25 + st]; lastSt = st; }
    const path = new Array(n);
    let a = Math.floor(lastSt / 5), b = lastSt % 5;
    path[n - 1] = b;
    for (let i = n - 1; i > 0; i--) { const z = back[i * 25 + a * 5 + b]; path[i - 1] = a; b = a; a = z; }
    return { A, B, path: path.map(x => x + 1), total, relax, marg };
  }

  // Wie viele Übergänge auf dem Weg sind eigentlich unmöglich (nur per Notfall-Kosten)?
  function conflictsOnPath(M, V) {
    let c = 0;
    for (let i = 1; i < M.n; i++) if (V.relax[i] && M.T[(i - 1) * 25 + (V.path[i - 1] - 1) * 5 + V.path[i] - 1] === INF) c++;
    return c;
  }

  // Kosten eines Schritts auf dem gewählten Weg (für "offen"-Umgebung)
  function stepCost(M, extra, relax, path, i) {
    let c = M.N[i * 5 + path[i] - 1] + (extra ? extra[i * 5 + path[i] - 1] : 0);
    if (i > 0) {
      let t = M.T[(i - 1) * 25 + (path[i - 1] - 1) * 5 + path[i] - 1];
      if (t === INF) t = K.CONFLICT;
      c += t;
    }
    if (i >= 2) c += M.TRI[(i - 1) * 125 + (path[i - 2] - 1) * 25 + (path[i - 1] - 1) * 5 + path[i] - 1];
    return c;
  }

  // ===================================================================
  // 7. Lehrbuch-Muster (Tonleitern + Arpeggien), rechte Hand
  // ===================================================================
  // Finger je Tonleiterstufe (1.–7. Stufe) im Inneren einer Tonleiter.
  const W7 = [1, 2, 3, 1, 2, 3, 4];
  const SCALE_FINGERS = {
    dur: { 0: W7, 7: W7, 2: W7, 9: W7, 4: W7, 11: W7,
      5: [1, 2, 3, 4, 1, 2, 3], 10: [4, 1, 2, 3, 1, 2, 3], 3: [3, 1, 2, 3, 4, 1, 2],
      8: [3, 4, 1, 2, 3, 1, 2], 1: [2, 3, 1, 2, 3, 4, 1], 6: [2, 3, 4, 1, 2, 3, 1] },
    moll: { 9: W7, 4: W7, 11: W7, 2: W7, 7: W7, 0: W7,
      5: [1, 2, 3, 4, 1, 2, 3], 6: [3, 4, 1, 2, 3, 1, 2], 1: [3, 4, 1, 2, 3, 1, 2],
      8: [3, 4, 1, 2, 3, 1, 2], 3: [3, 1, 2, 3, 4, 1, 2], 10: [4, 1, 2, 3, 1, 2, 3] },
  };
  const STEPS = { dur: [0, 2, 4, 5, 7, 9, 11], harm: [0, 2, 3, 5, 7, 8, 11], nat: [0, 2, 3, 5, 7, 8, 10] };
  const DUR_NAMES = ['C', 'Des', 'D', 'Es', 'E', 'F', 'Ges/Fis', 'G', 'As', 'A', 'B', 'H'];
  const MOLL_NAMES = ['c', 'cis', 'd', 'es', 'e', 'f', 'fis', 'g', 'gis', 'a', 'b', 'h'];

  // Linke Hand: Finger je Tonleiterstufe im Inneren (aufwärts gelesen; Einstieg/Schluss regelt applyPattern).
  // Quelle: übliche Lehrbuch-Fingersätze (ABRSM/Hanon), z. B. C-Dur links 5432 1321 4321 321.
  const L7 = [1, 4, 3, 2, 1, 3, 2], L_H = [1, 3, 2, 1, 4, 3, 2], L_FIS = [4, 3, 2, 1, 3, 2, 1], L_B4 = [3, 2, 1, 4, 3, 2, 1];
  const SCALE_FINGERS_L = {
    dur: { 0: L7, 7: L7, 2: L7, 9: L7, 4: L7, 5: L7, 11: L_H, 6: L_FIS, 1: L_B4, 3: L_B4, 8: L_B4, 10: L_B4 },
    moll: { 9: L7, 4: L7, 2: L7, 7: L7, 0: L7, 5: L7, 11: L_H, 6: L_FIS, 1: L_B4, 8: L_B4,
      3: [2, 1, 4, 3, 2, 1, 3], 10: [2, 1, 3, 2, 1, 4, 3] },
  };
  function buildScales(table) {
    const out = [];
    for (let t = 0; t < 12; t++) {
      for (const kind of ['dur', 'harm', 'nat']) {
        const fing = table[kind === 'dur' ? 'dur' : 'moll'][t];
        const pcs = STEPS[kind].map(s => (t + s) % 12);
        const fingerOfPc = {}; const degOfPc = {};
        pcs.forEach((p, k) => { fingerOfPc[p] = fing[k]; degOfPc[p] = k; });
        const name = kind === 'dur' ? `${DUR_NAMES[t]}-Dur` : `${MOLL_NAMES[t]}-Moll (${kind === 'harm' ? 'harmonisch' : 'natürlich'})`;
        out.push({ type: 'scale', kind, tonic: t, name, pcs, fingerOfPc, degOfPc, size: 7, fingerOf: p => fingerOfPc[p] });
      }
    }
    return out;
  }
  const SCALES = buildScales(SCALE_FINGERS), SCALES_L = buildScales(SCALE_FINGERS_L);
  // Arpeggien (Grundstellung): Finger für [Grundton, Terz, Quinte]
  const ARP_W = [1, 2, 3], ARP_B = [4, 1, 2], ARP_S = [2, 3, 1];
  const ARP_FINGERS = {
    dur: { 0: ARP_W, 7: ARP_W, 5: ARP_W, 2: ARP_W, 9: ARP_W, 4: ARP_W, 11: ARP_W, 6: ARP_W, 1: ARP_B, 3: ARP_B, 8: ARP_B, 10: ARP_B },
    moll: { 9: ARP_W, 4: ARP_W, 2: ARP_W, 7: ARP_W, 0: ARP_W, 11: ARP_W, 5: ARP_W, 3: ARP_W, 6: ARP_B, 1: ARP_B, 8: ARP_B, 10: ARP_S },
  };
  // Linke Hand, [Grundton, Terz, Quinte] im Inneren: Daumen auf den Grundton, wenn er weiß ist (C-Dur 5421),
  // sonst auf den ersten weißen Akkordton (Des-Dur 2142, B-Dur 3213). Ganz schwarze Dreiklänge wie rechts.
  const AL_W = [1, 4, 2], AL_3 = [2, 1, 4], AL_5 = [3, 2, 1];
  const ARP_FINGERS_L = {
    dur: { 0: AL_W, 7: AL_W, 5: AL_W, 2: AL_W, 9: AL_W, 4: AL_W, 11: AL_W, 6: AL_W, 1: AL_3, 3: AL_3, 8: AL_3, 10: AL_5 },
    moll: { 9: AL_W, 4: AL_W, 2: AL_W, 7: AL_W, 0: AL_W, 11: AL_W, 5: AL_W, 3: AL_W, 6: AL_3, 1: AL_3, 8: AL_3, 10: AL_5 },
  };
  function buildArps(table) {
    const out = [];
    for (let t = 0; t < 12; t++) {
      for (const kind of ['dur', 'moll']) {
        const pcs = [t, (t + (kind === 'dur' ? 4 : 3)) % 12, (t + 7) % 12];
        const fing = table[kind][t];
        const fingerOfPc = {}, degOfPc = {};
        pcs.forEach((p, k) => { fingerOfPc[p] = fing[k]; degOfPc[p] = k; });
        const name = `${kind === 'dur' ? DUR_NAMES[t] + '-Dur' : MOLL_NAMES[t] + '-Moll'}-Arpeggio`;
        out.push({ type: 'arp', kind, tonic: t, name, pcs, fingerOfPc, degOfPc, size: 3, fingerOf: p => fingerOfPc[p] });
      }
    }
    return out;
  }
  const ARPS = buildArps(ARP_FINGERS), ARPS_L = buildArps(ARP_FINGERS_L);

  // Chromatische Tonleiter (rechte Hand): schwarz = 3, weiß = 1; F und C = 2, wenn E bzw. H im Lauf daneben liegt
  const CHROM = { type: 'chrom', kind: 'chrom', tonic: -1, name: 'chromatische Tonleiter', size: 12 };
  function patFinger(S, notes, run, i) {
    if (S.type !== 'chrom') return S.fingerOf(notes[i].pc);
    const m = notes[i].midi;
    if (isBlack(m)) return 3;
    const pc = pcOf(m);
    if (pc === 5 || pc === 0) {                       // F oder C: liegt der weiße Nachbar (E bzw. H) im Lauf direkt daneben?
      const nb = m - 1;
      if ((i > run.s && notes[i - 1].midi === nb) || (i < run.e && notes[i + 1].midi === nb)) return 2;
    }
    return 1;
  }

  // Läufe finden: gleiche Richtung, Schritte 1–3 (Tonleiter) bzw. 3–5 (Arpeggio)
  function detectRuns(M) {
    const notes = M.notes, n = M.n, runs = [];
    const step = (i, kind) => {
      const s = notes[i + 1].midi - notes[i].midi, gap = notes[i + 1].start - notes[i].start;
      if (gap > (MODE.easy ? EASY.RUN_MAX_IOI : T.RUN_MAX_IOI) || gap < T.CHORD) return 0;
      const a = Math.abs(s);
      if (kind === 'scale' && a >= 1 && a <= 3) return Math.sign(s);
      if (kind === 'arp' && a >= 3 && a <= 5) return Math.sign(s);
      return 0;
    };
    for (const kind of ['scale', 'arp']) {
      let i = 0;
      while (i < n - 1) {
        const d = step(i, kind);
        if (!d) { i++; continue; }
        let j = i;
        while (j < n - 1 && step(j, kind) === d) {
          if (kind === 'scale' && j > i && Math.abs(notes[j + 1].midi - notes[j].midi) === 3 && Math.abs(notes[j].midi - notes[j - 1].midi) === 3) break;
          j++;
        }
        const L = j - i + 1;
        if (L >= (kind === 'scale' ? R.SCALE_MIN_RUN : R.ARP_MIN_RUN)) {
          const cands = runCandidates(notes, i, j, d, kind, M.hand);
          if (cands.length) runs.push({ kind, s: i, e: j, dir: d, cands });
        }
        i = j;
      }
    }
    return runs;
  }

  function runCandidates(notes, s, e, dir, kind, hand) {
    const pool = kind === 'scale' ? (hand === 'L' ? SCALES_L : SCALES) : (hand === 'L' ? ARPS_L : ARPS);
    const odir = hand === 'L' ? -dir : dir;   // Richtung in echten Tonhöhen (links ist gespiegelt)
    const out = [];
    if (kind === 'scale') {
      let chrom = true;
      for (let i = s; i < e; i++) if (Math.abs(notes[i + 1].midi - notes[i].midi) !== 1) { chrom = false; break; }
      if (chrom) return [CHROM];
    }
    for (const S of pool) {
      let ok = true;
      for (let i = s; i <= e && ok; i++) {
        const p = notes[i].pc;
        if (!(p in S.degOfPc)) { ok = false; break; }
        if (i > s) {
          const d0 = S.degOfPc[notes[i - 1].pc], d1 = S.degOfPc[p];
          if (d1 !== (d0 + odir + S.size) % S.size) ok = false;   // nächster Ton der Tonleiter/des Akkords
        }
      }
      if (!ok) continue;
      if (S.type === 'arp') { // nur Grundstellung: Lauf beginnt oder endet auf dem Grundton
        const p0 = notes[s].pc, p1 = notes[e].pc;
        if (p0 !== S.tonic && p1 !== S.tonic) continue;
      }
      out.push(S);
    }
    return out;
  }

  const bit = f => 1 << (f - 1);

  // Wendet ein Muster S auf die Läufe einer Gruppe an. Gibt false zurück, wenn es nicht passt.
  function applyPattern(M, runs, S, mask, extra, fixedMask) {
    const notes = M.notes;
    for (const run of runs) {
      let restart = true, freeUntilThumb = 0;
      // vor deiner Korrektur: frei ab dem vorvorigen Daumen des Musters (einschließlich)
      const preFree = new Uint8Array(run.e - run.s + 1);
      for (let j = run.s + 1; j <= run.e; j++) if (fixedMask[j])
        for (let i = j - 1, th = 0; i >= run.s && !fixedMask[i]; i--) { preFree[i - run.s] = 1; if (patFinger(S, notes, run, i) === 1 && ++th >= R.RESUME_AFTER_THUMBS) break; }
      for (let i = run.s; i <= run.e; i++) {
        if (preFree[i - run.s]) { restart = true; continue; }
        if (fixedMask[i]) { restart = true; freeUntilThumb = i > run.s ? R.RESUME_AFTER_THUMBS : 0; continue; }   // deine Vorgabe geht vor
        const p = patFinger(S, notes, run, i);
        if (freeUntilThumb > 0) {                // nach deiner Korrektur: frei bis zum übernächsten Daumen des Musters
          if (p === 1) freeUntilThumb--;
          restart = true;
          continue;
        }
        const isStart = restart || i === run.s;
        const isEnd = i === run.e;
        restart = false;
        let hard = 31;
        if (isEnd) {
          let set = bit(p);
          const prevP = patFinger(S, notes, run, i - 1);
          if (run.dir > 0 && p === 1) {
            for (let q = prevP + 1; q <= 5; q++) set |= bit(q);                             // Schluss ohne Untersatz …
            if ((notes[i].turn || notes[i].phraseEnd) && set !== bit(1)) set &= ~bit(1);   // … Pflicht am Wendeton/Phrasenende
          }
          if (M.hand === 'R' && run.dir < 0 && prevP === 1 && p !== 1) set |= bit(2);  // 2 über den Daumen (Lehrbuch-Variante nur rechts, z. B. Es-Dur abwärts)
          hard = set;
        } else if (!isStart) hard = bit(p);
        if (isStart && !isEnd) {
          let soft = bit(p);
          const nextP = patFinger(S, notes, run, i + 1);
          if (run.dir < 0 && p === 1) {
            for (let q = nextP + 1; q <= 5; q++) soft |= bit(q);                           // Einstieg oben ohne Übersetzen …
            if ((notes[i].turn || notes[i].phraseStart) && soft !== bit(1)) soft &= ~bit(1); // … am Wendeton/Phrasenanfang
          }
          if (M.hand === 'R' && run.dir > 0 && nextP === 1 && p !== 1) soft |= bit(2);  // 2 vor dem Daumen (nur rechts, z. B. B-Dur 2123…)
          if (notes[i].phraseStart) hard &= soft;      // nichts davor: Startfinger wie im Buch
          else for (let f = 1; f <= 5; f++) if (!(soft & bit(f))) extra[i * 5 + f - 1] += K.START_DEVIATION;
        }
        mask[i] &= hard;
        if (!mask[i]) return false;
      }
    }
    return true;
  }

  function applyPatterns(M, mask, extra, status, info, fixedMask) {
    const runs = detectRuns(M);
    // Läufe, die sich einen Wendeton teilen, zu Gruppen verbinden
    runs.sort((a, b) => a.s - b.s || a.e - b.e);
    const groups = [];
    for (const r of runs) {
      const g = groups.find(G => G.kind === r.kind && G.runs.some(x => x.e === r.s || x.s === r.e));
      if (g) {
        const common = g.cands.filter(c => r.cands.includes(c));
        if (common.length) { g.runs.push(r); g.cands = common; continue; }
      }
      groups.push({ kind: r.kind, runs: [r], cands: r.cands.slice() });
    }
    const chosen = [];
    for (const G of groups) {
      const p0 = M.notes[G.runs[0].s].pc, p1 = M.notes[G.runs[G.runs.length - 1].e].pc;
      const freeV = viterbi(M, mask, extra);
      const freeConf = conflictsOnPath(M, freeV);
      let best = null;
      for (const S of G.cands) {
        const m2 = mask.slice(), e2 = extra.slice();
        if (!applyPattern(M, G.runs, S, m2, e2, fixedMask)) continue;
        const v = viterbi(M, m2, e2);
        if (conflictsOnPath(M, v) > freeConf) continue;          // Muster würde Unspielbares erzwingen
        const tier = (p0 === S.tonic ? 1 : 0) + (p1 === S.tonic ? 1 : 0);  // beginnt/endet auf dem Grundton
        if (!best || tier > best.tier || (tier === best.tier && v.total < best.cost - 1e-9)) best = { S, cost: v.total, tier, m2, e2 };
      }
      if (best) {
        mask.set(best.m2); extra.set(best.e2);
        for (const r of G.runs) for (let i = r.s; i <= r.e; i++) {
          if (!fixedMask[i]) status[i] = 'muster';
          info[i].pattern = best.S.name;
        }
        chosen.push({ name: best.S.name, from: G.runs[0].s, to: G.runs[G.runs.length - 1].e });
      } else {
        for (const r of G.runs) for (let i = r.s; i <= r.e; i++) info[i].patternDropped = G.cands.map(c => c.name);
      }
    }
    return chosen;
  }

  // ===================================================================
  // 8. Wiederholungen (gleiche Stelle = gleicher Fingersatz)
  // ===================================================================
  function ioi(notes, i) { return i + 1 < notes.length ? notes[i + 1].start - notes[i].start : 0; }
  function rhythmSame(notes, i, j) {
    const a = ioi(notes, i), b = ioi(notes, j);
    return Math.abs(a - b) <= Math.max(R.RHYTHM_TOL_ABS, R.RHYTHM_TOL_REL * Math.max(a, b));
  }

  function findRepeatGroups(M) {
    const notes = M.notes, n = M.n, L0 = R.REPEAT_MIN_LEN;
    const byKey = new Map();
    const record = (s, d, len) => {
      len = Math.min(len, d);                      // Vorkommen dürfen sich nicht überlappen
      if (len < L0) return;
      // Kurze Motive (< 6 Töne): auch der letzte Ton muss gleich lang dauern (bis zum nächsten Anschlag).
      // Sonst ist "A G F E (lang, Phrasenende)" dasselbe wie "A G F E (weiter nach D)" – musikalisch zwei Stellen.
      // Anlass: Flaggen in "Fly Me To The Moon" (15.11.2026).
      if (len < 6) { const e1 = s + len - 1, e2 = s + d + len - 1; if (e1 + 1 < n && e2 + 1 < n && !rhythmSame(notes, e1, e2)) return; }
      const key = len + ':' + notes.slice(s, s + len).map(x => x.midi).join(',');
      let g = byKey.get(key);
      if (!g) { g = { len, starts: new Set() }; byKey.set(key, g); }
      g.starts.add(s); g.starts.add(s + d);
    };
    // Figuren mit kurzer Periode (z. B. "Es C Es C …"): Fingersatz soll sich mit derselben Periode wiederholen
    const recordPeriodic = (s, d, run) => {
      if (d < 2 || run < d + 1 || run + d < L0) return;   // mind. Figur + Figur + 1 Ton, insgesamt ≥ L0 Töne (jede Länge)
      const end = s + run + d;                     // Figur reicht von s bis end-1
      // Einstiegspunkt vereinheitlichen: "Es C" und "C Es" sind dieselbe Figur
      const cyc = notes.slice(s, s + d).map(x => x.midi);
      let bestR = 0, bestKey = null;
      for (let r = 0; r < d; r++) { const k = cyc.slice(r).concat(cyc.slice(0, r)).join(','); if (bestKey === null || k < bestKey) { bestKey = k; bestR = r; } }
      const key = 'p' + d + ':' + bestKey;
      let g = byKey.get(key);
      if (!g) { g = { len: d, starts: new Set(), periodic: true }; byKey.set(key, g); }
      for (let t = s + bestR; t + d <= end; t += d) g.starts.add(t);
    };
    // Folgt eine Stelle direkt auf sich selbst (Lauf länger als der Abstand), ist sie periodisch: alle Vorkommen zählen.
    const flush = (s, d, run) => { if (run >= d + 1) recordPeriodic(s, d, run); else if (run >= L0) record(s, d, run); };
    for (let d = 1; d < n; d++) {
      let run = 0;
      for (let i = 0; i + d < n; i++) {
        const j = i + d;
        if (notes[i].midi === notes[j].midi) {
          if (run > 0 && rhythmSame(notes, i - 1, j - 1)) run++;
          else { flush(i - run, d, run); run = 1; }
        } else { flush(i - run, d, run); run = 0; }
      }
      flush(n - d - run, d, run);
    }
    const groups = [...byKey.values()].map(g => {
      const all = [...g.starts].sort((a, b) => a - b), starts = [];
      for (const s of all) if (!starts.length || s >= starts[starts.length - 1] + g.len) starts.push(s);
      return { len: g.len, starts, periodic: !!g.periodic };
    }).filter(g => g.starts.length >= 2);
    // Motive mit den meisten Vorkommen zuerst (dann längere): so passen längere Wiederholungen,
    // die das Motiv enthalten, automatisch dazu.
    groups.sort((a, b) => (b.periodic - a.periodic) || b.starts.length - a.starts.length || b.len - a.len);
    return groups;
  }

  // Gemeinsamer Fingersatz für alle Vorkommen: Kosten aller Vorkommen werden addiert,
  // inklusive Einstieg und Ausstieg ins jeweilige Umfeld (auch Drei-Ton-Regeln an den Rändern).
  function solveGroup(M, mask, extra, starts, L) {
    const n = M.n, N = M.N, Tm = M.T, TRI = M.TRI, m = starts.length, BIG = K.BIG;
    const base = viterbi(M, mask, extra);
    const ex = (i, f) => extra[i * 5 + f];
    const tx = (i, f, g) => { const t = Tm[i * 25 + f * 5 + g]; return t === INF ? BIG : t; };
    const tri = (i, a, b, c) => (i >= 1 && i <= n - 2 ? TRI[i * 125 + a * 25 + b * 5 + c] : 0);
    const prevAdj = starts.map((s, o) => o > 0 && starts[o - 1] + L === s);
    const nextAdj = starts.map((s, o) => o < m - 1 && starts[o + 1] === s + L);
    // Einstieg E(f0,f1) und Ausstieg X(p,q), summiert über Vorkommen ohne direkten Nachbarn
    const E = new Float64Array(25), X = new Float64Array(25);
    const Eo = starts.map(() => new Float64Array(25)), Xo = starts.map(() => new Float64Array(25));
    starts.forEach((s, o) => {
      if (s > 0 && !prevAdj[o]) for (let f0 = 0; f0 < 5; f0++) for (let f1 = 0; f1 < 5; f1++) {
        let best = INF;
        for (let y = 0; y < 5; y++) for (let z = 0; z < 5; z++) {
          const a0 = base.A[(s - 1) * 25 + y * 5 + z]; if (a0 === INF) continue;
          best = Math.min(best, a0 + tx(s - 1, z, f0) + tri(s - 1, y, z, f0) + tri(s, z, f0, f1));
        }
        Eo[o][f0 * 5 + f1] = Math.min(best, BIG);
      }
      const e = s + L - 1;
      if (e < n - 1 && !nextAdj[o]) for (let pp = 0; pp < 5; pp++) for (let q = 0; q < 5; q++) {
        let best = INF;
        for (let c = 0; c < 5; c++) {
          if (!(mask[e + 1] & (1 << c))) continue;
          const b0 = base.B[(e + 1) * 25 + q * 5 + c]; if (b0 === INF) continue;
          best = Math.min(best, tx(e, q, c) + tri(e, pp, q, c) + N[(e + 1) * 5 + c] + ex(e + 1, c) + b0);
        }
        Xo[o][pp * 5 + q] = Math.min(best, BIG);
      }
      for (let k = 0; k < 25; k++) { E[k] += Eo[o][k]; X[k] += Xo[o][k]; }
    });
    const NS = new Float64Array(L * 5), TS = new Float64Array(L * 25), TR = new Float64Array(L * 125);
    for (const s of starts) {
      for (let k = 0; k < L; k++) for (let f = 0; f < 5; f++) NS[k * 5 + f] += (mask[s + k] & (1 << f)) ? N[(s + k) * 5 + f] + ex(s + k, f) : BIG;
      for (let k = 0; k < L - 1; k++) for (let f = 0; f < 5; f++) for (let g = 0; g < 5; g++) TS[k * 25 + f * 5 + g] += tx(s + k, f, g);
      for (let k = 1; k < L - 1; k++) for (let x = 0; x < 125; x++) TR[k * 125 + x] += TRI[(s + k) * 125 + x];
    }
    const adjEnds = []; starts.forEach((s, o) => { if (nextAdj[o]) adjEnds.push(s + L - 1); });
    const wrap = (p0, q, f0, f1) => { let c = 0; for (const e of adjEnds) c += tx(e, q, f0) + tri(e, p0, q, f0) + tri(e + 1, q, f0, f1); return c; };

    let best = { total: INF };
    const through = new Float64Array(L * 5).fill(INF);
    for (let f0 = 0; f0 < 5; f0++) for (let f1 = 0; f1 < 5; f1++) {
      const G = new Float64Array(L * 25).fill(INF), H = new Float64Array(L * 25).fill(INF), back = new Int8Array(L * 25);
      G[25 + f0 * 5 + f1] = NS[f0] + NS[5 + f1] + TS[f0 * 5 + f1] + E[f0 * 5 + f1];
      for (let k = 2; k < L; k++) for (let b = 0; b < 5; b++) for (let c = 0; c < 5; c++) {
        let v = INF, arg = 0;
        for (let a = 0; a < 5; a++) {
          const g0 = G[(k - 1) * 25 + a * 5 + b]; if (g0 === INF) continue;
          const w = g0 + TR[(k - 1) * 125 + a * 25 + b * 5 + c];
          if (w < v) { v = w; arg = a; }
        }
        if (v < INF) { G[k * 25 + b * 5 + c] = v + TS[(k - 1) * 25 + b * 5 + c] + NS[k * 5 + c]; back[k * 25 + b * 5 + c] = arg; }
      }
      for (let pp = 0; pp < 5; pp++) for (let q = 0; q < 5; q++) H[(L - 1) * 25 + pp * 5 + q] = X[pp * 5 + q] + wrap(pp, q, f0, f1);
      for (let k = L - 2; k >= 1; k--) for (let a = 0; a < 5; a++) for (let b = 0; b < 5; b++) {
        let v = INF;
        for (let c = 0; c < 5; c++) v = Math.min(v, TR[k * 125 + a * 25 + b * 5 + c] + TS[k * 25 + b * 5 + c] + NS[(k + 1) * 5 + c] + H[(k + 1) * 25 + b * 5 + c]);
        H[k * 25 + a * 5 + b] = v;
      }
      for (let k = 1; k < L; k++) for (let a = 0; a < 5; a++) for (let b = 0; b < 5; b++) {
        const v = G[k * 25 + a * 5 + b] + H[k * 25 + a * 5 + b];
        if (v < through[k * 5 + b]) through[k * 5 + b] = v;
        if (k === 1 && v < through[a]) through[a] = v;
      }
      for (let pp = 0; pp < 5; pp++) for (let q = 0; q < 5; q++) {
        const tot = G[(L - 1) * 25 + pp * 5 + q] + H[(L - 1) * 25 + pp * 5 + q];
        if (tot < best.total) {
          const F = new Array(L); F[L - 1] = q; F[L - 2] = pp;
          for (let k = L - 1; k >= 2; k--) F[k - 2] = back[k * 25 + F[k - 1] * 5 + F[k]];
          best = { total: tot, F: F.map(x => x + 1) };
        }
      }
    }
    // Pro Vorkommen prüfen, ob der gemeinsame Fingersatz dort spielbar ist
    const F = best.F, ok = [], why = [];
    for (let o = 0; o < m; o++) {
      const s = starts[o];
      let bad = false, reason = null;
      for (let k = 0; k < L && !bad; k++) {
        if (!(mask[s + k] & bit(F[k]))) { bad = true; reason = 'belegt'; }
        else if (k > 0 && Tm[(s + k - 1) * 25 + (F[k - 1] - 1) * 5 + F[k] - 1] === INF) { bad = true; reason = 'unspielbar'; }
      }
      if (!bad && s > 0 && !prevAdj[o] && Eo[o][(F[0] - 1) * 5 + F[1] - 1] >= BIG) { bad = true; reason = 'unspielbar'; }
      if (!bad && s + L - 1 < n - 1 && !nextAdj[o] && Xo[o][(F[L - 2] - 1) * 5 + F[L - 1] - 1] >= BIG) { bad = true; reason = 'unspielbar'; }
      ok.push(!bad); why.push(reason);
    }
    // "offen" innerhalb der Gruppe
    const open = [], alt = [];
    for (let k = 0; k < L; k++) {
      let b2 = INF, a2 = null;
      for (let f = 0; f < 5; f++) if (f !== F[k] - 1 && through[k * 5 + f] < b2) { b2 = through[k * 5 + f]; a2 = f + 1; }
      const delta = (b2 - best.total) / m;
      const lo = Math.max(0, k - R.OPEN_WINDOW), hi = Math.min(L - 1, k + R.OPEN_WINDOW);
      let local = 0;
      for (let j = lo; j <= hi; j++) {
        local += NS[j * 5 + F[j] - 1];
        if (j > lo) local += TS[(j - 1) * 25 + (F[j - 1] - 1) * 5 + F[j] - 1];
        if (j > lo + 1) local += TR[(j - 1) * 125 + (F[j - 2] - 1) * 25 + (F[j - 1] - 1) * 5 + F[j] - 1];
      }
      local /= m;
      const isOpen = delta < BIG / m && delta <= R.OPEN_REL * Math.max(local, R.OPEN_FLOOR);
      open.push(isOpen); alt.push(isOpen ? a2 : null);
    }
    return { F, ok, why, open, alt };
  }

  function applyRepeats(M, mask, extra, status, info, fixedMask) {
    const groups = findRepeatGroups(M);
    const covered = new Uint8Array(M.n);
    const done = [];
    const openG = new Array(M.n).fill(null);
    for (const g of groups) {
      // nicht überlappende Vorkommen auswählen; mindestens eines muss noch frei sein
      const starts = g.starts;
      // überspringen, wenn alle Vorkommen schon festgelegt UND gleich gefingert sind
      const fixedSame = starts.every(s => { for (let k = 0; k < g.len; k++) if (!covered[s + k] || mask[s + k] !== mask[starts[0] + k]) return false; return true; });
      if (fixedSame) continue;
      const res = solveGroup(M, mask, extra, starts, g.len);
      const exceptions = [];
      starts.forEach((s, o) => {
        if (!res.ok[o]) {
          exceptions.push(s);
          for (let k = 0; k < g.len; k++) { if (!covered[s + k] && !fixedMask[s + k]) status[s + k] = 'ausnahme'; info[s + k].repeatException = res.why[o]; }
          return;
        }
        for (let k = 0; k < g.len; k++) {
          const i = s + k;
          mask[i] = bit(res.F[k]);
          covered[i] = 1;
          if (status[i] === 'frei') status[i] = 'wiederholung';
          info[i].repeat = { starts: starts.slice(), len: g.len, pos: k };
          openG[i] = res.open[k] ? res.alt[k] : (openG[i] || null);
        }
      });
      done.push({ len: g.len, starts: starts.map(s => M.notes[s].src), exceptions: exceptions.map(s => M.notes[s].src),
        reasons: exceptions.map(s => res.why[starts.indexOf(s)]) });
    }
    return { groups: done, openG };
  }

  // ===================================================================
  // 9. Stufe-A-Prüfung (unabhängig vom Optimierer): zählt unmögliche Griffe
  // ===================================================================
  function checkPlayable(notesIn, fingers, profile, hand) {
    const P = pairTable(profile);
    if (hand === 'L') notesIn = notesIn.map(x => Object.assign({}, x, { midi: MIRROR - x.midi }));
    const idx = notesIn.map((_, i) => i).sort((x, y) => (notesIn[x].start - notesIn[y].start) || (notesIn[x].midi - notesIn[y].midi));
    const v = [];
    for (let k = 1; k < idx.length; k++) {
      const a = notesIn[idx[k - 1]], b = notesIn[idx[k]], f = fingers[idx[k - 1]], g = fingers[idx[k]];
      const na = { midi: a.midi, start: a.start, dur: a.dur || 0 }, nb = { midi: b.midi, start: b.start, dur: b.dur || 0 };
      const d = b.midi - a.midi, t = b.start - a.start, held = isHeld(na, nb, P);
      const bad = txt => v.push({ index: idx[k], text: txt });
      if (!(f >= 1 && f <= 5) || !(g >= 1 && g <= 5)) { bad('kein gültiger Finger'); continue; }
      if (f === g) {
        if (d === 0) { if (t < T.REPEAT_MIN) bad('Tonwiederholung zu schnell'); }
        else if (held) bad('gleicher Finger auf zwei Tasten gleichzeitig');
        else if (t < T.SAME_FINGER_MIN + T.SAME_FINGER_PER_ST * Math.abs(d)) bad('gleicher Finger, Wechsel zu schnell');
        continue;
      }
      if (d === 0) continue;
      const lo = Math.min(f, g), hi = Math.max(f, g), p = P[lo + '-' + hi], D = f < g ? d : -d;
      const inHand = (lo === 1 && D < 0) ? (hi !== 5 && -D <= p.crossMax) : (D >= p.minPrac && D <= p.maxPrac);
      if (inHand) continue;
      if (held) { bad(D > p.maxPrac ? `Spanne ${lo}–${hi} über der Grenze, während gehalten` : 'verdrehte Fingerfolge, während gehalten'); continue; }
      const excess = Math.max(1, (lo === 1 && D < 0) ? -D - p.crossComf : D > p.maxPrac ? D - p.maxComf : p.minComf - D);
      if (t < T.SHIFT_MIN + T.SHIFT_PER_ST * excess) bad('Handsprung in der Zeit nicht machbar');
    }
    return v;
  }

  // ===================================================================
  // 10. Hauptfunktion
  // ===================================================================
  /**
   * computeFingering(notes, opts)
   *  opts.profile  : Handwerte (PROFILES.meine, .standard, .klein oder eigene)
   *  opts.fixed    : { notenIndex: finger } – deine Vorgaben (Index wie in notes)
   *  opts.patterns : Lehrbuch-Muster anwenden (Standard true)
   *  opts.repeats  : Wiederholungen angleichen (Standard true)
   * Rückgabe: { fingers, open, alt, status, violations, patterns, repeats, totalCost, explain(i) }
   */
  function computeFingering(notesIn, opts) {
    MODE.easy = !!(opts && opts.style === 'einfach');
    opts = opts || {};
    const profile = opts.profile || PROFILES.meine;
    const hand = opts.hand === 'L' ? 'L' : 'R';
    const M = buildModel(notesIn, profile, hand);
    const n = M.n;
    const mask = new Uint8Array(n).fill(31), extra = new Float64Array(n * 5), fixedMask = new Uint8Array(n);
    const status = new Array(n).fill('frei'), info = Array.from({ length: n }, () => ({}));
    const fixed = opts.fixed || {};
    for (const key of Object.keys(fixed)) {
      const k = M.pos[+key], f = +fixed[key];
      if (k === undefined || !(f >= 1 && f <= 5)) continue;
      mask[k] = bit(f); fixedMask[k] = 1; status[k] = opts._anchorsAreChords ? 'akkord' : 'fest';
    }
    if (opts._extra) for (const key of Object.keys(opts._extra)) {   // intern (computeHand): Zusatzkosten je Finger, z. B. Nachbar-Akkord
      const k = M.pos[+key]; if (k === undefined) continue;
      opts._extra[key].forEach((v, f) => { extra[k * 5 + f] += v; });
    }
    const patterns = opts.patterns === false ? [] : applyPatterns(M, mask, extra, status, info, fixedMask);
    const rep = opts.repeats === false ? { groups: [], openG: new Array(n).fill(null) } : applyRepeats(M, mask, extra, status, info, fixedMask);
    const V = viterbi(M, mask, extra);

    // "offen": zweitbeste Lösung durch diese Note kaum teurer (nur freie Noten)
    const openS = new Array(n).fill(false), altS = new Array(n).fill(null);
    for (let i = 0; i < n; i++) {
      if (status[i] === 'fest' || status[i] === 'muster') continue;
      if (status[i] === 'wiederholung') { if (rep.openG[i]) { openS[i] = true; altS[i] = rep.openG[i]; } continue; }
      const f = V.path[i];
      let b2 = INF, a2 = null;
      for (let g = 1; g <= 5; g++) {
        if (g === f || !(mask[i] & bit(g))) continue;
        const v = V.marg[i * 5 + g - 1];
        if (v < b2) { b2 = v; a2 = g; }
      }
      if (b2 === INF) continue;
      const delta = b2 - V.total;
      let local = 0;
      for (let j = Math.max(0, i - R.OPEN_WINDOW); j <= Math.min(n - 1, i + R.OPEN_WINDOW); j++) local += stepCost(M, extra, V.relax, V.path, j);
      if (delta <= R.OPEN_REL * Math.max(local, R.OPEN_FLOOR)) { openS[i] = true; altS[i] = a2; }
    }

    // zurück in Eingabe-Reihenfolge
    const out = k => { const arr = new Array(n); for (let i = 0; i < n; i++) arr[M.notes[i].src] = k(i); return arr; };
    const fingers = out(i => V.path[i]);
    const result = {
      version: VERSION,
      profile: profile.name || 'eigene Werte',
      fingers,
      open: out(i => openS[i]),
      alt: out(i => altS[i]),
      status: out(i => status[i]),
      violations: checkPlayable(notesIn, fingers, profile, hand),
      hand,
      patterns: patterns.map(p => ({ name: p.name, from: M.notes[p.from].src, to: M.notes[p.to].src })),
      repeats: rep.groups,
      releaseHints: M.notes.filter(x => x.mustRelease).map(x => x.src),   // Note muss vor dem nächsten Ton losgelassen werden
      totalCost: V.total,
    };
    Object.defineProperty(result, '_ctx', { value: { M, V, mask, extra, status, info, notesIn, opts } });
    result.explain = srcIndex => explain(result, srcIndex);
    return result;
  }

  // Vorgabe setzen: Note i bekommt Finger f, der Rest wird passend neu berechnet.
  function withFixed(result, srcIndex, finger) {
    const { notesIn, opts } = result._ctx;
    const fixed = Object.assign({}, opts.fixed || {});
    if (finger == null) delete fixed[srcIndex]; else fixed[srcIndex] = finger;
    return computeFingering(notesIn, Object.assign({}, opts, { fixed }));
  }

  // ===================================================================
  // 11. Begründung je Note
  // ===================================================================
  function explain(result, srcIndex) {
    const { M, V, status, info, mask, extra } = result._ctx;
    const i = M.pos[srcIndex];
    if (i === undefined) return '';
    const notes = M.notes, path = V.path, f = path[i], nt = notes[i];
    const parts = [];
    const st = status[i], inf = info[i];
    if (st === 'fest') parts.push('von dir festgelegt');
    if (inf.pattern) parts.push(`Lehrbuch-Muster ${inf.pattern}`);
    if (inf.repeat) parts.push(`gleich wie an den anderen ${inf.repeat.starts.length - 1} Stelle(n) dieser Wiederholung`);
    if (inf.repeatException === 'unspielbar') parts.push('nur hier anders: der gemeinsame Fingersatz der Wiederholung wäre an dieser Stelle unspielbar');
    else if (inf.repeatException) parts.push('nur hier anders: diese Stelle gehört auch zu einer anderen Wiederholung, deren Fingersatz Vorrang hat');
    if (inf.patternDropped) parts.push('Tonleiter erkannt, Muster hier verlassen, weil es sonst nicht spielbar wäre oder deiner Vorgabe widerspricht');

    const local = g => {
      const det = []; let c = nodeCost(nt, g, det) + extra[i * 5 + g - 1];
      if (i > 0) c += trans(notes[i - 1], nt, path[i - 1], g, M.P, det);
      if (i < M.n - 1) c += trans(nt, notes[i + 1], g, path[i + 1], M.P, det);
      if (extra[i * 5 + g - 1] > 0) det.push({ p: extra[i * 5 + g - 1], code: 'start', txt: 'Einstieg nicht wie im Lehrbuch' });
      if (i >= 2) c += triCost(notes[i - 2], notes[i - 1], nt, path[i - 2], path[i - 1], g, M.P, det);
      if (i >= 1 && i < M.n - 1) c += triCost(notes[i - 1], nt, notes[i + 1], path[i - 1], g, path[i + 1], M.P, det);
      if (i < M.n - 2) c += triCost(nt, notes[i + 1], notes[i + 2], g, path[i + 1], path[i + 2], M.P, det);
      return { c, det };
    };
    const me = local(f);
    // Was passiert rund um diese Note?
    const into = [], outof = [];
    if (i > 0) trans(notes[i - 1], nt, path[i - 1], f, M.P, into);
    if (i < M.n - 1) trans(nt, notes[i + 1], f, path[i + 1], M.P, outof);
    const nx = outof.find(x => x.code === 'cross' || x.code === 'shift');
    const pv = into.find(x => x.code === 'cross' || x.code === 'shift');
    if (nx && nx.code === 'cross') parts.push(path[i + 1] === 1 ? `danach Daumenuntersatz auf ${nm(notes[i + 1])}` : `danach setzt ${path[i + 1]} über den Daumen auf ${nm(notes[i + 1])}`);
    if (nx && nx.code === 'shift') parts.push(`danach Lagenwechsel (${ht(Math.abs(notes[i + 1].midi - nt.midi))})`);
    if (pv && pv.code === 'cross') parts.push(f === 1 ? 'Daumen untergesetzt' : 'über den Daumen gesetzt');
    if (pv && pv.code === 'shift') parts.push('Hand springt hierher (Lagenwechsel)');
    if (!nx && !pv && parts.length === 0) parts.push('bleibt in der Handlage');
    if (nt.mustRelease) parts.push('Hinweis: diese Taste vor dem nächsten Ton loslassen (zu weit zum Halten – Pedal hilft)');

    // Vergleich mit der besten anderen Wahl
    let bestAlt = null;
    for (let g = 1; g <= 5; g++) {
      if (g === f) continue;
      const L = local(g);
      if (!bestAlt || L.c < bestAlt.c) bestAlt = Object.assign({ g }, L);
    }
    let cmp = '';
    if (bestAlt) {
      if (bestAlt.c === INF) {
        const why = bestAlt.det.find(x => x.p === INF);
        cmp = `Jeder andere Finger wäre hier unspielbar${why ? ' (z. B. ' + bestAlt.g + ': ' + why.txt + ')' : ''}.`;
      } else {
        const diff = bestAlt.c - me.c;
        const tally = {};
        for (const x of bestAlt.det) tally[x.txt] = (tally[x.txt] || 0) + x.p;
        for (const x of me.det) tally[x.txt] = (tally[x.txt] || 0) - x.p;
        const top = Object.entries(tally).filter(([, p]) => p > 0.01).sort((a, b) => b[1] - a[1]).slice(0, 2).map(([t]) => t);
        const allowed = !!(mask[i] & bit(bestAlt.g));
        cmp = `Finger ${bestAlt.g} wäre ${diff >= 0 ? '+' + fmt(diff) : fmt(diff)} Punkte ${diff >= 0 ? 'teurer' : 'günstiger, aber ' + (allowed ? 'passt nicht zum Rest' : 'vom Muster/der Wiederholung ausgeschlossen')}${top.length && diff >= 0 ? ': ' + top.join(', ') : ''}.`;
      }
    }
    return `${f} – ${parts.join('; ')}. ${cmp}`.trim();
  }

  // ===================================================================
  // 12. Akkorde: mehrstimmiger Fingersatz für eine Hand
  // ===================================================================
  // Anschläge, die fast gleichzeitig beginnen, bilden einen Griff. Jeder Griff bekommt Finger in
  // Tonhöhen-Reihenfolge (rechts: tief = Daumen; links gespiegelt). Rechenweg:
  //   1. Viterbi über Griffe: Kandidaten = alle Fingerfolgen, die die Hand gleichzeitig greifen kann
  //      (harte Spannen-Grenze), Kosten = Griffform + Übergang (äußere Stimmen + gleicher Finger + Zeit).
  //   2. Einzeltöne dazwischen werden mit dem Melodie-Kern verfeinert (Lehrbuch-Muster, Wiederholungen,
  //      Drei-Ton-Regeln). Die Akkorde sind dabei über ihren äußeren Ton (rechts oben, links unten) fest verankert.
  //   3. Gleiche Akkorde bekommen den gleichen Griff, wenn er überall spielbar ist.
  const KC = {
    CHORD_STRETCH: 2.0,      // gleichzeitig über "bequem": doppelt so teuer wie nacheinander (Hand kann sich nicht kurz öffnen)
    SKIP_FINGER: 0.6,        // Terz oder mehr mit Nachbarfingern ohne Daumen (z. B. 3–4 auf C–E): lieber einen Finger auslassen
    HOLD_BREAK: 3.0,         // gehaltener Ton müsste zu früh losgelassen werden, obwohl er sich halten ließe
    CHORD_SAME_FINGER: 1.0,  // beim Griffwechsel rückt derselbe Finger weiter (statt 4 Punkte wie in einer Melodie)
    HAND_MOVE: 0.5,          // je Halbton, den die Handlage beim Griffwechsel wandert (über 2 Halbtöne)
    NONSTD: 4.0,             // v0.6: Griff weicht vom üblichen Griff seiner Form ab (STD_GRIPS) → einheitlicher Stil über alle Songs
    ROLL: 30.0,              // Akkord ist für die Hand zu weit: wird gebrochen (unvermeidbar, steht in der Meldung)
  };
  const NATP = { 1: 0, 2: 2, 3: 4, 4: 5, 5: 7 };
  // v0.6: Übliche Griffe je Akkordform, damit dieselbe Form in jedem Song gleich gegriffen wird.
  // Schlüssel = Abstände von unten nach oben in gespiegelter Tonhöhe (rechts = echte Tonhöhe), Wert = Finger von unten nach oben.
  // Rechts: Grundstellung 1-3-5, 1. Umkehrung 1-2-5, 2. Umkehrung 1-3-5, Oktave/Quinte/Sexte 1-5, Vierklang mit Oktave 1-2-3-5.
  // Links ergibt die Spiegelung automatisch 5-3-1, 5-3-1 (1. Umk.), 5-2-1 (2. Umk.), 5-1, 5-3-2-1 – die Tabellen passen zusammen.
  const STD_GRIPS = { '5': '25', '12': '15', '7': '15', '8': '15', '9': '15', '10': '15', '11': '15',
    '3,4': '135', '4,3': '135', '3,5': '125', '4,5': '125', '5,3': '135', '5,4': '135',
    '4,3,5': '1235', '3,4,5': '1235', '5,3,4': '1235', '5,4,3': '1235' };
  const T_GROUP = 0.05;      // Anschläge so nah beieinander = ein Griff (Video-Akkorde streuen 40–80 ms)

  function makeNotes(notesIn, hand) {
    const order = notesIn.map((_, i) => i).sort((x, y) => (notesIn[x].start - notesIn[y].start) || (mir(notesIn[x].midi, hand) - mir(notesIn[y].midi, hand)));
    return order.map(i => ({ midi: mir(notesIn[i].midi, hand), o: notesIn[i].midi, pc: pcOf(notesIn[i].midi), start: notesIn[i].start,
      dur: notesIn[i].dur || 0, src: i, black: isBlack(notesIn[i].midi) }));
  }
  // Griffe bilden: neuer Griff, wenn der Anschlag > T_GROUP nach dem ersten Ton des Griffs kommt oder die Taste schon drin ist.
  function groupNotes(notes) {
    const groups = [];
    for (const nt of notes) {
      const g = groups[groups.length - 1];
      if (g && nt.start - g.start <= T_GROUP && !g.notes.some(x => x.midi === nt.midi)) g.notes.push(nt);
      else groups.push({ start: nt.start, notes: [nt] });
    }
    for (const g of groups) { g.notes.sort((a, b) => a.midi - b.midi); g.k = g.notes.length; }
    return groups;
  }
  function combos(k) {
    const out = [];
    const rec = (start, acc) => { if (acc.length === k) { out.push(acc.slice()); return; } for (let f = start; f <= 5; f++) { acc.push(f); rec(f + 1, acc); acc.pop(); } };
    rec(1, []); return out;
  }
  const COMBOS = [null, combos(1), combos(2), combos(3), combos(4), combos(5)];

  // Griffform: Kosten und ob die Hand das gleichzeitig greifen kann.
  function chordShape(g, F, P, det) {
    let c = 0, ok = true;
    const add = (p, code, txt) => { c += p; if (det) det.push({ p, code, txt }); };
    const ns = g.notes;
    const std = STD_GRIPS[ns.slice(1).map((x, i) => x.midi - ns[i].midi).join(',')];
    if (std && F.join('') !== std) add(KC.NONSTD, 'nonstd', `üblicher Griff für diese Akkordform wäre ${std.split('').join('-')}`);
    for (let i = 0; i < ns.length; i++) {
      c += nodeCost(ns[i], F[i], det);
      for (let j = i + 1; j < ns.length; j++) {
        const p = P[F[i] + '-' + F[j]], D = ns[j].midi - ns[i].midi;
        if (D > p.maxPrac) { ok = false; if (det) det.push({ p: INF, code: 'chord-span', txt: `${F[i]}–${F[j]} schafft ${ht(D)} nicht gleichzeitig (Grenze ${p.maxPrac})` }); }
      }
      if (i + 1 < ns.length) {
        const f = F[i], g2 = F[i + 1], p = P[f + '-' + g2], D = ns[i + 1].midi - ns[i].midi, th = f === 1;
        if (D > p.maxRel) add((th ? K.SPAN_LARGE_THUMB : K.SPAN_LARGE) * (D - p.maxRel), 'span-large', `weite Spanne ${f}–${g2} im Griff (${ht(D)})`);
        if (D > p.maxComf) add(KC.CHORD_STRETCH * (D - p.maxComf), 'stretch', `Griff ${f}–${g2} über bequem (${D} statt höchstens ${p.maxComf})`);
        if (D < p.minRel) add((th ? K.SPAN_SMALL_THUMB : K.SPAN_SMALL) * (p.minRel - D), 'span-small', `enge Spanne ${f}–${g2} im Griff`);
        if (th && D > NAT[g2]) add(K.REACH * (D - NAT[g2]), 'reach', `${g2} greift weiter als in der natürlichen Lage`);
        if (!th && g2 === f + 1 && D >= 3) add(KC.SKIP_FINGER * (D - 2), 'skip', `${f}–${g2} auf ${ht(D)} – lieber einen Finger auslassen`);
      }
    }
    return { c, ok };
  }

  // Übergang zwischen zwei Griffen. Zwei Einzeltöne: genau wie im Melodie-Kern.
  function chordTrans(A, FA, B, FB, P, det) {
    if (A.k === 1 && B.k === 1) return trans(A.notes[0], B.notes[0], FA[0], FB[0], P, det);
    // Handlage: wo läge der Daumen, wenn die Finger natürlich lägen? Kosten = wie weit die Hand wandert,
    // dazu ein Viertel der Kosten der äußeren Stimmen (Melodie oben, Bass unten). Bei Griffwechseln ist
    // "derselbe Finger rückt weiter" normal und kostet nicht wie in einer Melodie.
    const pairs = [[0, 0], [A.k - 1, B.k - 1]];
    const cs = [];
    for (const [i, j] of pairs) {
      let v = trans(A.notes[i], B.notes[j], FA[i], FB[j], P);
      if (v === INF) { if (det) trans(A.notes[i], B.notes[j], FA[i], FB[j], P, det); return INF; }
      if (B.k > 1 && FA[i] === FB[j] && A.notes[i].midi !== B.notes[j].midi && (A.k > 1 || B.start - (A.notes[i].start + A.notes[i].dur) >= T.NO_PAUSE)) v = Math.min(v, KC.CHORD_SAME_FINGER);   // v0.7: Akkord→Akkord = ganze Hand verschiebt sich (erlaubt); Einzelton→Akkord nur mit Pause   // v0.6: in einen Griff hinein setzt man die Hand neu auf – Weiterrücken erlaubt; aus einem Griff heraus nicht   // Griffwechsel Akkord→Akkord: Finger rückt mit der Hand weiter (v0.5: nicht bei Einzelton davor/danach)
      cs.push(v);
    }
    const pos = (G2, F2) => G2.notes.reduce((t, nt, i) => t + nt.midi - NATP[F2[i]], 0) / G2.k;
    const move = Math.abs(pos(B, FB) - pos(A, FA));
    let c = KC.HAND_MOVE * Math.max(0, move - 2) + 0.25 * (cs[0] + cs[1]);
    if (det && move > 2) det.push({ p: KC.HAND_MOVE * (move - 2), code: 'hand-move', txt: `Hand wandert ${ht(Math.round(move))}` });
    // derselbe Finger auf einer anderen Taste: braucht Zeit (Akkordwechsel)
    for (let i = 0; i < A.k; i++) for (let j = 0; j < B.k; j++) {
      if (FA[i] !== FB[j] || A.notes[i].midi === B.notes[j].midi) continue;
      const gap = B.start - A.notes[i].start, d = Math.abs(B.notes[j].midi - A.notes[i].midi);
      if (gap < T.SAME_FINGER_MIN + T.SAME_FINGER_PER_ST * d) { if (det) det.push({ p: INF, code: 'same-too-fast', txt: `Finger ${FA[i]} schafft den Griffwechsel nicht in ${fmt(gap * 1000)} ms` }); return INF; }
      if ((A.k === 1 || B.k === 1) && B.start - (A.notes[i].start + A.notes[i].dur) < T.NO_PAUSE) { c += K.NO_PAUSE_SAME; if (det) det.push({ p: K.NO_PAUSE_SAME, code: 'same-no-pause', txt: `Finger ${FA[i]} müsste ohne Pause auf eine andere Taste` }); }
    }
    // gehaltene Töne aus A, die beim Anschlag von B noch klingen: Finger muss frei bleiben
    let hold = 0;
    for (let i = 0; i < A.k; i++) {
      const a = A.notes[i];
      if (!overlaps(a, B.notes[0]) || B.notes.some(b => b.midi === a.midi)) continue;
      const clash = FB.some((f, j) => f === FA[i]) || B.notes.some((b, j) => (b.midi - a.midi) * (FB[j] - FA[i]) < 0);
      const far = B.notes.some((b, j) => { const lo = Math.min(FB[j], FA[i]), hi = Math.max(FB[j], FA[i]); return lo !== hi && Math.abs(b.midi - a.midi) > P[lo + '-' + hi].maxPrac; });
      if ((clash || far) && B.notes.every(b => canHold(a, b, P))) hold += KC.HOLD_BREAK;
    }
    if (hold && det) det.push({ p: hold, code: 'hold-break', txt: 'gehaltener Ton müsste früher losgelassen werden' });
    return c + hold;
  }

  function solveChords(groups, P, fixedBySrc) {
    const G = groups.length;
    const cands = groups.map(g => {
      let list = (COMBOS[Math.min(g.k, 5)] || []).map(F => ({ F, ...chordShape(g, F, P) }));
      if (g.k > 5) list = [];
      const fx = g.notes.map(nt => fixedBySrc[nt.src]);
      if (fx.some(Boolean)) { const l2 = list.filter(x => fx.every((f, i) => !f || x.F[i] === f)); if (l2.length) list = l2; }
      const okList = list.filter(x => x.ok);
      g.rolled = list.length > 0 && okList.length === 0;
      if (okList.length) list = okList; else list.forEach(x => { x.c += KC.ROLL; });
      return list;
    });
    const V = cands.map(l => new Float64Array(l.length).fill(INF)), BK = cands.map(l => new Int16Array(l.length).fill(-1));
    const relaxed = new Uint8Array(G);
    cands[0].forEach((x, t) => { V[0][t] = x.c; });
    for (let i = 1; i < G; i++) {
      for (let pass = 0; pass < 2; pass++) {
        let any = false;
        cands[i].forEach((x, t) => {
          let best = INF, arg = -1;
          cands[i - 1].forEach((y, u) => {
            if (V[i - 1][u] === INF) return;
            let tr = chordTrans(groups[i - 1], y.F, groups[i], x.F, P);
            if (tr === INF) { if (!pass) return; tr = K.CONFLICT; }
            if (V[i - 1][u] + tr < best) { best = V[i - 1][u] + tr; arg = u; }
          });
          if (arg >= 0) { V[i][t] = best + x.c; BK[i][t] = arg; any = true; }
        });
        if (any) break;
        relaxed[i] = 1;
      }
    }
    let t = 0;
    V[G - 1].forEach((v, k) => { if (v < V[G - 1][t]) t = k; });
    const pick = new Array(G);
    for (let i = G - 1; i >= 0; i--) { pick[i] = t; t = BK[i][t]; }
    return { cands, pick, relaxed, total: V[G - 1][pick[G - 1]] };
  }

  // Prüfung (unabhängig): unmögliche Griffe und Griffwechsel.
  function checkHand(notesIn, fingers, profile, hand) {
    hand = hand === 'L' ? 'L' : 'R';
    const P = pairTable(profile), groups = groupNotes(makeNotes(notesIn, hand)), v = [];
    const Fs = groups.map(g => g.notes.map(nt => fingers[nt.src]));
    groups.forEach((g, gi) => {
      const F = Fs[gi], bad = txt => v.push({ index: g.notes[g.k - 1].src, text: txt });
      if (F.some(f => !(f >= 1 && f <= 5))) { bad('kein gültiger Finger'); return; }
      if (new Set(F).size !== F.length) { bad('ein Finger auf zwei Tasten im selben Griff'); return; }
      for (let i = 1; i < F.length; i++) if (F[i] < F[i - 1]) { bad('Finger im Griff verdreht'); return; }
      for (let i = 0; i < g.k; i++) for (let j = i + 1; j < g.k; j++)
        if (g.notes[j].midi - g.notes[i].midi > P[F[i] + '-' + F[j]].maxPrac) { bad(`Griff ${F[i]}–${F[j]} zu weit`); return; }
      if (gi > 0 && chordTrans(groups[gi - 1], Fs[gi - 1], g, F, P) === INF) bad('Griffwechsel in der Zeit nicht machbar');
    });
    return v;
  }
  function unavoidableHand(notesIn, profile, hand) {
    hand = hand === 'L' ? 'L' : 'R';
    const P = pairTable(profile), groups = groupNotes(makeNotes(notesIn, hand));
    if (!groups.length) return [];
    const S = solveChords(groups, P, {}), out = [];
    groups.forEach((g, i) => { if (S.relaxed[i] || g.rolled || g.k > 5) out.push(g.notes[g.k - 1].src); });
    return out;
  }

  // Orientierungs-Marken (v0.5): An welchen Tönen braucht man die Fingerzahl wirklich?
  // Erster Ton / Phrasenanfang, Kreuzen, Lagenwechsel (Daumenlage midi−NATP wandert > 2 Halbtöne), derselbe Finger auf
  // neuer Taste, Fingerwechsel auf derselben Taste, Akkord-Ankerton (rechts oben, links unten), deine Vorgaben.
  // Innerhalb einer Handlage (z. B. 1-2-3-4-5 nebeneinander) bleibt der Balken ohne Zahl.
  function cueFlags(notesIn, fingers, hand, fixedBySrc) {
    const groups = groupNotes(makeNotes(notesIn, hand)), cue = new Array(notesIn.length).fill('');
    groups.forEach((g, gi) => {
      g.notes.forEach(nt => { if (fixedBySrc && fixedBySrc[nt.src]) cue[nt.src] = 'vorgabe'; });
      if (g.k > 1) { const a = g.notes[g.k - 1]; if (!cue[a.src]) cue[a.src] = 'akkord'; return; }
      const b = g.notes[0];
      if (cue[b.src]) return;
      if (gi === 0) { cue[b.src] = 'anfang'; return; }
      const pg = groups[gi - 1];
      const last = pg.notes.reduce((x, y) => (y.start + y.dur > x.start + x.dur ? y : x));
      if (isPhraseBreak(last, b)) { cue[b.src] = 'phrase'; return; }
      const a = pg.notes.reduce((x, y) => (Math.abs(y.midi - b.midi) < Math.abs(x.midi - b.midi) ? y : x));
      const f = fingers[a.src], gF = fingers[b.src], d = b.midi - a.midi;
      if (d === 0) { if (f !== gF) cue[b.src] = 'wechsel'; return; }
      if (f === gF) { cue[b.src] = 'gleicher-finger'; return; }
      if ((gF - f) * d < 0) { cue[b.src] = 'kreuzen'; return; }
      if (Math.abs((b.midi - NATP[gF]) - (a.midi - NATP[f])) > 2) cue[b.src] = 'lage';
    });
    return cue;
  }

  /**
   * computeHand(notes, opts) – Fingersatz für alle Töne EINER Hand, auch mit Akkorden.
   *  opts.hand: 'R' | 'L', opts.profile, opts.fixed: { notenIndex: finger }, opts.patterns, opts.repeats
   * Rückgabe wie computeFingering, dazu chords (Griffe) und status 'akkord' für Akkordtöne.
   */
  function computeHand(notesIn, opts) {
    opts = opts || {};
    MODE.easy = opts.style === 'einfach';
    const hand = opts.hand === 'L' ? 'L' : 'R', profile = opts.profile || PROFILES.meine, P = pairTable(profile);
    const notes = makeNotes(notesIn, hand), groups = groupNotes(notes);
    if (groups.every(g => g.k === 1)) {
      const r = computeFingering(notesIn, Object.assign({}, opts, { hand }));
      r.chords = []; r.rolled = []; r.chordRepeats = [];
      const fx = {}; for (const k of Object.keys(opts.fixed || {})) fx[+k] = +opts.fixed[k];
      r.cue = cueFlags(notesIn, r.fingers, hand, fx); return r;
    }
    const fixed = opts.fixed || {}, fixedBySrc = {};
    for (const k of Object.keys(fixed)) fixedBySrc[+k] = +fixed[k];
    const S = solveChords(groups, P, fixedBySrc);
    const chordF = groups.map((g, i) => S.cands[i][S.pick[i]].F);

    // Verfeinerung: Linie aus Einzeltönen + äußerem Akkordton (rechts oben, links unten = gespiegelt oben)
    const line = [], lineSrc = [], anchor = {};
    groups.forEach((g, i) => {
      const nt = g.notes[g.k - 1];
      line.push({ midi: nt.o, start: g.start, dur: nt.dur });
      lineSrc.push(i);
      if (g.k > 1) anchor[line.length - 1] = chordF[i][g.k - 1];
      else if (fixedBySrc[nt.src]) anchor[line.length - 1] = fixedBySrc[nt.src];
    });
    // v0.5: Einzeltöne direkt vor/nach einem Akkord sehen in der Linie nur dessen Ankerton. Damit derselbe Finger nicht von
    // einem anderen Akkordton (z. B. Daumen oben im Akkord) auf die Nachbartaste rutscht, bekommen sie diese Kosten vorab.
    const lineExtra = {};
    groups.forEach((g, i) => {
      if (g.k !== 1) return;
      const b = g.notes[0], add = [0, 0, 0, 0, 0];
      for (const j of [i - 1, i + 1]) {   // v0.7: vor und nach einem Akkord
        const G = groups[j]; if (!G || G.k < 2) continue;
        G.notes.forEach((c, q) => { const dd = Math.abs(c.midi - b.midi); if (!dd) return;
          const [x, y] = j < i ? [c, b] : [b, c], gap = y.start - (x.start + x.dur);
          if (gap < T.NO_PAUSE) add[chordF[j][q] - 1] += K.NO_PAUSE_SAME;
          else if (MODE.easy && dd <= EASY.STEP_MAX && j < i) add[chordF[j][q] - 1] += EASY.SAME_STEP + K.SAME_FINGER; });
      }
      if (add.some(Boolean)) lineExtra[i] = add;
    });
    const lr = computeFingering(line, Object.assign({}, opts, { hand, fixed: anchor, _anchorsAreChords: true, _extra: lineExtra }));
    const fingers = new Array(notesIn.length), status = new Array(notesIn.length), open = new Array(notesIn.length).fill(false), alt = new Array(notesIn.length).fill(null);
    const lineOf = new Array(notesIn.length);
    groups.forEach((g, i) => {
      if (g.k === 1) {
        const s = g.notes[0].src; fingers[s] = lr.fingers[i]; status[s] = fixedBySrc[s] ? 'fest' : lr.status[i]; open[s] = lr.open[i]; alt[s] = lr.alt[i]; lineOf[s] = i;
      } else g.notes.forEach((nt, j) => { fingers[nt.src] = chordF[i][j]; status[nt.src] = fixedBySrc[nt.src] ? 'fest' : 'akkord'; lineOf[nt.src] = i; });
    });
    // Sicherheit: Wo die Verfeinerung einen Griffwechsel unspielbar macht, gilt die Lösung aus Schritt 1.
    const Fsrc = () => groups.map(g => g.notes.map(nt => fingers[nt.src]));
    for (let pass = 0; pass < 3; pass++) {
      const Fs = Fsrc(); let changed = false;
      for (let i = 1; i < groups.length; i++) {
        if (chordTrans(groups[i - 1], Fs[i - 1], groups[i], Fs[i], P) === INF && chordTrans(groups[i - 1], chordF[i - 1], groups[i], chordF[i], P) !== INF) {
          for (const k of [i - 1, i]) groups[k].notes.forEach((nt, j) => { if (fingers[nt.src] !== chordF[k][j]) { fingers[nt.src] = chordF[k][j]; open[nt.src] = false; changed = true; } });
        }
      }
      if (!changed) break;
    }
    // Gleiche Akkorde = gleicher Griff (wenn überall spielbar und kaum teurer)
    const byKey = new Map();
    groups.forEach((g, i) => { if (g.k < 2) return; const key = g.notes.map(x => x.midi).join(','); if (!byKey.has(key)) byKey.set(key, []); byKey.get(key).push(i); });
    const chordRepeats = [];
    for (const idx of byKey.values()) {
      if (idx.length < 2) continue;
      const Fs = Fsrc(), count = new Map();
      idx.forEach(i => { const k = Fs[i].join(''); count.set(k, (count.get(k) || 0) + 1); });
      const ranked = [...count.entries()].sort((a, b) => b[1] - a[1]);
      let done = false;
      for (const [key] of ranked) {
        const F = key.split('').map(Number), changes = [];
        let ok = true;
        for (const i of idx) {
          if (Fs[i].join('') === key) continue;
          if (groups[i].notes.some(nt => fixedBySrc[nt.src])) { ok = false; break; }
          const sh = chordShape(groups[i], F, P); if (!sh.ok) { ok = false; break; }
          // v0.7: Fenster um den Akkord neu bewerten; Einzeltöne direkt davor/danach dürfen dafür einen anderen Finger bekommen
          // (sonst würde die Regel „nie gleicher Finger ohne Pause“ den üblichen Griff verhindern)
          const Fn = Fs.slice(); Fn[i] = F; const refit = {};
          const win = (FF, a, b) => { let t = 0; for (let k = Math.max(1, a); k <= Math.min(groups.length - 1, b); k++) { const v = chordTrans(groups[k - 1], FF[k - 1], groups[k], FF[k], P); if (v === INF) return INF; t += v; } return t; };
          for (const j of [i - 1, i + 1]) {
            const G = groups[j]; if (!G || G.k !== 1 || fixedBySrc[G.notes[0].src]) continue;
            let best = Fn[j][0], bc = win(Fn, j, j + 1);
            for (let g = 1; g <= 5; g++) { const T2 = Fn.slice(); T2[j] = [g]; const v = win(T2, j, j + 1); if (v < bc - 1e-9) { bc = v; best = g; } }
            if (best !== Fn[j][0]) { Fn[j] = [best]; refit[j] = best; }
          }
          const oldC = win(Fs, i - 1, i + 2), newC = win(Fn, i - 1, i + 2);
          if (newC === INF || newC + sh.c - oldC - chordShape(groups[i], Fs[i], P).c > 4) { ok = false; break; }
          for (const j in refit) changes.push(['single', +j, refit[j]]);
          changes.push(i);
        }
        if (!ok) continue;
        for (const i of changes) { if (Array.isArray(i)) { const nt = groups[i[1]].notes[0]; fingers[nt.src] = i[2]; continue; } groups[i].notes.forEach((nt, j) => { fingers[nt.src] = F[j]; }); }
        idx.forEach(i => groups[i].notes.forEach(nt => { if (status[nt.src] === 'akkord') status[nt.src] = 'akkord-wiederholung'; }));
        chordRepeats.push({ chord: groups[idx[0]].notes.map(x => nameOf(x.o)).join('–'), times: idx.length, fingers: F.join('-') });
        done = true; break;
      }
      if (!done) chordRepeats.push({ chord: groups[idx[0]].notes.map(x => nameOf(x.o)).join('–'), times: idx.length, fingers: null });
    }
    const chords = groups.filter(g => g.k > 1).map(g => ({ notes: g.notes.map(nt => nt.src), fingers: g.notes.map(nt => fingers[nt.src]), rolled: !!g.rolled }));
    const result = {
      version: VERSION, profile: profile.name || 'eigene Werte', hand,
      fingers, open, alt, status,
      violations: checkHand(notesIn, fingers, profile, hand),
      patterns: lr.patterns.map(p => ({ name: p.name, from: groups[lineSrc[p.from]].notes[0].src, to: groups[lineSrc[p.to]].notes[0].src })),
      repeats: lr.repeats, chordRepeats, chords,
      rolled: groups.filter(g => g.rolled).map(g => g.notes[0].src),
      releaseHints: lr.releaseHints.map(i => groups[lineSrc[i]].notes[groups[lineSrc[i]].k - 1].src),
      totalCost: S.total,
    };
    result.cue = cueFlags(notesIn, fingers, hand, fixedBySrc);
    result.explain = srcIndex => {
      const li = lineOf[srcIndex]; if (li === undefined) return '';
      const g = groups[li];
      if (g.k === 1) return lr.explain(li);
      const F = g.notes.map(nt => fingers[nt.src]), names = g.notes.map(nt => nameOf(nt.o) + (Math.floor(nt.o / 12) - 1));
      const ord = hand === 'L' ? [...names].reverse().join('–') + ' mit ' + [...F].reverse().join('-') : names.join('–') + ' mit ' + F.join('-');
      const det = []; chordShape(g, F, P, det);
      const why = det.filter(x => x.p > 0.01 && x.txt).map(x => x.txt);
      let s = `${fingers[srcIndex]} – Akkord ${ord}`;
      if (status[srcIndex] === 'fest') s += '; von dir festgelegt';
      if (status[srcIndex] === 'akkord-wiederholung') s += '; gleicher Griff wie bei den anderen gleichen Akkorden';
      if (g.rolled) s += '; zu weit für einen Griff – brechen (von unten nach oben anschlagen) oder Pedal';
      s += why.length ? '. Kosten: ' + why.slice(0, 2).join(', ') + '.' : '. Bequemer Griff.';
      return s;
    };
    return result;
  }

  // ===================================================================
  // 13. Hand-Zuordnung (für Daten ohne Hand-Angabe, z. B. einfarbige Videos)
  // ===================================================================
  // Viterbi über Anschläge: Zustand = Trennstelle im Griff (alles darunter links, darüber rechts).
  // Kosten: Griff zu weit für eine Hand, mehr als 5 Töne, Hand wandert, Hände überkreuzt,
  // gehaltener Ton gehört weiter zu seiner Hand, leichte Vorliebe "tief = links".
  const KH = {
    SPAN_OVER: 2.0,          // je Halbton, den ein Griff über "bequem" (1–5) hinausgeht
    SPAN_IMPOSSIBLE: 25.0,   // Griff über der Grenze (1–5 max)
    MOVE: 0.12,              // je Halbton, den die Hand wandert
    JUMP_FAST: 4.0,          // Hand müsste über eine Oktave in < 0,2 s springen
    CROSS: 12.0,             // linke Hand über der rechten (gleichzeitig)
    SIDE: 0.04,              // je Halbton auf der "falschen" Seite von C4 (nur als Zünglein an der Waage)
    HELD_SWAP: 6.0,          // Ton klingt noch, aber die Hand greift so weit weg, dass er losgelassen werden müsste
    SINGLE_SIDE: 1.5,        // Einzelton genau zwischen den Händen: zur näheren Hand
  };
  function assignHands(notesIn, opts) {
    opts = opts || {};
    const profile = opts.profile || PROFILES.meine, P = pairTable(profile);
    const comf = P['1-5'].maxComf, max = P['1-5'].maxPrac;
    const notes = makeNotes(notesIn, 'R'), groups = groupNotes(notes), G = groups.length;
    const out = new Array(notesIn.length).fill('R');
    if (!G) return out;
    const spanCost = arr => { if (arr.length < 2) return 0; const s = arr[arr.length - 1] - arr[0]; return (s > max ? KH.SPAN_IMPOSSIBLE * (s - max) : 0) + KH.SPAN_OVER * Math.max(0, s - comf) + (arr.length > 5 ? 50 : 0); };
    const center = arr => (arr[0] + arr[arr.length - 1]) / 2;
    // Zustand je Griff: s = Anzahl Töne links. Mitgeführt (entlang des besten Wegs): Lage beider Hände + gehaltene Töne.
    let prev = null;
    const hist = [];
    for (let gi = 0; gi < G; gi++) {
      const g = groups[gi], ms = g.notes.map(x => x.midi), k = g.k, cur = [];
      for (let s = 0; s <= k; s++) {
        const L = ms.slice(0, s), R = ms.slice(s);
        const base = spanCost(L) + spanCost(R) + L.reduce((t, m) => t + KH.SIDE * Math.max(0, m - 60), 0) + R.reduce((t, m) => t + KH.SIDE * Math.max(0, 59 - m), 0);
        let best = { c: INF };
        const cands = prev || [{ c: 0, cL: 48, cR: 67, tL: -9, tR: -9, held: [] }];
        cands.forEach((p, pi) => {
          if (p.c === INF) return;
          let c = p.c + base;
          const dt = g.start;
          // gehaltene Töne der Hände (klingen noch deutlich)
          const hL = p.held.filter(h => h.hand === 'L' && h.end - g.start > T.HELD_OVERLAP).map(h => h.midi);
          const hR = p.held.filter(h => h.hand === 'R' && h.end - g.start > T.HELD_OVERLAP).map(h => h.midi);
          if (L.length && hL.length) { const all = L.concat(hL).sort((a, b) => a - b); if (all[all.length - 1] - all[0] > max) c += KH.HELD_SWAP; }
          if (R.length && hR.length) { const all = R.concat(hR).sort((a, b) => a - b); if (all[all.length - 1] - all[0] > max) c += KH.HELD_SWAP; }
          for (const [arr, cc, tt] of [[L, p.cL, p.tL], [R, p.cR, p.tR]]) {
            if (!arr.length) continue;
            const mv = Math.abs(center(arr) - cc);
            c += KH.MOVE * mv;
            if (mv > 12 && dt - tt < 0.2) c += KH.JUMP_FAST;
          }
          const topL = L.length ? L[L.length - 1] : (hL.length ? Math.max(...hL) : null);
          const botR = R.length ? R[0] : (hR.length ? Math.min(...hR) : null);
          if (topL !== null && botR !== null && topL >= botR) c += KH.CROSS;
          // Einzelton allein: zur Hand, deren letzte Lage näher ist
          if (k === 1) { const m = ms[0], dL = Math.abs(m - p.cL), dR = Math.abs(m - p.cR); if (s === 1 && dL > dR + 4) c += KH.SINGLE_SIDE; if (s === 0 && dR > dL + 4) c += KH.SINGLE_SIDE; }
          if (c < best.c) {
            const held = p.held.filter(h => h.end > g.start + 0.01).concat(g.notes.map((nt, j) => ({ midi: nt.midi, end: nt.start + nt.dur, hand: j < s ? 'L' : 'R' })));
            best = { c, from: pi, cL: L.length ? center(L) : p.cL, cR: R.length ? center(R) : p.cR, tL: L.length ? g.start : p.tL, tR: R.length ? g.start : p.tR, held };
          }
        });
        cur.push(best);
      }
      hist.push(cur); prev = cur;
    }
    let s = 0; hist[G - 1].forEach((x, k) => { if (x.c < hist[G - 1][s].c) s = k; });
    for (let gi = G - 1; gi >= 0; gi--) {
      groups[gi].notes.forEach((nt, j) => { out[nt.src] = j < s ? 'L' : 'R'; });
      s = hist[gi][s].from;
    }
    return out;
  }

  // ===================================================================
  // 14. Hilfen für mehrstimmige Daten
  // ===================================================================
  // Oberstimme: höchste Note je Anschlag (für Schritt 1, solange Akkorde fehlen)
  function toMelody(notes, hand) {
    const sg = hand === 'L' ? -1 : 1;    // rechts Oberstimme, links Unterstimme
    const s = notes.map((x, i) => Object.assign({ _i: i }, x)).sort((a, b) => a.start - b.start || sg * (b.midi - a.midi));
    const out = [];
    for (const x of s) if (!out.length || x.start - out[out.length - 1].start > T.CHORD) out.push(x);
    return out;
  }

  // Stellen, die mit KEINEM Fingersatz gehen (Eingabe selbst zu schnell/zu weit): Index der Note danach
  function unavoidable(notesIn, profile, hand) {
    const M = buildModel(notesIn, profile, hand);
    const V = viterbi(M, new Uint8Array(M.n).fill(31), null);
    const out = [];
    for (let i = 1; i < M.n; i++) if (V.relax[i] && M.T[(i - 1) * 25 + (V.path[i - 1] - 1) * 5 + V.path[i] - 1] === INF) out.push(M.notes[i].src);
    return out;
  }

  return { VERSION, unavoidable, unavoidableHand, computeHand, assignHands, checkHand, groupNotes: (n, h) => groupNotes(makeNotes(n, h === 'L' ? 'L' : 'R')), T, K, R, PROFILES, pairTable, computeFingering, withFixed, checkPlayable, toMelody, SCALES, ARPS, SCALES_L, ARPS_L, _internal: { trans, nodeCost, buildModel, viterbi, detectRuns, findRepeatGroups } };
}));
