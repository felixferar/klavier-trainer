"""Gemeinsame Grundlage für layouttest, markstest und shottest (Vergleichsansicht „Video neben Noten“).
Diese drei Tests luden früher /tmp/dshot.py – eine Hilfsdatei aus einer alten Sitzung, die nie im Repo lag. Deshalb starteten sie seit Wochen nicht
(bemerkt 27.11.2026: „5 rote Tests“ waren keine fehlgeschlagenen Prüfungen, sondern Tests ohne Eingabe).
geo/lo: Tastatur-Geometrie des Embers-Videos, genau wie in cmptest.py. JS: öffnet die Vergleichsansicht mit einem Platzhalter-Player."""
import json, os
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
meta = json.load(open(os.path.join(H, 'embers_v434_meta.json')))
keys = meta['keys']; lo = keys[0]['m']; rows = meta['scanRows']
geo = {'x': [keys[0]['x'], keys[-1]['x']], 'kw': meta['kw'], 'yT': rows['yT'], 'yA': rows['yA'], 'yB': rows['yB'], 'yC': rows['yC'], 'sh': 0, 'kx': [round(k['x'], 4) for k in keys], 'ar': round(753 / 320, 4)}
JS = """async([geo,lo])=>{const wait=ms=>new Promise(z=>setTimeout(z,ms));NAT.ok=true;grabVideo=async()=>null;
  const notes=[];for(let i=0;i<10;i++)notes.push({m:lo+30,start:1+i,dur:0.5,hand:'R'});
  const a={id:'a',type:'midi',title:'T',artist:'x',data:b64FromBuf(writeMidi(notes)),fromYT:'abcdefghijk',video:{v:2,src:'yt',start:2,first:3,fps:25,keys:[lo,lo+geo.kx.length-1],geo}};LIB=[a];
  window.openYT=()=>{cmpMode(!!CMP);show('yt')};let vt=3.2;ytp={getCurrentTime:()=>vt,pauseVideo(){},seekTo(t){vt=t},setPlaybackRate(){},playVideo(){},getPlayerState:()=>2,getPlaybackQuality:()=>'tiny',destroy(){}};
  openCompare(a);await wait(600)}"""
