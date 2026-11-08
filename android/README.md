# Klavier Trainer – Android-App

## Einmalig einrichten (ca. 20 Minuten)
1. **Android Studio** installieren: https://developer.android.com/studio (kostenlos, Windows/Mac).
2. Diesen Ordner `KlavierTrainer` entpacken und in Android Studio mit **File → Open** öffnen.
   Beim ersten Öffnen lädt Android Studio alles Nötige herunter, das dauert ein paar Minuten.
3. **Virtuelles Handy anlegen:** rechts **Device Manager → + → Create Virtual Device**,
   z. B. „Pixel 8“ mit dem neuesten Android-Image.

## App am PC starten (wie am Handy)
- Oben den grünen **▶ Run**-Knopf drücken. Das virtuelle Handy startet und zeigt die App.
- **Quer drehen:** die Dreh-Buttons in der Leiste neben dem Emulator.
- **Mikrofon im Emulator:** in der Emulator-Leiste **⋯ (Extended Controls) → Microphone →
  „Virtual microphone uses host audio input“** einschalten. Dann hört die App über das
  Mikrofon deines PCs zu (z. B. das Klavier daneben oder Töne von einem anderen Gerät).

## Neue Version von Claude übernehmen
Ersetze die Datei `app/src/main/assets/www/index.html` durch die neue Version und drück
wieder **▶ Run**. Alles andere bleibt gleich.

## Später aufs echte Handy
- **Build → Build App Bundle(s) / APK(s) → Build APK(s)** erzeugt eine `.apk`-Datei,
  die du aufs Handy kopierst und installierst („Installation aus unbekannten Quellen“ erlauben).
- Oder Handy per USB anschließen (Entwickleroptionen + USB-Debugging an) und direkt ▶ Run.

## Aufbau
- `app/src/main/assets/www/index.html` – die komplette App-Oberfläche und Logik
- `app/src/main/java/.../MainActivity.java` – Android-Hülle: Vollbild, Bildschirm bleibt an,
  Mikrofon-Berechtigung, Dateiauswahl für MIDI, Zurück-Taste
