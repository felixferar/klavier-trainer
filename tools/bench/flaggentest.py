"""v4.90: Flaggen aus der Vergleichsansicht gehen automatisch an Claude (Archiv klavier-diagnose, diag/flags/…json):
Song- und Videozeit jeder Flagge, die Noten rund um die Flagge (±4 s – Flaggen sitzen nur ungefähr), Titel/Video-ID; beim Setzen zusätzlich ein Bildschirmfoto. Ohne Schlüssel wird nichts gesendet."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};const puts=[];
 const f0=window.fetch;window.fetch=async(u,opt)=>{u=String(u);if(u.includes('api.github.com')){if(opt&&opt.method==='PUT'){const b=JSON.parse(opt.body);puts.push({u,c:decodeURIComponent(escape(atob(b.content)))})}
   if(u.endsWith('/user'))return new Response(JSON.stringify({login:'felixferar'}),{status:200});return new Response('{}',{status:201})}return f0(u,opt)};
 let shots=0;window.shotSend=async()=>{shots++};
 const notes=[];for(let i=0;i<20;i++)notes.push({midi:60+(i%3),start:i*0.5,dur:0.4,hand:'R'});
 /* ohne Schlüssel: nichts */
 save('kt_ghtok','');CMP={it:{id:'fly1',title:'Fly Me to the Moon',videoId:'Wa8fAoJmjQA'},notes,off:1.5,dens:[1],dur:12};tlSetFlags([3.0]);await w(2800);o.noTok=puts.filter(p=>p.u.includes('diag/flags')).length;
 /* mit Schlüssel */
 save('kt_ghtok','ghp_test');tlSetFlags([3.0,7.4]);await w(2800);const fp=puts.filter(p=>p.u.includes('diag/flags/'));o.n=fp.length;
 if(fp.length){const j=JSON.parse(fp[0].c);o.path=fp[0].u.split('/contents/')[1];o.title=j.title;o.vid=j.videoId;o.flags=j.flags.map(f=>[f.T,f.video,f.near.length]);o.near0=j.flags[0].near[0]}
 /* Flagge über den Knopf → auch Foto */
 window.ytp={getCurrentTime:()=>6.5};const before=shots;$('#tlFlag').click();await w(900);o.shot=shots>before;
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':780,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3000);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'ohne Schlüssel nichts gesendet':r['noTok']==0,'mit Schlüssel gesendet':r['n']>=1 and r.get('path','').startswith('diag/flags/') and r['path'].endswith('_Wa8fAoJmjQA.json'),
           'Titel/Video-ID':r.get('title')=='Fly Me to the Moon' and r.get('vid')=='Wa8fAoJmjQA',
           'Song- und Videozeit + Noten rundherum':r.get('flags')==[[3.0,4.5,10],[7.4,8.9,10]] or (r.get('flags') and r['flags'][0][:2]==[3.0,4.5] and r['flags'][0][2]>0),
           'beim Setzen auch ein Foto':r['shot'],'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
