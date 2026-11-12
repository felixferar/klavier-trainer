"""v4.70 Akkord-Erkennung (chordAlign) für Video-Songs: golden hour E4 bei 1,118 s gehört zum Akkord bei 1,000 s; schnelle Wechselnoten (0,12 s, ohne Überlappung) und Melodie über gehaltenem Bass bleiben; Nicht-Video-Songs unverändert"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""()=>{const o={};const mk=(ns,video)=>{const it={id:'a'+Math.random(),type:'midi',title:'A',artist:'x',data:b64FromBuf(writeMidi(ns))};if(video)it.video={v:2};return songForItem(it)};
 const gh=[{m:54,start:1,dur:.365,hand:'L'},{m:57,start:1,dur:.258,hand:'L'},{m:61,start:1,dur:.324,hand:'R'},{m:64,start:1.118,dur:.227,hand:'R'},
   {m:57,start:17.49,dur:3.2,hand:'L'},{m:68,start:17.49,dur:.165,hand:'R'},{m:66,start:17.655,dur:.084,hand:'R'},{m:68,start:17.781,dur:.165,hand:'R'},
   {m:30,start:30,dur:2,hand:'L'},{m:65,start:30.12,dur:1.85,hand:'R'}];
 const s=mk(gh,true);const e=s.notes.find(n=>n.midi===64);o.eStart=+e.start.toFixed(3);o.eEnd=+(e.start+e.dur).toFixed(3);o.fix=s.chordFix;
 o.fast=s.notes.filter(n=>n.midi===66||n.midi===68).map(n=>+n.start.toFixed(3));o.mel=+s.notes.find(n=>n.midi===65).start.toFixed(3);
 const s2=mk(gh,false);o.noVideo=+s2.notes.find(n=>n.midi===64).start.toFixed(3);
 LIB=[];const it={id:'gh',type:'midi',title:'G',artist:'x',data:b64FromBuf(writeMidi(gh)),video:{v:2}};LIB=[it];openMem(it);o.firstGroup=[...MEM.gs[0].mids].sort((a,b)=>a-b);return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3000)
        r=await pg.evaluate(JS);print(json.dumps(r),errs)
        ok=(abs(r['eStart']-1)<0.002 and abs(r['eEnd']-1.345)<0.003 and r['fix']==1 and r['fast']==[17.49,17.655,17.781] and abs(r['mel']-30.12)<0.002
            and abs(r['noVideo']-1.118)<0.002 and r['firstGroup']==[54,57,61,64] and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
