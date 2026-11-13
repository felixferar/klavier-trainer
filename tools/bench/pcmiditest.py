"""v4.76: Am PC (Chrome, Web MIDI, ohne Android-Hülle) läuft das Klavier wie am Handy: Status „Klavier verbunden“, Auswendig zählt Tasten als Klavier (nicht als Bildschirm), Loslassen kommt an."""
import sys,asyncio,json
from playwright.async_api import async_playwright
INIT=r"""(()=>{const inp={name:'GZUT-MIDI',state:'connected',onmidimessage:null};window.__inp=inp;
 const acc={inputs:new Map([['1',inp]]),outputs:new Map(),onstatechange:null};window.__acc=acc;
 navigator.requestMIDIAccess=()=>Promise.resolve(acc)})()"""
JS=r"""async()=>{const o={};window.playTone=()=>{};window.__instantEnd=true;await new Promise(r=>setTimeout(r,900));
 const send=(s,a,v)=>{if(__inp.onmidimessage)__inp.onmidimessage({data:new Uint8Array([s,a,v])})};
 o.nat=typeof KTNative!=='undefined';o.label=kbInfo().label;
 const chip=$('#memKb');
 const notes=[];let t=0;for(let i=0;i<10;i++){notes.push({m:60+(i%5)*2,start:t,dur:.4,hand:'R'});t+=.5}
 const it={id:'pc',type:'midi',title:'P',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);
 o.chipShown=chip&&chip.style.display!=='none';o.chipTxt=chip?chip.textContent.trim():'';
 MEM.rec.secs.forEach(r=>{r.watched=true;r.runs=1});memStart(0,false);const R=MEM.run;
 R.vt=MEM.gs[R.pos].start;const p0=R.pos;for(const m of MEM.gs[R.pos].mids)send(0x90,m,90);
 o.adv=R.pos>p0;o.touch=!!R.touch;o.held=[...KB.held].length;
 for(const m of MEM.gs[p0].mids)send(0x80,m,0);o.released=[...KB.held].length;
 /* Klavier weg → nicht verbunden */
 __inp.state='disconnected';if(__acc.onstatechange)__acc.onstatechange({port:__inp});o.after=kbInfo().label;
 return o}"""
async def main(url):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx=await b.new_context(viewport={'width':1280,'height':800});await ctx.add_init_script(INIT)
        pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+url);await pg.wait_for_timeout(600)
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'ohne Android-Hülle':not r['nat'],'Status verbunden':r['label']=='Klavier verbunden',
           'Chip sichtbar':r['chipShown'] and 'verbunden' in r['chipTxt'],
           'Taste zählt im Auswendig-Modus':r['adv'] and not r['touch'],
           'Loslassen kommt an':r['held']>0 and r['released']==0,
           'Klavier weg → nicht verbunden':r['after']!='Klavier verbunden','keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await b.close()
asyncio.run(main(sys.argv[1]))
