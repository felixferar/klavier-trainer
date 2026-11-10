"""v4.35: ein gespeicherter Song enthält video.geo (Lage der Tastatur im Videobild: x erste/letzte Taste, Tastenbreite, Zeilen, Oktav-Verschiebung); fehlen die Angaben, wird trotzdem gespeichert (geo=null)."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""()=>{const o={};const mk=()=>{SCAN.keys=[{m:40,x:0.1234567},{m:80,x:0.9}];SCAN.kw=0.0165749;SCAN.fromFile=false;SCAN.start=0.2;SCAN.firstNote=3;SCAN.oneColor=false;SCAN.frames=100;SCAN.lastVt=4;
            SCAN.result=Array.from({length:6},(_,i)=>({m:60+i,start:1+i,dur:.5,hand:'R'}));ytItem={id:'y1',videoId:'abcdefghijk',title:'T',type:'yt'}};
          mk();scanRows={yC:0.4456,yA:0.5304,yB:0.6317,yT:0.4788};scanDet={shift:-12,octEst:true};scanSave(true);o.mit=LIB[0]&&LIB[0].video;
          LIB=[];mk();scanRows=null;scanDet=null;scanSave(true);o.ohne=LIB[0]&&LIB[0].video;o.gespeichert=LIB.length;return o}""")
        print(json.dumps(r));ok=r['mit']['geo']['yA']==0.53 and r['mit']['geo']['x']==[0.1235,0.9] and r['mit']['geo']['sh']==-12 and r['ohne']['geo'] is not None and r['gespeichert']==1
        print('pageerrors',errs,'ERGEBNIS','OK' if ok and not errs else 'FEHLER');await br.close()
asyncio.run(main())
