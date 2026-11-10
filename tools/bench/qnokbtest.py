"""v4.32: Warteschlange wartet NICHT auf manuelle Tastaturmarkierung: ohne erkannte Tastatur wird das Video als Fehler gemeldet, markKeyboard wird nicht aufgerufen. Einzelumwandlung (keine Warteschlange) fragt weiter nach."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def run(pg,queue):
    return await pg.evaluate("""async(queue)=>{NAT.ok=true;const o={mark:0,err:null,diag:0};
      convUI=()=>{};convLandscape=async()=>false;waitMainVideo=async()=>true;
      let t=0;ytp={mute(){},setPlaybackRate(){},playVideo(){},getCurrentTime:()=>(t+=5),getPlayerState:()=>1,getDuration:()=>600,pauseVideo(){},unMute(){}};
      grabVideo=async()=>{const d=new ImageData(100,50);for(let i=0;i<d.data.length;i+=4){d.data[i]=d.data[i+1]=d.data[i+2]=120;d.data[i+3]=255}return d};
      markKeyboard=async()=>{o.mark++;return false};diagSave=async()=>{o.diag++};convCancelled=()=>{o.cancelled=true};
      showConvError=(m,ti)=>{o.err=String(m).slice(0,60)};
      Q.on=queue;Q.res=null;Q.finish=(ok,info)=>{o.qfinish=[ok,String(info).slice(0,50)]};
      ytAuto=true;await autoConvert({start:0,videoId:'x',title:'t'});return o}""",queue)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        out={}
        for q in (True,False):
            pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(400)
            out['queue' if q else 'einzeln']=await run(pg,q);out['err_'+str(q)]=errs;await pg.close()
        print(json.dumps(out,ensure_ascii=False,indent=1));await br.close()
asyncio.run(main())
