"""v5.26/v5.27 Auswendig v6 (v5.27: beim Vorspielen mitspielen) (musikalischer Schneeball) – Regeln einzeln geprüft. Konzept: claude/konzept-auswendig-v6.md
4–6 Formteile (> 30 Anschläge → 2 Hälften, Zwilling übernimmt, fast gleich erkannt) · 3 Stufen je 1× sauber (Kennenlernen mit Noten · Aus dem Kopf dunkel mit
Start-Anker, 0 Hilfen, Hilfe bleibt stehen · Im Fluss) · lokaler Schneeball (max. 3 Teile) · ganzer Song an 2 Tagen · 1 Streifer bei > 30 Anschlägen ·
Vorspielen mit Klang nur auf Knopf / tiefstes A · Wiederholungen gebündelt am Anfang, misslungen → Balken sinkt · Hand-Filter L/R/L+R · Übernahme aus v9.
usage: python3 tools/bench/awv6test.py $PWD/web/index.html"""
import sys, asyncio, json
from playwright.async_api import async_playwright
JS = open(__file__.replace('awv6test.py', 'awv6test.js')).read()
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS)
        await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    K = r['nParts']
    L = [x[1] for x in r['parts']]
    c = {'Häppchen nach Last (≤ 26, außer dem letzten ≥ 12 bzw. an Formgrenzen), Formteil-Grenzen an Ruheton/Atempause': max(L) <= 26 and r['cutsOk'],
         '4–6 Formteile; langer schneller Teil (44 Anschläge) → mehrere Häppchen; Zwilling und „fast gleich“ erkannt': 4 <= len(r['forms']) <= 6 and r['longSplit'] >= 2 and any(x[3] >= 0 for x in r['parts']) and any(x[4] >= 0 for x in r['parts']),
         'Start: Teil 1 Kennenlernen mit Noten, Vorspiel-Knopf, Hand-Umschalter': r['p1'] == ['learn', 0] and r['learnScreen'] == [True, True, True],
         'Kennenlernen: 1 falscher Ton (≤ 30 Anschläge) = nicht sauber': r['learnWrong'] == [False, 0],
         'tiefstes A = vorspielen MIT Klang': r['demo'] == [True] and r['demoTones'] >= 4,
         'beim Vorspielen mitspielen: kein Abbruch, kein neuer Versuch, nichts zählt, Tasten grün; Überspringen nur per Knopf': r['along'] == [True, True, True, 0, True, True] and r['demoSkip'],
         'nach dem Durchgang: tiefes A spielt vor, Mitspielen startet keinen neuen Versuch, kein Auto-Weiter': r['doneDemo'] == [True, True] and r['doneAlong'] == [True, True, True] and r['doneAfter'] == [True, True],
         'Kennenlernen 1× sauber → Aus dem Kopf': r['learnOk'] == [True, 1] and r['p2'] == 'head',
         'Aus dem Kopf: dunkel mit Start-Anker': r['anchor'] == [True, 'anker'],
         'Hilfe (B): Griff bleibt stehen, bis gespielt; zählt als nicht sauber': r['helpStays'] == [1, 'hilfe', True] and r['helpGone'] and r['headHelp'] == [False, 1],
         'Aus dem Kopf: falscher Ton ohne Hilfe zeigt nichts an, zählt aber (≤ 30)': r['headWrong'] == [False, 0, 1],
         'Aus dem Kopf 1× sauber → Im Fluss → sitzt, Wiederholung morgen': r['headOk'] == [True, 2] and r['p3'] == 'flow' and r['flowOk'][:4] == ['flow', True, 3, 1] and 18 <= r['flowOk'][4] <= 22,
         'Zusammensetzen 1+2 in 2 Schritten: erst am Stück aus dem Kopf (dunkel, wartet, Anker, Hilfe-Knopf), dann im Fluss': r['part2'] == [3] and r['snow1'] == ['snowk', 0, 1] and r['snowkScreen'] == [True, 'anker', False, True, 2] and r['snow1k'] == [True, True, False] and r['snow1b'] == ['snow', 0, 1] and r['snow1ok'] == [True, True],
         'Im Fluss: leicht ungleichmäßig (±0,1 s) = sauber': r['flowWobble'][0] is True,
         'Im Fluss: Denkpause (2,2 s statt ~0,3 s) = nicht sauber': r['flowPause'][0] is False and r['flowPause'][1] >= 1 and r['flowPause'][3],
         'Im Fluss: Hänger > 3 s → nächster Griff erscheint, Durchgang läuft weiter (kein Abbruch, nicht sauber)': r['hang'] == [1, True, 'hilfe', False] and r['hangGone'] and r['hangEnd'][0] and r['hangEnd'][1] is False and r['hangEnd'][2] == 0 and r['hangEnd'][3] == 0,
         'Zwilling „bekannt“, sitzt erst nach dem Spielen im Zusammenhang': r['twinKnown'],
         
         'Genau gleiches Häppchen übernimmt den Stand (kein neues Lernen)': r['twinSkipped'],
         'Schneeball: höchstens 3 Häppchen im Formteil, Naht zum vorigen Formteil, jedes Häppchen gekoppelt; lange Formteile einmal am Stück': r['snowMax3'] and r['snowAll'] and r['kBefore'] and r['snowSpans'][0] == 'S0-1' and r['formRuns'] == r['formNeed'],
         '> 30 Anschläge: 1 Streifer erlaubt, 2 nicht': r.get('tol2', [None])[0] is False and r.get('tol') == [True, 1, 1],
         'nach misslungenem Durchgang am Stück: erst die knifflige Stelle (±3 Griffe, im Durchgang), dann zurück am Stück': r['spotAfterFail'][0] == 'spot' and r['spotAfterFail'][3] <= r['spotAfterFail'][1] < r['spotAfterFail'][2] <= r['spotAfterFail'][4] and r['spotAfterFail'][2] - r['spotAfterFail'][1] <= 6 and r['backToChain'] == 'snow',
         'erst alle Teile + Schneebälle, dann der ganze Song': r['allSit'] and r['w1'] == 'whole',
         'ganzer Song Tag 1 → morgen nochmal (jetzt nichts mehr)': r['w1r'][:2] == [True, 1] and r['after1'] is None,
         'nächster Tag: Wiederholungen gebündelt am Anfang, dann ganzer Song → Song sitzt': r['revBundled'] and r['sits'],
         'misslungene Wiederholung: Teil zurück auf Aus dem Kopf, Balken sinkt': r['revFail'][0] is False and r['revFail'][1] == 1 and r['revFail'][2] == 0 and r['revFail'][3],
         'mitten in der Sitzung fällig → kommt erst in der nächsten Sitzung': r['midSess'] is None and r['newSess'] in ('rev', 'whole'),
         'Hand-Filter: L / R mit eigenem Lernstand, zurück zu Beide unverändert': r['handL'][0] == 'L' and r['handL'][1] == 'v10L' and all(r['handL'][2:]) and r['handR'] == ['R', True] and r['handBack'] == ['LR', True],
         'Übernahme aus v9 (gelernt → sitzt, verbunden → Schneeball, Tage)': r['mig'] == [True, True, 1, True],
         'Song-Seite liest den v6-Stand': r['info'] == [K, K],
         'keine JS-Fehler': not errs}
    bad = [k for k, v in c.items() if not v]
    for k, v in c.items(): print(('OK  ' if v else 'FAIL') + ' ' + k)
    print('ALLE OK' if not bad else f'{len(bad)} FEHLER'); sys.exit(1 if bad else 0)
asyncio.run(main())
