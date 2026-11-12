"""v4.47: Bildschirmfoto an Claude: Knopf nur in der Vergleichsansicht, Foto + Zahlen werden hochgeladen, ohne Schluessel/ohne Capture sauberer Hinweis"""
import sys,asyncio,json,base64,io
from PIL import Image
from playwright.async_api import async_playwright
exec(open('/tmp/dshot.py').read().split("async def main")[0].replace("import sys,asyncio,json,os",""))
b=io.BytesIO();Image.new('RGB',(1080,2200),(40,80,120)).save(b,'PNG');PNG='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':400,'height':780});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500)
        r=await pg.evaluate("""async([geo,lo,png])=>{const o={};const wait=ms=>new Promise(z=>setTimeout(z,ms));let toasts=[];window.toast=m=>toasts.push(m);
          const ups=[];window.ghUpload=async(path,b64,msg)=>{ups.push({path,len:b64.length,b64});return {ok:true}};
          o.settingsRow=!!$('#shotBtn');localStorage.removeItem('kt_ghtok');shotFabShow();o.btnHiddenOutside=$('#shotFab').classList.contains('hidden');
          // ohne Schluessel
          localStorage.removeItem('kt_ghtok');await shotSend();o.noTok=[toasts.slice(),ups.length];toasts=[];
          localStorage.setItem('kt_ghtok',JSON.stringify('ghp_test'));
          // ohne Capture
          nat=async()=>({ok:false});await shotSend();o.noCap=[toasts.slice(),ups.length];toasts=[];
          // mit Capture in der Vergleichsansicht
          nat=async()=>({ok:true,img:png});
          const notes=[{m:lo+30,start:1,dur:1,hand:'R'}];const a={id:'a',type:'midi',title:'T',artist:'x',data:b64FromBuf(writeMidi(notes)),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:2,first:3,fps:25,keys:[lo,lo+geo.kx.length-1],geo}};LIB=[a];
          window.openYT=()=>{cmpMode(!!CMP);show('yt')};let vt=3.6;ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(t){vt=t},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2,getPlaybackQuality:()=>'tiny',destroy(){}};
          openCompare(a);await wait(400);shotFabShow();o.btnShown=!$('#shotFab').classList.contains('hidden');
          $('#shotFab').click();await wait(900);
          o.ups=ups.map(u=>u.path.replace(/\\d{4}-\\d\\d-\\d\\dT[\\d-]+/,'TS'));o.toast=toasts.slice();
          const j=ups.find(u=>u.path.endsWith('.json'));const info=JSON.parse(decodeURIComponent(escape(atob(j.b64))));
          o.info={ver:info.version,screen:info.screen,hasRects:!!(info.rects.ytBox&&info.rects.cmpScene),q:info.cmp&&info.cmp.quality,off:info.cmp&&info.cmp.off,vt:info.cmp&&info.cmp.vt};
          const im=ups.find(u=>u.path.endsWith('.jpg'));o.jpgOK=atob(im.b64).slice(0,2)==='\\xff\\xd8';
          // Einstellungs-Knopf: zeigt Hinweis, sendet erst nach 8 s
          ups.length=0;toasts=[];back&&0;$('#shotBtn').click();o.settingsToast=toasts.slice();o.sofort=ups.length;
          return o}""",[geo,lo,PNG]);print(json.dumps(r,ensure_ascii=False),errs)
        ok=(r['settingsRow'] and r['btnHiddenOutside'] and r['noTok'][1]==0 and 'Schlüssel' in r['noTok'][0][0] and r['noCap'][1]==0 and 'nicht möglich' in r['noCap'][0][0]
            and r['btnShown'] and len(r['ups'])==2 and r['ups'][0].startswith('diag/shots/TS') and r['jpgOK'] and 'gesendet' in r['toast'][-1]
            and r['info']['q']=='tiny' and r['info']['hasRects'] and r['info']['off']==2 and 'Version 4.49' in (r['info']['ver'] or 'Version 4.49') and r['sofort']==0 and r['settingsToast'] and not errs)
        print('OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
