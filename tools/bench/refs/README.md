# Referenzen für echte YouTube-Aufnahmen

Für echte Videos gibt es keine Musterlösung aus einer Notendatei. Die Gegenprobe (`gegenprobe.py`) zählt aus den Pixeln der Handy-Aufnahme, wann eine Taste gefärbt ist. `--dump` friert diese Zählung hier ein.

**Status aller Dateien hier: `"review": "unreviewed"`** – das ist eine Messung, keine geprüfte Wahrheit. Wird eine Stelle von Hand am Video geprüft (Bild für Bild oder per Ohr durch den Nutzer), kommt sie in `reviewed` mit Datum und Befund. Fehler im Zähler werden in `gegenprobe.py` behoben, danach werden alle Listen neu erzeugt (nie von Hand in den Listen).

Zeiten sind Rohzeit der Aufnahme (Sekunden, `frame`-Zeit), nicht App-Zeit.

## Einstell- und Prüfmenge (Hold-out)
- **Einstellmenge** (hier wurden Schwellen gewählt, 09.11.2026): die 13 Dateien in diesem Ordner (golden hour ×6, Wake Me Up ×3, SpongeBob, GUnDodr9GLo, 163bCfINABY, Peter PlutaX).
- **Prüfmenge (Hold-out):** jede Aufnahme, die nach dem Eintrag in dieser Liste hochgeladen wird. Sie dient nur zum Prüfen, nie zum Einstellen von Schwellen. Erst wenn eine Prüf-Aufnahme einen Fehler zeigt und dieser behoben wurde, wandert sie in die Einstellmenge, und eine neue wird Prüfmenge.
- Aktuell **leer**. Nächste zwei Aufnahmen vom Nutzer = Hold-out, möglichst anderer Kanal/Stil.

## Werkzeuge (`tools/bench`)
- `regress.sh APP.html` – Rückfalltest aller Aufnahmen (Gegenprobe je Aufnahme)
- `meas.py` + `instrument.py` – Nachspielen mit Farb-/Zustandsprotokoll und Rohereignissen
- `classify.py DIAGDIR NOTES.json` – ordnet jede Abweichung ein (verschluckt / geteilt / erfunden)
- `ghost_features.py` – Buntheit der vom Geisterfilter gelöschten Töne
