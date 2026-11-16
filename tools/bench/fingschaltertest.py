"""v5.24 Fingersatz-Schalter: Standard aus; in den Einstellungen umschaltbar: Ich › Fingersatz und Player-Zahnrad › Üben (kein Knopf im Lernen),
gespeichert und überall gleich (Ich › Fingersatz). Im Lernen werden die Zahlen beim nächsten Durchgang berechnet.
usage: python3 tools/bench/fingschaltertest.py $PWD/web/index.html [BILDORDNER]"""
import asyncio,sys,json,os
from playwright.async_api import async_playwright
SEED=r"""()=>{localStorage.clear();localStorage.setItem('kt_onb','1');
 const mk=(n,o)=>{const ns=[];let t=0;for(let i=0;i<n;i++){ns.push({m:60+(i*3+o)%14,start:t,dur:.4,hand:i%3?'R':'L'});t+=.45}return ns};
 LIB=[{id:'a',type:'midi',title:'Für Elise',artist:'Beethoven',data:b64FromBuf(writeMidi(mk(80,0)))}];save('kt_lib',LIB);
 S.fingers=false;saveS();navStack.length=0;navStack.push('home');show('home');setTab('start');renderHome();return 1}"""
VIS="s=>{const e=$(s);if(!e)return false;const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'}"
async def main():
  shots=sys.argv[2] if len(sys.argv)>2 else None
  async with async_playwright() as p:
    br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']);r={};errs=[]
    for name,vp in (('hoch',{'width':390,'height':844}),('quer',{'width':844,'height':390})):
      pg=await br.new_page(viewport=vp);pg.on('pageerror',lambda e:errs.append(str(e)))
      await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(1500);await pg.evaluate(SEED);await pg.wait_for_timeout(200)
      o={'standardAus':await pg.evaluate("S.fingers!==true")}
      # Player: Zahnrad › Üben › Fingersatz
      await pg.evaluate("playAs(LIB[0],'learn')");await pg.wait_for_timeout(400);await pg.click('#pSet');await pg.wait_for_timeout(400)
      o['playerSichtbar']=await pg.evaluate("("+VIS+")('#fingChk')")
      if shots:await pg.screenshot(path=os.path.join(shots,f'player-{name}.png'))
      await pg.evaluate("$('#fingChk').click()");await pg.wait_for_timeout(100)
      o['playerAn']=await pg.evaluate("S.fingers===true&&JSON.parse(localStorage.getItem('kt_settings')).fingers===true")
      await pg.evaluate("$('#fingChk').click()");o['playerAus']=await pg.evaluate("S.fingers===false&&JSON.parse(localStorage.getItem('kt_settings')).fingers===false")
      await pg.evaluate("closeSheets();navStack.length=0;navStack.push('home');show('home')")
      # Lernen: kein eigener Knopf; Einschalten unter Ich › Fingersatz wirkt beim nächsten Durchgang
      await pg.evaluate("openMem(LIB[0])");await pg.wait_for_timeout(300);await pg.evaluate("$('#memGo').click()");await pg.wait_for_timeout(600)
      o['keinKnopf']=await pg.evaluate("!$('#memFing')");o['vorherOhneZahlen']=await pg.evaluate("!MEM.song.notes.some(n=>n.fing)")
      o['stopSichtbar']=await pg.evaluate("("+VIS+")('#memStop')")
      await pg.evaluate("memStop();$('#fing2').checked=true;$('#fing2').dispatchEvent(new Event('change'))")
      await pg.evaluate("$('#memGo').click()");await pg.wait_for_timeout(600)
      o['zahlenBerechnet']=await pg.evaluate("MEM.song.notes.filter(n=>n.fing).length/MEM.song.notes.length")
      if shots:await pg.screenshot(path=os.path.join(shots,f'lernen-{name}.png'))
      o['playerGleich']=await pg.evaluate("syncUI(),$('#fingChk').checked===true")
      await pg.evaluate("memStop();back()");r[name]=o;await pg.close()
    await br.close()
  print(json.dumps(r,ensure_ascii=False),errs)
  c={}
  for n,o in r.items():
    c.update({f'{n}: Standard aus':o['standardAus'],f'{n}: Schalter im Player sichtbar':o['playerSichtbar'],f'{n}: Player an + gespeichert':o['playerAn'],f'{n}: Player aus':o['playerAus'],
      f'{n}: kein Knopf im Lernen':o['keinKnopf'],f'{n}: vorher keine Zahlen':o['vorherOhneZahlen'],f'{n}: Beenden sichtbar':o['stopSichtbar'],
      f'{n}: nach Ich › an Zahlen im Lernen':o['zahlenBerechnet']>0.9,f'{n}: Player-Schalter gleich':o['playerGleich']})
  c['keine Fehler']=not errs
  for k,v in c.items():
    if not v:print('  NICHT OK:',k)
  print('OK' if all(c.values()) else 'FEHLER');sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
