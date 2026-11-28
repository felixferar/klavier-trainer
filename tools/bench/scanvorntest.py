"""v5.80: Sobald die Tastatur gefunden ist, springt das Video zurück und liest ab dort, wo die Tastatur schon zu sehen war (Felix 28.11., Snowman).
Geprüft: Sprungziel (von Anfang an sichtbar → Start; mit Vorspann → kurz vor dem ersten Bild mit Tastatur; sofort gefunden → kein Sprung),
autoConvert spult wirklich zurück und das Lesen startet dort, die Suchbilder werden danach nicht mehr nachgebaut, Schalter KB_REWIND=false = altes Verhalten.
usage: python3 tools/bench/scanvorntest.py web/index.html"""
import sys,asyncio,json,os
from playwright.async_api import async_playwright
UNIT=r"""()=>{const o={};const real=detectKeys;
  const mk=(t,kb)=>{const f=new ImageData(4,4);f.t=t;f.t0=t-0.05;f.kb=kb;return f};
  detectKeys=(f)=>f.kb?{lo:10,hi:45}:null;const best={rows:{yA:0.8},det:{lo:10,hi:45}};
  o.vonAnfang=rewindTo([1,1.3,1.6,1.9,2.2].map(t=>mk(t,true)),best,0);
  o.vorspann=rewindTo([8,8.3,8.6,8.9,9.2,9.5].map((t,i)=>mk(t,i>=3)),best,0);
  o.sofort=rewindTo([0.1,0.2].map(t=>mk(t,true)),best,0);
  o.startstelle=rewindTo([31,31.5,32].map(t=>mk(t,true)),best,30);
  o.andereTasten=rewindTo([5,5.3,5.6].map((t,i)=>{const f=mk(t,true);if(i<1)f.kb=false;return f}),best,0);
  detectKeys=real;return o}"""
FLOW=r"""async(rw)=>{NAT.ok=true;window.KB_REWIND=rw;const o={seeks:[],rates:[],run:null};
  convUI=()=>{};convLandscape=async()=>false;waitMainVideo=async()=>true;diagSave=async()=>{};
  let t=0,rate=1,state=1;const tick=setInterval(()=>{if(state===1)t+=0.1*rate},100);
  ytp={mute(){},unMute(){},setPlaybackRate(r){rate=r;o.rates.push(r)},playVideo(){state=1},pauseVideo(){state=2},getCurrentTime:()=>t,getPlayerState:()=>state,getDuration:()=>200,
       seekTo(x){o.seeks.push(+x.toFixed(2));t=x;state=3;setTimeout(()=>{state=1},300)}};
  let n=0;grabVideo=async()=>{n++;const f=new ImageData(4,4);f.data.fill(140);f.kb=true;return f};
  const realD=detectKeys,realT=tryKeyboard,realP=pickKb;detectKeys=f=>f.kb?{lo:10,hi:45}:null;
  /* Tastatur wird erst ab dem 12. Suchbild „erkannt“ (wie Snowman: Suche dauert), sichtbar ist sie von Anfang an */
  tryKeyboard=img=>({rows:{yA:0.8,yB:0.9,yC:0.74,yT:0.75},det:{lo:10,hi:45,w:10,W:400},img,n:35});pickKb=l=>n>=12?l[0]:null;
  scanRun=async(live)=>{o.run={live,t:+t.toFixed(2),nextRw:SCAN.nextRw}};
  ytAuto=true;await autoConvert({start:0,videoId:'x',title:'t'});clearInterval(tick);
  detectKeys=realD;tryKeyboard=realT;pickKb=realP;return o}"""
EARLY=r"""()=>{const o={};SCAN.rw=0;SCAN.fromFile=false;const ev=[{m:60,start:1,end:1.5}];o.skip=earlyFromBars(ev)===ev;SCAN.rw=null;return o}"""
async def main(url):
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']);R={};errs=[]
        for name,js,arg in [('unit',UNIT,None),('mitSprung',FLOW,True),('ohneSprung',FLOW,False),('early',EARLY,None)]:
            pg=await br.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('file://'+os.path.abspath(url));await pg.wait_for_timeout(500)
            R[name]=await (pg.evaluate(js,arg) if arg is not None else pg.evaluate(js));await pg.close()
        await br.close()
    print(json.dumps(R,ensure_ascii=False,indent=1))
    u=R['unit'];m=R['mitSprung'];w=R['ohneSprung']
    c={'von Anfang an sichtbar → zurück an den Start':u['vonAnfang']==0,
       'mit Vorspann → kurz vor dem ersten Bild mit Tastatur':u['vorspann'] is not None and 8.3<=u['vorspann']<=8.5,
       'sofort gefunden → kein Sprung':u['sofort'] is None,
       'Startstelle des Links bleibt Untergrenze':u['startstelle']==30,
       'erstes Bild ohne Tastatur → ab dem zweiten':u['andereTasten'] is not None and 4.7<=u['andereTasten']<=4.8,
       'autoConvert spult an den Start zurück':m['seeks']==[0] and m['run'] and m['run']['nextRw']==0 and m['run']['t']<1.0,
       'zurückgespult wird langsam (0,25×)':0.25 in m['rates'],
       'Schalter aus: kein Sprung, Lesen an der Fundstelle':w['seeks']==[] and w['run'] and w['run']['nextRw'] is None,
       'nach dem Sprung keine nachgebauten Töne aus den Suchbildern':R['early']['skip'],
       'keine JS-Fehler':not errs}
    if errs:print(errs)
    for k,v in c.items():print(('OK   ' if v else 'FEHL ')+k)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main(sys.argv[1]))
