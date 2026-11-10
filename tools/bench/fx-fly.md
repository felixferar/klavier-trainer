# v4.17 Kandidat: Fly-Fixes (Phantom-E am Anfang, tiefes Cis-Paar am Ende) – Testkopie, nicht veröffentlicht

Basis v4.15. Testkopie `/tmp/bench/Gw.html`. (v4.16 = Warteschlange, wartet auf Reviewer; dieser Kandidat enthält sie NICHT.)

## Ursachen (Messung an der Handy-Aufnahme von v4.15)
1. Phantom-E: zwei frühe Balken (E4 bei −1,63 s / −1,29 s, Länge 0,15/0,16 s) wurden in nur 2 von 14 Standbildern gesehen (n=2). Mit 16 Standbildern (v4.10) reicht „n≥2“ nicht mehr. Fix: nötig n ≥ max(2, aufrunden(Standbilder/5)); gilt nicht, wenn der Balken ≥ 0,2 s lang ist (R1cu: echtes E4, n=2, 0,29 s, bleibt).
2. Fehlende Bassnoten: v4.15 löschte alle Tasten > 8 s ohne Balken. Bei Fly sind Cis1/Cis2 (244,7–257,2 s) laut Nutzer echt gehaltene Noten. Unterscheidung zu Einblendungen: Let It Go hat 8 solcher Tasten gleichzeitig (Endbildschirm, ch 0,8–0,9), Canon hat fast farblose Tasten (ch 0,05). Fix: nur löschen, wenn ≥ 3 davon gleichzeitig (±0,3 s) beginnen ODER Taste fast farblos (ch < 0,15).

## Ergebnis
| Test | Ergebnis |
|---|---|
| Fly (Handy v4.15, nachgespielt) | erste Note C#4 bei 1 s (kein E davor), Cis1+Cis2 12,4 s bleiben |
| Let It Go | 574 (wie v4.15, 8 Endbildschirm-Noten weg) |
| Canon | 591 (wie v4.15) |
| 29 Handy-Aufnahmen | gleich wie v4.13 außer Let It Go −8, Canon −3 (= v4.15), R1cu bleibt 643 |
| Prüfstand 24 Videos | 0,992 / 0,952 / 52 Zusatznoten (v4.15: 0,992 / 0,951 / 53) |

Hinweis: Die Schwellen (n/5, 0,2 s, ≥3 gleichzeitig, ch 0,15) sind an wenigen Fällen eingestellt (Fly, R1cu, Let It Go, Canon). Variante n≥3 ab 8 Standbildern kostete im Prüfstand Treffer (0,987) und wurde verworfen. Bestätigung am Handy für Fly, Let It Go, Canon nötig.

## Diff
```diff
--- web/index.html	2026-11-10 10:21:58.243113638 +0100
+++ /tmp/bench/Gw.html	2026-11-10 11:21:15.883056107 +0100
@@ -444,7 +444,7 @@
         <div style="display:flex;gap:8px;margin-top:8px"><input class="field" id="ghTok" type="password" placeholder="github_pat_…" autocomplete="off" style="flex:1;min-width:0"><button class="btn sm" id="ghTest">Prüfen</button></div></div></div>
       <div class="li"><div class="grow"><b>YouTube-Umwandlung aufzeichnen</b><small>Speichert nach der nächsten Umwandlung eine Diagnose-Datei. Schick sie an Claude, dann lässt sich die Erkennung mit deinem echten Video verbessern.</small></div><input type="checkbox" class="sw" id="diagChk"></div>
     </div>
-    <div class="list" style="margin-top:18px"><div class="li"><div class="grow"><b>App aktualisieren</b><small id="verTxt">Version 4.15</small></div><button class="btn sm" id="reloadBtn">Neu laden</button></div>
+    <div class="list" style="margin-top:18px"><div class="li"><div class="grow"><b>App aktualisieren</b><small id="verTxt">Version 4.17</small></div><button class="btn sm" id="reloadBtn">Neu laden</button></div>
       <div class="li hidden" id="oldApp"><div class="grow"><b>Neue App-Version installieren</b><small>Behebt verlorene Daten beim Start ohne Internet. Deine Daten werden übernommen.</small></div><a class="btn sm pri" style="text-decoration:none" href="https://github.com/felixferar/klavier-trainer/releases/download/app/KlavierT
   </div>
 </div>
@@ -1805,7 +1805,7 @@
 const OLD_APP=!NAT.ok&&/KlavierTrainerApp\//.test(navigator.userAgent);
 if(NAT.ok)setTimeout(()=>{nat('kbAuto');kbUI()},300); // reconnect the last keyboard silently
 function updVer(){const src=NAT.info&&NAT.info.source,h=location.host;
-  $('#verTxt').textContent='Version 4.15 · '+(src==='online'?'online (Updates automatisch)':src==='cache'?'offline – zuletzt geladene Version':src==='offline'?'offline – eingebaute Version':h.endsWith('github.io')?'online (Updates automatisch)':h.startsWith('appassets')?'offline-Version':'Vorschau');
+  $('#verTxt').textContent='Version 4.17 · '+(src==='online'?'online (Updates automatisch)':src==='cache'?'offline – zuletzt geladene Version':src==='offline'?'offline – eingebaute Version':h.endsWith('github.io')?'online (Updates automatisch)':h.startsWith('appassets')?'offline-Version':'Vorschau');
   $('#oldApp').classList.toggle('hidden',!OLD_APP)}
 updVer();
 if(OLD_APP&&load('kt_oldhint')!==dayKey()){save('kt_oldhint',dayKey());setTimeout(()=>toast('Neue App-Version verfügbar – siehe Einstellungen',4500),1500)}
@@ -2083,7 +2083,7 @@
   found.sort((a,b)=>a.m-b.m||a.start-b.start);const notes=[];
   for(const f of found){const g=notes.find(n=>n.m===f.m&&Math.abs(n.start-f.start)<0.15);if(g){g.n++;g.ss+=f.start;g.ee+=f.end;g.start=g.ss/g.n;g.end=g.ee/g.n;g.cf=Math.max(g.cf,f.cf)}else notes.push({...f,n:1,ss:f.start,ee:f.end})}
   const hv=ev.filter(e=>e.hue!=null).map(e=>e.hue); // a bar whose colour is none of the song's colours is no note (white player icon / title letters in the only still that shows the keyboard)
-  const early=notes.filter(n=>n.start+SCAN.start<readFrom-0.04&&(fr.length<2?n.cf>=0.3:n.n>=2)&&(hv.length<4||n.hue==null||hv.some(h=>hueDist(h,n.hue)<=45))); // a real bar falls and shows up in several stills at a consistent time – a static title/sparkle does notif(!early.length)return ev;
+  const early=notes.filter(n=>n.start+SCAN.start<readFrom-0.04&&(fr.length<2?n.cf>=0.3:(n.n>=Math.max(2,Math.ceil(fr.length/5))||(n.n>=2&&n.end-n.start>=0.2)))&&(hv.length<4||n.hue==null||hv.some(h=>hueDist(h,n.hue)<=45))); // a real bar falls and shows up in several stills at a consistent time – a static title/sparkle does n
   const out=ev.slice();
   for(const n of early){const same=out.find(e=>e.m===n.m&&e.start<=readFrom-SCAN.start+0.1&&e.end>=n.start-0.1&&e.start>=n.start-0.15); // the key was still lit when reading began → correct its start
     if(same){same.start=n.start;if(n.hue!=null&&same.hue==null)same.hue=n.hue}
@@ -2135,7 +2135,8 @@
       const full=(e,f)=>e.ch>0&&f.ch>0&&e.ch>=0.7*f.ch&&chRef[isWhitePC(e.m%12)?0:1]!=null&&e.ch>=0.7*chRef[isWhitePC(e.m%12)?0:1];
       ev=ev.filter(e=>e.bar||!ev.some(f=>f!==e&&f.bar&&Math.abs(f.m-e.m)<=2&&Math.abs(f.start-e.start)<0.15&&!full(e,f))&&e.end-e.start>=0.1);
       // a long lit key without any falling bar (> 8 s) is an overlay / end screen / lit-up logo, not a note (measured: no bar-less note > 4.2 s in 20 recordings)
-      ev=ev.filter(e=>e.bar||e.end-e.start<=8)}}
+      // overlay / end screen: ≥3 such keys lit at the same moment (a screen lighting up many keys) or a key that is almost colourless (dark tint); one or two held bass notes whose bar was missed stay
+      {const lg=ev.filter(e=>!e.bar&&e.end-e.start>8);ev=ev.filter(e=>!(lg.includes(e)&&(lg.filter(o=>Math.abs(o.start-e.start)<0.3).length>=3||!(e.ch>=0.15))))}}}
   // length from the bar: the bar is exactly as long as the note; the key itself can look lit a bit longer (glow of a neighbour)
   if(SCAN.lane&&SCAN.barDelay!=null){const kIdx=new Map(SCAN.keys.map((k,i)=>[k.m,i])),d=SCAN.barDelay;
     for(const e of ev){const ln=SCAN.lane[kIdx.get(e.m)];let bi=-1,bd=0.12;for(let i=0;i<ln.ons.length;i++){const de=SCAN.dK&&SCAN.dK[SCAN.keys[kIdx.get(e.m)].black?1:0],x=Math.abs(ln.ons[i]+(de!=null?de:d)-e.start);if(x<bd){bd=x;bi=i}}
```
