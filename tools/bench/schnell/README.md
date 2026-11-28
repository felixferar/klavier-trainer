# Schnellmessung ohne Browser (seit v5.76)

Spielt die Handy-Aufnahmen direkt in Node durch `scanCore`/`finishScan` der App-Datei und bewertet gegen die Kanal-MIDI.
Alle 29 Videos dauern etwa 2 Minuten (mit Playwright eine halbe Stunde). Gleiche Bewertung wie `midiref.py`/`score.py`/`fehlerarten.py`.

```
python3 tools/bench/schnell/unpack.py /home/claude/work/echt          # einmal: je Video die neueste Aufnahme auspacken (Standbild für die Tastatursuche)
python3 tools/bench/schnell/bench.py web/index.html TAG alle          # alle 29; auch: einstell | pruef | einzelne Video-IDs
python3 tools/bench/schnell/bench.py web/index.html TAG2 alle --base TAG --set GH_E=0.7   # Vergleich mit einem früheren Lauf, Schalter setzen
node tools/bench/schnell/seamview.js VIDEOID bild.png 12              # gefundene Nähte als Bild ansehen (vier Bahn-Zeilen, Zeit nach unten)
```
Ordner (über Umgebungsvariablen änderbar): `KLAVIER_DIAG` (Archiv, Standard `/home/claude/klavier-diagnose`), `KLAVIER_ECHT` (ausgepackte Aufnahmen und fester Sollwert
`truth2.json`, Standard `/home/claude/work/echt`), `KLAVIER_RUNS` (Ergebnisse, Standard `/home/claude/work/runs`).

- Der Sollwert je Video wird beim ersten Lauf bestimmt (`truth2.py`) und dann festgehalten, damit alle Läufe auf derselben Zeitachse liegen.
- Die Tastatur wird mit der Suche der jeweiligen App-Datei neu aus dem Standbild bestimmt (`--relayout`), wie am Handy.
- Schalter (`--set NAME=WERT`) sind `window.NAME` in der App: `SEAM2`, `SEAM_LABEL`, `KB_FIT`, `KB_ABRUPT`, `BAR_COVER`, `BAR_VETO`, `BAR_REP`, `BAR_SNAP`, `BAR_SAT`, `GH_E`, `GH_REL`, `GH_HUE`, `GLOW1`–`GLOW4`, `GLOW1_T`, `GLOW1_SAME`, `PALE_KEY`, `SPLIT_REP`, `SPLIT_STRONG`; seit v5.77: `RECAL_GUARD`, `BAR_PALE` (`"immer"` = auch ohne blasse Tasten), `PREGLOW`, `STEP_R`, `STEP_HALO`, `GLOW4_EMPTY`, `SPLIT_OWNSEAM`, `SPLIT_BARQ`, `SEAM_LOOSE`, `SINGLE_SM`, `SINGLE_REFT`.
- `ueberlagerung.py TAG`: wie viele Restfehler an Stellen liegen, an denen zwei MIDI-Spuren dieselbe Taste gleichzeitig spielen.
- Grenze: das ist Nachspielen der aufgenommenen Zeilen, kein Test am Handy.
