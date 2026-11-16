"""v5.18: Fortschritt im ganzen Song – ein Balken oben (Übersicht groß, Spielbildschirm über die ganze Breite), Abschnitte nach Länge, dann Verbinden und ganzer Song,
aktueller markiert, Prozent + „noch …“, nach jedem Durchgang „+x %“ und der Balken wächst sichtbar.
usage: python3 tools/bench/awfortschritttest.py $PWD/web/index.html [shot-dir]"""
import sys, asyncio, json
from playwright.async_api import async_playwright
JS = r"""()=>{window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};window.toast=()=>{};KB.state='off';const o={};
 const notes=[];let t=0;for(let bar=0;bar<8;bar++){notes.push({m:48,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:60+((bar+q)%5)*2,start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 const it={id:'fort',type:'midi',title:'Fortschritt',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);window.AW_NOW=Date.UTC(2026,10,16,9);openMem(it);
 const gs=MEM.gs,v=()=>MEM.rec.v9,tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs[j].mids)memPress(m,'kb')};
 const runWait=()=>{const R=MEM.run;let g=0;while(!R.done&&g++<300&&MEM.run===R){if(R.pv){tick(0.5);continue}if(R.pos<=R.b)play(R.pos);tick(0.1)}return R};
 o.n=MEM.C.length;const p0=awProg();o.start=p0.total;o.weights=Math.abs(p0.segs.reduce((a,x)=>a+x.f,0)+p0.L.f+p0.W.f-1)<1e-9;
 o.homeBig=/0 %/.test($('#memSum .big').textContent)&&/noch 100 %/.test($('#memSum').textContent)&&/Noch: \d+ neu/.test($('#memSum').textContent);
 o.homeSegs=$('#memSum .awBar').querySelectorAll('i').length===o.n+2&&$('#memSum .awBar i.cur')!=null&&/ohne App/.test($('#memSum .awLab').textContent);
 /* Weg eines Abschnitts: jede Stufe mehr = mehr Prozent */
 const seq=[{st:0,fc:0,box:0},{st:0,fc:1,box:0},{st:1,fl:0,box:0},{st:1,fl:1,box:0},{st:1,fl:2,box:0},{st:2,box:0},{st:3,tp:0,box:0},{st:3,tp:1,box:0},{st:3,tp:2,box:0},{st:3,tp:2,box:1},{box:2},{box:3},{box:4}].map(x=>awChP(Object.assign({st:3,tp:2},x)));
 o.mono=seq.every((x,i)=>i===0||x>seq[i-1])&&seq[0]===0&&seq[seq.length-1]===1;
 /* ein fehlerfreier Durchgang: Balken wächst, „+x %“ */
 awNext();let R=MEM.run;const M0=$('#memMapR').innerHTML;o.runSegs=(M0.match(/<i /g)||[]).length===o.n+2&&(M0.match(/class="cur"/g)||[]).length===1&&/Song 0 %/.test($('#memMapR').textContent);
 R=runWait();const M1=$('#memMapR');o.gain=[R.ok,/\+\d/.test((M1.querySelector('.awGain')||{}).textContent||''),awProg().total>0];
 const b=[...M1.querySelectorAll('.awBar b')].find(b=>parseFloat(b.dataset.to)>0);o.grows=!!b&&parseFloat(b.style.width)<parseFloat(b.dataset.to);
 o.after=awProg().total;
 /* Übersicht danach: „+x %“ seit dem letzten Besuch */
 memHome();o.homeGain=/\+/.test(($('#memSum .awGain')||{}).textContent||'');
 /* alles geschafft = 100 % */
 v().ch.forEach(c=>{c.box=4;c.st=3});v().ln=v().ch.map(()=>1);v().whole.days=['a','b'];o.full=awProg().total;memHome();o.fullTxt=/100 %/.test($('#memSum .big').textContent)&&/geschafft/.test($('#memSum').textContent);
 /* ehrlich: Rückschritt senkt den Wert */
 v().ch[0].box=2;o.drop=awProg().total<1;
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        res = {}
        for name, vp in [('quer', {'width': 753, 'height': 360}), ('hoch', {'width': 360, 'height': 753})]:
            pg = await br.new_page(viewport=vp); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
            r = await pg.evaluate(JS); r['errs'] = errs
            # Spielbildschirm: Balken über die ganze Breite
            await pg.evaluate("()=>{const v=MEM.rec.v9;v.ch.forEach((c,k)=>{c.box=k<2?2:0;c.st=k<2?3:k===2?1:0;c.fl=1});v.ln=[1];v.whole.days=[];memHome();awNext()}")
            await pg.wait_for_timeout(300)
            r['wide'] = await pg.evaluate("()=>{const b=$('#memMapR .awBar').getBoundingClientRect(),c=$('#memCv').getBoundingClientRect();return Math.round(b.width)>=Math.round(c.width)-2}")
            if len(sys.argv) > 2:
                await pg.screenshot(path=f'{sys.argv[2]}/fortschritt-lauf-{name}.png')
                await pg.evaluate("()=>{const R=MEM.run;let g=0;while(!R.done&&g++<300){if(R.pv){for(let x=0;x<0.5;x+=1/60)awTick(R,1/60);continue}if(R.pos<=R.b)for(const m of MEM.gs[R.pos].mids)memPress(m,'kb');for(let x=0;x<0.1;x+=1/60)awTick(R,1/60)}}")
                await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{sys.argv[2]}/fortschritt-fertig-{name}.png')
                await pg.evaluate("memHome()"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{sys.argv[2]}/fortschritt-uebersicht-{name}.png')
            res[name] = r; await pg.close()
        await br.close()
    print(json.dumps(res, ensure_ascii=False))
    ok = True
    for name, r in res.items():
        c = {'Start 0 %, Gewichte ergeben 100 %': r['start'] == 0 and r['weights'],
             'Übersicht: große Zahl, „noch 100 %“, „Noch: x neu“': r['homeBig'],
             'Übersicht: Teilstücke = Abschnitte + Verbinden + ganzer Song, nächster markiert, Beschriftung': r['homeSegs'],
             'jede Stufe eines Abschnitts zählt mehr (0 → 100 %)': r['mono'],
             'Spielbildschirm: Balken mit allen Teilstücken, aktueller markiert, „Song 0 %“': r['runSegs'],
             'nach fehlerfreiem Durchgang „+x %“, Wert steigt': r['gain'] == [True, True, True],
             'Balken wächst sichtbar (startet beim alten Stand)': r['grows'],
             'Übersicht zeigt „+x %“ seit dem letzten Besuch': r['homeGain'],
             'alles gelernt, verbunden, 2 Tage ganzer Song = 100 %, „geschafft“': abs(r['full'] - 1) < 1e-9 and r['fullTxt'],
             'Rückschritt senkt den Wert (ehrlich)': r['drop'],
             'Balken über die ganze Breite (mind. so breit wie die Notenbahn)': r['wide'],
             'keine Fehler': not r['errs']}
        for k, x in c.items():
            print(('OK  ' if x else 'FEHLER ') + f'[{name}] ' + k); ok = ok and x
    sys.exit(0 if ok else 1)
asyncio.run(main())
