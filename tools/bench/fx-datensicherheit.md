# Datensicherheits-Fixes (Testkopie, nicht veröffentlicht) – Stand 10.11.2026

Basis: Web v4.13 (682837a). Testkopie: `/tmp/bench/Fx.html`, Test: `tools/bench/datentest.py` (lokal, nicht eingecheckt).

## Test vorher/nachher (Playwright, gesetzter Zustand statt echter Umwandlung)
| Test | v4.13 | Fix |
|---|---|---|
| T1 Speicher voll, manuell speichern | Ergebnis weg (SCAN.result=null), kein Song | Meldung „NICHT gespeichert“, Ergebnis bleibt |
| T2 Speicher voll in Warteschlange | meldet ok:true | ok:false, Warteschlange bricht ab |
| T3 Update bei offenem Ergebnis | lädt neu (1×) | lädt nicht neu |
| T3b Update ohne offenes Ergebnis | lädt neu | lädt neu (unverändert) |
| T5 Abbrechen im 500-ms-Fenster | Song wird doch gespeichert | nichts gespeichert |
| T10 normaler Auto-Pfad | 1 Song | 1 Song |

Nachspielen Let It Go (582) und golden hour (286) unverändert. Nicht umgesetzt: Duplikatschutz der Warteschlange (F4, Entscheidung offen), Zeitlimit für native Antwort (F5), Fehlerfang in scanRun (F6).

## Diff
```diff
--- web/index.html	2026-11-09 23:05:13.631039674 +0100
+++ /tmp/bench/Fx.html	2026-11-10 09:59:32.744525738 +0100
@@ -1789,10 +1789,11 @@
 $('#reloadBtn').onclick=()=>location.reload();
 // new version online → load it by itself when the app is opened / comes back to the front (never during a conversion)
 let updBusy=false;function doReload(){location.reload()}
-async function updCheck(){if(updBusy||SCAN.on||Q.on||ytAuto)return;updBusy=true;
+const convBusy=()=>SCAN.on||Q.on||ytAuto||!!SCAN.result; // a finished but not yet saved result also counts as busy
+async function updCheck(){if(updBusy||convBusy())return;updBusy=true;
   try{const r=await fetch(location.pathname+'?chk='+Date.now(),{cache:'no-store'}),t=await r.text(),m=t.match(/id="verTxt">Version ([0-9.]+)/),cur=($('#verTxt').textContent.match(/Version ([0-9.]+)/)||[])[1];
     let tried=null;try{tried=sessionStorage.getItem('kt_updTried')}catch(e){}
-    if(m&&cur&&m[1]!==cur&&tried!==m[1]&&!SCAN.on&&!Q.on&&!ytAuto){try{sessionStorage.setItem('kt_updTried',m[1])}catch(e){}doReload()}}catch(e){}
+    if(m&&cur&&m[1]!==cur&&tried!==m[1]&&!convBusy()){try{sessionStorage.setItem('kt_updTried',m[1])}catch(e){}doReload()}}catch(e){}
   updBusy=false}
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')updCheck()});setTimeout(updCheck,4000);
 
@@ -2236,7 +2237,7 @@
   const L=notes.filter(n=>n.hand==='L').length;
   $('#scDoneTxt').textContent=`${notes.length} Noten erkannt (${notes.length-L} rechts, ${L} links) · ${fmt(Math.max(...notes.map(n=>n.start+n.dur)))} Min`;
   $('#scName').value=(ytItem&&ytItem.title&&ytItem.title!=='YouTube-Video'?ytItem.title:'Song aus Video').slice(0,60);
-  SCAN.result=notes;if(ytAuto){ytAuto=false;convProgress(100,'Fertig');setTimeout(()=>{convUI(false);scanSave(true)},500);return}$('#scanDone').classList.add('on');$('#gDim').classList.add('on');
+  SCAN.result=notes;if(ytAuto){ytAuto=false;convProgress(100,'Fertig');setTimeout(()=>{convUI(false);if(SCAN.result)scanSave(true)},500);return}$('#scanDone').classList.add('on');$('#gDim').classList.add('on');
 }
 function scanSave(auto){
   const notes=SCAN.result;if(!notes)return;const title=(auto?$('#scName').value.trim():$('#scName').value.trim())||'Song aus Video';const ytOld=ytItem;
@@ -2245,8 +2246,15 @@
     video:{v:2,src:SCAN.fromFile?'file':'yt',start:SCAN.start,first:SCAN.firstNote||0,fps:SCAN.lastVt>0?Math.round(SCAN.frames/SCAN.lastVt):null,keys:[SCAN.keys[0].m,SCAN.keys[SCAN.keys.length-1].m]},
     octUnsure:!!(scanDet&&scanDet.octEst),oneColor:!!SCAN.oneColor};
   let s;try{s=songForItem(it,buf)}catch(e){toast('Fehler: '+e.message);return}
+  const libBak=LIB.slice();
   if(ytOld&&!SCAN.fromFile)LIB=LIB.filter(x=>x.id!==ytOld.id); // the video entry is replaced by the finished song
-  LIB.unshift(it);saveLib();if(auto)toast(`Song „${title}“ erstellt – ${notes.length} Noten`,3500);
+  LIB.unshift(it);
+  if(!save('kt_lib',LIB)){ // storage full: NOT saved – never report success (rule: 100 % saved or nothing)
+    LIB=libBak;const msg='Speicher voll – der Song wurde NICHT gespeichert. Lösche alte Songs und starte die Umwandlung neu.';
+    if(Q.on){SCAN.result=null;Q.cancel=true;Q.finish(false,msg);return}
+    toast(msg,6000);if(auto){$('#scanDone').classList.add('on');$('#gDim').classList.add('on')} // result stays, so "Speichern" works again after freeing space
+    return}
+  if(auto)toast(`Song „${title}“ erstellt – ${notes.length} Noten`,3500);
   $('#scanDone').classList.remove('on');$('#gDim').classList.remove('on');SCAN.result=null;if(SCAN.fromFile){fileAbort();keepAwake(false)}
   if(ytp){try{ytp.destroy()}catch(e){}ytp=null}clearInterval(ytTimer);navStack.pop();if(Q.on){Q.finish(true,title+' ('+notes.length+' Noten)');return}openSong(s,it.id);
 }
@@ -2329,7 +2337,7 @@
   r(!!ok)}
 $('#markCv').addEventListener('pointerdown',e=>{markDrag(e);const mv=ev=>markDrag(ev),up=()=>{removeEventListener('pointermove',mv);removeEventListener('pointerup',up)};addEventListener('pointermove',mv);addEventListener('pointerup',up)});
 $('#markYes').onclick=()=>markDone(true);$('#markNo').onclick=()=>markDone(false);
-function convCancelled(){if(Q.on)Q.cancel=true;ytAuto=false;if(SCAN.on){SCAN.on=false;clearInterval(SCAN.timer);nat('scanStop')}try{ytp.pauseVideo();ytp.unMute()}catch(e){}convUI(false);showConvError('Die Umwandlung wurde abgebrochen. Es wurde nichts gespeichert.')}
+function convCancelled(){if(Q.on)Q.cancel=true;ytAuto=false;SCAN.result=null;if(SCAN.on){SCAN.on=false;clearInterval(SCAN.timer);nat('scanStop')}try{ytp.pauseVideo();ytp.unMute()}catch(e){}convUI(false);showConvError('Die Umwandlung wurde abgebrochen. Es wurde nichts gespeichert.')}
 async function resumeVideo(){try{ytp.playVideo()}catch(e){}const t0=performance.now();while(performance.now()-t0<8000){let st=-1;try{st=ytp.getPlayerState()}catch(e){}if(st===1)return;await sleep(150)}}
 // reading runs, but after 15 s the keyboard still never looked normal → ask the user to mark it (video paused, then on from the same spot)
 async function markLate(){if(!SCAN.on||!ytAuto)return;SCAN.on=false;clearInterval(SCAN.timer);nat('scanStop');
```
