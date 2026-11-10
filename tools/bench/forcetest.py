"""v4.27: '#neu' in pending.txt -> qStart force: vorhandene Songs werden NICHT übersprungen; Status enthält Fortschritt/Fehler; ohne '#neu' bleibt alles wie vorher."""
import sys, asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(500); await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""async()=>{NAT.ok=true;const o={};window.__op=[];let puts=[];
          save('kt_ghtok','github_pat_test');ghRepo.v='x/klavier-diagnose';keepAwake=()=>{};
          let file=null;
          window.fetch=async(url,opt)=>{if(opt&&opt.method==='PUT'){puts.push(JSON.parse(opt.body));return {ok:true,status:200,json:async()=>({})}}
            if(url.endsWith('queue/pending.txt'))return {ok:true,status:200,json:async()=>file};
            return {ok:true,status:200,json:async()=>({sha:'s'})}};
          openYT=(it,a)=>{window.__op.push(it.videoId);setTimeout(()=>Q.finish(it.videoId!=='BBBBBBBBBBB',it.videoId==='BBBBBBBBBBB'?'kaputt':'ok'),20)};
          showConvError=()=>{};
          const mk=(t,sha)=>({sha,content:btoa(unescape(encodeURIComponent(t)))});
          LIB.push({id:'m1',type:'midi',title:'a',fromYT:'AAAAAAAAAAA',data:''});
          const L='https://youtu.be/AAAAAAAAAAA\\nhttps://youtu.be/BBBBBBBBBBB';
          file=mk(L,'s1');rqTouch=0;S.remoteQ=true;await rqPoll();
          o.ohneNeu={opened:window.__op.slice(),force:Q.force};window.__op=[];
          file=mk('#neu\\n'+L,'s2');rqTouch=0;await rqPoll();
          o.mitNeu={opened:window.__op.slice(),force:Q.force};
          const last=puts[puts.length-1];o.status=atob(last.content);o.statusDecoded=decodeURIComponent(escape(atob(last.content)));
          delete o.status;return o}""")
        print(json.dumps(r,ensure_ascii=False,indent=1)); print('pageerrors',errs); await br.close()
asyncio.run(main())
