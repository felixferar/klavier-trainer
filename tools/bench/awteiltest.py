"""v5.04: Note korrigiert → nur der betroffene Abschnitt beginnt neu, der Rest behält seinen Stand (auch Verbindungen).
Dazu: Übernahme aus dem alten v8-Lernstand (aus dem Kopf gekonnt → jetzt im Puls weiter), Zurücksetzen per Knopf (zweimal tippen).
usage: python3 tools/bench/awteiltest.py $PWD/web/index.html"""
import sys, asyncio, json
from playwright.async_api import async_playwright
JS = r"""()=>{window.AW_NOLOOP=true;window.playTone=()=>{};const o={};
 const mk=(chg)=>{const notes=[];let t=0;for(let bar=0;bar<12;bar++){notes.push({m:48+(bar%3)*2,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++){let m=64+((bar*3+q)%7)*2;if(chg&&bar===chg&&q===2)m+=1;notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2}return notes};
 const it={id:'teil',type:'midi',title:'Teil',artist:'x',data:b64FromBuf(writeMidi(mk(0)))};LIB=[it];save('kt_lib',LIB);openMem(it);
 const C0=MEM.C.map(c=>[c.t0,c.t1]),n=MEM.C.length;o.n=n;const v=MEM.rec.v9;v.ch.forEach((c,k)=>{c.st=2;c.tp=2;c.box=3;c.due=Date.now()+864e5});v.ln=v.ch.map(()=>1);v.ln.length=n-1;memSaveAll();
 /* Note in Takt 6 korrigieren (wie im Editor gespeichert) */
 it.data=b64FromBuf(writeMidi(mk(6)));save('kt_lib',LIB);openMem(it);const w=MEM.rec.v9;
 o.reset=w.ch.map(c=>c.box===0&&c.st===0?1:0);o.nReset=o.reset.reduce((a,b)=>a+b,0);o.kept=w.ch.filter(c=>c.box===3).length;
 o.where=w.ch.map((c,k)=>c.box===0?[+MEM.C[k].t0.toFixed(1),+MEM.C[k].t1.toFixed(1)]:null).filter(Boolean);
 o.lnKept=w.ln.filter(Boolean).length;o.lnOk=w.ln.every((x,k)=>!x||(w.ch[k].box===3&&w.ch[k+1].box===3));
 /* alter v8-Stand */
 const it2={id:'alt8',type:'midi',title:'Alt',artist:'x',data:b64FromBuf(writeMidi(mk(0)))};LIB.push(it2);save('kt_lib',LIB);openMem(it2);const n2=MEM.C.length;
 delete MEMS.alt8.v9;MEMS.alt8.v8={cv:2,n:n2,ch:MEM.C.map((c,k)=>({box:k===0?2:0,st:k<=1?1:0}))};memSaveAll();openMem(it2);const x=MEMS.alt8.v9;
 o.mig=[x.ch[0].st,x.ch[0].tp,x.ch[0].box,x.ch[1].st,x.ch[2].st];o.v8gone=!MEMS.alt8.v8;
 /* Zurücksetzen */
 memHome();const b=$('#memReset');b.click();const after1=MEMS.alt8.v9.ch[0].st;$('#memReset').click();o.resetBtn=[after1,MEMS.alt8.v9.ch[0].st];
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS); await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    c = {'Note geändert → 1–2 Abschnitte neu, Rest bleibt': 1 <= r['nReset'] <= 2 and r['kept'] == r['n'] - r['nReset'],
         'betroffener Abschnitt liegt um Takt 6 (12–14 s)': all(a <= 13.5 and b >= 12 for a, b in r['where']),
         'Verbindungen bleiben, wo beide Nachbarn unverändert sind': r['lnOk'] and r['lnKept'] >= r['n'] - 1 - 2 * r['nReset'],
         'alter v8-Stand: aus dem Kopf gekonnt → im Puls (75 %), gefunden → aus dem Kopf': r['mig'] == [2, 0, 0, 1, 0] and r['v8gone'],
         'Zurücksetzen erst nach zweitem Tippen': r['resetBtn'] == [2, 0],
         'keine Fehler': not errs}
    print(c); print('OK' if all(c.values()) else 'FEHLER')
asyncio.run(main())
