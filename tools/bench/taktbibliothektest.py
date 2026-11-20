"""Takt-Schnitt an allen umgewandelten Songs aus dem Diagnose-Archiv prüfen.

Liest alle *_done.ktd.gz aus dem Diagnose-Repo (je Video die neueste Umwandlung),
schneidet jeden Song mit awParts/awTakt aus web/index.html und meldet Auffälligkeiten:
Takt nicht erkannt, Zeile kürzer als 1 s, länger als 13 s, Last über 32.

usage: python3 tools/bench/taktbibliothektest.py $PWD/web/index.html [PFAD/klavier-diagnose]
"""
import sys, os, glob, json, asyncio, statistics as st
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diag import load

APP = sys.argv[1]
DIAG = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/klavier-diagnose'

def songs():
    best = {}
    for f in sorted(glob.glob(os.path.join(DIAG, 'diag', '*_done.ktd.gz'))):
        try:
            meta, _ = load(f)
        except Exception:
            continue
        vid, ns = meta.get('videoId'), meta.get('notes') or []
        if vid and len(ns) >= 40:
            best[vid] = ns
    return best

JS = """(ns)=>{const notes=ns.map(([m,s,d,h])=>({midi:m,start:s,dur:d,hand:h}));const gs=memGroups(notes);MEM.notes=notes;
  const C=awParts(gs,notes);return {takt:!!MEM.takt,n:C.length,L:C.map(P=>P.L),dur:C.map(P=>+(gs[P.b].start-P.t0).toFixed(2))}}"""

async def main():
    S = songs()
    if not S:
        print('keine Songs gefunden in', DIAG); sys.exit(2)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + APP); await pg.wait_for_timeout(1500)
        R = {k: await pg.evaluate(JS, ns) for k, ns in S.items()}
        await br.close()
    bad = []
    for k, r in R.items():
        why = []
        if not r['takt']: why.append('kein Takt')
        if min(r['dur']) < 1.0: why.append(f"kurz {min(r['dur'])} s")
        if max(r['dur']) > 13: why.append(f"lang {max(r['dur'])} s")
        if max(r['L']) > 32: why.append(f"Last {max(r['L'])}")
        if why: bad.append((k, r['n'], why))
    D = [x for r in R.values() for x in r['dur']]
    print(f"{len(R)} Songs · Takt erkannt {sum(r['takt'] for r in R.values())} · Zeilen {len(D)} · Dauer Median {st.median(D)} s")
    for k, n, why in bad: print(f'  auffällig {k:12} {n:3} Zeilen · ' + ', '.join(why))
    ok = not errs and sum(r['takt'] for r in R.values()) >= 0.95 * len(R) and len(bad) <= 0.1 * len(R)
    print('Seitenfehler', errs); print('OK' if ok else 'FEHLER'); sys.exit(0 if ok else 1)

asyncio.run(main())
