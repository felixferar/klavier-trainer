"""v4.73: Auswendig-Übersicht zeigt klar „wo bin ich“ – Abschnitt x von n, Stufe y von 4, was noch fehlt; ein Knopf mit Ziel; Abschnitts-Liste nur Anzeige (nicht antippbar); Lektion ohne Fachtext."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};window.__instantEnd=true;
 const notes=[];let t=0;for(let i=0;i<36;i++){notes.push({m:60+(i%5)*2,start:t,dur:.4,hand:'R'});t+=(i%12===11)?2.0:.5}
 const it={id:'hr',type:'midi',title:'H',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);
 o.n=MEM.secs.length;
 o.here0=($('#memHere')||{textContent:''}).textContent;o.go0=$('#memGo').textContent;
 /* Abschnitt 1 auf Stufe 2, Sicherheit 70 */
 const r=MEM.rec.secs[0];r.watched=true;r.runs=3;r.lvl=2;r.sk=70;memHome();
 o.here1=($('#memHere')||{textContent:''}).textContent;o.go1=$('#memGo').textContent;
 /* Liste: Antippen startet nichts */
 const li=document.querySelector('#memList [data-i]');if(li)li.click();o.tapRun=!!MEM.run;
 o.marks=$$('#memList .mk').length;
 /* Lektion: Ziel-Zeile ohne Fachtext */
 memStart(0,false);o.goal=$('#memGoal').textContent;memStop&&memStop();
 /* fälliger Abschnitt */
 r.passed=1;r.box=1;r.due=Date.now()-1000;memHome();o.go2=$('#memGo').textContent;o.here2=($('#memHere')||{textContent:''}).textContent;
 return o}"""
async def main(url):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':400,'height':780});errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+url);await pg.wait_for_timeout(800)
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        n=r['n']
        c={'mehrere Abschnitte':n>=2,
           'Wo bin ich (neu)':f'Abschnitt 1 von {n}' in r['here0'] and 'anhören' in r['here0'].lower(),
           'Knopf mit Ziel (neu)':r['go0'].startswith('Weiter: Abschnitt 1'),
           'Wo bin ich (Stufe 2)':f'Abschnitt 1 von {n}' in r['here1'] and 'Stufe 2 von 4' in r['here1'] and 'Noch ca.' in r['here1'] and 'bis Stufe 3' in r['here1'],
           'Knopf mit Ziel (Stufe 2)':r['go1']=='Weiter: Abschnitt 1 · Stufe 2',
           'Liste nicht antippbar':not r['tapRun'],
           'Liste als Weg':r['marks']==n,
           'Lektion ohne Fachtext':'Noch ca.' in r['goal'] and 'Ab 85' not in r['goal'] and '„Sauber“' not in r['goal'],
           'fällig':r['go2'].startswith('Wiederholen: Abschnitt 1') and 'Wiederholung' in r['here2'],
           'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await b.close()
asyncio.run(main(sys.argv[1]))
