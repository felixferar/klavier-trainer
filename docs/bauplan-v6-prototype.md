# Bauplan v6-Lernmodus (`v6-prototype`) – ZUR FREIGABE, noch kein Code (27.11.2026)

Grundlage: `analyse-first-principles-v6-2026-11-26.md`, /goal vom 26.11., Messung aus `fix-v5.59-durchgespielt.md`.

## 1. Grenzen des Moduls

| Bleibt in `web/index.html` (unverändert) | Neu: `web/lernen.js` (< 1.000 Zeilen) |
|---|---|
| Scan, MIDI lesen/schreiben, Bibliothek | Song-Modell bauen (Abschnitte, Raster, Akkorde) |
| Bluetooth/MIDI-Eingang, Klang (WebAudio) | 3 Übungsstufen, Erfolgsregel |
| Tastatur zeichnen, Diagnose-Upload | „Los“-Ablauf, Wiederholung |
| `memGroups`, `awTakt`, Formteile, `twin` (liefern Rohdaten) | Lernstand (7 Felder) |

- `lernen.js` kennt kein DOM und kein localStorage. Es bekommt Daten und vier Funktionen von außen:
  - `ton(midi, wann, dauer, laut)` – Klang
  - `zeige(zustand)` – was leuchtet, welcher Text
  - `speichere(songId, stand)` / `lade(songId)`
  - `jetzt()` – Uhr
- Eingang: `taste(midi, an/aus)` und `tick(dt)`.
- Dadurch läuft der Kern in Node ohne Browser. Tests brauchen kein Playwright und dauern Sekunden.
- Budget: Kern ≤ 700 Zeilen, Anbindung in `index.html` ≤ 300 Zeilen.
- Einschalten nur über einen Schalter (`?v6=1`). Der alte Zeilen-Modus bleibt daneben, bis v6 freigegeben ist.

**Offener technischer Punkt:** `apk.yml` kopiert nur `index.html` in die App (Offline-Notfallversion). Eine zweite Datei braucht dort eine Zeile mehr und wirkt offline erst mit einer neuen APK. Online lädt die App die Datei sofort. Für den Prototyp egal.

## 2. Song-Modell (wird berechnet, nicht gespeichert)

```
Song = {
  griffe:     [{t, tq, toene:[{midi, hand}], dauer}],  // tq = aufs Raster gezogene Zeit in Schlägen
  takt:       {schlag: s, zaehler: 4, eins: [..]},      // aus awTakt
  abschnitte: [{a, b, name:'A', wie: -1}],              // wie = Index des Originals bei Wiederholung
  akkorde:    [{griff, name:'Am'}],                     // je Takt, über dem Bass
  haendeOk:   true/false                                // Farbe = Hand plausibel?
}
```

- **Abschnitte** = Formteile aus dem bestehenden Code. Fly Me: A (Griff 0–12), B (13–25), C (26–45), A, B, D (72–88). Neu zu lernen sind 4.
  - Abschnitte über 24 Griffe werden am Takt halbiert.
- **Wiederholung** (`wie ≥ 0`): gilt als gelernt, sobald das Original die Stufe hat. Anzeige: „Wie Abschnitt A – kennst du schon“.
- **Überlappung:** Jeder Abschnitt ab dem zweiten beginnt 1 Takt früher. Den Takt spielt Felix selbst.
- **Raster:** `tq` = Griffzeit auf die nächste Achtel von `awTakt`. Passen weniger als 85 % der Griffe aufs Raster, gibt es für den Song kein „Im Takt“ mit Raster, sondern die Original-Zeiten. Die App sagt das dazu.
- **Akkorde:** je Takt tiefster Ton der linken Hand als Grundton, dazu die Töne des Takts → Dur/Moll/7. Passt nichts, steht nur der Basston da. Deutsche Namen (H statt B).
  - Prüfung ohne Gehör: Test gegen die bekannte Folge von Fly Me (Am – Dm – G – C – F – H – E – Am).
- **Hände:** Reicht eine „Hand“ über mehr als 2 Oktaven gleichzeitig oder kreuzen sich die Hände dauerhaft, gilt `haendeOk=false`. Dann wird nach Lage getrennt (tiefster Ton je Griff = links) und die App weist darauf hin.

## 3. Lernstand – 7 Felder je Song

```
{ cuts:  [0,13,26,46,59,72],   // Abschnittsgrenzen, beim ersten Öffnen eingefroren
  wie:   [-1,-1,-1,0,1,-1],    // Wiederholung von … (eingefroren, damit ein neuer Algorithmus nichts verschiebt)
  pos:   [6,6,4,0,0,0],        // je Abschnitt: wie weit in der festen Schrittfolge (0–6)
  tempo: 7,                    // Song-Tempo „Im Takt“ in Zehnteln
  ivl:   0,                    // Abstand in Tagen; 0 = Song noch nicht fertig
  due:   null,                 // Tag der nächsten Wiederholung
  stern: 0 }                   // 1 = Meisterprüfung bestanden (lila Stern)
```

Nichts sonst. Keine Sterne je Zeile, keine Fehlzähler, keine Verläufe. Das Protokoll (für die Auswertung) läuft getrennt weiter.

## 4. Die Schrittfolge je Abschnitt (fest, 6 Schritte in 3 Stufen)

| # | Stufe | Hände | Was passiert |
|---|---|---|---|
| 1 | Zeigen | links | Tasten leuchten, App wartet, Akkordname über dem Bass |
| 2 | Zeigen | rechts | wie 1 |
| 3 | Zeigen | zusammen | wie 1 |
| 4 | Aus dem Kopf | zusammen | dunkel, App wartet; nach 1,5 s Stillstand leuchtet genau der aktuelle Griff |
| 5 | Im Takt | rechts, App spielt links | nichts wartet |
| 6 | Im Takt | zusammen, leiser Puls | nichts wartet |

- Hat ein Abschnitt nur eine Hand, entfallen die Schritte 1, 2 und 5.
- Danach kommt der nächste Abschnitt. Sind alle durch: **ganzer Song im Takt**. Erst das macht den Song fertig (`ivl = 1`).
- Stockt Felix im ganzen Song, geht nur der betroffene Abschnitt zurück auf Schritt 6.
- Kein Vorspielen als eigene Stufe. Vorspielen bleibt als Knopf.

## 5. Eine Erfolgsregel

**Stocker** ist das einzige Maß:
- Zeigen: kein Scheitern möglich. Einmal durch = weiter.
- Aus dem Kopf: Stocker = die Hilfe wurde eingeblendet.
- Im Takt: Stocker = länger als 1 Schlag kein passender Griff, obwohl einer dran war.

**Geschafft** = bis zum Ende, höchstens 1 Stocker je 40 Griffe (mindestens 1 erlaubt). Das ist der Wert aus v5.59, geeicht an 27 echten Durchgängen (78 % geschafft).

Falsche Töne: werden gezeigt und gezählt, entscheiden nichts.

**Im Takt, genau:**
- Die Uhr läuft im Song-Tempo durch. Jeder Griff hat seine Zeit auf dem Raster.
- Ein gespielter Griff zählt, wenn er im Fenster ± ½ Schlag um seine Zeit liegt.
- Verpasste Griffe werden übersprungen. Die App hält nie an.
- 1 Takt Einzählen vor dem Start.

**Tempo:**
- Start = das Tempo, das Felix in „Aus dem Kopf“ von sich aus gespielt hat (Median seiner Griff-Abstände gegen das Original), abgerundet auf 10 %, mindestens 50 %.
- Geschafft → +10 % bis 100 %. Zweimal hintereinander nicht geschafft → −10 %.

**Meisterprüfung** (lila Stern): ganzer Song bei 100 %, kein Stocker, jeder Griff ± ⅛ Schlag, höchstens 2 falsche Töne. Nur auf Wunsch, nie Pflicht.

## 6. „Los“ – ein Knopf

```
los():
  1. fälliger fertiger Song? (due ≤ heute, der älteste, höchstens 1 pro Tag)
       → ganzer Song im Takt, 1 Durchgang. „Später“ überspringt ohne Folgen.
       geschafft  → ivl: 1 → 3 → 7 → 14 → 30, due = heute + ivl
       gestockt   → ivl eine Stufe zurück, due = morgen; der gestockte Abschnitt einmal Schritt 6
  2. aktueller Song (zuletzt geübt, nicht fertig) → erster Abschnitt mit pos < 6 → dessen nächster Schritt
  3. alles fertig → „Neuen Song hinzufügen“ oder freies Durchspielen
```

- Nach jedem Durchgang startet der nächste von selbst. Kein Menü dazwischen.
- **Aufhören:** nach 12 Minuten oder 3 nicht geschafften Durchgängen in Folge erscheint einmal: „Gute Stelle zum Aufhören“ und ein Satz in Worten, z. B. „Abschnitt B sitzt jetzt im Takt. Heute 2 Stocker, gestern 5.“ Weiterspielen bleibt möglich.
- Diese Sitzungsdaten leben nur im Arbeitsspeicher.

## 7. Übernahme des bisherigen Lernstands

- Alle Zeilen eines Abschnitts auf Stufe 4 („sitzt“) → `pos = 4` (Aus dem Kopf erledigt), es geht mit „Im Takt“ weiter.
- Fly Me startet damit direkt bei Schritt 5 von Abschnitt A. Nichts wird neu gelernt.
- Der alte Lernstand wird nicht gelöscht.

## 8. Bau-Etappen (jede einzeln testbar, nichts geht live)

| Etappe | Inhalt | Abnahme (automatisch) |
|---|---|---|
| E1 | Song-Modell: Abschnitte, Raster, Akkorde, Hände-Prüfung | Fly Me ergibt A B C A B D; Akkordfolge stimmt; Runaway wird als „Hände unklar“ erkannt |
| E2 | Zeigen + Aus dem Kopf (Warten, Hilfe nach 1,5 s, Hände) | Hilfe erscheint nur nach 1,5 s und nur für einen Griff; Überlappung 1 Takt |
| E3 | Im Takt: Uhr, Fenster, Stocker, Begleitung, Tempo | Felix' echte Durchgänge aus den Protokollen werden nachgespielt; Ergebnis je Durchgang plausibel |
| E4 | „Los“, Wiederholung, Aufhören-Hinweis, Übernahme | Kalender-Simulation über 60 Tage mit 3 Songs: nie mehr als 1 Wiederholung pro Tag |
| E5 | Anbindung in `index.html` hinter `?v6=1`, Oberfläche schlicht | Felix testet am Klavier |

Nach jeder Etappe: kurzer Bericht, Zeilenzahl von `lernen.js`.

## 9. Was bewusst NICHT gebaut wird

Sterne je Abschnitt, Nachüben-Regeln, „Stelle üben“, Übergangs-Modus, Zusammensetzen in Stücken, Bonus, Gesten auf dem tiefen A (außer „von vorn“), Tempo je Zeile, Verblassen in Stufen.

Kommt ein Wunsch nach so etwas auf, ist die erste Frage: Welche der drei Stufen oder welche eine Regel ist falsch eingestellt?

## 10. Drei Entscheidungen für Felix (Vorschlag steht jeweils drin)

1. **Hände-Reihenfolge** wie in der Tabelle (links → rechts → zusammen nur beim Zeigen)? Alternative: auch „Aus dem Kopf“ getrennt, das wären 2 Schritte mehr je Abschnitt.
2. **Puls bei beiden Händen im Takt:** leiser Schlag mit betonter Eins, sauber auf dem Raster (Vorschlag). Alternative: nur Einzählen, danach Stille.
3. **Fertig-Definition:** ganzer Song im Takt beim Start-Tempo geschafft (Vorschlag) oder erst bei 100 %?

## 11. Risiken

- **Raster:** „Im Takt“ steht und fällt mit `awTakt`. Bei Songs mit freiem Tempo (Rubato) passt kein Raster. Dann gelten die Original-Zeiten.
- **Verzögerung Bluetooth-MIDI + Klang:** Für ± ½ Schlag unkritisch, für die Meisterprüfung (± ⅛ Schlag ≈ 80 ms bei Fly Me) muss die Verzögerung einmal gemessen werden.
- **Eichung an einem Song:** Alle Schwellen stammen aus Fly Me. Der zweite Song (Testwoche) ist die eigentliche Probe.
