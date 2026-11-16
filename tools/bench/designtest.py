"""v5.21 Design C2: Zustände und Kontrast.
Prüft: erster Start ohne Songs (Einladung + Hinzufügen-Sheet), offline → „Kein Internet“ statt Umwandlung, Klavier-Fenster, Umwandlung läuft, Umwandlung fehlgeschlagen,
3 Tabs (Heute · Songs · Ich), Werkstatt nur im Entwicklermodus, und dass jeder sichtbare Text auf Heute/Songs/Ich/Song-Seite/Lernweg/Player mind. 4,5:1 Kontrast hat (große Schrift 3:1).
usage: python3 tools/bench/designtest.py $PWD/web/index.html"""
import asyncio,sys,json
from playwright.async_api import async_playwright
CONTRAST=r"""()=>{
 const lum=c=>{const m=c.match(/[\d.]+/g).map(Number);const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return [.2126*f(m[0])+.7152*f(m[1])+.0722*f(m[2]),m[3]==null?1:m[3]]};
 const mix=(fg,bg,a)=>fg.map((v,i)=>v*a+bg[i]*(1-a));
 const rgb=c=>c.match(/[\d.]+/g).map(Number);
 const bgOf=el=>{let stack=[];for(let e=el;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;const v=rgb(c);if(v[3]===undefined||v[3]>0){stack.push(v);if(v[3]===undefined||v[3]>=1)break}}
   let b=[11,13,18];for(let i=stack.length-1;i>=0;i--){const v=stack[i];b=v[3]===undefined?v.slice(0,3):mix(v.slice(0,3),b,v[3])}return b};
 const L=v=>{const f=x=>{x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4)};return .2126*f(v[0])+.7152*f(v[1])+.0722*f(v[2])};
 const res=[];for(const el of document.querySelectorAll('body *')){if(!el.childNodes.length)continue;const txt=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).join('');if(!txt)continue;
  const r=el.getBoundingClientRect();if(r.width<1||r.height<1||r.bottom<0||r.top>innerHeight)continue;const cs=getComputedStyle(el);if(cs.visibility==='hidden'||+cs.opacity<0.6)continue;
  let o=1;for(let e=el;e;e=e.parentElement){o*=+getComputedStyle(e).opacity}if(o<0.6)continue;
  const fgc=rgb(cs.color),b=bgOf(el),fg=fgc[3]===undefined?fgc.slice(0,3):mix(fgc.slice(0,3),b,fgc[3]);const l1=L(fg),l2=L(b),cr=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
  const big=parseFloat(cs.fontSize)>=18.66||(parseFloat(cs.fontSize)>=14&&+cs.fontWeight>=700);res.push([+cr.toFixed(2),big,txt.slice(0,40),cs.fontSize])}
 return res.filter(x=>x[0]<(x[1]?3:4.5)).sort((a,b)=>a[0]-b[0]).slice(0,15)}"""
SEED=r"""()=>{localStorage.clear();localStorage.setItem('kt_onb','1');
 const mk=(n,o)=>{const ns=[];let t=0;for(let i=0;i<n;i++){ns.push({m:60+(i*3+o)%14,start:t,dur:.4,hand:i%3?'R':'L'});t+=.45}return ns};
 LIB=[{id:'a',type:'midi',title:'Für Elise',artist:'Beethoven',data:b64FromBuf(writeMidi(mk(80,0)))},{id:'b',type:'midi',title:'River Flows in You',artist:'Yiruma',data:b64FromBuf(writeMidi(mk(60,2)))}];save('kt_lib',LIB);
 openMem(LIB[0]);const ch=MEM.rec.v9.ch;ch[0].box=2;ch[0].due=Date.now()+9e8;memSaveAll();navStack.length=0;navStack.push('home');show('home');setTab('start');ST.last={id:'a'};renderHome();return 1}"""
async def main():
  async with async_playwright() as p:
    br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=await br.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));r={};low=[]
    await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(1500)
    await pg.evaluate("localStorage.clear();localStorage.setItem('kt_onb','1');LIB=[];save('kt_lib',LIB);devSync();navStack.length=0;navStack.push('home');show('home');setTab('start');ST.last=null;renderHome()")
    r['leer']=await pg.inner_text('#contWrap .stTtl');low+=await pg.evaluate(CONTRAST)
    await pg.click('#contBtn');await pg.wait_for_timeout(300);r['sheet']=await pg.evaluate("$('#addSheet').classList.contains('on')");await pg.evaluate("closeSheets()")
    await pg.context.set_offline(True);await pg.evaluate("openSheet('#addSheet');$('#ytUrl').value='https://youtu.be/dQw4w9WgXcQ';$('#ytAdd').click()");await pg.wait_for_timeout(200)
    r['offline']=[await pg.inner_text('#convErrTtl'),await pg.evaluate("$('#yt').classList.contains('hidden')")];await pg.click('#convErrOk');await pg.context.set_offline(False)
    await pg.evaluate("NAT.ok=true;window.nat=()=>{};kbOpen()");await pg.wait_for_timeout(200);r['kb']=await pg.evaluate("$('#kbSheet').classList.contains('on')");low+=await pg.evaluate(CONTRAST);await pg.evaluate("closeSheets()")
    await pg.evaluate("navStack.push('yt');show('yt');convUI(true);convProgress(42,'Noten werden gelesen …','Song wird erstellt: X')");await pg.wait_for_timeout(200)
    r['conv']=await pg.inner_text('#convPct');low+=await pg.evaluate(CONTRAST)
    await pg.evaluate("convUI(false);showConvError('kaputt')");r['err']=await pg.evaluate("$('#convErr').classList.contains('on')");await pg.evaluate("$('#convErrOk').click();navStack.length=0;navStack.push('home');show('home')")
    await pg.evaluate(SEED);await pg.wait_for_timeout(300)
    r['tabs']=await pg.evaluate("[...$$('.tabbar button')].map(b=>b.textContent.trim())")
    for js in ["setTab('start')","setTab('songs')","setTab('stats')","setTab('start');openSongPage(LIB[0])","openMem(LIB[0])","back();playAs(LIB[0],'learn')"]:
      await pg.evaluate(js);await pg.wait_for_timeout(300);low+=await pg.evaluate(CONTRAST)
    await pg.evaluate("navStack.length=0;navStack.push('home');show('home');setTab('stats')");r['werk']=await pg.evaluate("getComputedStyle($('#werk')).display")
    r['modal']=await pg.evaluate("$('#modeModal').classList.contains('on')")
    await br.close()
  print(json.dumps(r,ensure_ascii=False),low[:5],errs)
  c={'erster Start: Einladung „Dein erster Song“':r['leer']=='Dein erster Song','Knopf öffnet Hinzufügen':r['sheet'],
     'offline: „Kein Internet“, keine Umwandlung':r['offline']==['Kein Internet',True],'Klavier-Fenster':r['kb'],'Umwandlung läuft':r['conv']=='42 %','Umwandlung fehlgeschlagen':r['err'],
     'Tabs Heute · Songs · Ich':r['tabs']==['Heute','Songs','Ich'],'Werkstatt aus ohne Schlüssel':r['werk']=='none','Frei üben ohne Zwischenfrage':r['modal'] is False,
     'Kontrast ≥ 4,5:1 (groß ≥ 3:1)':not low,'keine Fehler':not errs}
  for k,v in c.items():
    if not v:print('  NICHT OK:',k)
  print('OK' if all(c.values()) else 'FEHLER')
asyncio.run(main())
