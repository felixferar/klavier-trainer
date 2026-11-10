# v4.16 Kandidat: Warteschlange überspringt schon umgewandelte Videos (Testkopie, nicht veröffentlicht)

Basis: v4.15 (3fe8d09). Testkopie `/tmp/bench/Qs.html`, Test `tools/bench/queuetest.py`. Nutzer hat am 10.11. 10:28 „Ja“ gesagt.

## Test (Playwright, openYT durch Attrappe ersetzt)
Liste: A (schon in der Bibliothek), B, B (doppelt), C.
| | v4.15 | Fix |
|---|---|---|
| geöffnet | A, B, B, C (4) | B, C (2) |
| Meldung | „4 von 4 Songs erstellt.“ | „2 von 2 Songs erstellt. 2 schon vorhanden, übersprungen.“ |
| nur A | A nochmal umgewandelt | nichts gestartet, Hinweis „Alle 1 Videos sind schon als Song vorhanden“ |
Seitenfehler: keine. Geändert nur `qStart` (Erkennung unberührt).

## Diff
```diff
--- web/index.html	2026-11-10 10:21:58.243113638 +0100
+++ /tmp/bench/Qs.html	2026-11-10 10:28:22.797938188 +0100
@@ -444,7 +444,7 @@
         <div style="display:flex;gap:8px;margin-top:8px"><input class="field" id="ghTok" type="password" placeholder="github_pat_…" autocomplete="off" style="flex:1;min-width:0"><button class="btn sm" id="ghTest">Prüfen</button></div></div></div>
       <div class="li"><div class="grow"><b>YouTube-Umwandlung aufzeichnen</b><small>Speichert nach der nächsten Umwandlung eine Diagnose-Datei. Schick sie an Claude, dann lässt sich die Erkennung mit deinem echten Video verbessern.</small></div><input type="checkbox" class="sw" id="diagChk"></div
     </div>
-    <div class="list" style="margin-top:18px"><div class="li"><div class="grow"><b>App aktualisieren</b><small id="verTxt">Version 4.15</small></div><button class="btn sm" id="reloadBtn">Neu laden</button></div>
+    <div class="list" style="margin-top:18px"><div class="li"><div class="grow"><b>App aktualisieren</b><small id="verTxt">Version 4.16</small></div><button class="btn sm" id="reloadBtn">Neu laden</button></div>
       <div class="li hidden" id="oldApp"><div class="grow"><b>Neue App-Version installieren</b><small>Behebt verlorene Daten beim Start ohne Internet. Deine Daten werden übernommen.</small></div><a class="btn sm pri" style="text-decoration:none" href="https://github.com/felixferar/klavier-trainer/
   </div>
 </div>
@@ -977,6 +977,10 @@
   toast('Warteschlange wird vorbereitet …',2500);const list=[];let plBad=0;
   for(const r of raw){if(r.id)list.push(r);else{const ids=await ytPlaylistIds(r.list);if(!ids.length)plBad++;for(const id of ids.slice(0,50))list.push({id,start:0})}}
   if(!list.length){showConvError('Die Playlist konnte nicht gelesen werden. Ist sie öffentlich oder „nicht gelistet“? Sonst füge die Video-Links einzeln ein.','Warteschlange');return}
+  // videos that already exist as a finished song (or appear twice in the list) are skipped, so a restart after a crash does not create duplicates
+  const have=new Set(LIB.map(x=>x.fromYT).filter(Boolean));let skipped=0;
+  for(let i=list.length-1;i>=0;i--){if(have.has(list[i].id)||list.findIndex(o=>o.id===list[i].id)<i){list.splice(i,1);skipped++}}
+  if(!list.length){showConvError(`Alle ${skipped} Videos sind schon als Song vorhanden – nichts zu tun. (Zum Wiederholen den Song löschen.)`,'Warteschlange');return}
   save('kt_lastq',txt);closeSheets();Q.on=true;Q.cancel=false;Q.n=list.length;const ok=[],bad=[],back=navStack.length;
   for(Q.i=0;Q.i<list.length&&!Q.cancel;Q.i++){
     const it={id:'y'+Date.now()+Q.i,type:'yt',title:'YouTube-Video',videoId:list[Q.i].id,start:list[Q.i].start||0};
@@ -986,7 +990,7 @@
       ytAuto=false;if(SCAN.on){SCAN.on=false;clearInterval(SCAN.timer);try{nat('scanStop')}catch(e){}}try{fileAbort()}catch(e){}convUI(false);if(ytp){try{ytp.destroy()}catch(e){}ytp=null}clearInterval(ytTimer);while(navStack.length>back)navStack.pop()}
     await sleep(800)}
   Q.on=false;const left=list.length-ok.length-bad.length;while(navStack.length>back)navStack.pop();show(navStack[navStack.length-1]||'home');renderHome();
-  showConvError(`${ok.length} von ${list.length} Songs erstellt.`+(left>0?` ${left} nicht mehr gestartet (abgebrochen).`:'')+(plBad?` ${plBad} Playlist nicht lesbar.`:'')+(bad.length?'\n\nNicht geklappt:\n'+bad.join('\n'):''),'Warteschlange fertig')}
+  showConvError(`${ok.length} von ${list.length} Songs erstellt.`+(skipped?` ${skipped} schon vorhanden, übersprungen.`:'')+(left>0?` ${left} nicht mehr gestartet (abgebrochen).`:'')+(plBad?` ${plBad} Playlist nicht lesbar.`:'')+(bad.length?'\n\nNicht geklappt:\n'+bad.join('\n'):''),'Warteschlange
 $('#ytMulti').value=load('kt_lastq')||'';
 $('#ytMultiBtn').onclick=()=>$('#ytMultiBox').classList.toggle('hidden');
 $('#ytMultiGo').onclick=()=>qStart($('#ytMulti').value);
@@ -1805,7 +1809,7 @@
 const OLD_APP=!NAT.ok&&/KlavierTrainerApp\//.test(navigator.userAgent);
 if(NAT.ok)setTimeout(()=>{nat('kbAuto');kbUI()},300); // reconnect the last keyboard silently
 function updVer(){const src=NAT.info&&NAT.info.source,h=location.host;
-  $('#verTxt').textContent='Version 4.15 · '+(src==='online'?'online (Updates automatisch)':src==='cache'?'offline – zuletzt geladene Version':src==='offline'?'offline – eingebaute Version':h.endsWith('github.io')?'online (Updates automatisch)':h.startsWith('appassets')?'offline-Version':'Vors
+  $('#verTxt').textContent='Version 4.16 · '+(src==='online'?'online (Updates automatisch)':src==='cache'?'offline – zuletzt geladene Version':src==='offline'?'offline – eingebaute Version':h.endsWith('github.io')?'online (Updates automatisch)':h.startsWith('appassets')?'offline-Version':'Vors
   $('#oldApp').classList.toggle('hidden',!OLD_APP)}
 updVer();
 if(OLD_APP&&load('kt_oldhint')!==dayKey()){save('kt_oldhint',dayKey());setTimeout(()=>toast('Neue App-Version verfügbar – siehe Einstellungen',4500),1500)}
```
