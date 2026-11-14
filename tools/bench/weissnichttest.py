"""v4.98: Nie raten müssen – 3 falsche Töne am selben Anschlag → App zeigt + spielt ihn (Hilfe); 6 Fehler im Versuch → vorspielen + neu (zählt als nicht geschafft);
„Weiß nicht weiter“ per Knopf und per zweittiefster Taste (B ganz links) → Anschlag zeigen (Hilfe); keine Fortschrittsanzeige im Dunkeln."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};let tones=[];window.playTone=(m)=>tones.push(m);KB.state='off';
 const SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,72];const notes=[];let t=0;for(let r=0;r<2;r++)for(let bar=0;bar<4;bar++){notes.push({m:47+bar,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:SA[bar*4+q]+r,start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 const it={id:'wn',type:'midi',title:'WN',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);memHome();const gs=MEM.gs;MEM.rec.v8.ch[0].st=1;memHome();
 $('#memGo').click();let R=MEM.run;R.anchorUntil=0;flowTick(R,5);flowDraw();o.prog=$('#memProg').textContent;o.btn=!!$('#v8Help');
 /* 3 falsche Töne am selben Anschlag */
 tones=[];memPress(30,'kb');memPress(31,'kb');o.after2=R.hints;memPress(32,'kb');o.after3=R.hints;o.show3=R.showUntil>performance.now()&&[...gs[R.pos].mids].every(m=>tones.includes(m));flowDraw();o.msg3=$('#memMsg').textContent;
 /* Knopf „Weiß nicht weiter“ */
 for(const m of gs[R.pos].mids)memPress(m,'kb');R.showUntil=0;const h0=R.hints;$('#v8Help').click();o.btnHelp=R.hints===h0+1&&R.showUntil>performance.now();
 /* zweittiefste Taste */
 R.showUntil=0;const h1=R.hints;memPress(22,'kb');o.keyHelp=R.hints===h1+1&&R.showUntil>performance.now()&&MEM.run===R;
 /* 6 Fehler insgesamt → vorspielen + neu */
 const f0=MEM.rec.v8.ch[0].fails;R.wrongF=5;memPress(33,'kb');const R2=MEM.run;o.abort=R2!==R&&R2.mode==='recall'&&R2.previewUntil>performance.now()&&MEM.rec.v8.ch[0].fails===f0+1;
 /* in der kalten Wiederholung zählt der Abbruch als nicht geschafft */
 memStop();const c=MEM.rec.v8.ch[0];c.box=3;c.due=Date.now()-1;c.relearn=0;memHome();$('#memGo').click();R=MEM.run;o.rev=R.mode;R.anchorUntil=0;R.wrongF=5;memPress(33,'kb');o.revAbort=c.box===2&&c.relearn===1&&MEM.run.mode==='recall';
 /* Finden (Bildschirm an): kein Knopf, keine Sonderregeln */
 memStop();MEM.rec.v8.ch[1].st=0;c.due=Date.now()+36e5;memHome();const p=v8Pick();o.findMode=p.mode;$('#memGo').click();o.findBtn=!!$('#v8Help');
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'keine Fortschrittsanzeige im Dunkeln':r['prog']=='','Knopf „Weiß nicht weiter“ da':r['btn'],
           '3 falsche Töne am selben Anschlag → zeigen + anspielen':r['after2']==0 and r['after3']==1 and r['show3'] and 'zählt als Hilfe' in r['msg3'],
           'Knopf zeigt Anschlag (Hilfe)':r['btnHelp'],'B ganz links zeigt Anschlag (Hilfe)':r['keyHelp'],
           '6 Fehler → vorspielen + neu, zählt nicht':r['abort'],'kalt: Abbruch = Kasten zurück + auffrischen':r['rev']=='review' and r['revAbort'],
           'beim Finden kein Knopf':r['findMode']=='find' and not r['findBtn'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
