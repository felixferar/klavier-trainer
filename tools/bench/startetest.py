"""v4.85: (1) Jeder Abschnitt, der noch nicht sitzt, beginnt bei Schritt 1 – auch Zwillinge (kein Sprung zu „Aus dem Kopf“) und übernommene Abschnitte.
Was schon sitzt (⭐), bleibt. (2) „Nur rechte/linke Hand üben“ gibt es nicht mehr – auch nicht nach 2× „Nicht geschafft“; die Automatik läuft weiter."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};window.__instantEnd=true;KB.state='off';
 const LH=[47,43,50,45],SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0],SB=[66,69,71,74,76,74,71,69,71,69,66,64,66,69,71,0];
 const notes=[];let t=0;const ph=P=>{for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=P[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:q===2&&bar===3?0.95:0.45,hand:'R'})}t+=2}};
 for(const p of ['A','B','A','B'])ph(p==='A'?SA:SB);
 const it={id:'st',type:'midi',title:'Start',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 /* Stand von v4.84: Teil 1 sitzt, Teil 2 in Verblassen, Teil 3 bei Aus dem Kopf (Zwilling) */
 openMem(it);const sig=MEMS['st'].sig;MEMS['st']={sig,v6:1,k84:1,secs:MEM.secs.map((_,i)=>i===0?{lvl:3,box:1,due:Date.now()+9e8,runs:6,passed:1,watched:true,chained:true}:i===1?{lvl:2,fe:2,box:0,due:0,runs:3,passed:0,watched:true}:{lvl:3,box:0,due:0,runs:1,passed:0,watched:true,tw:1})};memSaveAll();
 openMem(it);const rs=MEM.rec.secs;o.n=rs.length;o.twin=MEM.twin.slice();o.after=rs.map(r=>r.passed>0?'P':r.lvl);
 /* Zwilling: Original sitzt → Zwilling trotzdem Schritt 1 */
 const ti=MEM.twin.findIndex(x=>x>=0);o.ti=ti;rs.forEach((r,i)=>{if(i<ti){r.passed=1;r.box=1;r.due=Date.now()+9e8;r.chained=true}});const nx=memPickNext(Date.now());o.twPick=nx&&nx.i===ti;o.twLvl=rs[ti].lvl;memHome();o.here=$('#memHere').textContent;
 /* Hände einzeln gibt es nicht mehr */
 o.hasBtn=!!$('#memHandR')||!!$('#memHandL');KB.state='on';const r0=rs[ti];r0.lvl=2;r0.fe=1;r0.watched=true;r0.runs=1;r0.passed=0;r0.box=0;
 const play=()=>{const R=MEM.run;let k=0;while(!R.done&&k++<400){R.vt=Math.max(R.vt??0,MEM.gs[R.pos].start);for(let x=0;x<4;x++)memPress(30+x,'kb');for(const m of MEM.gs[R.pos].mids)memPress(m,'kb')}};
 memStart(ti,false);play();memStart(ti,false);play();o.cat=MEM.run.ev.cat;o.nf=r0.nf;o.tip=$('#memMsg').textContent.includes('einer Hand');o.auto=!!MEM.autoT;
 memStop();KB.state='off';return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'4 Teile, Zwillinge erkannt':r['n']==4 and sum(1 for x in r['twin'] if x>=0)==2,
           'was sitzt, bleibt; der Rest beginnt bei Schritt 1':r['after']==['P',1,1,1],
           'Zwilling beginnt bei Schritt 1':r['twPick'] and r['twLvl']==1 and 'Kennst du schon' not in r['here'] and 'Schritt 1' in r['here'],
           'kein „Nur rechte/linke Hand“':not r['hasBtn'] and not r['tip'],'nach 2× Nicht geschafft läuft die Automatik weiter':r['cat']=='n' and r['auto'],
           'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
