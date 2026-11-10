"""v4.43 Etappe 2: Noten in der Vergleichsansicht bearbeiten (antippen, loeschen, Ton, Laenge, hinzufuegen, rueckgaengig, speichern als neuer Song)"""
import sys,os,json,asyncio
from playwright.async_api import async_playwright
H=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures')
meta=json.load(open(os.path.join(H,'embers_v434_meta.json')));keys=meta['keys'];rows=meta['scanRows'];lo=keys[0]['m']
geo={'x':[keys[0]['x'],keys[-1]['x']],'kw':meta['kw'],'yT':rows['yT'],'yA':rows['yA'],'yB':rows['yB'],'yC':rows['yC'],'sh':0,'kx':[round(k['x'],4) for k in keys],'ar':meta.get('ar',1280/544)}
JS="""async([geo,lo])=>{const o={};
 const mk=(id)=>({id,type:'midi',title:'Test',artist:'x',data:b64FromBuf(writeMidi([{m:60,start:1,dur:2,hand:'R'},{m:64,start:5,dur:1,hand:'R'}])),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:2,first:3,fps:25,keys:[lo,lo+geo.kx.length-1],geo}});
 const a=mk('a');LIB=[a];const origData=a.data;
 window.openYT=(it,auto,cmp)=>{cmpMode(!!CMP);show('yt')};
 let vt=0;ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(t){vt=t},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2,destroy(){}};
 const wait=ms=>new Promise(z=>setTimeout(z,ms));
 openCompare(a);vt=1+2+0.5;await wait(300);cmpDraw();
 const H1=CMP.hit,xcol=m=>H1.P.X(geo.kx[m-lo]);
 o.hit=!!H1;o.editHidden0=$('#cmpEdit').classList.contains('hidden');o.saveHidden0=$('#cmpSave').classList.contains('hidden');
 ceTap(xcol(60),H1.rh-0.3*H1.pps);o.sel60=CMP.sel&&CMP.sel.midi===60;o.editShown=!$('#cmpEdit').classList.contains('hidden');
 $('#ceUp').click();o.up=CMP.sel.midi;$('#ceLong').click();o.long=CMP.sel.dur;$('#ceShort').click();$('#ceShort').click();o.short=CMP.sel.dur;
 o.dirty=CMP.dirty;o.saveShown=!$('#cmpSave').classList.contains('hidden');
 $('#ceUndo').click();o.undo1=CMP.notes.find(n=>n.start===1).dur; // Rueckgaengig: eine Aenderung (Kuerzer) zurueck
 $('#ceUndo').click();$('#ceUndo').click();$('#ceUndo').click();o.undoAll={m:CMP.notes[0].midi,d:CMP.notes[0].dur,dirty:CMP.dirty,n:CMP.notes.length};
 // Tonbereich-Grenze
 CMP.notes[0].midi=lo;CMP.sel=CMP.notes[0];$('#ceDn').click();o.lowLimit=CMP.notes[0].midi===lo&&!CMP.dirty;CMP.notes[0].midi=60;CMP.sel=null;
 // loeschen
 ceTap(xcol(60),H1.rh-0.3*H1.pps);$('#ceDel').click();o.del={n:CMP.notes.length,sel:CMP.sel,moments:CMP.moments.slice()};
 // hinzufuegen: Taste ohne klingende Note antippen
 vt=1+2+0.5;cmpDraw();ceTap(xcol(67),CMP.hit.rh+10);o.add={n:CMP.notes.length,sel:CMP.sel&&CMP.sel.midi,dur:CMP.sel&&CMP.sel.dur,start:CMP.sel&&CMP.sel.start};
 // speichern
 o.saveOK=ceSave();const nl=LIB.length;o.lib={n:nl,first:LIB[0].title,edited:LIB[0].edited,origTitle:LIB[1]&&LIB[1].title,origUnchanged:LIB[1]&&LIB[1].data===origData,origNoEdited:!(LIB[1]&&LIB[1].edited)};
 const s=songFromMidi(bufFromB64(LIB[0].data),'x');o.saved=s.notes.map(n=>[n.midi,Math.round(n.start*100)/100,Math.round(n.dur*100)/100]).sort();
 o.videoKept=JSON.stringify(LIB[0].video)===JSON.stringify(a.video)&&LIB[0].fromYT==='abcdefghijk';
 // zweite Aenderung: derselbe bearbeitete Song wird ueberschrieben
 CMP.sel=CMP.notes.find(n=>n.midi===67);$('#ceLong').click();ceSave();o.second={n:LIB.length,dur:songFromMidi(bufFromB64(LIB[0].data),'x').notes.find(n=>n.midi===67).dur};
 // verlassen mit ungespeicherter Aenderung speichert automatisch
 CMP.sel=CMP.notes.find(n=>n.midi===67);$('#ceLong').click();$('#yBack').click();await wait(100);
 o.leave={cmpNull:CMP===null,dur:Math.round(songFromMidi(bufFromB64(LIB[0].data),'x').notes.find(n=>n.midi===67).dur*100)/100,n:LIB.length};
 return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':420,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS,[geo,lo]);print(json.dumps(r,ensure_ascii=False));print('pageerrors',errs)
        c=[r['hit'],r['editHidden0'],r['saveHidden0'],r['sel60'],r['editShown'],r['up']==61,abs(r['long']-2.1)<1e-6,abs(r['short']-1.9)<1e-6,r['dirty'],r['saveShown'],
           abs(r['undo1']-2.0)<1e-6 or abs(r['undo1']-2.1)<1e-6,r['undoAll']=={'m':60,'d':2,'dirty':False,'n':2},r['lowLimit'],
           r['del']['n']==1 and r['del']['sel'] is None and r['del']['moments']==[5],
           r['add']['n']==2 and r['add']['sel']==67 and r['add']['dur']==0.5 and abs(r['add']['start']-1.5)<0.05,
           r['saveOK'],r['lib']['n']==2,r['lib']['first']=='Test (bearbeitet)',r['lib']['edited'],r['lib']['origTitle']=='Test',r['lib']['origUnchanged'],r['lib']['origNoEdited'],
           sorted(x[0] for x in r['saved'])==[64,67],r['videoKept'],r['second']['n']==2,abs(r['second']['dur']-0.6)<0.02,r['leave']['cmpNull'],abs(r['leave']['dur']-0.7)<0.02,r['leave']['n']==2,not errs]
        print(c);ok=all(c);print('ERGEBNIS','OK' if ok else 'FEHLER');sys.exit(0 if ok else 1)
asyncio.run(main())
