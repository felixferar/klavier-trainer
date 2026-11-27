"""v4.33 Live-Modus: aus = kein Abruf; neue cmd.txt = Befehle ausgefuehrt (tab/menue/klick), Ergebnis + Bildschirmbericht geschrieben; gleiche Datei nicht nochmal; Kommentarzeilen ignoriert; unbekannter Befehl/Knopf harmlos."""
import sys,asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(500); await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(2500)
        r=await pg.evaluate("""async()=>{const o={};let calls=0,puts={},file=null;
          save('kt_ghtok','github_pat_test');ghRepo.v='x/klavier-diagnose';NAT.ok=true;
          LIB.push({id:'t1',type:'yt',title:'Testsong Alpha',fromYT:'zzz',notes:[]});setTab('songs');
          window.fetch=async(url,opt)=>{if(opt&&opt.method==='PUT'){const b=JSON.parse(opt.body);puts[url.split('contents/')[1]]=decodeURIComponent(escape(atob(b.content)));return {ok:true,status:200,json:async()=>({})}}
            calls++;if(url.endsWith('queue/cmd.txt')){if(!file)return {ok:false,status:404,json:async()=>({})};return {ok:true,status:200,json:async()=>file}}
            return {ok:true,status:200,json:async()=>({sha:'s'})}};
          const mk=(txt,sha)=>({sha,content:btoa(unescape(encodeURIComponent(txt)))});
          await lvExec('klick Überspringen');await new Promise(z=>setTimeout(z,400));setTab('songs');o.vorher=lvSnap().split(String.fromCharCode(10)).pop();S.remoteQ=false;file=mk('tab start','a1');await lvTick();o.aus=calls;
          S.remoteQ=true;LV.chk=0;await lvTick();o.tabStart=tab;
          LV.chk=0;file=mk('# Kommentar\\ntab songs\\nmenue testsong\\nklick umbenennen-gibts-nicht\\nblabla','a2');await lvTick();
          o.menueOffen=!!document.querySelector('#songMenu.on');o.result=puts['queue/cmd-result.txt'];o.screen=(puts['queue/screen.txt']||'').split('\\n').slice(0,6).join(' // ');
          const n=Object.keys(puts).length;LV.chk=0;await lvTick();o.gleicheDateiNeuePuts=Object.keys(puts).length-n;
          LV.chk=0;file=mk('klick Löschen','a3');await lvTick();o.loeschenFrage=document.querySelector('#smDel').textContent;
          LV.chk=0;file=mk('klick Wirklich','a4');await lvTick();o.songNoch=LIB.some(x=>x.id==='t1');
          return o}""")
        globals().__setitem__('_R',r);print(json.dumps(r,ensure_ascii=False,indent=1)); globals().__setitem__('_E',errs);print('pageerrors',errs); await br.close()
asyncio.run(main())
# _URTEIL (27.11.2026): Dieser Test gab bisher nur Werte aus und urteilte nicht. Die Sollwerte stammen aus dem Kopfkommentar bzw. der Testbeschreibung.
r=_R;_c={'aus: kein Abruf':r['aus']==0,'Befehle ausgeführt (Tab, Menü)':'ok tab songs' in r['result'] and 'ok menue testsong' in r['result'] and r['menueOffen'],'unbekannter Knopf und Befehl sind harmlos':'kein Knopf umbenennen-gibts-nicht' in r['result'] and 'unbekannt: blabla' in r['result'],'Bildschirmbericht geschrieben':'Tab: songs' in r['screen'] and 'OFFEN songMenu' in r['screen'],'gleiche Datei nicht nochmal':r['gleicheDateiNeuePuts']==0,'Löschen fragt nach':r['loeschenFrage']=='Wirklich löschen?'}
if '_E' in globals(): _c['keine JS-Fehler']=not _E
for _k,_v in _c.items(): print(('OK   ' if _v else 'FEHL ')+_k)
sys.exit(0 if all(_c.values()) else 1)
