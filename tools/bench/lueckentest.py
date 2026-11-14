"""v4.91: Zwei gleiche Töne hintereinander, die die Erkennung ohne Lücke aneinanderstoßen lässt, bekommen eine sichtbare Lücke (≥ 0,07 s):
die erste Note endet früher, Beginn und Anzahl bleiben gleich. Echte Daten: Fly Me to the Moon (Wa8fAoJmjQA) und gPCp9XTaWII, falls vorhanden; sonst Testnoten."""
import sys,asyncio,json,os
from playwright.async_api import async_playwright
songs={}
for vid in ['Wa8fAoJmjQA','gPCp9XTaWII']:
    p=f'/tmp/dg_{vid}/meta.json'
    if os.path.exists(p):songs[vid]=json.load(open(p))['notes']
songs['syn']=[[62,1.0,1.34,'L'],[62,2.34,1.0,'L'],[64,0,0.5,'R'],[64,0.54,0.5,'R']]
JS=r"""async(S)=>{const out={};for(const [k,N] of Object.entries(S)){const notes=N.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}));
 const it={id:'lu'+k,type:'video',title:k,video:{keys:[21,108],geo:{},first:0},data:b64FromBuf(writeMidi(notes))};const s=songForItem(it);
 const by=new Map();for(const n of s.notes){if(!by.has(n.midi))by.set(n.midi,[]);by.get(n.midi).push(n)}let touch=0,minGap=9;for(const a of by.values()){a.sort((x,y)=>x.start-y.start);for(let i=0;i+1<a.length;i++){const g=a[i+1].start-(a[i].start+a[i].dur);if(a[i].dur>0.13&&g<0.065)touch++;minGap=Math.min(minGap,g)}}
 out[k]={n:s.notes.length,nIn:N.length,touch,fix:s.gapFix||0}}return out}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3000)
        r=await pg.evaluate(JS,songs);print(json.dumps(r),errs)
        c={'keine aneinanderstoßenden gleichen Töne mehr':all(v['touch']==0 for v in r.values()),'Anzahl Noten gleich':all(v['n']==v['nIn'] for v in r.values()),
           'Testnoten korrigiert':r['syn']['fix']>=2,'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
