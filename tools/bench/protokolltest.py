"""v5.00: Lernprotokoll – jeder Versuch im neuen Ablauf landet in kt_v8log (bis 300, unabhängig vom alten 40er-Protokoll) und wird gebündelt in den
Diagnose-Speicher geschickt (diag/learn/…json, höchstens alle 2 min, nur Neues, Fehlschlag → beim nächsten Mal nochmal); ohne Schlüssel nichts."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};KB.state='off';const up=[];let okUp=true;
 save('kt_ghtok','x');window.ghUpload=async(path,b64,msg)=>{up.push({path,body:JSON.parse(decodeURIComponent(escape(atob(b64)))),msg});return {ok:okUp}};
 const SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,72];const notes=[];let t=0;for(let r=0;r<2;r++)for(let bar=0;bar<4;bar++){notes.push({m:47+bar,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:SA[bar*4+q]+r,start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 const it={id:'pr',type:'midi',title:'Proto',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);memHome();const gs=MEM.gs;await new Promise(r=>setTimeout(r,50));o.up0=up.length;
 window.AW_NOLOOP=true;const play=()=>{const R=MEM.run;let g=0;while(!R.done&&g++<300){if(R.pos<=R.b)for(const m of gs[R.pos].mids)memPress(m,'kb');awTick(R,1)}};
 $('#memGo').click();play();memStop();memHome();await new Promise(r=>setTimeout(r,50));
 o.up1=up.length;const u=up[0]||{};o.path=u.path||'';o.ent=(u.body&&u.body.entries||[]).map(e=>[e.mode,e.ok,e.song]);o.snap=!!(u.body&&u.body.snap&&u.body.snap.chunks&&u.body.snap.state);o.ver=u.body&&u.body.v;
 /* gleich nochmal: nichts Neues → kein Upload */
 memHome();await new Promise(r=>setTimeout(r,50));o.up2=up.length;
 /* neuer Versuch innerhalb von 2 min → wartet */
 $('#memGo').click();play();memStop();memHome();await new Promise(r=>setTimeout(r,50));o.up3=up.length;
 /* nach 2 min → nur der neue Versuch */
 save('kt_v8logat',Date.now()-130e3);okUp=false;memHome();await new Promise(r=>setTimeout(r,50));o.up4=up.length;o.ent4=up[up.length-1].body.entries.map(e=>e.mode);
 /* Fehlschlag → derselbe Versuch geht beim nächsten Mal mit */
 okUp=true;save('kt_v8logat',Date.now()-130e3);memHome();await new Promise(r=>setTimeout(r,50));o.up5=up.length;o.ent5=up[up.length-1].body.entries.map(e=>e.mode);
 /* alter Modus kürzt sein Protokoll, unseres bleibt */
 localStorage.setItem('kt_memeval',JSON.stringify(Array(45).fill({t:1})));o.logN=(load('kt_v8log')||[]).length;
 /* ohne Schlüssel nichts */
 save('kt_ghtok','');save('kt_v8logat',0);const L=load('kt_v8log');L.push(Object.assign({},L[0],{t:Date.now()+5}));save('kt_v8log',L);const n6=up.length;memHome();await new Promise(r=>setTimeout(r,50));o.noTok=up.length===n6;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'ohne Versuch kein Upload':r['up0']==0,
           'nach dem Versuch: Upload nach diag/learn mit Versuch, Abschnitten, Stand, Version':r['up1']==1 and r['path'].startswith('diag/learn/') and r['ent']==[['find',1,'pr']] and r['snap'] and bool(__import__('re').match(r'^\d+\.\d+$',r['ver'] or '')),
           'nichts Neues → kein Upload':r['up2']==1,'innerhalb von 2 min → wartet':r['up3']==1,
           'danach nur der neue Versuch':r['up4']==2 and r['ent4'] in (['find'],['fade']),
           'Fehlschlag → geht beim nächsten Mal mit':r['up5']==3 and r['ent5'] in (['find'],['fade']),
           'eigenes Protokoll, unabhängig vom alten':r['logN']>=2,'ohne Schlüssel nichts':r['noTok'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
