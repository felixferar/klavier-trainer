import json,sys
s=sys.stdin.read()
def R(a,b):
    global s
    assert a in s,a[:60];s=s.replace(a,b)
R("Stand 13.11.2026, 12:55","Stand 13.11.2026, 16:45")
R("**Zuerst dieses Dokument lesen, dann `projekt-dokumente/konzept-auswendig-lernen-v5-adaptiv.md`.**","**Zuerst dieses Dokument lesen, dann `claude/analyse-warum-auswendig-schwer-2026-11-13.md` und `claude/konzept-auswendig-lernen-v6-spass.md` (aktuelle Lernlogik; v5 ist nur noch Hintergrund).**")
R("- **Auswendig lernen** (aktueller Schwerpunkt): Song in Abschnitte, Stufen mit abnehmender Hilfe, Messung jedes Durchgangs, adaptiv. Konzept v5 ist vollständig entschieden; umgesetzt ist bisher Etappe 1 + viele Verbesserungen (siehe 5).",
  "- **Auswendig lernen** (aktueller Schwerpunkt, seit v4.81–4.84 neu): Song in Teile nach der Musik (≈ 10 s, Phrasenenden, Wiederholungen als Zwillinge), je Teil 3 Schritte (Kennenlernen → Verblassen 100/70/40/15 % → Aus dem Kopf, „Fast“ reicht), Anlauf, automatisches Verbinden mit dem Teil davor, Hände einzeln nur nach 2× „Nicht geschafft“, automatisch weiter nach 3 s. Messung jedes Durchgangs, aber dem Nutzer nur knapp angezeigt.")
R("- **Seit v4.76/4.77 auch am PC testbar:** App in Chrome, Klavier direkt per Bluetooth aus Chrome (siehe `claude/anleitung-am-pc-testen.md`).","- PC-Testen (v4.76/4.77, Web MIDI/Web Bluetooth) ist gebaut, aber vom Nutzer aufgegeben: PC-Bluetooth zu schwach. Getestet wird am Handy.")
R("- Auswendig: `openMem`, `memLoad`, `memGroups` (Anschläge), `memSplit` (Abschnitte, 8–16 Anschläge),","- Auswendig: `openMem`, `memLoad`, `memGroups` (Anschläge), `memSplit2` (Teile nach der Musik, DP, Ziel 10 s; `memSplit` alt nur für Übernahme), `memTwins`/`memTwinBoost` (Zwillinge), `memMigrate` (alter Stand → neue Teile), `memPickNext` (Auffrischen → Verbinden → nächster Teil), `memChainRange`, `memApply` (3 Schritte, `MEM_FADE`, `rec.fe`, `rec.nf`), `memAuto` (automatisch weiter), `memOnlyTick` (Hände einzeln),")
R("(Lernstand je Song/Abschnitt: lvl, sk, stRuns, box, due, runs, passed …)","(Lernstand je Song/Teil: lvl 1–3, fe (Verblassen-Etappe), passed, box, due, runs, chained, nf, tw; Kennungen sig `p2:`, v6, k84)")
R("(nächster: `v4.78-…`), Versionstext in `web/index.html` an **zwei Stellen** hochzählen (`Version 4.77</small>` und `'Version 4.77 · '`)","(nächster: `v4.85-…`), Versionstext in `web/index.html` an **zwei Stellen** hochzählen (`Version 4.84</small>` und `'Version 4.84 · '`)")
R("Testliste (alle grün auf v4.77): `pcbletest","Testliste (alle grün auf v4.84): `kettetest teiletest flowtest schrittetest weiterknopftest verblasstest nomictest pcbletest")
R("## 5. Was zuletzt gebaut wurde (v4.65 – v4.77)","## 5. Was zuletzt gebaut wurde (v4.65 – v4.84)")
R("Mit echtem Klavier noch ungeprüft. |","Mit echtem Klavier: PC-Bluetooth zu schwach, Nutzer hat aufgegeben. |\n| 4.78 | online 13.11. | Kein Mikrofon mehr (App fragte am PC ungefragt danach). Test `nomictest`. |\n| 4.79 | online 13.11. | Noten verblassen nach und nach (Grundlage für Schritt 2). Test `verblasstest`. |\n| 4.80 | online 13.11. | Weiter-Knöpfe kleben unten, kein Scrollen. Test `weiterknopftest`. |\n| 4.81 | online 13.11. | **Konzept v6:** 3 Schritte statt 4 Stufen mit 85-%-Schwelle; „Fast“ reicht; Übersicht „Du kannst m:ss von m:ss“. Test `schrittetest`. |\n| 4.82 | online 13.11. | Hilfe schneller und als Balken (Verblassen 1,5 s, Kopf 2 s); 4 Verblassen-Etappen; automatisch weiter nach 3 s / nächster Taste, Pause. Test `flowtest`. |\n| 4.83 | online 13.11., 16:41 | **Teile nach der Musik** (`memSplit2`), Zwillinge, Anlauf (2 Anschläge davor, grau), Übernahme alter Stand. Test `teiletest`. |\n| **4.84** | **online 13.11., 16:41** (Commit 76c138e, Pages success) | **Verbinden** automatisch (additiv), Hände einzeln nur nach 2× „Nicht geschafft“, weniger Zahlen für den Nutzer. Test `kettetest`. |")
i=s.index("## 6. Offene Punkte (Priorität)");j=s.index("## 7. Entscheidungen")
s=s[:i]+"""## 6. Offene Punkte (Priorität)

1. **Rückmeldung zu v4.83/4.84 am Handy** (Teile sinnvoll? Anlauf hilfreich? Verbinden?).
2. App spielt beim Lernen die andere Hand/Begleitung leise mit (Analyse-Konzept Punkt 4).
3. „Was ist anders?“ bei Zwillingen.
4. Lektionen mit Belohnungs-Bildschirm, Tages-Serie (Konzept v6 Etappe 2).
5. Design nach Referenz (`claude/design-referenz-2026-11-13.md`): ruhig, dunkel, mitfliegende Kamera – noch nicht beauftragt.
6. Geteilte Note (Erkennung, golden hour Dis4) – nur mit Rückfalltest.

---

"""+s[j:]
R("- Auswendig lernen: eigener Bereich; App führt; **Fortschritt nur nach Können, nie nach Tagen**;","- Auswendig lernen: „mach es wissenschaftlich am effizientesten“; jeder gute Durchgang bringt weiter („Fast“ reicht); nur knappe Anzeige, Zahlen sind für die App; Hände einzeln nur wenn wirklich schwierig; nach dem Durchgang automatisch weiter; eigener Bereich; App führt; **Fortschritt nur nach Können, nie nach Tagen**;")
R("- Am PC will der Nutzer „nur noch testen“ – keine Einrichtungs-Schritte.","- PC-Testen aufgegeben (Bluetooth zu schwach); Mikrofon-Eingabe ist entfernt.")
R("Die wichtigen Dokumente liegen im Projekt: `konzept-auswendig-lernen-v5-adaptiv.md` (aktuelles Konzept),","Die wichtigen Dokumente liegen im Projekt: `analyse-warum-auswendig-schwer-2026-11-13.md`, `konzept-auswendig-lernen-v6-spass.md` (aktuell), `design-referenz-2026-11-13.md`, `konzept-auswendig-lernen-v5-adaptiv.md` (Hintergrund),")
sys.stdout.write(s)
