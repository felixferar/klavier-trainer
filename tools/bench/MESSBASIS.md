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
