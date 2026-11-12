"""v4.56 Studio: Heute (Weiter mit, Wochen-Klaviatur, Faellig), Song-Seite, Auswendig-Kopf. Optional: Screenshots nach argv[2]"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS="""async()=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));
 navStack.length=0;navStack.push('home');show('home');
 const notes=[];let t=0;for(let i=0;i<60;i++){notes.push({m:60+(i%7)*2,start:t,dur:0.4,hand:'R'});t+=0.5;if(i%10===9)t+=0.6}
 const it={id:'w1',type:'midi',title:'Wake Me Up',artist:'Avicii',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 const n=memGroups(notes.map(x=>({midi:x.m,start:x.start,dur:x.dur}))).length;
 openMem(it);const k=MEM.rec.secs.length;MEM.rec.secs[0].passed=1;MEM.rec.secs[0].box=1;MEM.rec.secs[0].due=Date.now()-1000;MEM.rec.secs[1].passed=1;MEM.rec.secs[1].box=2;MEM.rec.secs[1].due=Date.now()+9e8;memSaveAll();back();
 ST.last={id:'w1'};renderHome();
 o.title=$('#contWrap .stTtl').textContent;o.sub=$('#contWrap .stSub').textContent;o.segs=$$('#contWrap .segs i').length===k;o.segDone=$$('#contWrap .segs i.d').length===2;
 o.keys=$$('#wkeys .k').length;o.bk=$$('#wkeys .bk').length;o.due=$$('#dueWrap .dueRow').length;o.dueTxt=($('#dueWrap .dueRow span')||{}).textContent;
 o.tab=$$('.tabbar button')[0].textContent.trim();
 // Song-Seite
 const row=$$('#recentList .song')[0];row.click();await wait(50);
 o.onPage=!$('#songp').classList.contains('hidden');o.pTitle=$('#spTitle').textContent;o.pBars=$$('#spBars>div').length===k;o.pGo=$('#spGo').textContent;o.pCmpHidden=$('#spCmp').classList.contains('hidden');
 window._shot1=1;
 o.menuOk=(()=>{$('#spMenu').click();const on=$('#songMenu').classList.contains('on');closeSheets();return on})();
 // Zurueck
 appBack();await wait(30);o.backHome=!$('#home').classList.contains('hidden');
 // Spielen
 openSongPage(it);$('#spPlay').click();await wait(200);o.player=!$('#player').classList.contains('hidden');
 navStack.length=0;show('home');
 // Auswendig-Kopf
 openSongPage(it);$('#spGo').click();await wait(50);o.memScreen=!$('#mem').classList.contains('hidden');o.kbChip=$('#memKb span').textContent;
 MEM.rec.secs[2].watched=true;memStart(2,false);o.stages=$$('#memStages i.d').length;o.tasti=!!$('#memTasti');
 memStop();
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(600);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        if len(sys.argv)>2:
            d=sys.argv[2]
            await pg.evaluate("()=>{navStack.length=0;show('home');setTab('start');renderHome()}");await pg.wait_for_timeout(300);await pg.screenshot(path=d+'/heute.png')
            await pg.evaluate("()=>{openSongPage(LIB[0])}");await pg.wait_for_timeout(300);await pg.screenshot(path=d+'/song.png')
            await pg.evaluate("()=>{openMem(LIB[0]);MEM.rec.secs.forEach(x=>x.watched=true);memStart(2,false)}");await pg.wait_for_timeout(500);await pg.screenshot(path=d+'/mem.png')
        ok=(r['title']=='Wake Me Up' and r['segs'] and r['segDone'] and r['keys']==7 and r['bk']==5 and r['due']==1 and r['onPage'] and r['pTitle']=='Wake Me Up' and r['pBars'] and r['pCmpHidden'] and r['menuOk'] and r['backHome'] and r['player'] and r['memScreen'] and r['stages']>=1 and r['tasti'] and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
