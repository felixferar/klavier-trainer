"""v5.32: Gleicher Akkord mehrmals hintereinander (z. B. linke Hand alle 0,23 s): die Töne eines Anschlags zählen für diesen Griff – nicht schon für den nächsten, gleichen.
Vorher sprang die App nach 3 von 4 Tönen weiter und schrieb den 4. dem nächsten Akkord zu (falsche Rhythmus-Hänger, übersprungene Griffe).
usage: python3 tools/bench/akkordwdhtest.py $PWD/web/index.html"""
import sys, asyncio, json
from playwright.async_api import async_playwright
JS = r"""()=>{window.toast=()=>{};window.playTone=()=>{};window.AW_NOLOOP=true;KB.state='off';const o={};
 const notes=[];let t=0;for(let i=0;i<24;i++){for(const m of [48,52,55,60])notes.push({m,start:t,dur:0.2,hand:m<57?'L':'R'});if(i%4===0)notes.push({m:72+(i%5),start:t,dur:0.2,hand:'R'});t+=i%4===3?0.6:0.23}
 const it={id:'akw',type:'midi',title:'Akkorde',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);const gs=MEM.gs,tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}};
 /* aus dem Kopf: jeder Anschlag einmal gedrückt → genau ein Griff weiter */
 awStart({k:0,mode:'head'});let R=MEM.run;const steps=[];for(let j=R.a;j<=Math.min(R.b,R.a+5);j++){const p0=R.pos;for(const m of gs[j].mids)memPress(m,'kb');tick(0.1);steps.push(R.pos-p0)}o.steps=steps;memStop();
 /* ganzer Song im Takt: keine Rhythmus-Hänger */
 awStart({k:0,mode:'whole'});R=MEM.run;let g=0;while(!R.done&&g++<5000){if(R.pos<=R.b){const j=R.pos;for(const m of gs[j].mids)memPress(m,'kb');tick(j<R.b?Math.max(0.02,gs[j+1].start-gs[j].start):0.1)}else tick(0.1)}
 o.whole=[R.ok,R.slips,R.miss,R.wrong];return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2000); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS); await br.close()
    print(json.dumps(r), errs)
    c = {'aus dem Kopf: ein Akkord gedrückt = genau ein Griff weiter (auch bei gleichem nächsten Akkord)': all(x == 1 for x in r['steps']),
         'ganzer Song im Takt: 0 Rhythmus-Hänger, geschafft': r['whole'] == [True, 0, 0, 0],
         'keine Fehler': not errs}
    for k, x in c.items(): print(('OK  ' if x else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
