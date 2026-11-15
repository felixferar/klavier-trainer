"""v5.03: Fingersatz in der App.
usage: python3 tools/bench/fingertest.py [APP.html]   (Standard: web/index.html)
 1. Seite lädt ohne pageerror; eingebettetes Modul = tools/fingering/fingering.js (Version 0.3.0).
 2. Song mit Händen: rechts C-Dur-Tonleiter → 1 2 3 1 2 3 4 5, links Akkord C3-E3-G3 → 5 3 1 (tief→hoch).
 3. Einfarbiger Song (alle Töne "R", Bass tief): Bass bekommt die linke Hand (fingH = L), Melodie rechts.
 4. Abspielen zeichnet mit Fingerzahlen ohne Fehler; Schalter "Fingersatz" aus → keine Rechnung, kein Fehler.
 5. Auswendig öffnen (gleiche Noten) ohne Fehler; Fingerzahlen an MEM.song nach einem Bild.
 6. Fingersatz-Flagge ⚑: markiert die Stelle, Upload nach diag/fingerflags/ mit Tönen ±3 s, Finger, Hand, Begründung; nochmal drücken = weg.
Bildschirmfoto: /tmp/fingertest.png
"""
import sys, os, asyncio, json, re
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
APPF = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'web', 'index.html'))
SRC = open(os.path.join(HERE, '..', 'fingering', 'fingering.js'), encoding='utf-8').read()
JS = r"""()=>{const o={};
 o.version=window.Fingering&&Fingering.VERSION;
 const el=document.getElementById('fingering-js');o.inline=el?el.textContent:'';
 const mk=(ns,id)=>{const it={id,type:'midi',title:'Fingertest '+id,artist:'x',data:b64FromBuf(writeMidi(ns))};return it};
 const scale=[60,62,64,65,67,69,71,72].map((m,i)=>({m,start:i*0.3,dur:0.27,hand:'R'}));
 const chord=[48,52,55].map(m=>({m,start:3,dur:1,hand:'L'}));
 const it=mk(scale.concat(chord),'f1');LIB=[it];
 const s=songForItem(it);openSong(s,it.id);S.fingers=true;draw();
 const R=s.notes.filter(n=>n.hand==='R').sort((a,b)=>a.start-b.start),L=s.notes.filter(n=>n.hand==='L').sort((a,b)=>a.midi-b.midi);
 o.rh=R.map(n=>n.fing).join('');o.lh=L.map(n=>n.fing).join('');o.lhH=L.map(n=>n.fingH).join('');
 // einfarbig: alle "R", Bass tief
 const one=[];for(let k=0;k<8;k++){one.push({m:36+(k%2?7:0),start:k*0.5,dur:0.45,hand:'R'});one.push({m:72+[0,2,4,5,7,5,4,2][k],start:k*0.5+0.25,dur:0.2,hand:'R'})}
 const it2=mk(one,'f2');LIB.push(it2);const s2=songForItem(it2);openSong(s2,it2.id);draw();
 o.bassH=[...new Set(s2.notes.filter(n=>n.midi<50).map(n=>n.fingH))].join('');o.melH=[...new Set(s2.notes.filter(n=>n.midi>=70).map(n=>n.fingH))].join('');
 // Schalter aus
 S.fingers=false;s2._fingKey=null;draw();o.offNoCalc=s2._fingKey===null;S.fingers=true;
 openSong(s,it.id);t=0.5;draw();
 return o}"""
JS_FLAG1 = r"""()=>{window.__up=[];save('kt_ghtok','test');ghUpload=async(p,b)=>{window.__up.push([p,b]);return {ok:true}};shotSend=async()=>{};
 const it=LIB[0];openSong(songForItem(it),it.id);t=1.0;draw();document.getElementById('pFlag').click();return {red:document.getElementById('pFlag').style.color}}"""
JS_FLAG2 = r"""()=>{const u=window.__up[window.__up.length-1];const o={n:window.__up.length,path:u&&u[0],info:u&&u[1]};
 document.getElementById('pFlag').click();o.after=(load('kt_fingflags')||{})[songId].length;return o}"""
JS_MEM = r"""()=>{const it=LIB[0];let ok=true;try{openMem(it)}catch(e){ok=String(e)}return {ok}}"""
JS_MEM2 = r"""()=>{let e=null;try{memStart(0)}catch(x){e=String(x)}try{memDraw()}catch(x){e=e||String(x)}return {err:e,memFing:!!(MEM&&MEM.song&&MEM.song.notes.some(n=>n.fing))}}"""

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 900, 'height': 420}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + APPF); await pg.wait_for_timeout(1500)
        r = await pg.evaluate(JS); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/fingertest.png')
        f1 = await pg.evaluate(JS_FLAG1); await pg.wait_for_timeout(7000)  # Nachsende-Prüfung beim Öffnen verschiebt den Upload um bis zu 3 s
        f2 = await pg.evaluate(JS_FLAG2)
        import base64
        fi = json.loads(base64.b64decode(f2['info']).decode('utf-8')) if f2['info'] else {}; fl = (fi.get('flags') or [{}])[0]; nr = fl.get('near') or []
        print('Flagge:', f2['path'], json.dumps(nr[:2], ensure_ascii=False))
        m = await pg.evaluate(JS_MEM); await pg.wait_for_timeout(800)
        m2 = await pg.evaluate(JS_MEM2)
        inline = r.pop('inline'); body = re.sub(r'^/\* FINGERING-BEGIN[^\n]*\n', '', inline); body = re.sub(r'\n/\* FINGERING-END \*/$', '', body)
        checks = {
            'modul_gleich_quelle': body == SRC, 'version': r['version'] == '0.3.0',
            'rechts_tonleiter_12312345': r['rh'] == '12312345', 'links_akkord_531': r['lh'] == '531' and r['lhH'] == 'LLL',
            'einfarbig_bass_links': r['bassH'] == 'L' and r['melH'] == 'R', 'schalter_aus': r['offNoCalc'],
            'flagge_rot': f1['red'] != '', 'flagge_upload': f2['n'] == 1 and (f2['path'] or '').startswith('diag/fingerflags/') and fi.get('kind') == 'fingerflags',
            'flagge_inhalt': fl.get('T') == 1.0 and len(nr) >= 5 and all(x['f'] in (1, 2, 3, 4, 5) and x['fh'] in ('L', 'R') and x['why'] for x in nr),
            'flagge_weg': f2['after'] == 0,
            'auswendig_ok': m['ok'] is True, 'auswendig_finger': m2['memFing'] and not m2['err'], 'keine_pageerror': not errs,
        }
        print(json.dumps(r)); print('pageerrors', errs)
        for k, v in checks.items(): print(('OK    ' if v else 'FEHLER') + ' ' + k)
        bad = [k for k, v in checks.items() if not v]
        print('fingertest', 'OK' if not bad else 'FEHLER ' + ','.join(bad))
        await br.close(); sys.exit(1 if bad else 0)
asyncio.run(main())
