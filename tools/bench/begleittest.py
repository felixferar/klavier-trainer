"""v4.88: leise Begleitung in „Nebel im Fluss“.
Prüft: in sichtbaren Takten spielt die App die Noten mit 35 % Lautstärke; im Nebel still; abgestimmt auf die gemessene Verspätung
(App-Ton kommt um lat später – fällt mit dem eigenen Anschlag zusammen, kein Echo); verpasste Töne in sichtbaren Takten nicht doppelt; Schalter an/aus."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const o={};let calls=[];window.playTone=(m,d,v,g)=>calls.push({m,g,vt:MEM.run?MEM.run.vt:null});KB.state='off';
 const LH=[47,43,50,45],SA=[74,71,69,71,74,76,74,71,69,66,69,71,74,71,69,0],SB=[66,69,71,74,76,74,71,69,71,69,66,64,66,69,71,0];
 const notes=[];let t=0;const ph=P=>{for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=P[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:q===2&&bar===3?0.95:0.45,hand:'R'})}t+=2}};
 for(const p of ['A','B','A','B'])ph(p==='A'?SA:SB);
 const it={id:'bg',type:'midi',title:'Begl',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];openMem(it);flowPrep();const gs=MEM.gs,fl=MEM.rec.fl,W0=MEM.wins[0];
 const sweep=()=>{const R=MEM.run;let k=0;while(!R.done&&k++<5000)flowTick(R,0.02);return R};
 /* Aufwärmen, keine Taste: alle Takte sichtbar → Begleitung spielt jede Note genau einmal, leise */
 fl.lat=0;flowStart(0);calls=[];let R=sweep();const nWin=R.accNs.length;const acc=calls.filter(c=>c.g!=null&&c.g!==undefined);
 o.nWin=nWin;o.acc=acc.length;o.gains=[...new Set(acc.map(c=>+c.g.toFixed(3)))];o.other=calls.filter(c=>c.g==null&&c.m<90).length;o.btn=$('#memTempoR').textContent;
 /* Verspätung 0,1 s: der App-Ton kommt um 0,1 s × Tempo später als die Note */
 fl.lat=0.1;flowStart(0);calls=[];R=MEM.run;const n0=R.accNs.find(n=>n.start>=gs[R.a].start+0.01);sweep();const c0=calls.find(c=>c.g!=null&&c.m===n0.midi&&c.vt>=n0.start);o.delay=c0?+(c0.vt-n0.start).toFixed(3):null;o.expDelay=+(0.1*R.speed).toFixed(3);
 /* Nebel auf Takt 1+2: dort still */
 fl.lat=0;fl.fog[W0.b0]=1;fl.fog[W0.b0+1]=1;flowStart(0);calls=[];R=MEM.run;const inFog=new Set(R.accNs.filter((n,q)=>R.nbar[q]===W0.b0||R.nbar[q]===W0.b0+1));sweep();
 o.fogAcc=calls.filter(c=>c.g!=null&&[...inFog].some(n=>n.midi===c.m&&Math.abs(c.vt-n.start)<0.05)).length;o.visAcc=calls.filter(c=>c.g!=null).length;
 /* Schalter aus */
 memHome();const b=$('#memTempo').querySelector('[data-a]');b.click();o.accOff=fl.acc===false;flowStart(0);calls=[];sweep();o.offAcc=calls.filter(c=>c.g!=null).length;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'sichtbar: jede Note einmal mitgespielt':r['acc']==r['nWin'] and r['nWin']>0,'35 % Lautstärke':r['gains']==[round(0.35*0.75*0.8,3)],
           'verpasste Töne nicht doppelt':r['other']==0,'Schalter sichtbar':'an' in r['btn'],
           'auf Verspätung abgestimmt':r['delay'] is not None and abs(r['delay']-r['expDelay'])<=0.025,
           'im Nebel still':r['fogAcc']==0 and r['visAcc']>0,'Schalter aus = still':r['accOff'] and r['offAcc']==0,'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
