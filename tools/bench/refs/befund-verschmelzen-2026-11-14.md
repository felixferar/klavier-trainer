# Befund: verschmolzene schnelle Wiederholungen (14.11.2026, auf v4.99)

## Häufigkeit (mit Sollwert, score.py zählt 'zerschnitten'/'verschmolzen')
- YouTube-Test (10 Videos, 1879 Noten): 1 zerschnitten, **6 verschmolzen** – der häufigste echte Notenfehler.
- Datei-Weg derselben Videos: 2 verschmolzen. Prüfstand: alt24 1, Störgruppe 3, Prüfgruppe 1.
- Alle 6: zwei Töne derselben Taste mit 30–150 ms Pause (z. B. 18,02 s + 0,75 s, dann 18,80 s).

## Ursache (Pixel der Handy-Aufnahmen angesehen)
- Die **Taste** leuchtet in allen 6 Fällen ohne ein einziges Ruhe-Bild durch (bei 24 Bildern/s ist die Pause kürzer als ein Bild). Aus der Taste allein ist der zweite Anschlag nicht zu sehen.
- Die **Balken-Zeilen** zeigen den Spalt: Er wandert in 1–3 Bildern von oben nach unten durch die 4 Zeilen. Durch Unschärfe und Kompression ist er aber oft nur halb dunkel (z. B. (75,36,124) statt Hintergrund) und nur in 1–2 der 4 Zeilen sichtbar. Die App verlangt dagegen einen Hintergrund über ≥ 75 % der Tastenbreite in ≥ 3 Zeilen.

## Geprüft und verworfen
| Variante | YouTube-Test verschmolzen / zerschnitten | Prüfstand | echte Fremdvideos |
|---|---|---|---|
| v4.99 | 6 / 1 | – | – |
| „weicher Spalt“ (näher am Hintergrund als an der Balkenfarbe), 3 Zeilen | 5 / 2 | – | – |
| weicher Spalt + 2 Zeilen | 3 / **30** | – | – |
| nur 2 Zeilen statt 3 (harter Spalt) | 4 / 1 | alt24 F1@100 0,990 → 0,990, sonst gleich | **+1987 neue Balkenanfänge**, davon 541 genau 200–250 ms nach dem vorigen Balkenanfang |

Die Häufung bei 200–250 ms nach dem Balkenanfang sind **Buchstaben im Balken** (sie sitzen immer gleich weit hinter der Vorderkante). Mit nur 2 Zeilen werden sie in Fremdvideos massenhaft als Spalt gelesen → falsche Teilungen. Der Prüfstand und die selbst erzeugten Testvideos haben zu wenig solche Beschriftungen, deshalb fiel es dort nicht auf. **Nicht übernommen.**

## Folgerung
Mit den 4 dicht liegenden Zeilen lässt sich ein halb dunkler Spalt nicht sicher von Buchstaben trennen. Lösbar ist das mit dem geplanten Umbau (Schritt 3–5):
weit verteilte Zeilen, in denen man verfolgt, wie der Spalt mit der Fallgeschwindigkeit nach unten wandert,
und die Unterscheidung „Buchstabe = fester Abstand hinter der Vorderkante desselben Balkens“ gegen „Spalt = Ende eines Balkens + Anfang eines neuen“.
Für den Prüfstand: gen.py braucht Beschriftungen in wechselnden Abständen und Größen sowie mehr schnelle Wiederholungen (30–150 ms), sonst misst er diesen Fehler zu günstig.
