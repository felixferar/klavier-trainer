"""Test rqPoll (Links automatisch abholen): aus = kein Abruf; beschäftigt/kürzlich benutzt = kein Abruf; neue Datei = qStart einmal; gleiche Datei = nicht nochmal; 404/leer/ohne Links = nichts; Status wird geschrieben."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(400); await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate("""async()=>{const o={};let calls=[],puts=[],file=null,started=[];
          save('kt_ghtok','github_pat_test');ghRepo.v='x/klavier-diagnose';NAT.ok=true;keepAwake=()=>{};
          window.fetch=async(url,opt)=>{calls.push((opt&&opt.method||'GET')+' '+url.replace('https://api.github.com',''));
            if(opt&&opt.method==='PUT'){puts.push(url);return {ok:true,status:200,json:async()=>({})}}
            if(url.endsWith('queue/pending.txt')){if(!file)return {ok:false,status:404,json:async()=>({})};return {ok:true,status:200,json:async()=>file}}
            return {ok:true,status:200,json:async()=>({sha:'s'})}};
          qStart=async t=>{started.push(t)};
          const mk=(txt,sha)=>({sha,content:btoa(unescape(encodeURIComponent(txt)))});
          const L='https://youtu.be/AAAAAAAAAAA\\nhttps://youtu.be/BBBBBBBBBBB';file=mk(L,'sha1');
          rqTouch=0;S.remoteQ=false;await rqPoll();o.aus=calls.length;
          S.remoteQ=true;rqTouch=Date.now();await rqPoll();o.kuerzlichBenutzt=calls.length;
          rqTouch=0;SCAN.on=true;await rqPoll();o.beschaeftigt=calls.length;SCAN.on=false;
          file=null;await rqPoll();o.n404={started:started.length,sha:load('kt_rq_sha')};
          file=mk(L,'sha1');await rqPoll();o.neu={started:started.length,text:started[0],sha:load('kt_rq_sha'),puts:puts.length};
          const c0=started.length;await rqPoll();o.gleicheDatei=started.length-c0;
          file=mk('kein link hier','sha2');await rqPoll();o.ohneLinks={started:started.length,sha:load('kt_rq_sha')};
          const many=Array.from({length:60},(_,i)=>'https://youtu.be/'+String(i).padStart(11,'x')).join('\\n');file=mk(many,'sha3');await rqPoll();o.viele=started[started.length-1].split('\\n').length;
          return o}""")
        print(json.dumps(r,ensure_ascii=False)); print('pageerrors',errs); await br.close()
asyncio.run(main())
