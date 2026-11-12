"""v4.64: Song-Seite/Auswendig/Spielen/Menue arbeiten nach dem Speichern im Editor mit der NEUEN Version (nicht mit einer alten Kopie des Eintrags)"""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS="""async()=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));
 NAT.ok=false;navStack.length=0;navStack.push('home');show('home');
 const mk=(n)=>{const ns=[];for(let i=0;i<n;i++)ns.push({m:60+(i%7),start:1+i*0.5,dur:0.3,hand:'R'});return b64FromBuf(writeMidi(ns))};
 const it={id:'sync1',title:'Sync',type:'midi',data:mk(20),fromYT:true,video:true};
 LIB=[it];save('kt_lib',LIB);
 openSongPage(it);
 // what the editor does when saving: a NEW object replaces the entry in the library
 const it2=Object.assign({},it,{data:mk(24),edited:true,data0:it.data});LIB=LIB.map(x=>x.id===it.id?it2:x);
 // 1) song page: tap "Auswendig"
 $('#spGo').click();await wait(50);
 o.memNotes=MEM.song.notes.length;o.memSame=MEM.item===it2;
 // 2) song page: play
 back();back();await wait(30);
 navStack.length=0;navStack.push('home');show('home');
 openSongPage(it);
 const it3=Object.assign({},it2,{data:mk(28),edited:true});LIB=LIB.map(x=>x.id===it.id?it3:x);
 $('#spPlay').click();await wait(80);
 o.playNotes=(typeof song!=='undefined'&&song)?song.notes.length:-1;
 // 3) item menu -> Auswendig
 const it4=Object.assign({},it3,{data:mk(30),edited:true});LIB=LIB.map(x=>x.id===it.id?it4:x);
 openSongMenu(it);$('#smMem').click();await wait(50);
 o.menuNotes=MEM.song.notes.length;
 return o}"""
async def main(f):
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':400,'height':780})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+f);await pg.wait_for_timeout(1200)
        r=await pg.evaluate(JS);print(json.dumps(r),errs)
        ok=r['memNotes']==24 and r['memSame'] and r['playNotes']==28 and r['menuNotes']==30 and not errs
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main(sys.argv[1]))
