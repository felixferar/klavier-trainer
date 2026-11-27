"""Baut die Ansicht der Hand-Simulation als eine HTML-Datei (Kern + Daten eingebettet).
usage: python3 tools/handsim/bauen.py DATEN.json AUSGABE.html     (DATEN.json: node tools/handsim/lauf.js --daten DATEN.json)"""
import sys, os
H = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(H, 'ansicht.html'), encoding='utf-8').read()
html = html.replace('/*KERN*/', open(os.path.join(H, 'kern.js'), encoding='utf-8').read()).replace('/*DATEN*/', open(sys.argv[1], encoding='utf-8').read())
open(sys.argv[2], 'w', encoding='utf-8').write(html); print(len(html), 'Zeichen →', sys.argv[2])
