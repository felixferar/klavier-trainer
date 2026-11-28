# Messbasis Notenerkennung (Schritt 0 des Umbauplans, Stand 14.11.2026)

Gemessen wird gegen **echte Sollnoten**: `gen.py` schreibt zu jedem Video die exakte Notenliste. Die Gegenprobe (`gegenprobe.py`) ist nur noch ein Alarm für fremde Videos ohne Sollwert.

## Gruppen (fest, nicht neu würfeln)
| Gruppe | Seeds | Erzeugen | Zweck |
|---|---|---|---|
| alt24 | 1–24 | `gen.py SEED DIR` | Rückfalltest, eingefroren (bitgleich wie bisher) |
| stoer | 101–124 | `STOER=1 gen.py SEED DIR` | Banner, Pause-Symbol, Wasserzeichen, Endkarte, Hand über der Tastatur |
| pruef | 201–212 ohne, 213–224 mit `STOER=1` | wie oben | Hold-out: **nie daran einstellen**, nur einmal pro Meilenstein messen |

`STOER` nutzt einen eigenen Zufallsgenerator. Ohne `STOER` bleibt jedes alte Video bitgleich (geprüft: md5 von Seed 3 identisch).

## Ablauf
```
python3 tools/bench/gen.py SEED /tmp/bench                 # Videos + Sollnoten (alt24)
cd / && python3 -m http.server 8765 --bind 127.0.0.1 &      # run.py lädt die App über http
python3 tools/bench/run.py /tmp/bench 1 2 … 24 --par 2      # Datei-Weg in Echtzeit, schreibt SEED.rec.json (die gelesenen Zeilen)
APP=web/index.html python3 tools/bench/replay.py /tmp/bench --json OUT.json   # schnell: Zeilen nachspielen + bewerten
python3 tools/bench/score.py SOLL.json IST.json            # Bewertung einer einzelnen Notenliste
```
`replay.py` druckt die alten Zahlen (Treffer/Präzision/Zusatznoten bei 70 ms) **und** die neuen (`score.py`): Anschlag-F1 bei ±50 ms und ±100 ms, Median der Anschlagabweichung, Längenfehler, Oktave. Gesamtwerte = aufsummierte Treffer, nicht Mittel der F1.
Die aufgezeichneten Zeilen hängen nur von der Tastatursuche ab. Solange die sich nicht ändert, lassen sich alt und neu auf denselben `rec.json` vergleichen.

## Zahlen (Nachspielen, Details je Video in `refs/messbasis-2026-11-14.json`)
| Gruppe | Version | Treffer | Präzision | Zusatznoten | F1@50 | F1@100 |
|---|---|---|---|---|---|---|
| alt24 | v4.90 | 0,992 | 0,953 | 51 | 0,952 | 0,972 |
| alt24 | v4.93 | 0,994 | 0,986 | 15 | 0,967 | 0,990 |
| stoer | v4.90 | 0,990 | 0,823 | 215 | 0,866 | 0,899 |
| stoer | v4.93 | 0,990 | 0,836 | 196 | 0,876 | 0,907 |
| pruef | v4.90 | 0,991 | 0,780 | 287 | 0,840 | 0,875 |
| pruef | v4.93 | 0,994 | 0,803 | 248 | 0,857 | 0,891 |

`run.py` (echter Datei-Weg, v4.90) ergab für alt24 0,992 / 0,951 / 53, wie bisher dokumentiert. Das Nachspielen weicht um ±2 Zusatznoten ab, weil die Bildzeiten im Echtzeitlauf leicht schwanken. **Vergleiche immer Nachspielen gegen Nachspielen.**

Größte Fehlerquelle in den Stör-Gruppen: die Hand über der Tastatur (ca. 180–240 Zusatznoten). Das ist der Fall für den Balkenmodus (Umbauplan Schritt 4–5).

## Echte Handy-Aufnahmen (Unterschiedstest, kein Sollwert)
Aufnahmen aus `klavier-diagnose/diag` mit `diag.py --out` umwandeln. Dann alt und neu auf demselben `rec.json` nachspielen (exakter Handy-Zustand) und jede Abweichung mit der Gegenprobe ansehen. Für große Aufnahmen (bis 400 MB) `rec.json` im Browser per `fetch` laden, nicht über Playwright übergeben.

## Gruppe kbox (v5.43)
Namenskästchen wie KISHAKEYS (weißes Kästchen unten am Balken, grauer Rand): `KBOX=1 python3 tools/bench/gen.py SEED DIR` für SEED 401–406, dann `run.py DIR 401 … 406` und `replay.py DIR`.
- v5.42: F1@100 0,925 (40 Zusatznoten = zerschnittene Noten).
- v5.43: 0,980 (8). Rest: 7 zerschnittene Noten auf schwarzen Tasten bei 60 Bildern/s (Seed 406).
Ohne KBOX bleiben alle Seeds bitgleich.

## Echte Aufnahmen mit Vergleichs-MIDI (seit 27.11.2026, v5.76)
Der wichtigste Maßstab für die Erkennung. 29 Handy-Aufnahmen aus `klavier-diagnose/diag`, zu denen der Kanal die MIDI-Datei veröffentlicht hat (`refs/echt/README.md`).
- **Einstellmenge:** 25 Videos (40 981 Töne). Daran wird eingestellt.
- **Prüfmenge:** 4 Videos (Kg8z, pR19, Sdij, 0iqb; 5 276 Töne). Gedacht als Gegenprobe. **Stand 28.11.: Kg8z, 0iqb und pR19 wurden bei der Arbeit an v5.76 angesehen und haben Regeln beeinflusst (0iqb allein: 256 → 69 Fehler) – nur Sdij ist noch unberührt.** Für eine saubere Gegenprobe braucht es neue Videos mit MIDI.
- Zwei Videos mit „anderer Fassung“ (HQoz, 3Sp4) zählen nicht mit.

Bewertung: `midiref.py` (Soll an das Video anpassen) + `score.py` (Anschlag ±100 ms) + `fehlerarten.py` (Art jedes Fehlers).
Seit v5.76 wird der Sollwert vorher bereinigt, sonst misst man Fehler, die keine sind:
- derselbe Ton in zwei Spuren oder doppelt gemeldet (gleiche Taste, Beginn ≤ 50 ms auseinander) zählt einmal,
- bei mehr als 4 Spuren werden nur die Spuren genommen, die das Video zeigt (Lost Sky hat 8, Streicher und Chor sind nicht im Bild).

| Menge | Version | F1@100 | Fehler | verschmolzen | zerschnitten | verschoben | übersehen | Nachbartaste | Oktave | erfunden |
|---|---|---|---|---|---|---|---|---|---|---|
| Einstell (25) | v5.75 | 0,9777 | 1972 | 734 | 68 | 59 | 237 | 464 | 37 | 314 |
| Einstell (25) | v5.76 | 0,9941 | 538 | 119 | 79 | 34 | 179 | 46 | 20 | 27 |
| Einstell (25) | v5.77 | 0,9948 | 476 | 120 | 78 | 36 | 136 | 28 | 19 | 23 |
| Prüf (4) | v5.75 | 0,9054 | 813 | 88 | 36 | 17 | 390 | 46 | 16 | 203 |
| Prüf (4) | v5.76 | 0,9699 | 273 | 56 | 59 | 10 | 113 | 5 | 3 | 17 |
| Prüf (4) | v5.77 | 0,9814 | 159 | 32 | 67 | 2 | 33 | 5 | 3 | 15 |
| alle 29 | v5.75 | 0,9677 | 2785 | 822 | 104 | 76 | 627 | 510 | 53 | 517 |
| alle 29 | v5.76 | 0,9908 | 811 | 175 | 138 | 44 | 292 | 51 | 23 | 44 |
| alle 29 | v5.77 | 0,9930 | 635 | 152 | 145 | 38 | 169 | 33 | 22 | 38 |

Videos mit mindestens 99 %: 13 → 20 von 29, mit mindestens 98 %: 19 → 26. (v5.75 erkennt genau wie v5.70.)
Mit engerer Grenze (Beginn höchstens 0,05 s daneben, F1@50): 0,9010 → 0,9488. Ohne jeden Fehler: 4. Mehr Fehler als vorher haben vier Videos: 2FeF (0 → 3, drei falsch geteilte Töne), _3MN (16 → 18), Pufb (5 → 6) und 9Pbx (30 → 31).
Die Zahlen stammen aus dem Nachspielen der aufgenommenen Pixelzeilen mit der Tastatursuche der jeweiligen App-Datei (nicht vom Handy selbst).
Schnell nachmessen (2 Minuten für alle 29): `tools/bench/schnell/` (siehe README dort). Alle Tests ehrlich zählen: `tools/bench/alle.py`.

**v5.77 (28.11.2026):** F1@50 0,9488 → 0,9509. Kein Video schlechter als mit v5.76. Größte Schritte: Kg8z 165 → 75 Fehler, Sdij 26 → 5, Lh8A 65 → 37.
Unter 98 % nur noch 0iqb (95,6 %). **Die Prüfmenge ist nicht mehr unabhängig** – auch Sdij hat sich bewegt (durch eine Regel, die an Kg8z gefunden wurde; Sdij selbst wurde dafür nicht angesehen).
**Überlagerungen:** 151 der 635 Fehler liegen an Stellen, an denen zwei MIDI-Spuren dieselbe Taste gleichzeitig spielen (`python3 tools/bench/schnell/ueberlagerung.py TAG`).
Das Video zeigt dort nur einen Balken; endet der kürzere Ton, blinkt die Taste – im Bild nicht von einem Neuanschlag zu unterscheiden. Diese Fehler kann die Erkennung nicht beheben
(Kg8z 54 von 75, V7dy 33 von 47, QwKb 23 von 47, _3MN 15 von 16). Sie bleiben in der Zahl oben mitgezählt.
**Achtung beim Nachsehen einzelner Stellen:** bei 5Owc und 0iqb liegt die Zeitachse der App 0,76 s bzw. 0,90 s neben dem festgehaltenen Sollwert (der erste Ton wird heute früher gefunden).
Die Bewertung gleicht das aus; wer Soll- und Ist-Zeiten von Hand vergleicht, muss es auch tun.

Zusätzlich ohne Sollwert: alle 98 Videos des Archivs alt gegen neu nachspielen und jede größere Abweichung ansehen. So wurden bei v5.76 zwei Fehler gefunden,
die die 29 Videos nicht zeigen: Namensschilder (dunkle Kästchen in den Balken sahen aus wie Lücken) und ein falscher Schnitt bei langsamem Kamera-Zoom.

Gebautes Bild für Tests: `nahtsuchetest.py` (Tonwiederholungen, Namensschilder, Bildwechsel, Zoom). Es zeigt auch die Grenze der vier Bahn-Zeilen:
fallen die Balken sehr schnell (260 px/s bei 30 Bildern/s), werden nur 16 von 30 Tönen getrennt – mit acht Zeilen alle 30. Das ist noch nicht eingebaut (braucht einen Test am Handy).
