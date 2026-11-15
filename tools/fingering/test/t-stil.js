// Einheitlicher Stil (v0.6): Gleiche Akkordform (Abstände von unten nach oben) soll in allen Songs gleich gegriffen werden.
// Misst: Anteil der Griffe, die im häufigsten Griff ihrer Form liegen (Stil einfach, beide Hände, 21 Songs). Ziel ≥ 80 % (v0.5: 70,5 %).
// Dazu: übliche Griffe (Dreiklänge, Oktave) in verschiedenem Zusammenhang immer gleich. Aufruf: node test/t-stil.js
const fs=require('fs'),F=require('../fingering.js'),datei=require('./daten.js');
const songs=[];for(let s=301;s<=315;s++){const y=JSON.parse(fs.readFileSync(datei(s+'.json')));songs.push(y.notes.map(x=>({midi:x.m,start:x.s,dur:x.d,hand:x.h})));}
for(const f of ['14-21-25_D4COOEBwBjk_done.json','16-04-51_41Z7W_0dJu8_done.json','14-49-51_GUnDodr9GLo_done.json','15-01-34_163bCfINABY_done.json','16-43-39_mu6gef4lM80_done.json']){const r=JSON.parse(fs.readFileSync(datei(f)));const n=r.events.map(e=>({midi:e[0],start:e[1],dur:Math.max(.02,e[2]-e[1])}));const h=F.assignHands(n);n.forEach((x,i)=>x.hand=h[i]);songs.push(n);}
const e=JSON.parse(fs.readFileSync(datei('embers-notes.json'))).map(x=>({midi:x[0],start:x[1],dur:x[2]}));const he=F.assignHands(e);e.forEach((x,i)=>x.hand=he[i]);songs.push(e);
const by={};let tot=0;
for(const ns of songs)for(const H of ['R','L']){const sub=ns.filter(x=>x.hand===H);if(!sub.length)continue;const r=F.computeHand(sub,{hand:H,style:'einfach'});
 for(const c of r.chords){const ms=c.notes.map(i=>sub[i].midi);const ord=ms.map((m,k)=>k).sort((a,b)=>ms[a]-ms[b]);const sm=ord.map(k=>ms[k]),sf=ord.map(k=>c.fingers[k]);
  const key=H+':'+sm.slice(1).map((m,k)=>m-sm[k]).join(',');(by[key]=by[key]||{})[sf.join('')]=((by[key]||{})[sf.join('')]||0)+1;tot++;}}
let main=0;const rows=Object.entries(by).map(([k,v])=>{const n=Object.values(v).reduce((a,b)=>a+b,0),top=Math.max(...Object.values(v));main+=top;return [k,n,v]}).sort((a,b)=>b[1]-a[1]);
rows.slice(0,14).forEach(([k,n,v])=>console.log(k.padEnd(12),String(n).padStart(4),JSON.stringify(v)));
const share=100*main/tot;console.log(`Griffe gesamt ${tot}, davon im häufigsten Griff ihrer Form: ${main} = ${share.toFixed(1)} %`);
// gleicher Dreiklang C-E-G in 6 verschiedenen Zusammenhängen (davor ein Melodieton von unten/oben/weit weg)
let same=0;const want={R:'135',L:'531'};
for(const H of ['R','L'])for(const pre of [-5,-1,2,7,9,14]){const b=H==='R'?60:48,ns=[{midi:b+pre,start:0,dur:0.4},{midi:b,start:0.5,dur:0.9},{midi:b+4,start:0.5,dur:0.9},{midi:b+7,start:0.5,dur:0.9}];
 const r=F.computeHand(ns,{hand:H,style:'einfach'});if([1,2,3].map(i=>r.fingers[i]).join('')===want[H])same++;}
console.log(`C-Dur-Dreiklang nach 6 verschiedenen Vortönen, beide Hände: ${same}/12 im üblichen Griff`);
const ok=share>=80&&same===12;console.log(ok?'OK':'FEHLER');process.exitCode=ok?0:1;
