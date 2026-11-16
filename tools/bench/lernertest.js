async([seed])=>{let S0=seed>>>0;const rnd=()=>{S0|=0;S0=S0+0x6D2B79F5|0;let t=Math.imul(S0^S0>>>15,1|S0);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
 window.AW_NOLOOP=true;let tones=[];window.playTone=m=>tones.push(m);window.playClick=()=>{};window.toast=()=>{};KB.state='off';
 const out={viol:[],att:{},days:[],stuck:0,help:0,wrongs:0,demos:0,demoTones:0,perPart:{}};const V=m=>{if(out.viol.length<30)out.viol.push(m)};
 /* Song mit Form A B A B' C (C lang und schnell) */
 const A=[64,67,72,67,65,69,72,69,67,71,74,71,64,67,72,64],B=[69,72,76,72,65,69,72,69,67,71,74,77,72,67,64,60],B2=B.slice(0,12).concat([72,69,65,64]),Cs=[...Array(40)].map((_,i)=>72+[0,4,7,12,7,4][i%6]-(i>=20?5:0));
 const notes=[];let t=0;const sec=(mel,d)=>{mel.forEach((m,i)=>{notes.push({m,start:t,dur:d*0.9,hand:'R'});if(i%4===0)notes.push({m:43+(i/4%4)*2,start:t,dur:d*3.6,hand:'L'});t+=d});t+=0.9};
 sec(A,0.32);sec(B,0.32);sec(A,0.32);sec(B2,0.32);sec(Cs,0.2);
 const it={id:'lerner6',type:'midi',title:'Lerner v6',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);
 const DAY=864e5,T0=Date.UTC(2026,10,16,17);window.AW_NOW=T0;openMem(it);out.parts=MEM.C.map(P=>[P.n,P.L,MEM.F[P.f].lab,P.twin,P.near]);
 const gs=()=>MEM.gs,tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs()[j].mids)memPress(m,'kb')};
 const wrongKeyOf=j=>{let m=Math.max(...gs()[j].mids)+1;while(gs()[j].mids.has(m)||(gs()[j+1]&&gs()[j+1].mids.has(m)))m++;return m};
 /* Gedächtnis je Anschlag: wächst mit jedem Spielen, sinkt über Nacht */
 const mem=new Float64Array(gs().length).fill(0);
 const pErr=(R,j)=>{const m=mem[j];if(R.mode==='learn')return 0.03;const base=R.mode==='head'?0.35:R.mode==='whole'?0.12:0.18;return base*Math.pow(1-m,2)};
 const learnFrom=R=>{for(let j=R.a;j<=R.b;j++)mem[j]=Math.min(1,mem[j]+(R.mode==='learn'?0.25:0.18))};
 const doRun=()=>{awNext();const R=MEM.run;if(!R)return null;const key=R.mode+(R.half!=null?'½':'');out.att[key]=(out.att[key]||0)+1;
   if(R.mode==='learn'&&rnd()<0.3){memPress(21,'kb');out.demos++;const n0=tones.length;tick(4);if(tones.length>n0)out.demoTones++;}
   const RR=MEM.run;let g=0;
   if(RR.timed){let q=RR.a;while(!RR.done&&g++<300000&&MEM.run===RR){awTick(RR,1/120);if(RR.wait0&&!RR.pv){tick(0.3);play(q);q++;continue}
       while(q<=RR.b&&!RR.pv&&RR.vt>=gs()[q].start+(0.03+(rnd()-0.5)*0.04)*RR.speed){if(rnd()<pErr(RR,q)){memPress(wrongKeyOf(q),'kb');out.wrongs++}play(q);q++}}}
   else{while(!RR.done&&g++<3000&&MEM.run===RR){if(RR.pv){tick(0.5);continue}if(RR.pos<=RR.b){const j=RR.pos;
       if(RR.mode!=='learn'&&rnd()<pErr(RR,j)){if(RR.mode==='head'&&rnd()<0.5){/* weiß nicht weiter: lange nachdenken, dann Hilfe */const sh=RR.hints;tick(12);if(RR.show!=null||RR.hints!==sh)V('Zeit-Hilfe ohne Wunsch');memPress(22,'kb');out.help++;tick(2);if(RR.show!==j)V('Hilfe bleibt nicht stehen');}
         else{memPress(wrongKeyOf(j),'kb');out.wrongs++;if(RR.mode==='head'&&RR.show!=null&&!RR.hints)V('falscher Ton zeigt Hilfe')}}
       else if(RR.mode==='learn'&&rnd()<pErr(RR,j)){memPress(wrongKeyOf(j),'kb');out.wrongs++}
       play(j)}tick(0.1)}}
   if(!RR.done)out.stuck++;learnFrom(RR);return RR};
 let songSits=null,allSit=null,total=0;
 for(let day=0;day<14;day++){window.AW_NOW=T0+day*DAY;openMem(it);let n=0,sawNonRev=false;const d={day,att:0,rev:0,ok:0};
   while(n++<45){const p=awPick();if(!p)break;if(p.mode==='rev'||(p.mode==='whole'&&p.rev)){d.rev++;if(sawNonRev)V(`Tag ${day}: Wiederholung mitten in der Sitzung`);if(day===0)V('Wiederholung am ersten Tag')}else sawNonRev=true;
     const R=doRun();if(!R)break;d.att++;total++;if(R.ok)d.ok++;if(R.mode!=='whole'&&R.mode!=='snow'){const k='T'+(R.k+1);(out.perPart[k]=out.perPart[k]||[0,0])[0]++;if(R.ok)out.perPart[k][1]++}}
   const v=MEM.rec.v10;d.st=v.ch.map(c=>c.st).join('');d.sn=v.sn.filter(Boolean).length;d.whole=new Set(v.whole.days).size;d.pct=Math.round(awProg().total*100);out.days.push(d);
   if(allSit==null&&v.ch.every(c=>c.st===3))allSit=day;if(songSits==null&&awSongSits(v))songSits=day;
   for(let j=0;j<mem.length;j++)mem[j]*=0.85} /* über Nacht etwas vergessen */
 out.songSits=songSits;out.allSit=allSit;out.total=total;out.lat=MEM.rec.v10.lat;return out}
