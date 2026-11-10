import sys,asyncio,json,os,base64,cv2
from playwright.async_api import async_playwright
n=int(sys.argv[1]);D='/tmp/bench/bk1';j=json.load(open(f'{D}/{n}.json'));st=j['style']
cap=cv2.VideoCapture(f'{D}/{n}.mp4');fps=cap.get(cv2.CAP_PROP_FPS)
def fr(t):
    cap.set(cv2.CAP_PROP_POS_FRAMES,int(round(t*fps)));ok,f=cap.read();return f
def b64(f):
    ok,b=cv2.imencode('.jpg',f,[cv2.IMWRITE_JPEG_QUALITY,92]);return base64.b64encode(b).decode()
t_show=st['intro']+float(sys.argv[2]) if len(sys.argv)>2 else st['intro']+3.0
rest=b64(fr(0.1+st['intro']*0)) # intro may show title; use frame just before first note
first=min(x['s'] for x in j['notes'])
rest=b64(fr(st['intro']+max(0.0,first-0.1)));show=b64(fr(t_show))
notes=[{'midi':x['m'],'start':x['s'],'dur':x['d'],'hand':x['h']} for x in j['notes']]
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':430,'height':800},device_scale_factor=2)
        await pg.goto('file:///home/claude/klavier-trainer/web/index.html');await pg.wait_for_timeout(600);await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(2600);await pg.evaluate("try{lvExec('klick Überspringen')}catch(e){}");await pg.wait_for_timeout(400)
        r=await pg.evaluate("""async([rest,showImg,notes,intro,tshow,speed])=>{
          const ld=b=>new Promise(res=>{const i=new Image();i.onload=()=>{const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);res(x.getImageData(0,0,c.width,c.height))};i.src='data:image/jpeg;base64,'+b});
          const im=await ld(rest);const t=tryKeyboard(im);if(!t)return {err:'keine Tastatur'};
          scanDet=t.det;scanRows=t.rows;scanImg=im;scanBox={x:0,y:0,w:1280,h:720};SCAN.keys=keyLayout(t.det,0);SCAN.kw=t.det.w/t.det.W;
          const geo=videoGeo();
          LIB=[];window.openYT=(it,auto,cmp)=>{cmpMode(!!CMP);show('yt')};
          let vt=tshow;ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(x){vt=x},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2};
          CMP={it:{},notes:notes.slice().sort((a,b)=>a.start-b.start),moments:cmpMoments(notes),lo:SCAN.keys[0].m,g:geo,off:intro,lit:null,litT:0,busy:false,gen:0,step:false,speed:speed,calibrating:false};
          openYT({},false,true);$('#ytBox').style.backgroundImage='url(data:image/jpeg;base64,'+showImg+')';$('#ytBox').style.backgroundSize='100% 100%';
          cmpLoop();await new Promise(z=>setTimeout(z,300));return {geo:{kw:geo.kw,yT:geo.yT,ar:geo.ar,n:geo.kx.length}}}""",[rest,show,notes,st['intro'],t_show,float(sys.argv[3])/720 if len(sys.argv)>3 else st['pps']/720])
        print(r);await pg.screenshot(path=f'/tmp/ov{n}.png');await br.close()
asyncio.run(main())
