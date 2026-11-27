"""v4.28: pickKb lehnt schlechte Tastaturpassung ab (res > 0.16): Intro-Grafik von rYglC8WAm5g (res 0.172) wird NICHT als Tastatur genommen, echte Tastatur (mid still, res ~0.11) schon.
usage: python3 tools/bench/kbtest.py APP.html [INTRO.jpg ECHT.jpg]
Ohne Bilder holt der Test sie aus dem privaten Diagnose-Archiv ($KLAVIER_DIAG, sonst /home/claude/klavier-diagnose): aus dem Scan vom 10.11. (v4.23),
bei dem die App die Intro-Grafik für die Tastatur hielt – „still“ ist das Intro, das erste Bild aus der Song-Mitte die echte Tastatur.
Fehlt das Archiv: SKIP (nichts geprüft). Bis 27.11.2026 lief der Test nie, weil er zwei Bilddateien verlangte, die nirgends lagen, und er hatte kein Urteil."""
import sys,asyncio,json,base64,os,gzip,struct
from playwright.async_api import async_playwright
def aus_archiv():
    p=os.path.join(os.environ.get('KLAVIER_DIAG','/home/claude/klavier-diagnose'),'diag','2026-11-10T13-51-52_rYglC8WAm5g_done.ktd.gz')
    if not os.path.exists(p): return None
    f=gzip.open(p);h=f.read(8);m=json.loads(f.read(struct.unpack_from('<I',h,4)[0]));f.close()
    b=lambda u:u.split(',',1)[1]
    return {'intro':b(m['still']),'real':b(m['midStills'][0]['img'])}
async def main():
    app=sys.argv[1]
    if len(sys.argv)>=4: bs={k:base64.b64encode(open(f,'rb').read()).decode() for k,f in (('intro',sys.argv[2]),('real',sys.argv[3]))}
    else: bs=aus_archiv()
    if not bs: print('SKIP – Diagnose-Archiv nicht gefunden, nichts geprüft');return 0
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath(app));await pg.wait_for_timeout(500)
        r=await pg.evaluate("""async(bs)=>{const o={};const get=async b=>{const im=new Image();im.src='data:image/jpeg;base64,'+b;await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const x=c.getContext('2d');x.drawImage(im,0,0);return x.getImageData(0,0,c.width,c.height)};
          for(const [k,b] of Object.entries(bs)){const img=await get(b);const t=tryKeyboard(img);const pk=pickKb([t]);o[k]={tryKeyboard:t?{res:+t.det.res.toFixed(3),nb:t.det.nb,w:+t.det.w.toFixed(1)}:null,pickKb:!!pk}}return o}""",bs)
        print(json.dumps(r));print('pageerrors',errs);await br.close()
    c={'Intro-Grafik wird NICHT als Tastatur genommen':not r['intro']['pickKb'],'echte Tastatur wird genommen':r['real']['pickKb'],'keine JS-Fehler':not errs}
    for k,v in c.items(): print(('OK   ' if v else 'FEHL ')+k)
    return 0 if all(c.values()) else 1
sys.exit(asyncio.run(main()))
