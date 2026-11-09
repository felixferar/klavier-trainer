# Statusbericht: YouTube-Video → Noten (Klavier Trainer)

Stand: 09.11.2026 abends, Commit `bc52cb3` (Web-App v4.1, Android-App 1.0) · Repo: https://github.com/felixferar/klavier-trainer (öffentlich, Branch `main`)

Dieser Bericht ist als Übergabe an einen anderen Entwickler oder eine andere KI gedacht. Er beschreibt, was die Funktion tut, wo der Code liegt, welche Fehler gefunden und behoben wurden, was getestet ist und was offen ist.

---

## 1. Kurzfassung

| Punkt | Stand |
|---|---|
| Funktion | YouTube-Klavier-Tutorial (Synthesia-Stil: fallende Balken, Tastatur unten) wird in der App einmal abgespielt, aus den Pixeln wird eine MIDI-Datei gebaut, die als Song zum Üben gespeichert wird. |
| Gesamtzustand (v4.1) | Nachspielen der Handy-Aufnahmen gegen die unabhängige Gegenprobe: golden hour 100 % / 100 %, SpongeBob 100 % / 100 %, Wake Me Up 97,6 % gefunden / 99,6 % richtig. Prüfstand (24 Videos): 98,8 % / 95,4 %. |
| Schwächen | Leuchteffekt-Videos (Geisternoten auf Nachbartasten), 9 verschluckte schnelle Wiederholungen in Wake Me Up. |
| Aufnahme am Handy | Einwandfrei: ~24 Bilder/s, Querformat, 1280 px Zeilenbreite. Diagnosen laden automatisch ins private Repo. |
| Nächster Schritt | D2-Nachfolger: erst messen, woran sich eine echte Wiederholung von einer Leucht-Geisternote unterscheidet, dann Vorschlag an den Prüfer. |

---

## Arbeitsweise seit 09.11. nachmittags (vom Nutzer verlangt)
Keine Code-Änderung ohne: (1) Ursachenanalyse in 2–3 Sätzen, (2) Datenbeleg aus Diagnose/Nachspielen, (3) minimalen Fix mit Seiteneffekten und Prüfweg – Fehler VOR dem Fix nachstellen, danach Rückfalltest auf allen Handy-Aufnahmen und dem Prüfstand. Ein Prüfer-Prompt für eine zweite KI liegt beim Nutzer; Vorschläge werden erst nach dessen Freigabe umgesetzt. Diagnosen kommen automatisch ins private Repo `felixferar/klavier-diagnose` (Abholen: `tools/bench/fetch_diag.sh`).

## Update v3.8–4.1 / App 0.9–1.0 (09.11. nachmittags)
| Version | Ursache (belegt) | Fix | Ergebnis |
|---|---|---|---|
| 3.8 | `restColors`: HSV-Sättigung nahe Schwarz instabil ((0,0,1) → S=1 → Wert 2 > Weiß) → 6/16 schwarze Tasten mit weißer Ruhefarbe → Skoove-Werbebild als Tastatur akzeptiert → 23–26 Töne vor dem 1. Akkord | Buntheit S·V statt S | golden hour 286/286, 100 % richtig |
| – | „fehlender Schlussakkord“ war Fehlalarm der Gegenprobe (heller Abspann mit grünen Grafiken) | nur Werkzeug: `gegenprobe.py` ignoriert Bilder ohne Tastatur | – |
| 3.9 | Schwarzbild-Prüfung (Mittel < 12) traf dunkles Intro mit Schrift (Mittel 4,5, 2 % hell) | schwarz = < 0,1 % helle Pixel (`isBlackImg`) | Wake Me Up startet |
| 4.0 A | Schrift in kurzen Pillen ließ Lesezeilen 3 Bilder „leer“ → zweiter Balkenanfang → Ton geteilt | Balken endet nur bei sichtbarem Hintergrund (`bgK` in ≥ 2 Zeilen) | 23 Teilstücke weg |
| 4.0 C | Ein-Bild-Ruhe-Regel scheiterte bei schwarzen Tasten (sat<0,2 bei (0,0,2) falsch) | sat·val<0,2 | Wiederholungen bleiben getrennt |
| App 1.0 B | Keyboard aus → Android meldet Gerät ohne Info → NullPointerException | Null-Prüfung, still neu versuchen | – |
| 4.1 D1 | Wiederholung nach 2–4 Bildern exakter Ruhe wurde als Flackern verklebt | `clean` auch für 1–4 Ruhe-Bilder | Wake Me Up 96,0 → 97,6 %, SpongeBob 100 % |
| (D2 verworfen) | Geisterfilter löscht kurze Wiederholungen ohne Balken neben Nachbar-Anschlag | clean-Töne ausnehmen | Leuchteffekt-Videos −4 bis −8 Punkte → verworfen |

Offen: 9 Wiederholungen in Wake Me Up (Geisterfilter, D2-Nachfolger: echte Handfarbe vs. Nachbar-Leuchten unterscheiden); Leuchteffekt-Geisternoten (Prüfstand 10/17/19/23: 70–83 % richtig); Diagnose-Aufzeichnung bei 1280 px nach ~2:45 voll; zwei unausgewertete Aufnahmen (GUnDodr9GLo, 163bCfINABY).

## Update v3.0–3.2 / App 0.8 (09.11. mittags)
- **v3.0 Tastatursuche bei echten (versetzten) schwarzen Tasten**: Startwert der Tastenbreite = (kleiner + großer Abstand der schwarzen Tasten) / 3 statt 25-%-Abstand mit Rundung (Verhältnis lag bei echten Tastaturen an der Rundungsgrenze ~1,5); `findKeyboardRows` Gruppenmuster ab 1,28×. Prüfstand `gen.py` zeichnet schwarze Tasten jetzt versetzt (70 % der Videos, `BK=0` = alt). 24 realistische Videos live: 61,7 % → 95,5 % gefunden; Nachspielen 98 % / 95,6 %.
- **v3.1 / App 0.8**: `onRenderProcessGone` (Darstellung abgestürzt → protokollieren + neu starten statt App-Absturz; Verdacht für den Absturz beim Drehen mit 1080p), globales Absturzprotokoll (`info.crash`, Einstellungen → Fehlersuche). Keyboard-Meldungen („verbunden“/„verloren“) nicht mehr beim Üben.
- **v3.2 Wiederholte Töne**: ein einzelnes Bild mit exakter Ruhefarbe trennt zwei gleiche Töne (vorher 2 Bilder nötig; helle Balkenränder ohne dunkle Lücke). SpongeBob 92 → 112 Noten (Gegenprobe 93 % / 100 %), golden hour unverändert, Prüfstand 98,5 %.
- Handy-Test SpongeBob (App 0.7, quer, 1280 px, hd1080, 24,6 Bilder/s): lief gut; Drehen 1× abgestürzt, 1× ok.
- **Offen**: Leuchteffekt-Geisternoten auf versetzten schwarzen Tasten (Prüfstand-Videos 10/17/19/23): weißer Balken wird der hineinragenden schwarzen Taste zugeordnet. Erster Fix (Balken nicht auf die schwarze Taste zentriert → nicht zählen) brachte 97,5 % richtig, kostete aber Treffer; verfeinerte Variante griff nicht. Noch nicht im Code.

## Update v2.9 / App 0.7 (09.11., nach diesem Bericht)
- **Querformat**: Während der YouTube-Umwandlung dreht die App quer (Brücke `orient`, nur mit App ≥ 0.7), das Video füllt den Bildschirm bis auf eine 40-px-Fortschrittsleiste darunter. Nichts liegt über dem Video, auch Hinweise nicht, weil alles darüber mitfotografiert würde. Beim Ende der Umwandlung (`convUI(false)`) wird wieder freigegeben.
- **Breitere Zeilen**: `ow` = echte Pixelbreite des Videobereichs, nativ begrenzt auf 1280 (vorher 480, nativ max. 640). Der Scanner läuft auf einem eigenen `HandlerThread` (`kt-scan`).
- **Markieren von Hand** (`markKeyboard`, `#markOv`): wenn nach 25 s Video keine Tastatur gefunden wurde (`autoConvert`) oder 15 s nach Lesebeginn `okT` noch fehlt (`markLate`). Das Video pausiert; Standbild (auf das Videobild zugeschnitten) mit gelber Linie (schwarze Tasten) und blauer Linie (weiße Tasten) plus rote C-Markierungen; „Weiter“ nur bei erkannter Tastatur. Danach läuft das Video an derselben Stelle weiter (nie zurück); „Abbrechen“ → nichts gespeichert.
- **MIDI-Export**: Song-Menü → „Als MIDI-Datei speichern“ (nur `type:'midi'`), Brücke `save` mit `b64:true, mime:'audio/midi'` (App ≥ 0.7, Fähigkeit `caps` in `info`: `b64save`, `orient`, `scanWide`).
- Diagnose-Grenze 110 MB (breitere Zeilen).
- Tests: Rückfalltest golden hour unverändert (288/287); UI-Tests mit simulierter Brücke (Export → gültige MThd-Datei, Querformat-Layout, Markieren mit echtem Standbild → 39 Tasten); APK-Build grün. Zweites Nutzer-Video `SG_cv29mAsA` (SpongeBob, gleicher Kanal/Stil, C3–C6): Tastatursuche auf einem Standbild trifft C3/C4/C5 exakt. **Noch kein 88-Tasten-Video getestet.**
- Am Handy noch nicht bestätigt: Querformat, Zeilenbreite 1280, Markieren, Export.

## 2. Architektur

- **Android-Hülle** (Java, `android/app/src/main/java/de/klaviertrainer/app/MainActivity.java`, minSdk 26): WebView, lädt die Web-App immer unter `https://appassets.androidplatform.net/www/index.html`. Inhalt kommt per Interceptor von GitHub Pages (Timeout 3 s Verbindung / 5 s Lesen), sonst aus der zuletzt geladenen Kopie (`filesDir/www`), sonst aus der eingebauten Kopie (`assets/www`).
- **Web-App**: eine einzige Datei `web/index.html` (~2.300 Zeilen, Vanilla JS, kein Build). Push auf `main` unter `web/` → GitHub Pages in ca. 1 Minute; die App lädt die neue Version beim nächsten Start (keine Neuinstallation nötig).
- **Brücke Web ↔ App**: `KTNative` (androidx.webkit `WebMessageListener`, nur eigener Origin, nur Hauptframe). Nachrichten als JSON-Strings. Relevante Befehle:
  - `capture` → PixelCopy-Bild des ganzen WebView als JPEG-Data-URL (Antwort `{cmd:'capture',ok,img}`)
  - `scanStart {x,y,w,h,rows[],ow,interval}` → nativer Scanner: alle `interval` ms (40) ein PixelCopy des Videobereichs, verkleinert auf `ow` Pixel Breite (480); sendet nur die angegebenen Pixelzeilen als `{cmd:'rows',t,w,n,d:base64(RGB)}`
  - `scanStop`, `save {name,data}` (Android-Speichern-Dialog), `info`
- **Native Scanner**: `MainActivity.java` `startScan` (Zeile ~459), `scanTick` (~483), `sendRows` (~503). Läuft auf dem Main-Looper.
- **Wichtig**: Ein Push unter `android/` baut per GitHub Actions eine neue APK; die muss der Nutzer neu installieren. Änderungen nur in `web/` brauchen das nicht.

## 3. Ablauf der Umwandlung (YouTube-Link)

Alle Zeilennummern beziehen sich auf `web/index.html` @ `6e167d8`.

1. `autoConvert(it)` (Z. 2203): Video stumm starten, `waitMainVideo` (Z. 2197) wartet auf das Ende der YouTube-Werbung (Player-Zustand 1 und laufende Zeit).
2. Tastatursuche während das Video läuft: `grabVideo` (PixelCopy-Standbild) → Liste der letzten 14 Bilder → aus den letzten 5 ein Median-Bild + das letzte Bild → `tryKeyboard` (Z. 2193: `cropBars` → `findKeyboardRows` Z. 1803 → `detectKeys` Z. 1836) → `pickKb` (Z. 2192) wählt das Bild mit dem genauesten Muster der schwarzen Tasten.
3. Gefunden → `scanRun(true)` (Z. 2098):
   - `keyLayout(det)` (Z. 1873) → Liste `{m (MIDI-Note), x (0..1), black}`
   - `restColors` (Z. 2181) → Ruhefarbe pro Taste (aus dem Fundbild + den letzten 5 Suchbildern; je Taste das „am wenigsten leuchtende“)
   - `nat('scanStart', …)` mit 7 Zeilen: `yA` (durch die schwarzen Tasten), `yB` (durch die weißen Tasten unterhalb der schwarzen), `yC` (knapp über der Tastatur), dazu 4 Zeilen weit oberhalb der Tastatur (`laneHigh`, nur fallende Balken, kein Glühen)
4. Pro empfangenem Bild: `scanFrame` (Z. 1880) rechnet die native Zeit mit gleitendem Mittel in Videozeit um und ruft `scanCore(px,w,n,f)` (Z. 1892) auf:
   - je Taste: Farbe an der Tastenmitte (Median aus 5 Abtastpunkten) vs. Ruhefarbe → `pressed`, wenn Abstand > 55 (schwarz) bzw. > 70 (weiß) und gefärbt
   - Zustandsautomat je Taste → `SCAN.events` (`{m,start,end,hue}`)
   - Balken in den oberen Zeilen: `laneBars` (Z. 1944) → Balken als zusammenhängende Läufe, einer Taste zugeordnet; Spalt-Erkennung für schnelle Wiederholungen
   - **Freigabe `okT`**: gezählt wird erst, wenn die Tastatur ~8 Bilder lang „normal“ aussah (höchstens 12 % der Tasten „weder ruhend noch leuchtend“ und nicht zu viele leuchtend). Das soll Kanal-Intros ausschließen.
   - Abspann-Erkennung: Phasen mit vielen „komischen“ Tasten werden gemerkt (`SCAN.oddR`) und erst am Ende ausgewertet.
5. Ende (Player-Zustand 0) → `scanStop` (Z. 2117) → `finishScan` (Z. 1997): Balkenverzögerung, Geisternoten-Filter, Notenlängen aus Balkenlängen, frühe Noten aus den Standbildern (`earlyFromBars` Z. 1974), Hände nach Farbton (zwei Farben → L/R, eine Farbe → alles rechts), Anfang auf 1 s verschoben.
6. `scanSave` (Z. 2129) → `writeMidi` (Z. 2055, Format 1, 120 bpm, Spuren „Right“/„Left“) → als Song (`type:'midi'`, MIDI als base64) in `localStorage` `kt_lib` → Player öffnet sich mit Modi Abspielen/Lernen.
- Live-Zähler während der Umwandlung: `liveNotes` (Z. 2239) ruft alle 2 s `finishScan(true)`; Anzeige über `scanCountTxt()` („Tastatur wird noch geprüft“ solange `okT == null`).
- Weg 2 „Videodatei hochladen“: `fileConvert` (Z. 2246) nutzt denselben `scanCore`, liest aber jedes Bild über `<video>` + Canvas. Von den Fixes unten profitiert er ebenso; am Handy nicht separat getestet.

## 4. Gefundene und behobene Fehler (09.11.2026)

Testgerät des Nutzers: **Samsung Galaxy S22 (SM-S901B), Android 16, Hochformat**, Bildschirm 360×753 CSS-px, dpr 3. Referenzvideo: „JVKE – golden hour | EASY Piano Tutorial“, `D4COOEBwBjk`, 2:37, Tastatur C3–D6 (39 Tasten), Balken lila (links) / grün (rechts), Intro vor der Tastatur.

### Fehler 1: Zähler blieb bei 0, nur 7 Noten (Diagnose 1, v2.5) → behoben in v2.6
- **Ursache**: `detectKeys` setzte jede schwarze Taste genau auf die Fuge zwischen zwei weißen Tasten (`x0 + w*whiteIndex(m)`). Bei echten Tastaturen sitzen Cis/Fis links davon und Dis/Ais rechts, um bis zu ~0,16 Tastenbreiten (hier 2–4 px bei 21 px Tastenbreite und 480 px Zeilenbreite). Die Abtastung traf den weißen Rand → 10–11 von 16 schwarzen Tasten in ~80–97 % der Bilder „weder ruhend noch leuchtend“ → `okT` erst bei 150,6 s von 152 s → praktisch nichts gezählt.
- **Warum der Prüfstand das nicht fand**: `tools/bench/gen.py` zeichnet schwarze Tasten mittig.
- **Fix** (`detectKeys`): gemessene Mitte jeder erkannten schwarzen Taste verwenden (wenn innerhalb 0,25 Tastenbreiten vom Modell); sonst gelernten Versatz pro Tastenart (Median der Abweichungen je Cis/Dis/Fis/Gis/Ais).

### Fehler 2: Eine Handvoll falsch eingeschätzter Tasten blockiert alles → abgesichert in v2.7
- **Ursache**: Die Freigabe `okT` scheitert schon an ~5 von 39 Tasten, deren Ruhefarbe nicht stimmt, und zwar ohne jede Meldung.
- **Fix** (`scanCore`): Selbstkalibrierung. Bleibt eine Taste ~2 s (50 Bilder) unverändert (Farbabstand < 18) und ungefärbt (Sättigung < 0,25), wird diese Farbe ihre Ruhefarbe (`SCAN.stab`, Zähler `SCAN.recal`).
- **Test**: exakter Handy-Zustand aus Diagnose 1 (alte Positionen + alte Ruhefarben) → 288 statt 7 Noten.

### Fehler 3: Viel zu viele Noten (Diagnose 2, v2.6: 567 Noten) → behoben in v2.7 + v2.8
- **Ursache**: `restColors` nahm die Ruhefarben nur aus den letzten 5 Suchbildern. Bei golden hour zeigten einige davon noch das Intro (keine Tastatur) → 10 von 16 schwarzen Tasten bekamen Weiß als Ruhefarbe → jede ruhende schwarze Taste galt als gedrückt (dazu Fehlzuordnungen auf weiße Nachbarn).
- **Fix v2.8**: Das Fundbild (`scanImg`, in dem die Tastatur erkannt wurde) ist immer mit in der Auswahl. Zusätzlich korrigiert die Selbstkalibrierung aus v2.7 so etwas nach ~2 s.
- **Test**: Diagnose 2 nachgespielt → 285 (v2.7, Handy-Tasten) bzw. 287 Noten (v2.8, Tastatur neu bestimmt).

### Sonstige Änderungen
- v2.5: Diagnose-Aufnahme (Abschnitt 6).
- v2.7: Zähler-Text „Tastatur wird noch geprüft“ statt „0 Noten“, solange `okT` fehlt.
- Diagnose-Aufnahme schaltet sich nach einer gespeicherten Datei selbst ab.

## 5. Testergebnisse

Gegenprobe = einfacher, unabhängiger Zähler: Taste gilt als leuchtend, wenn die Tastenmitte deutlich gefärbt ist (Sättigung > 0,35, Helligkeit > 0,3); Ereignisse > 60 ms; Abgleich je Tonhöhe mit ±150 ms nach Ausgleich des Zeitversatzes.

| Datensatz | Code | Noten | gefunden | bestätigt |
|---|---|---|---|---|
| Diagnose 1 (Handy v2.5: 7 Noten) | v2.6+ | 288 | 98 % (284/289) | 99 % |
| Diagnose 2 (Handy v2.6: 567 Noten) | v2.7 | 285 | 97 % (280/289) | 98 % |
| Diagnose 2 | v2.8 | 287 | nicht separat gegengeprüft | – |

- Ergebnis golden hour (v2.6+, Diagnose 1): 219 rechts, 69 links, 221 Anschläge, davon 41 Akkorde, Tonumfang E3–B5. Die schnelle Fis4/Gis4-Wechselfigur der rechten Hand ab ~0:17 wird sauber erkannt.
- **Achtung beim Vergleichen**: Die App verschiebt den Song so, dass die erste Note bei 1,0 s liegt. Bei Diagnose 2 beträgt der Versatz App → Video +6,28 s.
- Live-Zähler (nachgestellt mit Diagnose 1): 0:16 → 14, 0:47 → 103, 1:38 → 204, 2:30 → 288.
- Synthetischer Prüfstand: zuletzt v1.9 (36 Videos, 98,2 % Treffer / 99 % Präzision). **Nach v2.6–2.8 nicht neu gelaufen.**

## 6. Diagnose-Werkzeuge

### Aufnahme am Handy
Einstellungen → Fehlersuche → „YouTube-Umwandlung aufzeichnen“ → Umwandlung starten → am Ende Android-Speichern-Dialog. Datei: `klavier-diagnose-DATUM.txt` (Android hängt eventuell `.json` an), 3–10 MB.

Format: `KTDIAG1\n` + base64(gzip( `KTD1` + u32le Kopflänge + JSON-Kopf + Frames ))
- Frame: f64le native Zeit (ms), f64le YouTube-Zeit (s), f64le geglättete Videozeit (s, NaN = verworfen), f64le Player-Zustand, danach `w·n·3` Bytes RGB (n = 7 Zeilen, w = 480)
- Kopf (JSON): `ua`, `screen`, `dpr`, `box`, `quality`/`qualityEnd`, `videoId`, `scanRows`, `scanDet`, `keys` (inkl. `rest` = Ruhefarben), `kw`, `rowsSent`, `still` (Fundbild als JPEG-Data-URL), `notes` (Ergebnis am Handy), `reason` (`done`/`hole`/`fewnotes`/`nokb`/`black`), `stills` (bei `nokb`/`black`)
- Code: `diagStart`/`diagFrame`/`diagSave` (ab Z. ~2145)

### Auswertung am PC
```
python3 tools/bench/diag.py DATEI --out /tmp/diag --replay
```
- gibt Bildrate, Abstände, Zeitstempel-Qualität, Player-Zustände aus
- schreibt `still.jpg`, `meta.json`, `rec.json` (Format von `tools/bench/replay.js`)
- `--replay`: bestimmt die Tastatur mit dem **aktuellen** Code neu aus `still.jpg` und spielt alle Bilder durch `scanCore`/`finishScan` → `replay-notes.json`
- **exakter Handy-Zustand** (alte Tastenpositionen + Ruhefarben vom Handy): `replay.js` direkt mit unverändertem `rec.json` ausführen
- Voraussetzung: Python 3, Playwright, `/usr/bin/google-chrome`

## 7. Bekannte Risiken und offene Punkte (priorisiert)

1. **Live-Test v2.8 am Handy fehlt.** Alles oben ist Nachspielen echter Handy-Daten. Nächster Schritt: Nutzer wandelt golden hour neu um (vorher in den Einstellungen „Neu laden“, bis „Version 2.8“ dasteht).
2. **Prüfstand bildet echte Videos schlecht ab.** `gen.py` sollte (a) schwarze Tasten wie beim echten Klavier versetzt zeichnen, (b) Intro-Bilder ohne Tastatur vor der Tastatur einbauen, (c) Versatz und Ruhefarben-Fehler als Regressionstest abdecken. Danach Bench neu laufen lassen (v2.6–2.8 nicht gegengeprüft).
3. **Tooling-Fehler**: `tools/bench/replay.py` liest `/tmp/bench/run.py` und `/tmp/bench/replay.js` (absolute Pfade aus einer früheren Sitzung) statt der Dateien im Repo → auf frischen Rechnern nicht lauffähig. `diag.py` ist davon nicht betroffen.
4. **Nur ein echtes Video getestet** (golden hour). Andere Referenzvideos (Interstellar `OQeUvNHR0Ac`: eine Farbe, dunkle Buchstaben; Fly `7mhJFks2n2g` / Time `SiirBAMcgkA`: 88 Tasten, sehr schmale Tasten) wurden mit den Fixes nicht am Handy geprüft. Seit v2.9: `ow` bis 1280 und Querformat → bei 88 Tasten ~18 px pro weißer Taste; noch kein 88-Tasten-Video getestet. Zweites Nutzer-Video SpongeBob `SG_cv29mAsA` hat denselben Stil wie golden hour.
5. ~~**Native Scanner läuft auf dem Main-Thread**~~ → erledigt in App 0.7 (HandlerThread). (PixelCopy-Callback, `getPixels`, Base64, JSON). Beim S22 unkritisch (24 Bilder/s), auf schwächeren Handys möglicherweise Bildverluste → wäre ein Fix in `android/` (Neuinstallation nötig).
6. ~~**Hochformat**~~ → erledigt in v2.9 (Querformat während der Umwandlung). Das Video wird als 16:9-Streifen in einer hohen Box gezeigt (`cropBars` schneidet die schwarzen Ränder ab). Querformat oder ein größerer Player brächte mehr Pixel pro Taste.
7. **Selbstkalibrierung (v2.7)**: übernimmt jede ~2 s stabile, ungefärbte Farbe als Ruhefarbe. Theoretisches Risiko: ein lange gehaltener, kaum gefärbter Tastendruck (z. B. sehr blasse Balkenfarbe) würde als „Ruhe“ gelernt. Bei golden hour kein Problem; bei Videos mit grauen oder weißen Leucht-Farben prüfen.
8. ~~**Keine Rückmeldung bei Teilausfall**~~ → erledigt in v2.9 (Markieren von Hand nach 25 s bzw. 15 s). Wenn `okT` sehr spät kommt, merkt der Nutzer das nur am Zähler. Eine Warnung („Tastatur wird seit X s nicht als normal erkannt“) plus automatische Diagnose wäre sinnvoll.
9. ~~**Kein MIDI-Export**~~ → erledigt in v2.9 / App 0.7. Die erzeugte MIDI-Datei liegt nur in der App (`kt_lib`, base64). Wunschkandidat: Knopf „Als MIDI-Datei speichern“ (Brücke `save` existiert, müsste Binärdaten unterstützen oder base64 im Dateiinhalt dekodieren).
10. **Sicherheit (projektweit)**: Keystore und Passwort (`klavier123`) liegen öffentlich im Repo.

## 8. Arbeitsregeln für dieses Projekt

- Vor jeder Änderung `git fetch`, `git status`, `git diff` prüfen; es arbeiten zeitweise mehrere Sitzungen am selben Repo.
- Nach jeder Änderung an `web/index.html` die Seite headless laden und auf `pageerror` prüfen. `node --check` auf das extrahierte Skript reicht nicht: Ein doppelt deklarierter Bezeichner (z. B. `noteTxt` gab es schon) legt die ganze App lahm und fällt nur im Browser auf.
- Versionstext `Version X.Y` in `web/index.html` bei jeder Änderung hochzählen (zwei Stellen), damit der Nutzer in den Einstellungen sieht, welche Version läuft.
- Entscheidungen des Nutzers (Abschnitt „Entscheidungen“ in `claude/video-erkennung-konzept.md` im Projekt): nur aus dem Bild, nie aus dem Ton; kein Server, keine Cloud; Video läuft genau einmal, nie zurückspringen; entweder 100 % fertig und gespeichert oder gar nichts; ein allgemeines Verfahren für alle Videos statt Nachbessern pro Video.
