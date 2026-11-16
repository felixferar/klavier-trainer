"""v5.32: Der Auswendig-Ablauf an 7 echten Songs aus den Handy-Aufnahmen (89 bis 910 Anschläge, u. a. Fly Me to the Moon, Für Elise).
Ein simulierter Lerner (Fehler, Hilfe, Vergessen über Nacht, höchstens 45 Versuche pro Tag) übt jeden Song bis zu 14 Tage.
Geprüft: jeder Song wird fertig („Song sitzt“), nichts hängt, keine Endlosschleife (höchstens 3 Fehlversuche hintereinander am selben Schritt),
überschaubarer Aufwand (im Schnitt höchstens 7 Versuche pro Häppchen inkl. Wiederholungen), keine Regelverstöße, keine Seitenfehler.
Dauer: einige Minuten. usage: python3 tools/bench/allesongstest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
JS = open(os.path.join(HERE, 'lernertest.js')).read()
SONGS = json.load(open(os.path.join(HERE, 'fixtures', 'echte_songs.json')))
async def one(app, name, notes):
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + app); await pg.wait_for_timeout(1500); await pg.evaluate("localStorage.clear()")
        try: r = await pg.evaluate(JS, [7, notes, 14])
        except Exception as e: r = {'crash': str(e)[:120]}
        await br.close()
    return r, errs
async def main():
    ok = True
    for name, notes in SONGS.items():
        r, errs = await one(sys.argv[1], name, notes)
        if 'crash' in r: print(f'FAIL {name}: Abbruch {r["crash"]}'); ok = False; continue
        n = len(r['parts']); per = r['total'] / n
        c = {'fertig': r['songSits'] is not None, 'hängt nicht': r['stuck'] == 0, 'keine Schleife': r.get('maxStreak', 0) <= 3,
             'Aufwand': per <= 7, 'Regeln': not r['viol'], 'Seite': not errs}
        good = all(c.values()); ok = ok and good
        print(('OK  ' if good else 'FAIL') + f" {name:12} {n:3} Häppchen · Song sitzt an Tag {None if r['songSits'] is None else r['songSits'] + 1} · {r['total']} Versuche ({per:.1f}/Häppchen) · Fehlserie {r.get('maxStreak', 0)}" + ('' if good else '  ← ' + ', '.join(k for k, x in c.items() if not x)), flush=True)
    print('OK' if ok else 'FEHLER'); sys.exit(0 if ok else 1)
asyncio.run(main())
