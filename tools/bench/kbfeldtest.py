"""v5.66: Tastatur sofort finden, auch wenn das YouTube-Feld „Weitere Videos“ über dem unteren Teil der schwarzen Tasten liegt.
Felix 27.11.: „Tastatur wird zu spät erkannt, die ersten Noten werden übersprungen“ – Sing (RgMoK2SUEyw), Scan 15:13: 11 Suchbilder, Lesestart erst bei 2,3 s.
fixtures/kb_weitere_videos.jpg = erstes Suchbild dieses Scans (nur der Tastaturbereich, der Rest geschwärzt).
usage: python3 tools/bench/kbfeldtest.py $PWD/web/index.html"""
import sys, os, base64, asyncio
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); app = 'file://' + os.path.abspath(sys.argv[1])
src = 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(HERE, 'fixtures/kb_weitere_videos.jpg'), 'rb').read()).decode()
JS = """async (s)=>{const i=await new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src=s});const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);
 const img=x.getImageData(0,0,i.width,i.height),f=o=>{window.KB_CONSENSUS=o;const t=tryKeyboard(img);return t&&{yA:t.rows.yA,yT:t.rows.yT,yC:t.rows.yC,lo:t.det.lo,hi:t.det.hi,res:t.det.res,n:t.n,pick:!!pickKb([t])}};return {alt:f(false),neu:f(true),max:KB_RES_MAX}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(app); await pg.wait_for_timeout(300); r = await pg.evaluate(JS, src); await br.close()
    n = r['neu'] or {}
    c = {'ohne die neue Regel wird dieses Bild abgelehnt (Gegenprobe)': not (r['alt'] and r['alt']['pick']),
         'Tastatur wird im ersten Bild gefunden': bool(r['neu'] and n.get('pick')),
         '36 Tasten C3–B5 (lo 24, hi 59)': (n.get('lo'), n.get('hi')) == (24, 59),
         'Passung gut (≤ 0,13)': n.get('res', 9) <= 0.13,
         'Zeile der schwarzen Tasten liegt über dem Feld (< 0,815 der Bildhöhe) und unter der Tastaturkante': n.get('yT', 9) + 0.03 < n.get('yA', 0) < 0.815,
         'Balkenzeile liegt über der Tastatur': n.get('yC', 9) < n.get('yT', 0),
         'keine JS-Fehler': not errs}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print(r); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
