# Fingersatz-Kern (v0.3.0: beide Hände, Akkorde, Hand-Zuordnung)

In der App eingebettet (`web/index.html`, Block `fingering-js`). Nach jeder Änderung hier: `python3 tools/fingering/einbauen.py`, dann `python3 tools/bench/fingertest.py`.

`fingering.js` – ein Modul, keine Abhängigkeiten. Im Browser als `window.Fingering`, in Node per `require`.

## Benutzen

```js
const r = Fingering.computeFingering(noten, {
  profile: Fingering.PROFILES.meine,   // oder .standard, .klein, oder eigene Werte
  fixed: { 12: 3 },                    // deine Vorgaben: Note 12 mit Finger 3
});
r.fingers[i]     // 1–5
r.open[i]        // true = zwei Lösungen fast gleich gut → du wählst
r.alt[i]         // die andere gute Lösung bei "offen"
r.status[i]      // 'frei' | 'fest' | 'muster' | 'wiederholung' | 'ausnahme'
r.explain(i)     // "3 – Lehrbuch-Muster C-Dur; danach Daumenuntersatz auf F. Finger 4 wäre +2,8 Punkte teurer: …"
r.violations     // unmögliche Griffe (Ziel: leer)
r.patterns       // erkannte Tonleitern/Arpeggien
r.repeats        // angeglichene Wiederholungen (+ Ausnahmen "nur hier")

const r2 = Fingering.withFixed(r, 12, 3);   // Korrektur setzen, Rest wird neu berechnet
```

`noten` = `[{ midi, start, dur }, …]` in Sekunden.

## Beide Hände, Akkorde (neu in 0.3.0)

```js
const hand = Fingering.assignHands(alleNoten);          // ['L','R',…] – nur nötig, wenn die Daten keine Hand haben
const r = Fingering.computeHand(notenEinerHand, { hand: 'L', profile: Fingering.PROFILES.meine });
r.fingers / r.open / r.status   // status zusätzlich 'akkord', 'akkord-wiederholung'
r.chords        // Griffe: { notes:[Index…], fingers:[…], rolled }
r.rolled        // Griffe, die für die Hand zu weit sind → brechen/Pedal
r.explain(i)    // "5 – Akkord C3–E3–G3 mit 5-3-1. …"
Fingering.checkHand(noten, fingers, profil, hand)   // unabhängige Prüfung (Griffe + Griffwechsel)
Fingering.unavoidableHand(noten, profil, hand)      // Stellen, die mit keinem Griff gehen
```
`computeFingering(noten, { hand: 'L' })` rechnet eine einstimmige Linie links (intern an D gespiegelt:
weiß bleibt weiß, Abstände bleiben gleich; eigene Lehrbuch-Tabellen für Tonleitern und Arpeggien links).

## Eigene Handwerte

```js
{ name: 'ich', span15: { comf: 12, max: 14 }, span12: { comf: 7, max: 11 } }
```
1–3, 1–4 und die Paare ohne Daumen werden daraus geschätzt (`Fingering.pairTable(profil)` zeigt die Tabelle).

## Tests

```
node test/t0-grundfaelle.js                 # Fünftonlage & kurze Figuren
node test/t1-tonleitern.js                  # T1 mit deinen Werten
node test/t1-tonleitern.js --profile klein  # andere Hand
node test/t1-tonleitern.js --pure           # nur Kostenmodell, ohne Lehrbuch-Schicht
node test/t-funktionen.js                   # Vorgaben, Wiederholungen, Ausnahmen, Begründungen
node test/t2-t5-songs.js [--detail]         # T2 + T5 an Testmelodien und Song-Daten aus dem Repo, 3 Handgrößen
node test/vergleich.js                      # App ↔ unabhängiger Prüfer (10 Stellen)
node test/t1-tonleitern.js --hand L         # T1 linke Hand (auch --profile klein/standard)
node test/t-links.js                        # Spiegeltest, Chromatik/Fünftonlage/Alberti links, T2 links
node test/t-akkorde.js                      # Dreiklänge, Umkehrungen, Kadenz, gehaltener Bass, zu weit, schnell, gleiche Akkorde
node test/t-haende-zuordnung.js             # Hand-Zuordnung gegen bekannte Hände (kt-test-301…315)
node test/t-haende-songs.js [--detail]      # T2 + T5 beide Hände mit allen Tönen, 3 Handgrößen
node test/t-lieder.js                       # bekannte Lieder mit Lehrbuch-Fingersatz, rechts + links
```

`r.releaseHints` = Noten, die laut Daten weiterklingen, aber zu weit weg zum Halten sind
(vor dem nächsten Ton loslassen / Pedal). Das ist ein Hinweis, kein Verstoß.

## Aufbau (wo steht was)

1. `T` – Zeitgrenzen (wann ist ein Sprung zu schnell)
2. `K` – alle Kosten als benannte Konstanten
3. `R` – Regeln (Mindestlänge Tonleiter 6 Töne, Wiederholung ab 4 Tönen, "offen" bei < 10 %)
4. Hand: Spannen-Tabelle aus deinen Werten (Parncutt-Grundlage)
5. Kosten: zwei Töne (`trans`), ein Ton (`nodeCost`), drei Töne (`triCost`)
6. Viterbi 2. Ordnung (rechnet Drei-Ton-Regeln exakt mit)
7. Lehrbuch-Muster: Tonleitern (Dur, Moll harm./nat.) und Arpeggien
8. Wiederholungen: gemeinsamer Fingersatz über alle Vorkommen inkl. Ein-/Ausstieg
9. Stufe-A-Prüfung `checkPlayable` – unabhängig vom Optimierer
