"""v5.02: Oktave von Hand (Song-Seite) und Tastatur-Verschiebung.
- Knopf „Oktave +/−“ verschiebt den Song (gespeichert, gilt in Spielen/Auswendig), nicht über die Klaviatur hinaus
- Üben: dreimal eine Oktave daneben → das Klavier wird NICHT mehr für alle Songs verschoben; geschätzte Oktave → nur dieser Song wandert
- alte automatische Oktav-Verschiebung (kt_kbshift = ±12) wird einmalig zurückgesetzt, Halbton-Transponierung bleibt"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};window.playTone=()=>{};
 const notes=[];for(let i=0;i<8;i++)notes.push({m:60+i%5,start:i*0.5,dur:0.4,hand:'R'});
 const it={id:'ok1',type:'midi',title:'Okt',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);
 openSongPage(it);o.sichtbar=getComputedStyle($('#spOct')).display!=='none';
 $('#spOctM').click();o.minus=fresh(it).octShift===-12&&$('#spOctV').textContent==='-1'&&(load('kt_lib')[0].octShift===-12);
 o.song=Math.min(...songForItem(fresh(it)).notes.map(n=>n.midi))===48;
 memLoad(fresh(it));o.memMin=MEM.song?Math.min(...MEM.song.notes.map(n=>n.midi)):null;o.mem=o.memMin===48;
 for(let i=0;i<5;i++)$('#spOctP').click();o.grenze=fresh(it).octShift===36; /* 60+5·12=120 > 108 → stoppt bei +3 Oktaven (Höchstton 64+36=100) */
 /* Üben: Song mit geschätzter Oktave, du spielst eine Oktave tiefer */
 const it2={id:'ok2',type:'midi',title:'Vid',artist:'x',data:b64FromBuf(writeMidi(notes)),video:{v:2,src:'yt',keys:[48,84]},octUnsure:true};LIB.push(it2);save('kt_lib',LIB);
 KB.shift=0;openItemPlay(it2);await new Promise(r=>setTimeout(r,300));S.wait=true;
 const press=()=>{const g=groups[gi];t=g.start;kbNoteOn(g.notes[0].midi-12)};press();press();press();
 o.kbBleibt=KB.shift===0&&(load('kt_kbshift')||0)===0;o.songWandert=fresh(it2).octShift===-12;
 return o}"""
async def run(path,pre):
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+path);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        for k,v in pre.items():await pg.evaluate(f"localStorage.setItem('{k}','{v}')")
        await pg.reload();await pg.wait_for_timeout(3000);r=await pg.evaluate(JS) if not pre else await pg.evaluate("({shift:KB.shift,saved:load('kt_kbshift')})")
        await br.close();return r,errs
async def main():
    r,e=await run(sys.argv[1],{});r['keine Fehler']=not e;print(json.dumps(r,ensure_ascii=False),e)
    a,e2=await run(sys.argv[1],{'kt_kbshift':'12'});b,e3=await run(sys.argv[1],{'kt_kbshift':'2'})
    r['alteOktavVerschiebungWeg']=a['shift']==0 and a['saved']==0;r['halbtonBleibt']=b['shift']==2;print(a,b)
    print('OK' if all(r.values()) and not(e2 or e3) else 'FEHLER')
asyncio.run(main())
