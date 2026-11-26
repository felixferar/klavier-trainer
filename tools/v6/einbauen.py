"""Kopiert tools/v6/lernen.js (Kern) und tools/v6/anbindung.js (Oberfläche) in web/index.html, zwischen die Marker LERNEN-BEGIN/END.
Die App bleibt eine einzige Datei (GitHub Pages + Offline-Kopie in der APK), der Lernmodus bleibt trotzdem ein eigenes Modul.
Aufruf: python3 tools/v6/einbauen.py   – tools/v6/test.js prüft den Kern in Node, tools/bench/v6test.py die eingebaute Fassung im Browser."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, '..', '..', 'web', 'index.html')
kern = open(os.path.join(HERE, 'lernen.js'), encoding='utf-8').read()
anb = open(os.path.join(HERE, 'anbindung.js'), encoding='utf-8').read()
html = open(APP, encoding='utf-8').read()
A = '<script id="lernen-js">/* LERNEN-BEGIN – Quelle: tools/v6/lernen.js, nicht hier bearbeiten */\n' + kern + '\n/* LERNEN-END */</script>\n'
B = '<script id="lernen-ui">/* LERNEN-UI-BEGIN – Quelle: tools/v6/anbindung.js, nicht hier bearbeiten */\n' + anb + '\n/* LERNEN-UI-END */</script>\n'
html = re.sub(r'<script id="lernen-js">.*?/\* LERNEN-END \*/</script>\n', '', html, flags=re.S)
html = re.sub(r'<script id="lernen-ui">.*?/\* LERNEN-UI-END \*/</script>\n', '', html, flags=re.S)
i = html.index('<script>\n', html.index('FINGERING-END'))           # Kern vor dem Hauptskript
html = html[:i] + A + html[i:]
j = html.rindex('<script>setTimeout(()=>{const s=document.getElementById(\'splash\')')  # Anbindung nach dem Hauptskript
html = html[:j] + B + html[j:]
open(APP, 'w', encoding='utf-8').write(html)
print('eingebaut: Kern', len(kern.splitlines()), 'Zeilen · Anbindung', len(anb.splitlines()), 'Zeilen')
