"""Kopiert tools/fingering/fingering.js in web/index.html (zwischen den Markern FINGERING-BEGIN/END).
Aufruf: python3 tools/fingering/einbauen.py   – danach prüft tools/bench/fingertest.py, dass beide gleich sind."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, '..', '..', 'web', 'index.html')
src = open(os.path.join(HERE, 'fingering.js'), encoding='utf-8').read()
html = open(APP, encoding='utf-8').read()
block = '<script id="fingering-js">/* FINGERING-BEGIN – Quelle: tools/fingering/fingering.js, nicht hier bearbeiten */\n' + src + '\n/* FINGERING-END */</script>\n'
if 'FINGERING-BEGIN' in html:
    html = re.sub(r'<script id="fingering-js">/\* FINGERING-BEGIN.*?/\* FINGERING-END \*/</script>\n', lambda m: block, html, flags=re.S)
else:
    i = html.index('<script>\n')
    html = html[:i] + block + html[i:]
open(APP, 'w', encoding='utf-8').write(html)
print('eingebaut:', len(src), 'Zeichen')
