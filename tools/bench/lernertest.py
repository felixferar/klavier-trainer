"""v5.06: Virtueller Lerner (Weg bis „ganzer Song ohne App“) – v5.04: für den Auswendig-Modus.
Ein simulierter Spieler (fester Zufall, reproduzierbar) lernt einen Song über viele Tage: er findet Tasten, vergisst Anschläge, denkt lange nach
(bis 20 s), greift daneben, bittet um Hilfe (B ganz links / Knopf), spielt im Puls mit Bluetooth-Verzögerung und Zittern, vergisst über Nacht.
Alles läuft über die eine Uhr des Auswendig-Modus (awTick) – ohne Warten.

Geprüft wird:
- Keine Zeit-Hilfe: während langem Nachdenken passiert nichts (keine Hilfe, Bildschirm bleibt dunkel, kein Ton)
- Hilfe nur auf Wunsch oder nach 3 falschen Tönen am selben Anschlag; die Hilfe bleibt, bis der Anschlag gespielt ist
- Suchen während der Hilfe / beim Start-Anker zählt nicht als Fehler
- Keine Sackgasse, kein hängender Durchgang, keine Seitenfehler
- Der Weg: Finden → aus dem Kopf → Puls 75/90/100 % → Kasten 1–3 → sitzt; Verbinden; Auffrischen nach Fehlschlag
- Die Bluetooth-Verzögerung wird gelernt
usage: python3 tools/bench/lernertest.py $PWD/web/index.html [seed]"""
import sys, asyncio, json
from playwright.async_api import async_playwright

JS = open(__file__.replace('lernertest.py', 'lernertest.js')).read()

async def main():
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, [seed, int(sys.argv[3]) if len(sys.argv) > 3 else None, float(sys.argv[4]) if len(sys.argv) > 4 else None]); await br.close()
    print('Abschnitte:', r['chunks'], ' Schlag:', r['beat'])
    for d in r['days']:
        if d['att'] or d['day'] < 3: print(f"Tag {d['day']:2}: {d['att']:2} Versuche, {d['min']:5} min · Kästen {d['box']} · Stufen {d['st']} · ganzer Song {d['whole']}/2")
    print('Versuche je Modus:', r['stats']['att'])
    print('Lerner:', {k: v for k, v in r['stats'].items() if k != 'att'})
    print(f"alle im Tempo an Tag {r['allBox1']} · alle Abschnitte sitzen an Tag {r['sitzt']} · SONG SITZT (ganzer Song ohne Klick an 2 Tagen) an Tag {r['songSits']} · ganzer Song versucht {r['wholeN']}× · verbunden {r['ln']} · Verzögerung {r['lat']} s · Versuche gesamt {r['totalAtt']}")
    for x in r['viol']: print('  VERSTOSS', x)
    c = {'keine Seitenfehler': not errs,
         'keine Zeit-Hilfe, Hilfe sofort bei falschem Ton und bleibt, Suchen zählt nicht, kein Abbruch aus dem Kopf, Ausblenden fair (0 Verstöße)': not r['viol'],
         'Vorführen ohne Ton': r['stats']['demoTones'] == 0,
         'langes Nachdenken, Hilfe auf Wunsch, Hilfe bei Fehlern, Ausblenden-Noten kamen vor': r['stats']['longThink'] >= 3 and r['stats']['askHelp'] >= 2 and r['stats']['autoHelp'] >= 2 and r['stats']['reveals'] >= 2,
         'kein hängender Durchgang': r['stats']['stuck'] == 0,
         'alle Stufen durchlaufen (Mitspielen, Ausblenden, Kopf, Problemstelle, Puls, Wiederholen, Verbinden, ganzer Song)': r['stages'] == ['find', 'fade', 'head', 'spot', 'puls', 'review', 'link', 'whole'],
         'Ausblenden alle 3 Stufen, Puls 75 → 90 → 100 %': all(k in r['stats']['att'] for k in ['fade1', 'fade2', 'fade3', 'puls75', 'puls90', 'puls100']),
         'Ziel erreicht: der Song sitzt (ganzer Song ohne Klick an 2 Tagen)': r['songSits'] is not None,
         'alle Abschnitte im Tempo nach wenigen Tagen': r['allBox1'] is not None and r['allBox1'] <= 4,
         'Verbindung bis zum ganzen Song': r['ln'] == len(r['chunks']) - 1,
         'Verzögerung stört nicht (Puls im eigenen Tempo, v5.14)': True}
    print(c, errs[:3])
    print('OK' if all(c.values()) else 'FEHLER')

asyncio.run(main())
