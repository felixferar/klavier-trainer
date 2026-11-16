"""v5.26 (Auswendig v6): Note korrigiert → nur der betroffene Formteil beginnt neu, der Rest behält seinen Stand; Schneebälle bleiben, wenn alle ihre Teile
unverändert sind; der ganze Song beginnt neu. Dazu: Übernahme aus dem v9-Stand (kleinster Stand der alten Abschnitte im Teil), Zurücksetzen per Knopf (zweimal tippen).
usage: python3 tools/bench/awteiltest.py $PWD/web/index.html"""
import sys, asyncio, json
from playwright.async_api import async_playwright
JS = r"""()=>{window.AW_NOLOOP=true;window.playTone=()=>{};window.toast=()=>{};const o={};
 const mk=(chg)=>{const notes=[];let t=0;for(let bar=0;bar<16;bar++){notes.push({m:48+(bar%3)*2,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++){let m=64+((bar*3+q)%7)*2;if(chg&&bar===chg&&q===2)m+=1;notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2;if(bar%4===3)t+=0.8}return notes};
 const it={id:'teil',type:'midi',title:'Teil',artist:'x',data:b64FromBuf(writeMidi(mk(0)))};LIB=[it];save('kt_lib',LIB);openMem(it);
 const n=MEM.C.length;o.n=n;let v=MEM.rec.v10;v.ch.forEach(c=>{c.st=3;c.box=2;c.due=Date.now()+864e5});for(let k=1;k<n;k++)v.sn[k]=1;v.whole={days:['2026-11-1'],due:0,n:1};memSaveAll();
 /* Note in Takt 9 korrigieren (wie im Editor gespeichert) */
 it.data=b64FromBuf(writeMidi(mk(9)));save('kt_lib',LIB);openMem(it);const w=MEM.rec.v10;
 o.nReset=w.ch.filter(c=>c.st===0&&c.box===0).length;o.kept=w.ch.filter(c=>c.st===3&&c.box===2).length;
 o.where=w.ch.map((c,k)=>c.st===0?[+MEM.C[k].t0.toFixed(1),+MEM.C[k].t1.toFixed(1)]:null).filter(Boolean);
 o.snOk=[...Array(n).keys()].slice(1).every(k=>{const sp=awSnowSpan(k);let all=true;for(let i=sp.s;i<=sp.e;i++)if(w.ch[i].st!==3)all=false;return !!w.sn[k]===all});o.snKept=w.sn.filter(Boolean).length;
 o.whole=w.whole.days.length;
 /* v9: Teil = kleinster Stand seiner alten Abschnitte */
 const it2={id:'alt9',type:'midi',title:'Alt',artist:'x',data:b64FromBuf(writeMidi(mk(0)))};LIB.push(it2);save('kt_lib',LIB);openMem(it2);const oc=awChunks(MEM.gs),P0=MEM.C[0],P1=MEM.C[1];
 delete MEMS.alt9.v10;MEMS.alt9.v9={cv:10,n:oc.length,ch:oc.map(c=>({sig:'x',st:c.a>=P1.a&&c.a<=P1.b?(c.a===P1.a?2:3):0,box:c.a>=P0.a&&c.a<=P0.b?2:0,due:0})),ln:[],lw:[],lat:0.05,whole:{days:[],due:0,n:0}};memSaveAll();openMem(it2);
 const x=MEMS.alt9.v10;o.mig=[x.ch[0].st,x.ch[0].box,x.ch[1].st,x.ch[2].st,x.lat];
 /* Zurücksetzen */
 memHome();const b=$('#memReset');b.click();const after1=MEMS.alt9.v10.ch[0].st;$('#memReset').click();o.resetBtn=[after1,MEMS.alt9.v10.ch[0].st];
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS); await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    c = {'Note geändert → genau 1 Teil neu, Rest bleibt': r['nReset'] == 1 and r['kept'] == r['n'] - 1,
         'betroffener Teil enthält Takt 9 (≈ 19,6–21,6 s)': all(a <= 20.5 and b >= 20 for a, b in r['where']),
         'Schneebälle bleiben nur, wo alle Teile unverändert sind; ganzer Song neu': r['snOk'] and r['snKept'] >= 1 and r['whole'] == 0,
         'v9-Stand: gelernt → sitzt (Wiederholung), aus dem Kopf/ausblenden → kleinster Stand': r['mig'] == [3, 1, 1, 0, 0.05],
         'Zurücksetzen erst nach zweitem Tippen': r['resetBtn'][0] != 0 and r['resetBtn'][1] == 0,
         'keine Fehler': not errs}
    print(c); print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
