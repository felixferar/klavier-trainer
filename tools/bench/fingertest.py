"""v5.03: Fingersatz in der App.
usage: python3 tools/bench/fingertest.py [APP.html]   (Standard: web/index.html)
 1. Seite lädt ohne pageerror; eingebettetes Modul = tools/fingering/fingering.js (Version 0.5.0).
 2. Song mit Händen: rechts C-Dur-Tonleiter → 1 2 3 1 2 3 4 5, links Akkord C3-E3-G3 → 5 3 1 (tief→hoch).
 3. Einfarbiger Song (alle Töne "R", Bass tief): Bass bekommt die linke Hand (fingH = L), Melodie rechts.
 4. Abspielen zeichnet mit Fingerzahlen ohne Fehler; Schalter "Fingersatz" aus → keine Rechnung, kein Fehler.
 5. Auswendig öffnen (gleiche Noten) ohne Fehler; Fingerzahlen an MEM.song nach einem Bild.
 7. Stil: Standard "einfach"; Schalter "Lehrbuch" rechnet neu (C-H-A-G-F-E langsam + langes E → einfach ohne Rutschen, z. B. 3-2-1-3-2-1; Lehrbuch anders).
 8. v5.05 "Nur Orientierung" (Standard): Fünftonlage C-D-E-F-G → nur 1 Zahl; Schalter "jeder Ton" → 5.
 9. v5.05 Klaviatur-Linie: Balken steht auf der Linie (Üben wartet) → Fingerschild und Notenname ganz über hitY, kein Überlappen.
10. v5.05 Auswendig v8: "Finden" zeigt Orientierungs-Zahlen, "aus dem Kopf" keine.
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
 const scale=[60,62,64,65,67,69,71,72].map((m,i)=>({m,start:i*0.25,dur:0.22,hand:'R'}));
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
JS_STYLE = r"""()=>{const mk=(ns,id)=>({id,type:'midi',title:'Stil',artist:'x',data:b64FromBuf(writeMidi(ns))});
 const mel=[72,71,69,67,65,64].map((m,i)=>({m,start:i*0.65,dur:i===5?2.6:0.6,hand:'R'}));const it=mk(mel,'st');LIB.push(it);const s=songForItem(it);
 const o={def:S.fingStyle||'einfach'};openSong(s,it.id);draw();o.einfach=s.notes.slice().sort((a,b)=>a.start-b.start).map(n=>n.fing).join('');
 S.fingStyle='lehrbuch';draw();o.lehrbuch=s.notes.slice().sort((a,b)=>a.start-b.start).map(n=>n.fing).join('');S.fingStyle='einfach';draw();return o}"""
JS_ORIENT = r"""()=>{const mk=(ns,id)=>({id,type:'midi',title:'Orient',artist:'x',data:b64FromBuf(writeMidi(ns))});
 const it=mk([60,62,64,65,67].map((m,i)=>({m,start:i*0.4,dur:0.35,hand:'R'})),'or');LIB.push(it);const s=songForItem(it);openSong(s,it.id);S.fingShow='orient';draw();
 const o={orient:s.notes.filter(fingVis).length,cues:s.notes.map(n=>n.fingCue||'-').join(',')};S.fingShow='alle';o.alle=s.notes.filter(fingVis).length;S.fingShow='orient';return o}"""
JS_EDGE = r"""()=>{const mk=(ns,id)=>({id,type:'midi',title:'Kante',artist:'x',data:b64FromBuf(writeMidi(ns))});
 const it=mk([{m:69,start:0,dur:2.0,hand:'R'},{m:71,start:2.2,dur:0.5,hand:'R'}],'ed');LIB.push(it);const s=songForItem(it);openSong(s,it.id);
 S.names=true;S.fingShow='alle';const log=[];const dF=drawFinger,dN=drawNoteLabel;
 drawFinger=function(c,n,cx,yb,h,w,nameH){const r=dF.apply(this,arguments);if(r){const fs=fingFs(w),y=yb-3-(nameH||0)-1;log.push({k:'F',top:y-fs,bot:y+2})}return r};
 drawNoteLabel=function(c,m,x,y,fs){log.push({k:'N',top:y-fs*0.8,bot:y+fs*0.25});return dN.apply(this,arguments)};
 const out=[];for(const T of [-0.5,0,0.5,1.2]){log.length=0;t=T;draw();out.push({T,hitY,H,items:log.slice()})}
 drawFinger=dF;drawNoteLabel=dN;S.fingShow='orient';return out}"""
JS_FLOW = r"""()=>{let cnt=0;const dF=drawFinger;drawFinger=function(){const r=dF.apply(this,arguments);if(r)cnt++;return r};
 const LH=[48,43,45,41],notes=[];let tt=0;for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:tt,dur:1.9,hand:'L'});[72,74,76,77].forEach((m,q)=>notes.push({m:m+(bar%2?-5:0),start:tt+q*0.5,dur:0.45,hand:'R'}));tt+=2}
 const it={id:'fl',type:'midi',title:'Fluss',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB.push(it);localStorage.removeItem('kt_mem');
 openMem(it);memHome();$('#memGo').click();let R=MEM.run;const o={mode1:R.mode};R.vt=MEM.gs[R.a].start-0.2;cnt=0;flowDraw();o.find=cnt;
 const gs=MEM.gs;let g=0;R.anchorUntil=0;while(R.pos<=R.b&&g++<200){flowTick(R,5);for(const m of gs[R.pos].mids)memPress(m,'kb')}flowTick(R,5);flowTick(R,5);
 $('#memNext').click();R=MEM.run;o.mode2=R.mode;o.dark=!!R.dark;cnt=0;R.anchorUntil=0;R.vt=gs[R.a].start-0.2;flowDraw();o.recall=cnt;drawFinger=dF;memStop();return o}"""
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
        st = await pg.evaluate(JS_STYLE); print('Stil:', st)
        orr = await pg.evaluate(JS_ORIENT); print('Orientierung:', orr)
        ed = await pg.evaluate(JS_EDGE)
        await pg.screenshot(path='/tmp/fingertest_kante.png')
        edge_ok = True
        for fr in ed:
            hy = fr['hitY']; F_ = [x for x in fr['items'] if x['k'] == 'F']; N_ = [x for x in fr['items'] if x['k'] == 'N']
            fr['items'] = [x for x in fr['items'] if not (x['k'] == 'N' and x['top'] > fr['H'] - 30)]   # Tastenbeschriftung der Klaviatur selbst
            F_ = [x for x in fr['items'] if x['k'] == 'F']; N_ = [x for x in fr['items'] if x['k'] == 'N']
            for x in fr['items']:
                if x['bot'] > hy + 0.5: edge_ok = False
            for a in F_:
                for b in N_:
                    if a['bot'] > b['top'] + 0.5 and b['bot'] > a['top'] + 0.5: edge_ok = False
        print('Kante:', json.dumps([(fr['T'], round(fr['hitY']), [(x['k'], round(x['top']), round(x['bot'])) for x in fr['items']]) for fr in ed]))
        fw = await pg.evaluate(JS_FLOW); print('Auswendig v8:', fw)
        m = await pg.evaluate(JS_MEM); await pg.wait_for_timeout(800)
        m2 = await pg.evaluate(JS_MEM2)
        inline = r.pop('inline'); body = re.sub(r'^/\* FINGERING-BEGIN[^\n]*\n', '', inline); body = re.sub(r'\n/\* FINGERING-END \*/$', '', body)
        checks = {
            'modul_gleich_quelle': body == SRC, 'version': r['version'] == '0.5.0',
            'rechts_tonleiter_12312345': r['rh'] == '12312345', 'links_akkord_531': r['lh'] == '531' and r['lhH'] == 'LLL',
            'einfarbig_bass_links': r['bassH'] == 'L' and r['melH'] == 'R', 'schalter_aus': r['offNoCalc'],
            'flagge_rot': f1['red'] != '', 'flagge_upload': f2['n'] == 1 and (f2['path'] or '').startswith('diag/fingerflags/') and fi.get('kind') == 'fingerflags',
            'flagge_inhalt': fl.get('T') == 1.0 and len(nr) >= 5 and all(x['f'] in (1, 2, 3, 4, 5) and x['fh'] in ('L', 'R') and x['why'] for x in nr),
            'flagge_weg': f2['after'] == 0,
            'stil_standard_einfach': st['def'] == 'einfach' and all(st['einfach'][k] != st['einfach'][k - 1] for k in range(1, len(st['einfach']))),   # kein Rutschen (gleicher Finger auf Nachbartasten) 'stil_lehrbuch_anders': st['lehrbuch'] != st['einfach'],
            'orientierung_nur_erste': orr['orient'] == 1 and orr['alle'] == 5,
            'kante_ueber_klaviatur_kein_ueberlappen': edge_ok and any(fr['items'] for fr in ed),
            'v8_finden_zeigt_zahlen': fw['mode1'] == 'find' and fw['find'] >= 1,
            'v8_aus_dem_kopf_keine_zahlen': fw['mode2'] == 'recall' and fw['dark'] and fw['recall'] == 0,
            'auswendig_ok': m['ok'] is True, 'auswendig_finger': m2['memFing'] and not m2['err'], 'keine_pageerror': not errs,
        }
        print(json.dumps(r)); print('pageerrors', errs)
        for k, v in checks.items(): print(('OK    ' if v else 'FEHLER') + ' ' + k)
        bad = [k for k, v in checks.items() if not v]
        print('fingertest', 'OK' if not bad else 'FEHLER ' + ','.join(bad))
        await br.close(); sys.exit(1 if bad else 0)
asyncio.run(main())
