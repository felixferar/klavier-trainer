"""v4.31: 409 beim Schreiben ins Archiv -> Upload und Status werden nacheinander ausgefuehrt und wiederholt, nichts geht verloren."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500)
        r=await pg.evaluate("""async()=>{save('kt_ghtok','x');ghRepo.v='a/b';const o={puts:[],conflicts:0};let busy=false,fails={};
          window.fetch=async(u,op)=>{const m=op&&op.method||'GET';
            if(m==='PUT'){ // gleichzeitiger Schreibzugriff = 409; erster Versuch jedes Pfads scheitert zusaetzlich einmal
              const path=u.split('/contents/')[1];if(busy){o.conflicts++;return{ok:false,status:409,json:async()=>({message:'conflict'})}}
              if(!fails[path]){fails[path]=1;o.conflicts++;return{ok:false,status:409,json:async()=>({message:'conflict'})}}
              busy=true;await new Promise(z=>setTimeout(z,150));busy=false;o.puts.push(path);return{ok:true,status:200,json:async()=>({})}}
            return{ok:true,status:200,json:async()=>({sha:'s'})}};
          RQ={ver:'v',n:1,force:false,res:[],t0:'t'};
          const [a,b]=await Promise.all([ghUpload('diag/x.ktd.gz','AAAA','m'),rqPut('queue/status.txt','hallo','s')]);
          o.upload=a;o.puts=o.puts.sort();return o}""")
        print(json.dumps(r));print('pageerrors',errs);await br.close()
asyncio.run(main())
