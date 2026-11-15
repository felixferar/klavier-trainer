"""v5.06: Regeln des Auswendig-Modus einzeln – Weg bis „ganzer Song ohne App“.
Mitspielen (2× in Folge ≤ 2 Fehler) · Ausblenden (3 Stufen, versteckte Note erscheint bei falschem Ton, zurück bei ≥ 3 gebrauchten Noten) · Aus dem Kopf (Anker bis gespielt,
keine Zeit-Hilfe, falscher Ton → richtiger erscheint sofort, es geht dort weiter, kein Abbruch, B ganz links) · Problemstelle (nach Hilfe, dann wieder ganz; ab 3 Hilfen zurück
zum Ausblenden) · Vorführen sichtbar ohne Ton (tiefstes A) · Im Puls (Einzählen, Metronom, 75 → 90 → 100 %, 1 Verpasser erlaubt) · Kästen · Verbinden ohne Obergrenze
· ganzer Song ohne Klick (folgt dem Spieler, überspringt, keine Hilfe, Rhythmus relativ, 2 Tage = sitzt, Patzer-Abschnitte werden fällig) · Vorgriff · 4-Ton-Akkord ·
Ende nach dem letzten Ton · Taste nach dem Versuch = weiter · Hintergrund zählt nicht · keine Zeitgeber.
usage: python3 tools/bench/awregeltest.py $PWD/web/index.html"""
import sys, asyncio, json
from playwright.async_api import async_playwright
JS = open(__file__.replace('awregeltest.py', 'awregeltest.js')).read()
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS)
        await pg.evaluate("()=>{window.__bg0=[(load('kt_v8log')||[]).length,JSON.stringify(MEM.rec.v9.ch)];Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true});awStart({k:0,mode:'head'});const R=MEM.run;for(const m of MEM.gs[R.pos].mids)memPress(m,'kb');memPress(30,'kb');document.dispatchEvent(new Event('visibilitychange'))}")
        r['bg'] = await pg.evaluate("({run:!!MEM.run,home:!$('#memHome').classList.contains('hidden'),zaehlt:(load('kt_v8log')||[]).length!==window.__bg0[0]||JSON.stringify(MEM.rec.v9.ch)!==window.__bg0[1]})")
        await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    c = {'Akkord-Versatz bleibt ein Anschlag': r['vorgriffGrp'],
         'Mitspielen: Bildschirm an; 3 Fehler = nicht gut; erst 2 gute in Folge → Ausblenden': r['p1'] == 'find' and r['findScreen'] and r['find1'] == [False, 0, 0] and r['find2'] == [True, 1, 0] and r['find3'] == [True, 0, 1, 0],
         'Ausblenden Stufe 1: jede 3. Note versteckt, Hinweis': r['p2'] == ['fade', 0] and r['hide0'].startswith('001001') and r['fadeState'] == 'ausblenden' and r['hiddenMsg'],
         'versteckte Note fehlt → falscher Ton lässt sie erscheinen (kein Fehler)': r['reveal'] == [True, 1, 0],
         'Ausblenden geschafft → nächste Stufe; zu viele gebrauchte Noten → Stufe zurück': r['fade0'] == [True, 1, 1] and r['hide1'].startswith('011011') and r['fadeBack'][0] is False and r['fadeBack'][1] >= 3 and r['fadeBack'][2] == 0,
         'Stufe 3: nur der Anfang sichtbar; geschafft → aus dem Kopf': r['hide2'].startswith('01') and set(r['hide2'][1:]) == {'1'} and r['fade2'] == [True, 2],
         'Aus dem Kopf: Anker bis gespielt (30 s), Suchen zählt nicht, dann dunkel': r['p3'] == 'head' and r['anchor0'] and r['anchorStays'] and r['anchorSearch'] == 0 and r['dark'],
         'keine Zeit-Hilfe: 25 s nachdenken → nichts, kein Ton': r['thinkNoHelp'],
         'falscher Ton → richtiger erscheint sofort und bleibt (20 s), Suchen zählt nicht, es geht dort weiter': r['wrongShows'] == [1, 1, True] and r['helpState'] == 'hilfe' and r['showStays'] and r['searchFree'] and r['continues'],
         'kein Abbruch bei vielen Fehlern': r['noAbort'],
         'ab 3 Hilfen → zurück zum Ausblenden (Stufe 2)': r['head1'] == [False, True, 1, 1] and r['p4'] == 'fade',
         'B ganz links → Hilfe; 1 Hilfe → Problemstelle um die Stelle': r['p5'] == 'head' and r['bHelp'] == [1, True] and r['spot'][0] is False and r['spot'][1] and r['spot'][1][0] <= r['spot'][2] <= r['spot'][1][1],
         'Problemstelle: nur die Stelle, mit Anker; geschafft → wieder ganzer Abschnitt aus dem Kopf → Puls': r['p6'] == 'spot' and r['spotRange'][2] and r['spotOk'] == [True, None] and r['p7'] == 'head' and r['head2'] == [True, 3],
         'Vorführen (tiefstes A): sichtbar, ohne Ton, Tasten zählen nicht, danach weiter': r['p8'] == ['puls', 75] and r['demo'][0] and r['demo'][1] == 'vorfuehren' and r['demoIgnore'] and r['demoKeys'] and r['demoSilent'] and r['demoEnd'],
         'Puls: „Start“ (wartet), Metronom auf dem Schlag': r['clicks'][0] and r['clicks'][1] >= 6 and abs(r['clicks'][2] - 0.5) < 0.02 and r['clicks'][3] and r['pulsTones'] >= 6,
         'Puls 75 → 90; 2 Verpasser = nochmal, 1 Verpasser = geschafft; 100 % → Kasten 1 (10 min)': r['puls1'] == [True, 1] and r['pulsMiss'] == [False, 2, 1] and r['oneMiss'] == [True, 1, 2] and r['p9'] == 100 and r['box1'] == [1, 10],
         'Kästen: 10 min → Kasten 2 (morgen) → gelernt → sitzt (14 Tage); Patzer → zurück + auffrischen': r['rev'] == ['review', 0] and r['revSp'] == 100 and r['box2'][0] == 2 and 18 <= r['box2'][1] <= 21 and r['box3'] == [3, True] and r['box4'] == [4, 14] and r['fail'] == [False, 3, 1],
         'Verbinden ohne Obergrenze (Kette wächst bis zum ganzen Song)': r['chain'][0] == 'link' and r['chain'][1] == 0 and r['chain'][2] == r['chain'][3] - 1 and r['chainSp'] == 100 and r['chainOk'] == [True, True],
         'ganzer Song: alles, dunkel, ohne Klick, ohne Anker, ohne Hilfe': r['w1'] == 'whole' and r['wSetup'][0] == 0 and r['wSetup'][1] == r['wSetup'][2] and r['wSetup'][3] and r['wSetup'][4] == 0 and not r['wSetup'][5] and r['wNoHelp'],
         'ganzer Song in eigenem (langsamerem) Tempo geschafft → 1 Tag, morgen nochmal': r['w1r'][0] and r['w1r'][1] == 0 and 0.75 <= r['w1r'][4] <= 0.9 and r['w1r'][5] == 1 and 18 <= r['w1r'][6] <= 21,
         'zweiter Tag (1 ausgelassen, die App springt mit) → Song sitzt, alle 14 Tage': r['w2'] == 'whole' and r['w2r'][0] and r['w2r'][1] == 1 and r['w2r'][2] and r['w2r'][3] == 14,
         'viele Patzer → nicht geschafft, Abschnitt mit Patzer wird fällig': r['w3'][0] is False and r['w3'][1] > 3 and r['w3'][2] and r['w3'][3] == 'review',
         'Vorgriff: versetzter Akkordton zuerst zählt nicht als Fehler': r['vorgriff'] == [0, True],
         '4-Ton-Akkord: 4. Ton nach dem Weiterspringen kein Fehler, 1 s später schon': r['chord4'] == 0 and r['chord4late'] >= 1,
         'Ende erst nach dem letzten Ton; Taste danach = weiter': r['endWait'] and r['endDone'] and r['keyNext'],
         'Hintergrund → endet, Übersicht, zählt nicht': r['bg'] == {'run': False, 'home': True, 'zaehlt': False},
         'Rückblick: Fehlerstelle (Anschlag 3, falsche Taste, Hilfe) wird erkannt und benannt': r['rb'] == [True, True, True, True, True],
         'Weg-Anzeige beim Spielen (erst Töne ohne Uhr, dann Takt)': r['weg'],
         'Start beim Spielen: wartet (Metronom tickt), falsche Taste startet nicht, erster Ton startet': r['start'] == [True] * 8,
         'Puls im eigenen Tempo (85 %, gleichmäßig) = bestanden, nichts verpasst': r['eigen'][:5] == [True, True, 0, 0, 0] and abs(r['eigen'][5] - 0.85) < 0.03,
         'ein Ton 0,3 s daneben = 1 ungleichmäßig, noch bestanden; zwei = nicht bestanden': r['einAus'] == [True, 1, True] and r['zweiAus'][0] is False and r['zweiAus'][1] == 2,
         'zu langsam (60 % vom Ziel) = nicht bestanden, mit Hinweis': r['langsam'] == [False, 0, True],
         'kleine Wackler (±70 ms) = bestanden (machbar)': r['wackel'] == [True, 0],
         '5 s Pause beendet den Durchgang': r['pause'] == [True, True],
         'Metronom beim Mitspielen: tickt mit der Musik, schweigt wenn das Lied wartet': r['findClick'] == [True, True, True],
         'Metronom ist ein echter Klick (kein Klavierton)': r['klick'] == [True],
         'perfekter Weg kurz (≤ 5 Durchgänge, ≤ 2 dunkel) und Übergang vom Abschnitt davor': r['pfad'][0] <= 5 and r['pfad'][1] <= 2 and r['pfad'][3] is True,
         'Puls-Start zeigt den ersten Ton (blau, mit Namen)': r['h1'] == ['start', True],
         'Taste beim Vorführen überspringt es': r['h2'] == [True, True],
         'Akkord halb gespielt + nächster Ton → geht weiter, kein Fehler': r['h3'] == [True, 0],
         'ganzer Song: 8 s Hänger → Durchgang endet (nicht bestanden)': r['h4'] == [True, True, True],
         'Puls: wahllos falsche Tasten nach dem Start → endet trotzdem nach 5 s ohne Fortschritt': r['h5'] == [True, True],
         'keine Zeitgeber im Lernablauf': r['timers'] == 0,
         'keine Fehler': not errs}
    for k, v in c.items():
        if not v: print('  NICHT OK:', k)
    print('OK' if all(c.values()) else 'FEHLER')
asyncio.run(main())
