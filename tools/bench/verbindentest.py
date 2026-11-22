"""v5.42: „Verbinden“ in der Vergleichsansicht – Gegenstück zu „Teilen“: eine Note, die als zwei gelesen wurde (z. B. Runaway/KISHAKEYS:
Namenskästchen schneiden jede Note in Kopf + Rest), wird wieder eine. Verbindet mit der nächsten Note derselben Taste danach (sonst davor), Lücke ≤ 0,5 s."""
import sys,os,json,asyncio
from playwright.async_api import async_playwright
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures')
meta=json.load(open(os.path.join(H,'embers_v434_meta.json')));keys=meta['keys'];rows=meta['scanRows'];lo=keys[0]['m']
geo={'x':[keys[0]['x'],keys[-1]['x']],'kw':meta['kw'],'yT':rows['yT'],'yA':rows['yA'],'yB':rows['yB'],'yC':rows['yC'],'sh':0,'kx':[round(k['x'],4) for k in keys],'ar':meta.get('ar',1280/544)}
JS="""async([geo,lo])=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));
 const mk=(id)=>({id,type:'midi',title:'Test',artist:'x',data:b64FromBuf(writeMidi([{m:60,start:1,dur:0.25,hand:'R'},{m:60,start:1.27,dur:1.0,hand:'R'},{m:64,start:5,dur:0.5,hand:'R'},{m:64,start:6.2,dur:0.5,hand:'R'}])),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:2,first:3,fps:25,keys:[lo,lo+geo.kx.length-1],geo}});
 const a=mk('a');LIB=[a];window.openYT=(it,auto,cmp)=>{cmpMode(!!CMP);show('yt')};
 let vt=0;ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(t){vt=t},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2,destroy(){}};
 openCompare(a);vt=3.1;await wait(300);cmpDraw();
 const N=m=>CMP.notes.filter(n=>n.midi===m).sort((x,y)=>x.start-y.start);
 o.btn=!!$('#ceJoin')&&$('#ceJoin').textContent==='Verbinden';
 const c0=CMP.notes.length;
 /* Kopf gewählt: mit dem Rest danach verbinden */
 CMP.sel=N(60)[0];ceUI();$('#ceJoin').click();let n60=N(60);o.headJoin=n60.length===1&&Math.abs(n60[0].start-1)<0.002&&Math.abs(n60[0].start+n60[0].dur-2.27)<0.002;o.count1=CMP.notes.length===c0-1;o.selKept=CMP.sel===n60[0];o.dirty=!!CMP.dirty;
 $('#ceUndo').click();o.undo=N(60).length===2;
 /* Rest gewählt: mit dem Kopf davor verbinden */
 CMP.sel=N(60)[1];ceUI();$('#ceJoin').click();n60=N(60);o.tailJoin=n60.length===1&&Math.abs(n60[0].start-1)<0.002&&Math.abs(n60[0].dur-1.27)<0.002;$('#ceUndo').click();
 /* Lücke 0,7 s: nicht verbinden */
 CMP.sel=N(64)[0];ceUI();const c1=CMP.notes.length;$('#ceJoin').click();o.farNo=CMP.notes.length===c1&&N(64).length===2;
 /* nichts gewählt */
 CMP.sel=null;o.noSel=ceJoin()===false;
 /* sichtbar im Querformat: Knopf passt in die Leiste */
 const r=$('#ceJoin').getBoundingClientRect(),bar=$('#cmpEdit').getBoundingClientRect();o.fits=r.right<=bar.right+1&&r.width>20;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(600);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS,[geo,lo]);print(json.dumps(r,ensure_ascii=False),errs)
        if len(sys.argv)>2:
            await pg.evaluate("CMP.sel=CMP.notes.find(n=>n.midi===60);ceUI();cmpDraw()");await pg.wait_for_timeout(2500);await pg.locator("#cmpBar").screenshot(path=sys.argv[2])
        ok=all(r.values()) and not errs
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
