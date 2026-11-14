# Testbericht Fingersatz – T2, T5 und unabhängiger Prüfer (14.11.2026)

Modul `fingering.js` Version 0.2.0, rechte Hand, einstimmig (bei Song-Daten: Oberstimme).

## Testmaterial
- 9 erfundene Melodien: Sprünge, Akkordbrechungen, Alberti, Wiederholungen und fast gleiche Stellen, schnelle Tonwiederholungen, Pentatonik auf schwarzen Tasten, Chromatik, schnelle Wechselsprünge, Pop-Refrain mit Pausen.
- Aus dem Repo: Embers (echter Song, mit Hand-Zuordnung), die 15 Testvideos kt-test-301 bis 315 (exakte Noten) und 6 echte YouTube-Aufnahmen (golden hour, Wake Me Up, SpongeBob, GUnDodr9GLo, 163bCfINABY, mu6gef4lM80). Bei den Aufnahmen gibt es keine Hand-Angabe, deshalb gilt dort als rechte Hand alles ab C4.
- Zusammen 3763 Töne, je mit 3 Handgrößen gerechnet: deine Werte, Standard (bequem 12/max 14), kleine Hand (bequem 10/max 12).

## Ergebnisse

| Test | Ziel | Ergebnis |
|---|---|---|
| T2 unmögliche Griffe, deine Werte | 0 | **0** |
| T2 Standard-Hand | 0 | **0** |
| T2 kleine Hand | 0 | **0** |
| T5 gleiche Stellen gleich gefingert | 100 % | **100 %** (2339 von 2339 Vergleichen) |
| T1 Tonleitern + Arpeggien (alle 3 Hände) | 100 % | **100 %** |
| T0 Grundfälle (Fünftonlage usw.) | alle | 24/24 |
| Funktionstest | alle | 12/12 |

- **Unvermeidbar:** An 5 Stellen (kleine Hand: 12) ist die Eingabe selbst unspielbar. Ein Beispiel ist ein Sprung über fast zwei Oktaven in 160 ms. Das liegt an den Daten, nicht am Fingersatz. Die App rechnet trotzdem weiter und meldet die Stelle.
- **Loslass-Hinweise:** Wenn ein Ton laut Daten weiterklingt, aber zu weit weg ist, um ihn zu halten (häufig in Embers), zählt das nicht als Fehler. Die App gibt dann den Hinweis: „vor dem nächsten Ton loslassen, Pedal hilft“.
- **„Nur hier“-Ausnahmen:** 9 Vorkommen sind echt unspielbar (meist in Embers). Dazu kommen 9 Vorkommen, bei denen sich zwei Wiederholungen überschneiden und eine Vorrang hat. Die Begründung sagt jetzt, welcher Fall vorliegt.
- **„Offen“:** 16 % der Töne sind markiert, verteilt auf 6 Entscheidungsstellen je 100 Töne. Sie häufen sich bei Sprüngen und schnellen Tonwiederholungen, wo es wirklich mehrere gleich gute Lösungen gibt.
- **Tempo:** Ein Song mit 400 Tönen braucht etwa 0,1 Sekunden.

## Was die Tests gefunden haben (und was ich geändert habe)
1. **Gehaltene Töne:** Embers hatte zunächst 24 „unmögliche“ Stellen. Ursache waren überlappende Balken in den Daten (Pedal). Jetzt gilt ein Ton erst ab deutlicher Überlappung als gehalten. Ist er zu weit weg, um ihn zu halten, gibt es einen Hinweis statt eines Fehlers.
2. **Wiederholungen, die sich überschneiden:** Ein kurzes Motiv in mehreren längeren Wiederholungen wurde unterschiedlich gefingert (T5 nur 97 %). Jetzt kommen Motive mit vielen Vorkommen zuerst dran.
3. **Begleitfiguren und Refrains direkt hintereinander:** Die Figur „Es C Es C …“ in Embers und die 17-Ton-Phrase im Refrain von Wake Me Up wiederholen sich direkt. Die App erkennt das jetzt als periodisch und fingert es überall gleich, egal wo die Figur beginnt.
4. **Chromatische Tonleiter:** Sie hatte kein Lehrbuch-Muster. Jetzt gilt: Daumen auf Weiß, 3 auf Schwarz, F und C mit 2. Das hat der Prüfer gefunden.
5. **Spanne gegen Sprung:** Eine Dehnung im sicheren Bereich, zum Beispiel eine Oktave mit 1–5, war im Modell teurer als ein Handsprung. Jetzt ist es umgekehrt. Nebeneffekt: Auch die kleine Hand besteht T1 jetzt zu 100 %.
6. **Zeit für Handsprünge:** Die Grenze für Stufe A ist strenger geworden: 150 ms plus 10 ms je Halbton (vorher 100 ms plus 5 ms). Der Schiedsrichter hatte einen 14-Halbton-Sprung in 0,12 s zu Recht als unspielbar eingestuft.
7. **Fingerwechsel auf derselben Taste:** Rückt derselbe Finger danach auf die nächste Taste weiter, zählt das jetzt als Lagenwechsel.

## Unabhängiger Prüfer
Ein frischer Prüfer hat 10 schwierige Stellen gefingert, ohne meine Lösung oder den Code zu kennen. Danach hat ein zweiter, ebenfalls frischer Schiedsrichter die abweichenden Stellen blind verglichen. Er bekam beide Lösungen als A und B, ohne zu wissen, welche von wem ist.

- **Übereinstimmung je Ton:** anfangs 77 %, nach den Korrekturen 86 %.
- **Identisch:** Des-Dur-Brechung, Chromatik (nach Korrektur), Wechselsprünge (nach Korrektur), golden hour, Embers.

| Stelle | Urteil Schiedsrichter | Stand jetzt |
|---|---|---|
| 1 Sprünge | Prüfer besser, App-Fehler | Teilweise korrigiert. Die App nimmt E4–E5 noch mit 1–4 statt 1–5 (im Modell nur 1 Punkt Unterschied). **Offen.** |
| 3 schnelle Tonwiederholung in Paaren | Prüfer besser, App-Fehler | App besser als vorher, aber noch anders. **Offen:** Paare wie „H H A A G G“ bei 0,12 s fingert der Prüfer 4-3-3-2-2-1 (Finger rutscht nach), die App vermeidet das. |
| 4 Pentatonik schwarz | gleichwertig | ok |
| 5 Chromatik | (vor dem Blindtest korrigiert) | jetzt identisch |
| 6 Wechselsprünge | App unspielbar | korrigiert, jetzt identisch |
| 7 Wake Me Up | Prüfer besser, App vertretbar | App beginnt 2-1-1 statt 5-4-4 |
| 8 GUnDodr9GLo | **App besser**, Prüfer vertretbar | ok |

Ehrlicher Hinweis: Diese 10 Stellen sind jetzt „Einstellmenge“, weil ich anhand von ihnen Regeln verbessert habe. Für den nächsten Vergleich braucht es neue Stellen, die die App noch nicht kennt. So wird es im Repo auch bei den Aufnahmen gemacht.

## Was als Nächstes kommt
1. **Linke Hand:** gespiegelte Spannen, eigene Lehrbuch-Tabellen (Tonleitern links fingern anders), dazu T1 und T2 für links.
2. **Akkorde:** mehrere Töne gleichzeitig, Finger-Reihenfolge im Griff, harte Spannen-Grenze, gebrochene und gehaltene Akkorde, Wechsel zwischen Griffen in der verfügbaren Zeit.
3. **Hand-Zuordnung:** Bei Aufnahmen ohne Hand-Angabe ist „ab C4 = rechts“ zu grob. Die Hand-Zuordnung sollte vor dem Fingersatz stehen.
4. **Offene Punkte aus dem Vergleich:** Oktaven lieber mit 1–5, schnelle Tonwiederholung in Paaren.
5. **Neuer Blindtest** mit frischen Stellen, sobald linke Hand und Akkorde da sind.
