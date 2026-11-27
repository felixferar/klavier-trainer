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
        globals().__setitem__('_R',r);print(json.dumps(r));globals().__setitem__('_E',errs);print('pageerrors',errs);await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'Upload und Status sind beide angekommen':r['puts']==['diag/x.ktd.gz','queue/status.txt'],'der 409-Konflikt wurde wiederholt':r['conflicts']>=1,'Upload meldet ok':r['upload'].get('ok') is True}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
