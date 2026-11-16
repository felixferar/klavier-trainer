"""v5.32: Auswendig – der einfache Ablauf, an echten Noten (Fly Me to the Moon).
Je Häppchen: mit Noten (Vertipper ok) → aus dem Kopf (dunkel, wartet, Anker, Positionsleiste, Hilfe nach 5 s mit Zusammenhang, 1 Hilfe ab 10 Griffen ok)
→ Kette (die letzten bis zu 3 Häppchen am Stück aus dem Kopf, wartet). Ein Schritt 3× nicht geschafft → einmal mit Noten, keine Endlosschleife.
Formteile mit mehr als 3 Häppchen einmal ganz am Stück. Dann der ganze Song (folgt dir), an 2 Tagen = sitzt. Wiederholungen gebündelt am Sitzungsanfang.
Vorspielen mit Klang und mitspielen, Hand-Filter, Übernahme aus v5.31.
usage: python3 tools/bench/auswendigtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
S = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = open(__file__.replace('auswendigtest.py', 'auswendigtest.js')).read()
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 753, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, S['fly_me']); await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    c = {'Start: Häppchen 1 mit Noten, Vorspiel-Knopf, 2 Schritte (Häppchen 1 hat keine Kette)': r['p1'] == 'learn(1)' and r['learnScreen'] == [True, True, 2],
         'Vorspielen klingt, mitspielen bricht nichts ab': r['demo'] == [True, True] and r['along'] == [True, True],
         'mit Noten: 2 Vertipper = geschafft': r['learn2wrong'] == [True, 2, 1],
         'aus dem Kopf: dunkel, Anker, kein Vorlauf; Positionsleiste': r['p2'] == 'head(1)' and r['anchor'] == [True, 'anker', 0] and r['dark'][0] == 'dunkel' and r['dark'][1].startswith('Häppchen 1 · Griff 2 von 13'),
         'Hilfe nicht vor 5 s, danach von selbst mit Zusammenhang (grau/blass)': r['before5'] is None and r['after5'] == [True, 1, 'hilfe', True, True],
         '1 Hilfe bei 13 Griffen = geschafft; Häppchen 1 sitzt (Wiederholung morgen)': r['head1help'] == [True, 1, 3, 1],
         '2 Hilfen = nicht geschafft; 3× → einmal mit Noten für das Häppchen, dann wieder aus dem Kopf': r['p3'] == 'head(2)' and r['headFails'] == [[False, 2]] * 3 and r['reLearn'][0] == 'learn(2)+N' and r['reLearn'][1:3] == r['reLearn'][3:5] and r['reScreen'] == [True, True] and r['reOk'] == [True, False, 0] and r['afterRe'] == 'head(2)' and r['head2'] == [True, 2],
         'Kette 1–2: dunkel, wartet (kein Tempo), 1 Hilfe bei 26 Griffen ok → Häppchen 2 sitzt': r['p4'] == 'snowk(1-2)' and r['chainScreen'] == [True, 'anker', False, 26] and r['chain'] == [True, 1, 3],
         'Kette 1–3 dreimal nicht geschafft → Kette einmal mit Noten → wieder Kette': r['p5'] == 'snowk(1-3)' and r['chainFails'] == [[False, 3]] * 3 and r['chainRe'][0].endswith('+N') and r['chainRe'][1:3] == r['chainRe'][3:5] and r['chainReOk'] == [True, False] and r['afterChainRe'] == 'snowk(1-3)',
         'danach nur noch: mit Noten → aus dem Kopf → Kette (max. 3 Häppchen), keine Sondermodi, dann ganzer Song': all(x.split('(')[0] in ('learn', 'head', 'snowk') for x in r['seq']) and all(int(x[x.index('(') + 1:x.index('-')]) >= int(x[x.index('-') + 1:x.index(')')]) - 2 for x in r['seq'] if x.startswith('snowk')) and r['whole'] == 'whole',
         'Zwilling (zweites A) wird nicht neu gelernt, nur in der Kette mitgespielt, sitzt danach': r['twin'][0][4] == 0 and r['twin'][1] is False and r['twin'][2] and r['twin'][3] == 3 and r['twin'][4],
         'ganzer Song Tag 1 → heute nichts mehr': r['w1'][0] is True and r['w1'][1] == 1 and r['w1'][2] is None,
         'nächster Tag: Wiederholungen gebündelt am Anfang, dann ganzer Song → Song sitzt': r['seq2'][0].startswith('rev') and all(x.startswith('rev') for x in r['seq2'][:r['seq2'].index(next(x for x in r['seq2'] if not x.startswith('rev')))]) and r['sits'],
         'Wiederholung nicht geschafft → zurück auf aus dem Kopf, Balken sinkt': r['revFail'][0] is False and r['revFail'][1] == 1 and r['revFail'][2],
         'mitten in der Sitzung fällig → erst nächste Sitzung': r['midSess'] is None,
         'Hand-Filter: eigener Lernstand, zurück unverändert': r['hand'][0] == 'L' and r['hand'][1] == 'v10L' and r['hand'][2] and r['handBack'],
         'Übernahme aus v5.31: Kette geschafft → sitzt; ohne Kette → aus dem Kopf, Kette als Nächstes; alte Sondermodi weg': r['mig'][0] == 1 and r['mig'][1] == '3320' and r['mig'][2] is False and r['mig'][3] == 'snowk(1-3)',
         'Formteil > 3 Häppchen: einmal ganz am Stück, wartend, dunkel': r['form'][0] == 'form(1-5)' and r['form'][1] is True and r['formRun'] == [False, True, True],
         'keine Fehler': not errs}
    for k, x in c.items(): print(('OK  ' if x else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
