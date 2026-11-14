# YouTube-Test mit echten Sollwerten (Umbauplan Schritt 0b)

15 Videos, erzeugt mit `LEN=55 python3 tools/bench/gen.py SEED DIR` (Seeds 301–315, ohne `STOER`).
Die `SEED.json` hier sind die exakten Sollnoten. Die Videos hat der Nutzer als `kt-test-SEED` „nicht gelistet“ auf YouTube hochgeladen,
teils mit echten YouTube-Endkarten. Die App wandelt sie am Handy um, die Diagnose landet in `klavier-diagnose/diag/…_VIDEOID_done.ktd.gz`.

Auswertung je Video:
```
python3 tools/bench/diag.py DIAG.ktd.gz --out /tmp/yt-d/SEED
python3 tools/bench/score.py tools/bench/refs/yt-test/SEED.json /tmp/yt-d/SEED/meta.json     # Handy-Ergebnis
```
Zuordnung Video-ID → Seed: über den Titel (`kt-test-SEED`); die Liste steht nach dem Hochladen in `ids.txt`.
