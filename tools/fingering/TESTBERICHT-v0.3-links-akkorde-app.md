# Fingersatz Schritt 3: linke Hand, Akkorde, Hand-Zuordnung, Einbau in die App (14.11.2026)

Modul `fingering.js` **v0.3.0**, App **v5.03** (Branch `v5.03-fingersatz`, Commit c22add0, **noch nicht veröffentlicht**).

## Ergebnisse auf einen Blick

| Test | Ziel | Ergebnis |
|---|---|---|
| T1 rechts (Dur, Moll harm./nat., Arpeggien), 3 Handgrößen | 100 % | **100 %** (wie bisher) |
| **T1 links**, 3 Handgrößen, auch langsam (0,4 s) | 100 % | **100 %** |
| T1b Ausschnitte links/rechts | 100 % | **432/432** je Hand |
| Spiegeltest links = rechts gespiegelt (300 Melodien) | 100 % | **300/300** |
| **Akkord-Grundfälle** (24 Dreiklänge je Hand, Umkehrungen, Vierklänge, Kadenz, gehaltener Bass, zu weit, schneller Wechsel, gleiche Akkorde, Tonleiter um einen Akkord, deine Vorgabe) | alle | **21/21** |
| **T2 beide Hände, alle Töne** (Embers, 15 Testvideos, 6 Aufnahmen: 5487 Töne, 1668 in Akkorden), 3 Handgrößen | 0 | **0 / 0 / 0** |
| T5 beide Hände (gleiche 4-Griff-Folgen) | hoch | **98,8 %** (mit Akkorden 98,9 %), ohne die „nur hier“-Ausnahmen |
| T2/T5 rechts Oberstimme (alter Test) | 0 / 100 % | **0 / 100 %** (wie bisher) |
| **Hand-Zuordnung** (kt-test-301…315, bekannte Hand) | besser als „ab C4“ | **94,1 %** statt 86,4 % |
| **Bekannte Lieder mit Lehrbuch-Fingersatz** (9 Stück, rechts + links) | – | **7/9 genau**, 87 % der Töne gleich |
| Blindtest-Stellen (alte Einstellmenge) | – | 86 % (unverändert) |
| App: fingertest + 21 bisherige Tests | grün | **alle grün**, keine Seitenfehler |
| Rechenzeit | – | alle 22 Songs (beide Hände) zusammen 0,5 s (Node) |

## Was neu ist

1. **Linke Hand.** Intern an D gespiegelt. Weiß bleibt weiß, schwarz bleibt schwarz, alle Abstände bleiben gleich, daher gilt das ganze Kostenmodell auch links. Dazu kommen eigene Lehrbuch-Tabellen für links (z. B. C-Dur 5432 1321, H-Dur 4321 4321, Des/Es/As/B 3214 3213, es-Moll 2143 2132, b-Moll 2132 1432, Arpeggien C 5421, Des 2142, B 3213). Die Varianten mit „2 vor/nach dem Daumen“ gibt es nur rechts.
2. **Akkorde** (`computeHand`). Töne, die höchstens 50 ms auseinander beginnen, bilden einen Griff.
   - Die Kandidaten sind alle Fingerfolgen, die die Hand **gleichzeitig** schafft. Die Spannen-Grenze ist hart.
   - Ein Griffwechsel kostet so viel, wie die Handlage wandert, plus ein Viertel der Kosten der äußeren Stimmen. Rückt derselbe Finger beim Griffwechsel weiter, ist das normal und kostet 1 statt 4 Punkte.
   - Gehaltene Töne müssen frei bleiben, sonst gibt es den Hinweis „loslassen“.
   - Einzeltöne dazwischen verfeinert der Melodie-Kern, mit Mustern, Wiederholungen und Drei-Ton-Regeln. Die Akkorde sind dabei über ihren äußeren Ton verankert.
   - Gleiche Akkorde bekommen den gleichen Griff, wenn er überall spielbar ist.
   - Zu weite Griffe werden als **„brechen / Pedal“** gemeldet.
   - Lehrbuch-Ergebnisse ohne Nachhelfen: Grundstellung 1-3-5 / 5-3-1, 1. Umkehrung 1-2-5 / 5-3-1, 2. Umkehrung 1-3-5 / 5-2-1, Oktave 1-5, Vierklang 1-2-3-5 / 5-3-2-1.
3. **Hand-Zuordnung** (`assignHands`). Viterbi über die Griffe. Die Kosten berücksichtigen: Griff zu weit für eine Hand, mehr als 5 Töne, Hand wandert, Hände überkreuzt, gehaltene Töne, leichte Vorliebe „tief = links“. Bei Embers stehen in den Daten fast alle Töne auf „R“, auch die Bässe. Mit der Zuordnung sinken die „unvermeidbaren“ Stellen dort von 99 auf 3, und es gibt nur noch einen zu weiten Griff statt 87.
4. **Neue Regeln** (alle alten Tests unverändert grün):
   - Ein Daumen-Paar, das weiter greift als die natürliche Fünftonlage, kostet 0,2 je Halbton. Dadurch gibt es Quinte/Oktave lieber mit 1–5 (Alberti links 5-1-3-1).
   - Unter- oder Übersetzen, obwohl ±3 Töne in eine Fünftonlage passen, kostet +1,5.
   - Ein gebrochener Dreiklang mit Oktave (4 Töne) zählt als Arpeggio, also C-E-G-C = 1-2-3-5 bzw. links 5-4-2-1.
   - Kommt bei „hin und zurück“ ein anderer Finger auf dieselbe Taste, hat die Hand die Lage gewechselt (Drei-Ton-Regel). Nebeneffekt: Es gibt weniger „offen“-Marken (16,2 % → 12,9 % der Töne).
5. **App v5.03:**
   - Die Fingerzahl steht unten im Balken, über dem Notennamen. Ist der Balken für beides zu kurz, steht nur die Fingerzahl dort. Das gilt beim Abspielen/Üben und beim Auswendig-Lernen.
   - Teilt die Fingersatz-Hand-Zuordnung einen Ton der anderen Hand zu als die Balkenfarbe (bei einfarbigen Videos), steht dort z. B. „L5“.
   - Neuer Schalter „Fingersatz auf den Balken“ in den Einstellungen und im Schnellmenü, Standard an.
   - Gerechnet wird mit deinen Handwerten, einmal je Song (neu, wenn Hände getauscht werden oder die Oktave sich ändert).

## Abweichungen und offene Punkte (ehrlich)

- **Für Elise, Anfang:** Die App gibt 4-3-4-3-4-1-3-2-1, das Buch 5-4-5-4-5-2-4-3-1. Bei der App springt der Daumen von H auf A, mit zwei Tönen dazwischen. Das sieht der Viterbi nicht, weil er nur drei Töne auf einmal betrachtet. Ein Nachlauf, der vier Töne prüft, findet die Buch-Lösung nicht, denn sie ändert zwei Stellen gleichzeitig. → **Viterbi 3. Ordnung** (Zustand = 3 Finger, 125 Zustände) ist der saubere Weg.
- **Ode an die Freude, Teil 2 links, Schluss:** Die App gibt …3-2-1-2-3-3, das Buch …5-4-3-4-5-5. Nach dem Modell ist die App 0,5 Punkte günstiger, weil schwache Finger und „3-4-5“ zusammen mehr kosten als ein langsamer Fingerwechsel auf C. Nicht nachgestellt, um nicht auf den eigenen Test hin zu optimieren.
- **„Nur hier“-Ausnahmen:** Wo sich zwei Wiederholungen überschneiden, gewinnt eine. Mit beiden Händen und allen Tönen betrifft das viele 4-Griff-Fenster (477). Das gab es schon vorher; mit vollen Songs fällt es mehr auf.
- **Hand-Zuordnung:** gemessen nur an den erzeugten Testvideos (echte Songs mit sicherer Hand-Angabe fehlen). Die Hand-Farben der App selbst werden nicht verändert. Die Zuordnung gilt nur für den Fingersatz.
- **Tabellen links aus dem Gedächtnis:** es-Moll, b-Moll und die Arpeggien mit schwarzem Grundton (Des 2142, B 3213, Fis-Dur/es-Moll 5421) bitte einmal mit einem Buch gegenprüfen.
- **Akkorde:** Pro Griff wird nur der direkt vorige Griff betrachtet. Ein Basston, der über mehrere Griffe gehalten wird, gilt nur beim nächsten Griff als gehalten.
- **Offen aus dem letzten Blindtest:** schnelle Tonwiederholung in Paaren (H H A A G G, der Prüfer rutscht mit einem Finger nach). Unverändert.
- **Neuer Blindtest** mit frischen Stellen (beide Hände, Akkorde) steht noch aus.

## Nachtrag 15.11.: Fingersatz-Flagge ⚑ (Commit bf89ee0)

- Neuer Knopf **⚑** oben im Player (Abspielen/Üben), neben dem Zahnrad. Er markiert die aktuelle Stelle. Nochmal drücken innerhalb von ±0,6 s entfernt die Markierung. Steht man auf einer markierten Stelle, ist der Knopf rot. Ist „Fingersatz“ aus, ist auch der Knopf weg.
- Die Stelle geht automatisch wie die Vergleichs-Flaggen ins private Archiv `felixferar/klavier-diagnose`, Ordner **`diag/fingerflags/`**. Gesendet werden Song, Zeit, alle Töne ±3 s mit Name, Hand (Farbe und Fingersatz-Hand), Finger, „offen“ und die Begründung der App. Dazu kommt ein Bildschirmfoto. Ohne Diagnose-Schlüssel bleibt die Flagge gespeichert und wird beim nächsten Öffnen des Songs nachgeschickt.
- Test: `fingertest` prüft Setzen, Upload, Inhalt und Entfernen, alles grün.
- Zum Auswerten: Archiv klonen, `diag/fingerflags/*.json` lesen. Das sind die frischen Stellen für den nächsten Blindtest.
- Hinweis: `memtest` ist wackelig beim Punkt „Verbinden“. Das passiert auch auf `main` v5.02 (dort 4 von 4 Mal) und hängt nicht mit dem Fingersatz zusammen.

## Am Handy testen (nach „veröffentlichen“)

1. App schließen und öffnen, unter Einstellungen „Version 5.03“ prüfen.
2. Einen Song mit beiden Händen abspielen: Auf den Balken stehen unten die Fingerzahlen, darüber der Notenname.
3. Einen einfarbigen Video-Song öffnen: Tiefe Töne haben „L…“-Zahlen.
4. Im Schnellmenü „Fingersatz“ ausschalten, die Zahlen verschwinden.
5. Auswendig, Stufe 1: Auch hier stehen die Fingerzahlen auf den Balken.
6. Bei einem komischen Fingersatz anhalten und **⚑** drücken. Die Meldung „⚑ an Claude gesendet“ muss kommen.
