()=>{window.AW_NOLOOP=true;let tones=[];window.playTone=(m,d,v,g)=>tones.push({m,g});window.playClick=a=>tones.push({m:96,click:1});window.toast=()=>{};KB.state='off';const o={};
 let timers=0;const sT=window.setTimeout,sI=window.setInterval;window.setTimeout=(f,t)=>{timers++;return sT(f,t)};window.setInterval=(f,t)=>{timers++;return sI(f,t)};
 const notes=[];let t=0;for(let bar=0;bar<8;bar++){notes.push({m:48,start:t,dur:1.9,hand:'L'});for(let q=0;q<4;q++)notes.push({m:60+((bar+q)%5)*2,start:t+q*0.5,dur:0.45,hand:'R'});t+=2}
 notes.push({m:54,start:4.0,dur:0.4,hand:'L'},{m:57,start:4.0,dur:0.4,hand:'L'},{m:66,start:4.118,dur:0.3,hand:'R'});
 const it={id:'regel',type:'midi',title:'Regel',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);const T0=Date.UTC(2026,10,16,9);window.AW_NOW=T0;openMem(it);
 const gs=MEM.gs,v=()=>MEM.rec.v9,ch=k=>v().ch[k],tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs[j].mids)memPress(m,'kb')};
 const runWait=(f)=>{const R=MEM.run;let g=0;while(!R.done&&g++<300&&MEM.run===R){if(R.pv){tick(0.5);continue}if(R.pos<=R.b){if(f)f(R);if(MEM.run!==R||R.done)break;play(R.pos)}tick(0.1)}return R};
 const wrongKeyOf=j=>{let m=Math.max(...gs[j].mids)+1;while(gs[j].mids.has(m)||(gs[j+1]&&gs[j+1].mids.has(m)))m++;return m};const pulse=(R,skip,lat)=>{let q=R.a,g=0;while(!R.done&&g++<40000&&MEM.run===R){awTick(R,1/120);if(R.wait0&&!R.pv){tick(0.5);if(!(skip&&skip.includes(q)))play(q);q++;continue}while(q<=R.b&&!R.pv&&R.vt>=gs[q].start+(lat||0.03)*R.speed){if(!(skip&&skip.includes(q)))play(q);q++}}return R};
 o.n=MEM.C.length;o.vorgriffGrp=gs.some(G=>G.mids.has(54)&&G.mids.has(57)&&!G.mids.has(66))&&gs.some(G=>G.mids.has(66));
 timers=0;let p=awPick();o.p1=p.mode;awNext();let R=MEM.run;o.findScreen=!R.dark;runWait(R=>{if(R.pos===R.a)for(const m of [30,31,32])memPress(m,'kb')});o.find1=[R.ok,ch(0).fc,ch(0).st];
 awNext();R=runWait(R=>{if(R.pos===R.a&&!R.w1){R.w1=1;memPress(30,'kb')}});o.find2=[R.ok,ch(0).fc,ch(0).st];awNext();R=runWait();o.find3=[R.ok,ch(0).fc,ch(0).st,ch(0).fl];
 awNext();R=MEM.run;o.p2=[R.mode,R.fl];o.hide0=[...Array(R.b-R.a+1)].map((_,i)=>awHidden(R,R.a+i)?1:0).join('');awDraw();o.fadeState=R.drawState;
 let jh=R.a;while(!awHidden(R,jh))jh++;while(R.pos<jh)play(R.pos);awDraw();o.hiddenMsg=$('#memMsg').textContent.includes('versteckt');memPress(30,'kb');o.reveal=[R.rev.has(jh),R.cues,R.wrong];play(R.pos);
 R=runWait();o.fade0=[R.ok,ch(0).fl,ch(0).st];
 awNext();R=MEM.run;o.hide1=[...Array(R.b-R.a+1)].map((_,i)=>awHidden(R,R.a+i)?1:0).join('');R=runWait(R=>{if(awHidden(R,R.pos))memPress(30,'kb')});o.fadeBack=[R.ok,R.cues,ch(0).fl];
 {let g=0;while(awPick().mode==='fade'&&g++<8){awNext();R=MEM.run;if(R.fl===2)o.hide2=[...Array(R.b-R.a+1)].map((_,i)=>awHidden(R,R.a+i)?1:0).join('');R=runWait()}}o.fade2=[R.ok,ch(0).st];
 awNext();R=MEM.run;o.p3=R.mode;awDraw();o.anchor0=R.drawState==='anker';tick(30);o.anchorStays=R.anchor;memPress(30,'kb');o.anchorSearch=R.wrong;play(R.pos);awDraw();o.dark=R.drawState==='dunkel';
 const h0=R.hints;tones=[];tick(25);o.thinkNoHelp=R.hints===h0&&R.show==null&&!tones.length;
 const pw=R.pos;memPress(30,'kb');o.wrongShows=[R.wrong,R.hints,R.show===pw];awDraw();o.helpState=R.drawState;tick(20);o.showStays=R.show===pw;memPress(31,'kb');memPress(32,'kb');o.searchFree=R.wrong===1;play(R.pos);o.continues=R.pos===pw+1&&R.show==null;
 for(let i=0;i<8;i++){memPress(33,'kb');if(R.show!=null)play(R.pos)}o.noAbort=MEM.run===R&&!R.pv;
 R=runWait();o.head1=[R.ok,R.hints>=3,ch(0).st,ch(0).fl];
 o.p4=awPick().mode;let g=0;while(awPick().mode==='fade'&&g++<6){awNext();runWait()}
 awNext();R=MEM.run;o.p5=R.mode;play(R.pos);play(R.pos);play(R.pos);const ph=R.pos;memPress(22,'kb');o.bHelp=[R.hints,R.show===ph];R=runWait();o.spot=[R.ok,ch(0).spot,ph];
 p=awPick();o.p6=p.mode;awNext();R=MEM.run;o.spotRange=[R.a,R.b,R.anchor];R=runWait();o.spotOk=[R.ok,ch(0).spot];
 p=awPick();o.p7=p.mode;awNext();R=runWait();o.head2=[R.ok,ch(0).st];
 awNext();R=MEM.run;o.p8=[R.mode,Math.round(R.speed*100)];tick(0.5);tones=[];memPress(21,'kb');R=MEM.run;awDraw();o.demo=[!!R.pv,R.drawState];
 tick(1);awDraw();o.demoKeys=$('#memMsg').textContent.includes('ohne Ton');const dp=R.pos;play(R.pos);o.demoIgnore=R.pos===dp&&R.wrong===0;{let g=0;while(R.pv&&g++<2000)awTick(R,1/60)}o.demoSilent=!tones.filter(x=>x.m<90).length;o.demoEnd=!R.pv&&!R.done;
 o.clicks=[R.wait0,R.clicks.length,+(R.beat.p).toFixed(2),R.beat.ok];tones=[];pulse(R);o.pulsTones=tones.filter(x=>x.m>=96).length;o.puls1=[R.ok,ch(0).tp];
 awNext();R=MEM.run;pulse(R,[R.a+2,R.a+4]);o.pulsMiss=[R.ok,R.miss,ch(0).tp];awNext();R=MEM.run;pulse(R,[R.a+3]);o.oneMiss=[R.ok,R.miss,ch(0).tp];
 awNext();R=MEM.run;o.p9=Math.round(R.speed*100);pulse(R);o.box1=[ch(0).box,Math.round((ch(0).due-window.AW_NOW)/6e4)];
 window.AW_NOW+=11*60e3;p=awPick();o.rev=[p.mode,p.k];awNext();R=MEM.run;o.revSp=Math.round(R.speed*100);pulse(R);o.box2=[ch(0).box,Math.round((ch(0).due-window.AW_NOW)/36e5)];
 const toK0=()=>{let g=0;while(MEM.run.k!==0&&g++<60){const R=MEM.run;if(R.timed)pulse(R);else runWait();awNext()}};
 window.AW_NOW=ch(0).due+1;awNext();toK0();pulse(MEM.run);o.box3=[ch(0).box,$('#memMsg').textContent.includes('Gelernt')];
 window.AW_NOW=ch(0).due+1;awNext();toK0();pulse(MEM.run);o.box4=[ch(0).box,Math.round((ch(0).due-window.AW_NOW)/864e5)];
 window.AW_NOW=ch(0).due+1;awNext();toK0();R=MEM.run;pulse(R,[R.a,R.a+1,R.a+2]);o.fail=[R.ok,ch(0).box,ch(0).relearn];
 const vv=v();vv.ch.forEach(c=>{c.box=3;c.st=3;c.due=window.AW_NOW+9e9;c.relearn=0;c.spot=null});vv.ln=[];for(let k=0;k<vv.ch.length-2;k++)vv.ln[k]=1;vv.lw=[];
 p=awPick();o.chain=[p.mode,p.s,p.e,vv.ch.length];awNext();R=MEM.run;o.chainSp=Math.round(R.speed*100);pulse(R);o.chainOk=[R.ok,!!vv.ln[vv.ch.length-2]];
 p=awPick();o.w1=p.mode;awNext();R=MEM.run;o.wSetup=[R.a,R.b,gs.length-1,R.dark,R.clicks.length,R.anchor];memPress(22,'kb');o.wNoHelp=R.hints===0&&R.show==null;
 const pl=(R,opt)=>{while(R.pos<=R.b&&MEM.run===R){const j=R.pos;if(opt&&opt.skip===j){tick(0.6);play(j+1);continue}tick((j>R.a?gs[j].start-gs[j-1].start:0.2)*1.2);play(j)}tick(3);return R};
 R=pl(R);o.w1r=[R.ok,R.miss,R.wrong,R.slips,+(R.tempo||0).toFixed(2),new Set(v().whole.days).size,Math.round((v().whole.due-window.AW_NOW)/36e5)];
 window.AW_NOW+=864e5;p=awPick();o.w2=p.mode;awNext();R=MEM.run;const sk=R.a+15;R=pl(R,{skip:sk});o.w2r=[R.ok,R.miss,awSongSits(v()),Math.round((v().whole.due-window.AW_NOW)/864e5)];
 window.AW_NOW=v().whole.due+1;p=awPick();awNext();R=MEM.run;R=(()=>{while(R.pos<=R.b&&MEM.run===R){const j=R.pos;if(j>=20&&j<=28){tick(0.4);play(Math.min(R.b,j+3));continue}tick(0.6);play(j)}tick(3);return R})();
 const sj=(R.skipAt||[-1])[0],kBad=MEM.C.findIndex(c=>sj>=c.a&&sj<=c.b);o.w3=[R.ok,R.miss,kBad>=0&&v().ch[kBad].due<=window.AW_NOW,awPick().mode];
 const kV=MEM.C.findIndex(c=>gs[c.a].start<=4.01&&gs[c.b].start>=4.0);awStart({k:kV,mode:'head'});R=MEM.run;let jj=gs.findIndex(G=>G.mids.has(54));while(R.pos<jj)play(R.pos);
 memPress(66,'kb');for(const m of gs[jj].mids)memPress(m,'kb');o.vorgriff=[R.wrong,R.pos>jj+1];
 awStart({k:kV,mode:'head'});R=MEM.run;while(R.pos<jj)play(R.pos);const ks=[...gs[jj].mids];for(const m of ks)memPress(m,'kb');o.chord4=R.wrong;tick(1.2);memPress(ks[3],'kb');o.chord4late=R.wrong;
 awStart({k:0,mode:'head'});R=MEM.run;while(R.pos<=R.b)play(R.pos);tick(0.2);o.endWait=!R.done;tick(3);o.endDone=R.done;tick(1);memPress(70,'kb');o.keyNext=MEM.run!==R;
 /* v5.09 Rückblick: falscher Ton + Hilfe an Anschlag 3 → Rückblick nennt ihn; Puls zu spät → "zu spät", nicht "falsche Taste" */
 awStart({k:0,mode:'head'});R=MEM.run;play(R.pos);play(R.pos);const j3=R.pos,wk=Math.max(...gs[j3].mids)+13;memPress(wk,'kb');while(R.pos<=R.b)play(R.pos);tick(3);
 o.rb=[R.done,R.worst===j3,!!(R.mk[j3]&&R.mk[j3].help&&R.mk[j3].wrong.includes(wk)),/Anschlag 3: richtig ist/.test(awHier(R)),awNm(wk)&&awHier(R).includes(awNm(wk))];
 o.weg=/Aus dem Kopf/.test($('#memStages').textContent)&&/Metronom läuft bei allen Schritten/.test($('#memStages').textContent);
 /* v5.11 Einzählen: 4 Klicks, der 5. Schlag = erster Ton; kein Anlauf-Ton (auch wenn der Abschnitt davor gekonnt ist); Klicks im Abschnitt fließend im selben Abstand */
 /* v5.12/5.14 Start beim Spielen: wartet (Metronom tickt), falsche Taste startet nicht, der erste Ton startet */
 {const v=awState();v.ch[0].box=2;v.ch[0].st=3;v.ch[1].st=3;v.ch[1].tp=0;awStart({k:1,mode:'puls'});const R1=MEM.run,t0=gs[R1.a].start;tones=[];tick(6);
  const waitClicks=tones.filter(x=>x.m>=96).length,still=R1.wait0;memPress(wrongKeyOf(R1.a),'kb');const noStart=R1.wait0&&R1.wrong===0;play(R1.a);
  o.start=[waitClicks>=6,still,noStart,!R1.wait0,R1.pos===R1.a+1,R1.clicks.every(x=>x.t>t0),true,true];memStop()}
 /* v5.14 Puls im eigenen Tempo: spielt(R,tempoFaktor,{j:verschiebung s}) */
 {const spiel=(f,shift)=>{const v=awState();v.ch[0].st=3;v.ch[0].tp=0;v.ch[0].box=0;awStart({k:0,mode:'puls'});const R=MEM.run,sp=R.speed*f;let T=0;const P=[];
    for(let j=R.a;j<=R.b;j++)P.push([(gs[j].start-gs[R.a].start)/sp+((shift||{})[j-R.a]||0),j]);P.sort((x,y)=>x[0]-y[0]);
    for(const [t,j] of P){tick(Math.max(0,t-T));T=Math.max(T,t);play(j)}tick(2);return R};
  let R=spiel(0.85);o.eigen=[R.done,R.ok,R.miss,R.wrong,R.off,+(R.tempo/R.speed).toFixed(2)];
  R=spiel(1.1,{3:0.3});o.einAus=[R.ok,R.off,!!(R.mk[R.a+3]&&R.mk[R.a+3].off)];
  R=spiel(1,{2:0.3,5:-0.25});o.zweiAus=[R.ok,R.off];
  R=spiel(0.6);o.langsam=[R.ok,R.off,/zu langsam/.test($('#memEv').textContent+$('#memMsg').textContent)];
  R=spiel(1,{1:0.06,2:-0.05,4:0.07,6:-0.06});o.wackel=[R.ok,R.off];
  awStart({k:0,mode:'puls'});const R5=MEM.run;play(R5.a);tick(6);o.pause=[R5.done,R5.miss>=R5.b-R5.a];memStop()}
 /* v5.12 Metronom auch beim Mitspielen: läuft mit der Musik, hält an, wenn das Lied wartet */
 {awStart({k:0,mode:'find'});const R2=MEM.run;tones=[];let q=R2.a,g=0;while(!R2.done&&g++<4000){awTick(R2,1/60);if(R2.pos===q&&R2.vt>=gs[q].start-1e-9){play(q);q++}}const flow=tones.filter(x=>x.m>=96).length;
  awStart({k:0,mode:'find'});const R3=MEM.run;tones=[];tick(8);const stop=tones.filter(x=>x.m>=96).length;o.findClick=[flow>=4,stop<=2,R2.clicks.length>0];memStop()}
 /* v5.13 Klick ist ein eigener Klick-Ton, kein Klavierton mehr */
 {awStart({k:0,mode:'puls'});const R4=MEM.run;tones=[];tick(3);o.klick=[tones.length>0&&tones.every(x=>x.click===1)];memStop()}
 /* v5.15: perfekter Weg – wie viele Durchgänge bis „im Tempo“ (Kasten 1)? Übergang: Kopf/Puls von Abschnitt 2 beginnen mit dem letzten Anschlag von Abschnitt 1 */
 {delete MEM.rec.v9;awState();const v=awState();let n=0,dark=0,modes=[],leadOk=null,g=0;
  while(v.ch[1].box<1&&g++<40){const p=awPick();if(!p)break;if(p.mode==='link')break;awStart(p);const R=MEM.run;if(p.k===1&&(p.mode==='head'||p.mode==='puls')&&leadOk==null)leadOk=R.lead===1&&R.a===MEM.C[1].a-1;
    if(p.k===1)modes.push(p.mode);if(R.timed){tick(0.5);let T=0;const P=[];for(let j=R.a;j<=R.b;j++)P.push([(gs[j].start-gs[R.a].start)/1.0,j]);for(const [t,j] of P){tick(Math.max(0,t-T));T=t;play(j)}tick(2)}
    else{tick(1.5);while(R.pos<=R.b&&!R.done){play(R.pos);tick(0.3)}tick(3)}if(p.k===1){n++;if(R.dark)dark++}}
  o.pfad=[n,dark,modes.join(','),leadOk]}
 /* v5.16 nicht hängen bleiben */
 {const v=awState();v.ch.forEach(c=>{c.st=3;c.box=0;c.tp=0});awStart({k:0,mode:'puls'});let R=MEM.run;awDraw();o.h1=[R.drawState,/blauen Ton/.test($('#memMsg').textContent)];memStop();
  awStart({k:0,mode:'puls'},true);R=MEM.run;const pv0=!!R.pv;memPress(gs[R.a].start?60:60,'kb');tick(0.1);o.h2=[pv0,!R.pv];memStop();
  let jc=gs.findIndex((G,j)=>G.mids.size>=2&&j+1<gs.length&&[...gs[j+1].mids].some(m=>!G.mids.has(m)));const kc=MEM.C.findIndex(C=>jc>=C.a&&jc<C.b);
  if(kc>=0){v.ch[kc].st=0;awStart({k:kc,mode:'find'});R=MEM.run;while(R.pos<jc){play(R.pos);tick(0.05)}const G=gs[jc],m1=[...G.mids][0],mn=[...gs[jc+1].mids].find(m=>!G.mids.has(m));memPress(m1,'kb');memPress(mn,'kb');o.h3=[R.pos>jc,R.wrong]}else o.h3=['kein Akkord',0];memStop();
  awStart({k:0,mode:'whole'});R=MEM.run;play(R.pos);play(R.pos);tick(9);o.h4=[R.done,R.stall===1,!R.ok];
  awStart({k:0,mode:'puls'});R=MEM.run;play(R.pos);let g=0;while(!R.done&&g++<20){memPress(wrongKeyOf(R.pos),'kb');tick(0.5)}o.h5=[R.done,R.stall===1]}
 /* v5.17 Song-Karte + Titel + Weiter sagt wohin */
 {awStart({k:1,mode:'head'});const M=$('#memMapR').innerHTML;o.map=[(M.match(/<i /g)||[]).length===MEM.C.length,(M.match(/outline:2px/g)||[]).length===1,/Abschnitt 2/.test($('#memRunT').textContent)];memStop()}
 o.timers=timers;return o}
