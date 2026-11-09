"""Baut eine instrumentierte Kopie von web/index.html für Messungen (ändert nie die echte Datei).
usage: instrument.py OUT.html
Protokolliert je Taste und Bild: [tt, Buntheit, 0, 0, Abstand zur Ruhefarbe, Farbton, gedrückt, Lane-an, Lane-belegt, Hintergrundzähler, sat, val, r, g, b]
und vor dem Geisterfilter SCAN.preGhost sowie bei earlyFromBars SCAN.dbgFound."""
import sys, os
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'web', 'index.html')
s = open(src).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
rep("    const st=SCAN.state[k];\n    if(pressed){", "    {SCAN.flog=SCAN.flog||SCAN.keys.map(()=>[]);const ln0=SCAN.lane[k];SCAN.flog[k].push([tt,sat*val,0,0,dist,h,pressed?1:0,ln0&&ln0.on?1:0,(laneOcc&&laneOcc[k])?1:0,SCAN.laneBgc?SCAN.laneBgc[k]:-1,sat,val,r,g,b])}\n    const st=SCAN.state[k];\n    if(pressed){")
rep("ev=ev.filter(e=>e.bar||!ev.some(", "SCAN.preGhost=ev.slice();ev=ev.filter(e=>e.bar||!ev.some(")
rep("cand.push({yb,m:SCAN.keys[k].m,start:on-SCAN.start", "(SCAN.dbgFound=SCAN.dbgFound||[]).push({t:im.t,m:SCAN.keys[k].m,ya:ya,yb:yb,h:circMean(hs),sp:Math.max(...hs.map(q=>hueDist(q,circMean(hs)))),x:k});cand.push({yb,m:SCAN.keys[k].m,start:on-SCAN.start")
rep("  const out=ev.slice();\n  for(const n of early){","  (SCAN.dbgEarly=SCAN.dbgEarly||[]).push(...early.map(n=>({m:n.m,s:n.start,e:n.end,n:n.n,cf:n.cf,h:n.hue,nst:fr.length})));\n  const out=ev.slice();\n  for(const n of early){")
open(sys.argv[1], 'w').write(s)
