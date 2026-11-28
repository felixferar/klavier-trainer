"""v5.53: Lernprotokolle kommen automatisch an – nach jedem Durchgang (höchstens 1×/min), jede Minute nachholen,
sofort wenn die App in den Hintergrund geht. Felix 23.11.: „Kannst du einstellen, dass du ständig automatisch an alle Daten kommst?“
usage: python3 tools/bench/uploadtest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""async (S)=>{window.toast=()=>{};window.AW_NOLOOP=true;window.playTone=()=>{};window.playClick=()=>{};const o={},up=[];
 save('kt_ghtok','x');window.ghUpload=async(p,b,m)=>{up.push({p,n:JSON.parse(decodeURIComponent(escape(atob(b)))).entries.length,t:Date.now()});return {ok:true}};
 const ns=S.fly_me,it={id:'fly_me',type:'midi',title:'Fly Me',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);MEMS={};save('kt_v8log',[]);save('kt_v8logat',0);save('kt_v8logsent',0);
 openMem(it);const gs=MEM.gs,sl=ms=>new Promise(r=>setTimeout(r,ms));
 const one=()=>{const r=zlStart({k:0,stage:4});let n=0;while(r.demo&&n++<5000)zlTick(r,0.02);for(let j=r.pos;j<=r.b;j++){if(j>r.a){let n=0;while(r.vt<gs[j].start-0.01&&n++<2000)zlTick(r,0.02)}for(const m of gs[j].mids)memPress(m,'kb')}memStop()};
 one();await sl(2000);o.a=up.length;o.an=up[0]&&up[0].n;
 one();await sl(2000);o.b=up.length; /* innerhalb 1 min: kein zweiter Upload */
 Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});document.dispatchEvent(new Event('visibilitychange'));await sl(500);
 o.c=up.length;o.cn=up[1]&&up[1].n;o.sentAll=load('kt_v8logsent')===(load('kt_v8log').slice(-1)[0]||{}).t;
 o.ver=$('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 800, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        try: r = await pg.evaluate(JS, SONGS)
        except Exception as e: r = {'crash': str(e)[:300]}
        await br.close()
    print(json.dumps(r, ensure_ascii=False))
    def t(f):
        try: return bool(f())
        except Exception: return False
    c = {'nach dem ersten Durchgang automatisch hochgeladen (ohne Übersicht)': t(lambda: r['a'] == 1 and r['an'] >= 1),
         'höchstens 1× pro Minute': t(lambda: r['b'] == 1),
         'App in den Hintergrund → Rest sofort hoch, nichts fehlt': t(lambda: r['c'] == 2 and r['cn'] >= 1 and r['sentAll']),
         'Version 5.81': t(lambda: r['ver'].startswith('Version 5.81')),
         'keine JS-Fehler': not errs and 'crash' not in r}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    print('errs', errs); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
