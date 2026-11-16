"""v5.26/v5.28 (Auswendig v6, Häppchen + Formteile): Virtueller Lerner – ein simulierter Spieler (fester Zufall, reproduzierbar) lernt einen Song (Form A B A B' C, C lang und schnell)
über bis zu 14 Tage: er greift daneben, denkt lange nach und bittet dann um Hilfe (B ganz links), hört sich Teile an (tiefstes A), spielt im Fluss mit
leichtem Zittern und vergisst über Nacht. Alles läuft über die eine Uhr des Auswendig-Modus (awTick) – ohne Warten.
Geprüft wird:
- keine Zeit-Hilfe, Hilfe nur auf Wunsch und sie bleibt stehen; ein falscher Ton zeigt nichts an
- Wiederholungen nie am ersten Tag und nur gebündelt am Anfang einer Sitzung
- kein hängender Durchgang, keine Seitenfehler; Vorspielen klingt
- Ziel: alle Teile sitzen am ersten Tag, der Song sitzt (ganzer Song an 2 Tagen) nach wenigen Tagen; überschaubare Versuche je Teil
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
        r = await pg.evaluate(JS, [seed]); await br.close()
    print('Häppchen [Anschläge, Last, Formteil, Zwilling, fast wie]:', r['parts'])
    for d in r['days']:
        if d['att']: print(f"Tag {d['day']:2}: {d['att']:2} Versuche ({d['ok']} sauber, {d['rev']} Wiederholungen) · Stufen {d['st']} · Schneeball {d['sn']} · ganzer Song {d['whole']}/2 · {d['pct']} %")
    print('Versuche je Modus:', r['att']); print('Versuche je Teil [gesamt, sauber]:', r['perPart'])
    print(f"Hilfe {r['help']}× · falsche Töne {r['wrongs']} · vorgespielt {r['demos']}× · alle Teile sitzen an Tag {r['allSit']} · SONG SITZT an Tag {r['songSits']} · Versuche gesamt {r['total']}")
    for x in r['viol']: print('  VERSTOSS', x)
    worst = max(v[0] for v in r['perPart'].values()) if r['perPart'] else 0
    c = {'keine Seitenfehler': not errs,
         'keine Zeit-Hilfe, Hilfe bleibt stehen, Wiederholungen nur gebündelt am Anfang und nie am ersten Tag (0 Verstöße)': not r['viol'],
         'kein hängender Durchgang': r['stuck'] == 0,
         'Hilfe und Fehler kamen vor (der Lerner ist nicht perfekt)': r['help'] >= 2 and r['wrongs'] >= 5,
         'Vorspielen klingt': r['demos'] == 0 or r['demoTones'] == r['demos'],
         'alle Stufen kamen vor (Kennenlernen, Kopf, Fluss, Schneeball, ganzer Song, Wiederholung)': all(k in r['att'] for k in ['learn', 'head', 'flow', 'snow', 'whole', 'rev']),
         'alle Häppchen sitzen spätestens am zweiten Tag (max. 45 Versuche pro Tag)': r['allSit'] is not None and r['allSit'] <= 1,
         'Ziel erreicht: der Song sitzt nach wenigen Tagen': r['songSits'] is not None and r['songSits'] <= 3,
         f'überschaubar: höchstens 25 Versuche je Häppchen (schlimmster: {worst})': worst <= 25}
    for k, v in c.items(): print(('OK  ' if v else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
