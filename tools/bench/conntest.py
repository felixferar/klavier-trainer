"""v4.57: Klavier-Status (Leiste, Chips, Fenster) in allen Zustaenden, Jetzt verbinden, Wiederverbinden beim Zurueckkehren; Note teilen im Editor"""
import sys,os,json,asyncio
from playwright.async_api import async_playwright
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures')
meta=json.load(open(os.path.join(H,'embers_v434_meta.json')));keys=meta['keys'];rows=meta['scanRows'];lo=keys[0]['m']
geo={'x':[keys[0]['x'],keys[-1]['x']],'kw':meta['kw'],'yT':rows['yT'],'yA':rows['yA'],'yB':rows['yB'],'yC':rows['yC'],'sh':0,'kx':[round(k['x'],4) for k in keys],'ar':meta.get('ar',1280/544)}
JS="""async([geo,lo])=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));
 navStack.length=0;navStack.push('home');show('home');
 const cmds=[];NAT.ok=true;window.nat=(c,a)=>{cmds.push(c)};
 const st=(m)=>{kbMsg(Object.assign({cmd:'kbState'},m))};
 const bar=()=>({cls:$('#kbBar').className,t:$('#kbBar b').textContent,s:$('#kbBar .s').textContent,act:$('#kbBar .act').textContent,hid:$('#kbBar').classList.contains('hidden')});
 st({state:'off',name:'',saved:''});o.none=bar();
 st({state:'off',name:'Casio',saved:'AA'});o.notFound=bar();
 st({state:'connecting',name:'Casio',saved:'AA'});o.busy=bar();
 st({state:'waiting',name:'Casio',saved:'AA',msg:'x'});o.waiting=bar();
 st({state:'on',name:'Casio',saved:'AA'});o.on=bar();o.chipMem=$('#memKb .t').textContent+'|'+$('#memKb').className;o.chipSp=$('#spKb .t').textContent;
 st({state:'lost',name:'Casio',saved:'AA'});o.lost=bar();
 st({state:'btoff',name:'Casio',saved:'AA'});o.btoff=bar();
 // Fenster: Jetzt verbinden nur mit gespeichertem, nicht verbundenem Klavier
 st({state:'off',name:'Casio',saved:'AA'});o.nowShown=!$('#kbNow').classList.contains('hidden');o.big=$('#kbBig b').textContent;
 st({state:'on',name:'Casio',saved:'AA'});o.nowHiddenOn=$('#kbNow').classList.contains('hidden');
 st({state:'off',name:'',saved:''});o.nowHiddenNone=$('#kbNow').classList.contains('hidden');
 // Antippen der Leiste bei gespeichertem, nicht gefundenem Klavier: sofort neu verbinden
 st({state:'off',name:'Casio',saved:'AA'});cmds.length=0;$('#kbBar').click();o.tapAuto=cmds.includes('kbAuto');closeSheets();
 // Jetzt verbinden
 cmds.length=0;st({state:'off',name:'Casio',saved:'AA'});$('#kbNow').click();o.nowCmd=cmds.includes('kbAuto');o.nowState=KB.state;
 // Wiederverbinden beim Zurueckkehren in die App
 st({state:'waiting',name:'Casio',saved:'AA'});cmds.length=0;
 Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'visible'});document.dispatchEvent(new Event('visibilitychange'));o.resume=cmds.includes('kbAuto');
 st({state:'connecting',name:'Casio',saved:'AA'});cmds.length=0;document.dispatchEvent(new Event('visibilitychange'));o.noDouble=!cmds.includes('kbAuto');
 st({state:'on',name:'Casio',saved:'AA'});cmds.length=0;document.dispatchEvent(new Event('visibilitychange'));o.noWhenOn=!cmds.includes('kbAuto');
 // ---- Note teilen
 const mk=(id)=>({id,type:'midi',title:'Test',artist:'x',data:b64FromBuf(writeMidi([{m:60,start:1,dur:1.26,hand:'R'},{m:64,start:5,dur:0.06,hand:'R'}])),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:2,first:3,fps:25,keys:[lo,lo+geo.kx.length-1],geo}});
 const a=mk('a');LIB=[a];
 window.openYT=(it,auto,cmp)=>{cmpMode(!!CMP);show('yt')};
 let vt=0;ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(t){vt=t},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2,destroy(){}};
 openCompare(a);vt=1+2+0.3;await wait(300);cmpDraw();
 const H1=CMP.hit,xcol=m=>H1.P.X(geo.kx[m-lo]);
 ceTap(xcol(60),H1.rh-0.3*H1.pps);o.sel=CMP.sel&&CMP.sel.midi===60;o.splitBtn=!!$('#ceSplit');
 const n0=CMP.notes.length,st0=CMP.sel.start,du0=CMP.sel.dur;
 $('#ceSplit').click();
 const ns=CMP.notes.filter(n=>n.midi===60).sort((x,y)=>x.start-y.start);
 o.count=CMP.notes.length-n0;o.parts=ns.length;o.endsOk=Math.abs((ns[1].start+ns[1].dur)-(st0+du0))<0.011&&Math.abs(ns[0].start-st0)<0.001;
 o.gap=Math.round((ns[1].start-(ns[0].start+ns[0].dur))*100)/100;o.durs=[ns[0].dur,ns[1].dur];o.cutAtPlayhead=Math.abs(ns[0].dur-(0.3-0.02))<0.06;
 o.sel2=CMP.sel===ns[0]||(CMP.sel&&CMP.sel.start===ns[0].start);
 $('#ceUndo').click();o.undo=CMP.notes.filter(n=>n.midi===60).length===1;
 // Abspielposition ausserhalb der Note: in der Mitte teilen
 vt=1+2+3;await wait(100);cmpDraw();ceTap(xcol(60),H1.rh-0.3*H1.pps);if(!CMP.sel||CMP.sel.midi!==60)CMP.sel=CMP.notes.find(n=>n.midi===60);ceUI();
 $('#ceSplit').click();const nm=CMP.notes.filter(n=>n.midi===60).sort((x,y)=>x.start-y.start);o.midParts=nm.length;o.cutNearMid=nm.length===2&&Math.abs(nm[0].dur-nm[1].dur)<0.1;$('#ceUndo').click();
 // zu kurze Note
 const sh=CMP.notes.find(n=>n.midi===64);CMP.sel=sh;const c0=CMP.notes.length;$('#ceSplit').click();o.shortNoSplit=CMP.notes.length===c0;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(600);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS,[geo,lo]);print(json.dumps(r,ensure_ascii=False),errs)
        c=lambda k:r[k]['cls'].split()[1] if len(r[k]['cls'].split())>1 else ''
        ok=(c('none')=='none' and c('notFound')=='off' and c('busy')=='busy' and c('waiting')=='off' and c('on')=='on' and c('lost')=='busy' and c('btoff')=='off'
            and r['on']['t']=='Klavier verbunden' and r['notFound']['t']=='Klavier nicht gefunden' and not r['on']['hid'] and r['chipMem'].startswith('Klavier verbunden|kbchip on') and r['chipSp']=='Klavier verbunden'
            and r['nowShown'] and r['nowHiddenOn'] and r['nowHiddenNone'] and r['tapAuto'] and r['nowCmd'] and r['nowState']=='connecting' and r['resume'] and r['noDouble'] and r['noWhenOn']
            and r['sel'] and r['splitBtn'] and r['count']==1 and r['parts']==2 and r['endsOk'] and r['gap']==0.04 and r['cutAtPlayhead'] and r['cutNearMid'] and r['undo'] and r['shortNoSplit'] and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
