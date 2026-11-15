async([seed,maxMiss,stp])=>{if(maxMiss!=null)AW.maxMiss=maxMiss;if(stp)window.AW_STEP=stp;
 let S0=seed>>>0;const rnd=()=>{S0|=0;S0=S0+0x6D2B79F5|0;let t=Math.imul(S0^S0>>>15,1|S0);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
 const out={viol:[],stats:{att:{},abort:0,askHelp:0,autoHelp:0,longThink:0,searchWhileShown:0,relearn:0,links:0,stuck:0,reveals:0,demoTones:0},days:[]};
 const V=(k,msg)=>{if(out.viol.length<30)out.viol.push(k+': '+msg)};
 window.AW_NOLOOP=true;let tones=[];window.playTone=(m,d,v,g)=>tones.push(m);window.toast=()=>{};KB.state='off';
 const LH=[[36,43],[41,48],[43,50],[36,43],[45,52],[41,48],[43,50],[36,43]],MEL=[[64,67,72,67],[65,69,72,69],[67,71,74,71],[64,67,72,0],[69,72,76,72],[65,69,72,69],[67,71,74,77],[72,67,64,0]];
 const notes=[];let t=0;for(let r=0;r<2;r++)for(let bar=0;bar<8;bar++){for(const m of LH[bar])notes.push({m,start:t,dur:1.9,hand:'L'});const M=MEL[bar];for(let q=0;q<4;q++){const m=M[q]+(r&&q===3&&M[q]?2:0);if(M[q])notes.push({m,start:t+q*0.5,dur:0.45,hand:'R'})}t+=2}
 const it={id:'lerner',type:'midi',title:'Lerner-Song',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);
 const T0=Date.UTC(2026,10,16,8,0,0);window.AW_NOW=T0;openMem(it);
 const gs=MEM.gs,C=MEM.C;out.chunks=C.map(c=>[c.a,c.b,+(c.t1-c.t0).toFixed(1)]);out.beat=awBeat();
 const str=C.map(()=>0),L_USER=0.06,TEMPO=1.2; /* Gedächtnis je Abschnitt; Bluetooth-Verzögerung 60 ms; im ganzen Song spielt er 20 % langsamer */
 const st=()=>MEM.rec.v9.ch,kOf=j=>C.findIndex(c=>j>=c.a&&j<=c.b);
 const step=window.AW_STEP||1/30,tick=(sec)=>{let x=0;while(x<sec-1e-9){const R=MEM.run;if(!R)return;const n0=tones.length;awTick(R,step);if(R.pv&&tones.length>n0)out.stats.demoTones+=tones.slice(n0).filter(m=>m<90).length;x+=step}};
 const press=ms=>{for(const m of ms)memPress(m,'kb')};
 const wrongKey=G=>{const j=gs.indexOf(G),bad=new Set([...G.mids,...(j>0?gs[j-1].mids:[]),...(gs[j+1]?gs[j+1].mids:[])]);let m=Math.max(...G.mids)+1;while(bad.has(m))m++;return m}; /* wirklich falscher Ton (nicht im Akkord davor/danach) */
 const watch=(R,label,f)=>{const h0=R.hints,tn=tones.length;f();if(MEM.run!==R)return;if(R.hints!==h0)V('Zeit-Hilfe',`${label}: Hilfe ohne Anlass (${R.mode})`);
   const nt=tones.slice(tn).filter(m=>m<90);if(nt.length&&!R.timed)V('Ton',`${label}: Töne ${nt} ohne Anlass`);awDraw();if(!R.done&&R.dark&&R.show==null&&!R.anchor&&R.drawState!=='dunkel')V('Bildschirm',`${label}: nicht dunkel (${R.drawState})`)};
 const pf=(j,f)=>Math.min(0.6,Math.max(0.02,(1-str[kOf(j)])*f));
 function playWaitGroup(R){const j=R.pos,G=gs[j],ks=[...G.mids];
   if(R.mode==='find'){tick(0.4+rnd());if(rnd()<0.2)press([wrongKey(G)]);press(ks);return}
   if(R.mode==='fade'){tick(0.3+rnd());if(awHidden(R,j)&&rnd()<pf(j,0.5)){const w0=R.wrong;press([wrongKey(G)]);if(R.wrong!==w0)V('Ausblenden','fehlende versteckte Note zählte als Fehler');if(!R.rev.has(j))V('Ausblenden','versteckte Note erschien nicht');out.stats.reveals++;tick(1)}press(ks);return}
   if(R.anchor){tick(1+rnd()*4);if(!R.anchor)V('Anker','Anker verschwand von selbst');const w0=R.wrong;if(rnd()<0.5){press([wrongKey(G)]);if(R.wrong!==w0)V('Anker','Suchen beim Anker zählte')}press(ks);return}
   if(rnd()>=pf(j,0.4)){tick(0.3+rnd()*1.2);press(ks);return}
   const r=rnd();
   if(r<0.3){out.stats.longThink++;const th=5+rnd()*15;watch(R,`${th.toFixed(0)} s nachdenken`,()=>tick(th));if(MEM.run===R)press(ks);return}
   if(r<0.65){const h0=R.hints;press([wrongKey(G)]);if(MEM.run!==R)return;if(R.show!==j||R.hints!==h0+1)V('Hilfe','falscher Ton zeigte den richtigen nicht sofort');out.stats.autoHelp++;
     tick(2+rnd()*5);if(R.show!==j)V('Hilfe','Hilfe verschwand von selbst');const w0=R.wrong;press([wrongKey(G)]);out.stats.searchWhileShown++;if(R.wrong!==w0)V('Hilfe','Suchen während der Hilfe zählte');
     press(ks);if(R.show===j)V('Hilfe','Hilfe blieb nach dem Spielen stehen');if(R.pos!==j+1&&R.pos<=R.b)V('Hilfe','nach der Hilfe ging es nicht an der Stelle weiter');return}
   out.stats.askHelp++;const h0=R.hints;if(rnd()<0.5)press([22]);else $('#memHelp').click();if(R.hints!==h0+1||R.show!==j)V('Hilfe','B / Knopf zeigte den Anschlag nicht');tick(2+rnd()*4);press(ks)}
 function playTimed(R){let q=R.a;const plan={};
   for(let j=R.a;j<=R.b;j++){const f=R.mode==='puls'?0.12:0.3;plan[j]={miss:rnd()<Math.min(0.4,(1-str[kOf(j)])*f),jit:(rnd()-0.5)*0.08,wrong:rnd()<0.02}}
   let guard=0;const fs=Math.min(step,1/120);while(MEM.run===R&&!R.done&&guard++<120000){awTick(R,fs);if(R.done||MEM.run!==R||R.pv)continue;if(R.wait0){tick(0.3+rnd());press([...gs[R.a].mids]);q=R.a+1;continue}
     while(q<=R.b&&R.vt>=gs[q].start+(L_USER+plan[q].jit)*R.speed){const P=plan[q];if(!P.miss){press([...gs[q].mids]);if(P.wrong)press([wrongKey(gs[q])])}q++;if(MEM.run!==R)break}}
   if(guard>=120000)V('Hängt','Puls-Durchgang endet nicht')}
 function playWhole(R){let guard=0;
   while(MEM.run===R&&R.pos<=R.b&&guard++<5000){const j=R.pos,G=gs[j];const ioi=j>R.a?gs[j].start-gs[j-1].start:0.3;tick(Math.max(0.05,ioi*TEMPO*(1+(rnd()-0.5)*0.15)));
     const h0=R.hints;if(rnd()<pf(j,0.25)){if(rnd()<0.5&&j<R.b){press([...gs[j+1].mids]);continue}press([wrongKey(G)])}press([...G.mids]);if(R.hints!==h0||R.show!=null)V('ganzer Song','Hilfe im ganzen Song')}
   tick(3)}
 function playRun(){let R=MEM.run,guard=0;
   while(R&&!R.done&&guard++<600){if(R.pv){tick(0.2);continue}
     if(R.mode==='whole')playWhole(R);else if(R.timed)playTimed(R);else if(R.pos<=R.b)playWaitGroup(R);else tick(0.2);
     if(MEM.run!==R){if(R.mode==='head'||R.mode==='spot')V('Abbruch','aus dem Kopf wurde abgebrochen');out.stats.abort++;R=MEM.run}}
   if(guard>=600){out.stats.stuck++;V('Hängt',`Durchgang hängt (${R&&R.mode})`)}return MEM.run}
 const learn=R=>{const ks=R.mode==='whole'?C.map((_,i)=>i):R.span?[...Array(R.span.e-R.span.s+1)].map((_,i)=>R.span.s+i):[R.k];
   const g={find:0.12,fade:0.15,head:0.22,spot:0.12,puls:0.2,review:0.25,link:0.15,whole:0.1}[R.mode];for(const x of ks)str[x]+=(R.ok?g:g*0.4)*(1-str[x])};
 const decay=days=>{st().forEach((c,k)=>{const tau=1.5*(1+3*c.box);str[k]*=Math.exp(-days/tau)})};
 let day=0,totalAtt=0,firstSitzt=null,allBox1=null,songSits=null;
 for(day=0;day<30;day++){if(day>0){decay(1);window.AW_NOW=T0+day*864e5}let n=0,mins=0;const sess0=window.AW_NOW;
   while(n<80){let p=awPick();
     if(!p){const W=MEM.rec.v9.whole,fut=st().filter(c=>c.box>=1&&c.due>window.AW_NOW).map(c=>c.due).concat(W.due>window.AW_NOW?[W.due]:[]);const nd=fut.length?Math.min(...fut):Infinity;if(nd-window.AW_NOW<=15*60e3&&window.AW_NOW-sess0<45*60e3){window.AW_NOW=nd+1000;continue}break}
     const tag=p.mode+(p.mode==='puls'?Math.round(AW.tempi[st()[p.k].tp]*100):'')+(p.mode==='fade'?st()[p.k].fl+1:'');out.stats.att[tag]=(out.stats.att[tag]||0)+1;if(p.mode==='head'&&st()[p.k].relearn)out.stats.relearn++;
     awNext();let R=MEM.run;if(!R||R.mode!==p.mode){V('Ablauf','Weiter startete etwas anderes als angekündigt');break}
     R=playRun();if(!R||!R.done)break;learn(R);if(R.mode==='link'&&R.ok)out.stats.links++;
     window.AW_NOW+=Math.round(R.clock*1000)+15000;mins+=R.clock/60;n++;totalAtt++}
   const ch=st(),W=MEM.rec.v9.whole;out.days.push({day,att:n,min:+mins.toFixed(1),box:ch.map(c=>c.box).join(''),st:ch.map(c=>c.st).join(''),whole:new Set(W.days).size});
   if(allBox1==null&&ch.every(c=>c.box>=1))allBox1=day;if(firstSitzt==null&&ch.every(c=>c.box>=AW.solid))firstSitzt=day;if(songSits==null&&awSongSits(MEM.rec.v9))songSits=day;if(songSits!=null&&day>=songSits+3&&firstSitzt!=null)break}
 const v=MEM.rec.v9;out.allBox1=allBox1;out.sitzt=firstSitzt;out.songSits=songSits;out.lat=v.lat;out.ln=v.ln.filter(Boolean).length;out.totalAtt=totalAtt;out.wholeN=v.whole.n;
 out.stages=['find','fade','head','spot','puls','review','link','whole'].filter(m=>Object.keys(out.stats.att).some(k=>k.startsWith(m)));
 return out}
