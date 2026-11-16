()=>{window.AW_NOLOOP=true;let tones=[];window.playTone=(m,d,v,g)=>tones.push({m,g});window.playClick=a=>{};window.toast=()=>{};KB.state='off';const o={};
 /* Song mit Form: A B A B' C A – B' ist fast wie B (anderes Ende), C ist ein langer schneller Teil (> 30 Anschläge) */
 const A=[60,62,64,65,67,65,64,62,60,64,67,72,67,64,62,60],B=[69,67,65,64,62,64,65,67,69,71,72,71,69,67,65,64],B2=B.slice(0,13).concat([67,62,60]),
   Cs=[...Array(44)].map((_,i)=>72+[0,2,4,5,7,9,11,12,11,9,7,5][i%12]+(i>=24?-12:0));
 const notes=[];let t=0;const sec=(mel,d)=>{mel.forEach((m,i)=>{notes.push({m,start:t,dur:d*0.9,hand:'R'});if(i%4===0)notes.push({m:48-(i/4%3)*2,start:t,dur:d*3.6,hand:'L'});t+=d});t+=0.9};
 sec(A,0.3);sec(B,0.3);sec(A,0.3);sec(B2,0.3);sec(Cs,0.2);sec(A,0.3);
 const it={id:'v6',type:'midi',title:'V6',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];save('kt_lib',LIB);const DAY=864e5,T0=Date.UTC(2026,10,16,9);window.AW_NOW=T0;openMem(it);
 const gs=()=>MEM.gs,v=()=>MEM.rec[awKey()],ch=k=>v().ch[k],tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs()[j].mids)memPress(m,'kb')};
 const runWait=f=>{const R=MEM.run;let g=0;while(!R.done&&g++<600&&MEM.run===R){if(R.pv){tick(0.5);continue}if(R.pos<=R.b){if(f&&f(R)===false){tick(0.1);continue}if(MEM.run!==R||R.done)break;play(R.pos)}tick(0.1)}return R};
 const wrongKeyOf=j=>{let m=Math.max(...gs()[j].mids)+1;while(gs()[j].mids.has(m)||(gs()[j+1]&&gs()[j+1].mids.has(m)))m++;return m};
 const pulse=(R,f)=>{let q=R.a,g=0;while(!R.done&&g++<200000&&MEM.run===R){awTick(R,1/120);if(R.wait0&&!R.pv){tick(0.3);play(q);q++;continue}while(q<=R.b&&!R.pv&&R.vt>=gs()[q].start+0.03*R.speed){if(f)f(R,q);play(q);q++}}return R};
 const run=(f,pf)=>{awNext();const R=MEM.run;return R.timed?pulse(R,pf):runWait(f)};
 const C=MEM.C;o.parts=C.map(P=>[P.n,!!P.h,P.twin,P.near]);o.nParts=C.length;
 o.partsOk=C.length>=4&&C.length<=6&&C.every(P=>!P.h||(P.n>30&&P.h[0].b+1===P.h[1].a&&P.h[0].a===P.a&&P.h[1].b===P.b))&&C.filter(P=>P.n>30).every(P=>P.h)&&C.some(P=>P.twin>=0)&&C.some(P=>P.near>=0);
 /* Teil 1: Kennenlernen → Aus dem Kopf → Im Fluss */
 let p=awPick();o.p1=[p.mode,p.k];awNext();let R=MEM.run;o.learnScreen=[!R.dark,$('#memDemo')!=null,$('#memHandR .awHand')!=null];
 /* 1 falscher Ton beim Kennenlernen (≤ 30 Anschläge) = nicht sauber */
 R=runWait(R=>{if(R.pos===R.a+2&&!R.w1){R.w1=1;memPress(wrongKeyOf(R.pos),'kb')}});o.learnWrong=[R.ok,ch(0).st];
 /* tiefstes A = vorspielen mit Klang, dann neu */
 awNext();R=MEM.run;tones=[];memPress(21,'kb');o.demo=[!!MEM.run.pv];tick(3);o.demoTones=tones.length;R=MEM.run;memPress(60,'kb');tick(0.1);o.demoSkip=!R.pv;
 R=runWait();o.learnOk=[R.ok,ch(0).st];
 p=awPick();o.p2=p.mode;awNext();R=MEM.run;awDraw();o.anchor=[R.dark,R.drawState];
 /* Hilfe (B): Griff bleibt stehen, bis er gespielt ist */
 play(R.pos);play(R.pos);memPress(22,'kb');const hj=R.pos;tick(20);awDraw();o.helpStays=[R.hints,R.drawState,R.show===hj];play(R.pos);o.helpGone=R.show==null;R=runWait();o.headHelp=[R.ok,ch(0).st];
 awNext();R=runWait(R=>{if(R.pos===R.a+3&&!R.w1){R.w1=1;memPress(wrongKeyOf(R.pos),'kb')}});o.headWrong=[R.ok,R.hints,ch(0).st];
 awNext();R=runWait();o.headOk=[R.ok,ch(0).st];
 p=awPick();o.p3=p.mode;R=run();o.flowOk=[R.mode,R.ok,ch(0).st,ch(0).box,Math.round((ch(0).due-T0)/36e5)];
 /* Teil 2 ganz → dann Schneeball 1+2 */
 for(let i=0;i<3;i++)run();o.part2=[ch(1).st];p=awPick();o.snow1=[p.mode,p.s,p.e];R=run();o.snow1ok=[R.ok,!!v().sn[1]];
 /* alles weiter mit perfektem Spiel – wir merken uns die Reihenfolge */
 const seq=[];let guard=0;
 while(guard++<200){p=awPick();if(!p||p.mode==='whole')break;seq.push(p.mode==='snow'?`S${p.s}-${p.e}`:`${p.mode}${p.k}${p.half!=null?'h'+p.half:''}`);
   if(p.mode==='snow'&&MEM.C[p.e].b-MEM.C[p.s].a+1>30&&!o.tol){ /* Toleranz: 2 Streifer = nicht geschafft, 1 Streifer = geschafft */
     let n=0;R=run(null,(R,q)=>{if(q>R.a+3&&n<2){n++;memPress(wrongKeyOf(q),'kb')}});o.tol2=[R.ok,R.wrong,R.tolW];
     n=0;R=run(null,(R,q)=>{if(q>R.a+3&&n<1){n++;memPress(wrongKeyOf(q),'kb')}});o.tol=[R.ok,R.wrong,R.tolW];continue}
   run()}
 o.seq=seq;const K=MEM.C.length,big=MEM.C.findIndex(P=>P.h),tw=MEM.C.findIndex(P=>P.twin>=0);
 o.halves=big>=0?[seq.indexOf(`learn${big}h0`)<seq.indexOf(`head${big}h0`),seq.indexOf(`head${big}h0`)<seq.indexOf(`learn${big}h1`),seq.indexOf(`head${big}h1`)<seq.indexOf(`head${big}`),seq.indexOf(`head${big}`)<seq.indexOf(`flow${big}`),!seq.includes(`learn${big}`)]:null;
 o.twinSkipped=tw>=0&&!seq.some(x=>x===`learn${tw}`||x===`flow${tw}`)&&ch(tw).st===3;
 o.snowSpans=['S0-1'].concat(seq.filter(x=>x[0]==='S'));o.snowMax3=o.snowSpans.every(x=>{const [a,b]=x.slice(1).split('-').map(Number);return b-a<=2});
 o.allSit=v().ch.every(c=>c.st===3)&&[...Array(K-1)].every((_,i)=>v().sn[i+1]);
 /* ganzer Song: Tag 1 */
 p=awPick();o.w1=p&&p.mode;R=run();o.w1r=[R.ok,new Set(v().whole.days).size,R.tolW];o.after1=awPick();
 /* nächster Tag, neue Sitzung: zuerst gebündelt die Wiederholungen, dann der ganze Song */
 window.AW_NOW=T0+DAY+2*36e5;openMem(it);const seq2=[];guard=0;let failed=-1,prBefore=null;
 while(guard++<40){p=awPick();if(!p)break;seq2.push(p.mode+(p.mode==='rev'?p.k:''));
   if(p.mode==='rev'&&failed<0){failed=p.k;prBefore=awProg().total;awNext();R=MEM.run;R=pulse(R,(R,q)=>{if(q===R.a+2){memPress(wrongKeyOf(q),'kb');memPress(wrongKeyOf(q)+1,'kb')}});o.revFail=[R.ok,ch(failed).st,ch(failed).box,awProg().total<prBefore];continue}
   run()}
 o.seq2=seq2;const firstNonRev=seq2.findIndex(x=>!x.startsWith('rev'));o.revBundled=seq2.slice(firstNonRev).every(x=>!x.startsWith('rev'))&&firstNonRev>0;
 o.sits=awSongSits(v());
 /* mitten in der Sitzung fällig gewordene Wiederholung kommt NICHT dazwischen */
 window.AW_NOW+=30*DAY;o.midSess=awPick();openMem(it);o.newSess=awPick()&&awPick().mode;
 /* Hand-Filter */
 const lrState=JSON.stringify(v());awSetHand('L');o.handL=[MEM.hand,awKey(),MEM.gs.every(G=>[...G.hands.values()].every(h=>h==='L')),MEM.C.length>=1,!!MEMS.v6.v10L];
 awSetHand('R');o.handR=[MEM.hand,MEM.gs.every(G=>[...G.hands.values()].every(h=>h==='R'))];awSetHand('LR');o.handBack=[MEM.hand,JSON.stringify(v())===lrState];
 /* Übernahme aus v9: alle alten Abschnitte im Kasten → alle Teile sitzen */
 const oc=awChunks(MEM.gs);MEMS.v6={v9:{cv:10,n:oc.length,ch:oc.map(c=>({sig:'x',st:3,box:2,due:0})),ln:oc.map(()=>1),lw:[],lat:0,whole:{days:['2026-11-1'],due:0,n:1}}};window.AW_NOW=T0;openMem(it);
 o.mig=[v().ch.every(c=>c.st===3),v().sn.filter(Boolean).length===K-1,v().whole.days.length,!!MEMS.v6.v9];
 /* Song-Seite / Übersicht nutzen den neuen Stand */
 o.info=(()=>{const i=memInfo(it);return i&&[i.n,i.done]})();
 return o}
