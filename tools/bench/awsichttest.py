"""v5.04: Bildschirm-Prüfung Auswendig-Modus (quer 780×360 und hoch 360×760).
- „Weiß nicht weiter“ im Dunkeln: voll deckend (keine Abdunklung), im Bild, Kontrast Schrift/Hintergrund ≥ 4,5
- Zustände: Start-Anker (Anschlag sichtbar), dunkel, Hilfe sichtbar, Puls mit Einzählen – Bildschirmfotos nach /tmp/awsicht_*.png zum Ansehen
- „Beenden“ und „Weiter“ erreichbar
usage: python3 tools/bench/awsichttest.py $PWD/web/index.html"""
import sys, asyncio, json
from playwright.async_api import async_playwright
SETUP = r"""()=>{window.AW_NOLOOP=true;window.playTone=()=>{};KB.state='off';const notes=[];let t=0;
 for(let bar=0;bar<8;bar++){notes.push({m:48+(bar%4)*2,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:64+((bar+q)%5)*2,start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 const it={id:'sicht',type:'midi',title:'Sicht',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);openMem(it);MEM.rec.v9.ch[0].st=1;return true}"""
EFF = r"""(sel)=>{const el=document.querySelector(sel);if(!el)return null;let o=1,x=el;while(x&&x.nodeType===1){o*=parseFloat(getComputedStyle(x).opacity);x=x.parentElement}
 const lum=c=>{const v=(c.match(/[\d.]+/g)||[0,0,0]).slice(0,3).map(Number).map(v=>{v/=255;return v<=0.03928?v/12.92:((v+0.055)/1.055)**2.4});return 0.2126*v[0]+0.7152*v[1]+0.0722*v[2]};
 let bg=null;x=el;while(x){const b=getComputedStyle(x).backgroundColor;const a=(b.match(/[\d.]+/g)||[]);if(b&&b!=='transparent'&&!(a.length===4&&+a[3]===0)){bg=b;break}x=x.parentElement}
 const fg=getComputedStyle(el).color,l1=lum(fg),l2=lum(bg||'rgb(0,0,0)'),cr=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05),r=el.getBoundingClientRect();
 return {opacity:+o.toFixed(2),contrast:+cr.toFixed(1),inView:r.width>0&&r.height>0&&r.top>=0&&r.left>=0&&r.bottom<=innerHeight+1&&r.right<=innerWidth+1,disabled:el.disabled,box:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]}}"""

async def main():
    res = {}; ok = True
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for name, vp in [('quer', {'width': 780, 'height': 360}), ('hoch', {'width': 360, 'height': 760})]:
            pg = await br.new_page(viewport=vp); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
            await pg.evaluate(SETUP)
            await pg.evaluate("()=>{awStart({k:0,mode:'head'});awDraw()}"); await pg.wait_for_timeout(150)
            st = {'anker': await pg.evaluate("MEM.run.drawState")}
            await pg.screenshot(path=f'/tmp/awsicht_{name}_anker.png')
            st['knopf'] = await pg.evaluate(EFF, '#memHelp')
            await pg.evaluate("()=>{const R=MEM.run;for(const m of MEM.gs[R.pos].mids)memPress(m,'kb');awDraw()}"); await pg.wait_for_timeout(100)
            st['dunkel'] = await pg.evaluate("MEM.run.drawState"); st['knopfDunkel'] = await pg.evaluate(EFF, '#memHelp')
            await pg.screenshot(path=f'/tmp/awsicht_{name}_dunkel.png')
            await pg.evaluate("()=>{document.querySelector('#memHelp').click()}"); await pg.wait_for_timeout(100)
            st['hilfe'] = await pg.evaluate("MEM.run.drawState"); await pg.screenshot(path=f'/tmp/awsicht_{name}_hilfe.png')
            st['beenden'] = await pg.evaluate(EFF, '#memStop')
            await pg.evaluate("()=>{const v=MEM.rec.v9;v.ch[0].st=2;awStart({k:0,mode:'puls'});const R=MEM.run;for(let i=0;i<45;i++)awTick(R,1/30);awDraw()}"); await pg.wait_for_timeout(100)
            st['puls'] = await pg.evaluate("MEM.run.drawState"); st['zaehlen'] = await pg.evaluate("$('#memMsg').textContent")
            await pg.screenshot(path=f'/tmp/awsicht_{name}_puls.png')
            await pg.evaluate("()=>{awFinish()}"); await pg.wait_for_timeout(100)
            st['weiter'] = await pg.evaluate(EFF, '#memNext'); await pg.screenshot(path=f'/tmp/awsicht_{name}_fertig.png')
            st['fehler'] = errs; res[name] = st; await pg.close()
        await br.close()
    print(json.dumps(res, ensure_ascii=False))
    c = {}
    for name, st in res.items():
        k, kd = st['knopf'], st['knopfDunkel']
        c[f'{name}: Knopf „Weiß nicht weiter“ voll deckend, im Bild, Kontrast ≥ 4,5'] = all(x and x['opacity'] >= 0.99 and x['inView'] and x['contrast'] >= 4.5 and not x['disabled'] for x in (k, kd))
        c[f'{name}: Zustände Anker → dunkel → Hilfe → Puls'] = (st['anker'], st['dunkel'], st['hilfe'], st['puls']) == ('anker', 'dunkel', 'hilfe', 'dunkel') and 'Einzählen' in st['zaehlen']
        c[f'{name}: Beenden und Weiter erreichbar'] = st['beenden']['opacity'] >= 0.99 and st['weiter']['inView'] and st['weiter']['opacity'] >= 0.99
        c[f'{name}: keine Fehler'] = not st['fehler']
    print(c); print('Bilder: /tmp/awsicht_*.png'); print('OK' if all(c.values()) else 'FEHLER')

asyncio.run(main())
