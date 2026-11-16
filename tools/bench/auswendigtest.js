(ns)=>{window.toast=()=>{};let tones=[];window.playTone=m=>tones.push(m);window.playClick=()=>{};window.AW_NOLOOP=true;KB.state='off';const o={};
 const DAY=864e5,T0=Date.UTC(2026,10,16,17);window.AW_NOW=T0;
 const it={id:'aw',type:'midi',title:'Fly',artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);openMem(it);
 const gs=()=>MEM.gs,C=()=>MEM.C,v=()=>MEM.rec[awKey()],tick=s=>{for(let x=0;x<s;x+=1/60){const R=MEM.run;if(!R)return;awTick(R,1/60)}},play=j=>{for(const m of gs()[j].mids)memPress(m,'kb')};
 const wrongKeyOf=j=>{let m=Math.max(...gs()[j].mids)+1;while(gs()[j].mids.has(m)||(gs()[j+1]&&gs()[j+1].mids.has(m)))m++;return m};
 const runWait=f=>{const R=MEM.run;let g=0;while(!R.done&&g++<900&&MEM.run===R){if(R.pv){tick(0.5);continue}if(R.pos<=R.b){if(f&&f(R)===false){tick(0.1);continue}if(MEM.run!==R||R.done)break;play(R.pos)}tick(0.1)}return R};
 const runWhole=()=>{const R=MEM.run;let g=0;while(!R.done&&g++<3000){if(R.pos<=R.b){const j=R.pos;play(j);tick(j<R.b?Math.max(0.02,gs()[j+1].start-gs()[j].start):0.1)}else tick(0.1)}return R};
 const run=f=>{awNext();return MEM.run.mode==='whole'?runWhole():runWait(f)};
 const lbl=p=>p.mode+(p.mode==='snowk'||p.mode==='form'?`(${p.s+1}-${p.e+1})`:`(${p.k+1})`)+(p.re?'+N':'');
 /* 1. Häppchen 1: mit Noten, Vertipper ok */
 let p=awPick();o.p1=lbl(p);awNext();let R=MEM.run;o.learnScreen=[!R.dark,$('#memDemo')!=null,document.querySelectorAll('#memStages .awSteps li').length];
 /* Vorspielen mit Klang + mitspielen */
 tones=[];memPress(21,'kb');tick(3);o.demo=[tones.length>=4,!!MEM.run.pv];R=MEM.run;play(R.a);tick(0.1);o.along=[!!R.pv,R.pos===R.a];$('#memSkip').click();tick(0.1);
 R=runWait(R=>{if((R.pos===R.a+3||R.pos===R.a+7)&&!R['w'+R.pos]){R['w'+R.pos]=1;memPress(wrongKeyOf(R.pos),'kb')}});o.learn2wrong=[R.ok,R.wrong,v().ch[0].st];
 /* 2. aus dem Kopf: dunkel, Anker, Positionsleiste, Hilfe nach 5 s mit Zusammenhang; 1 Hilfe bei 13 Griffen erlaubt */
 p=awPick();o.p2=lbl(p);awNext();R=MEM.run;awDraw();o.anchor=[R.dark,R.drawState,R.lead];play(R.a);tick(0.2);awDraw();o.dark=[R.drawState,R.posTxt];
 play(R.pos);tick(4);o.before5=R.show;const al=[];const ctx=$('#memCv').getContext('2d'),fr=ctx.fillRect;ctx.fillRect=function(){al.push(+this.globalAlpha.toFixed(2));return fr.apply(this,arguments)};tick(1.5);awDraw();ctx.fillRect=fr;
 o.after5=[R.show===R.pos,R.hints,R.drawState,al.includes(0.45),al.includes(0.3)];R=runWait();o.head1help=[R.ok,R.hints,v().ch[0].st,v().ch[0].box];
 /* 3. Häppchen 2 → aus dem Kopf: 2 Hilfen = nicht geschafft; 3× nicht geschafft → einmal mit Noten */
 run();p=awPick();o.p3=lbl(p);const tries=[];for(let i=0;i<3;i++){R=run(R=>{if((R.pos===R.a+2||R.pos===R.a+6)&&!R['h'+R.pos]){R['h'+R.pos]=1;memPress(22,'kb')}});tries.push([R.ok,R.hints])}
 o.headFails=tries;p=awPick();o.reLearn=[lbl(p),p.a,p.b,C()[1].a,C()[1].b];awNext();R=MEM.run;o.reScreen=[!R.dark,R.re];R=runWait();o.reOk=[R.ok,!!v().re,(v().fc||{})['head:1']||0];
 p=awPick();o.afterRe=lbl(p);R=run();o.head2=[R.ok,v().ch[1].st];
 /* 4. Kette 1–2: wartet, dunkel, Anker, 1 Hilfe bei 26 Griffen ok */
 p=awPick();o.p4=lbl(p);awNext();R=MEM.run;awDraw();o.chainScreen=[R.dark,R.drawState,R.timed,R.n];R=runWait(R=>{if(R.pos===C()[1].a&&!R.h){R.h=1;memPress(22,'kb')}});o.chain=[R.ok,R.hints,v().ch[1].st];
 /* 5. Häppchen 3 mit Kette 1–3; Kette 3× nicht geschafft → Kette einmal mit Noten */
 run();run();p=awPick();o.p5=lbl(p);const ct=[];for(let i=0;i<3;i++){R=run(R=>{if([C()[1].a,C()[1].a+3,C()[2].a].includes(R.pos)&&!R['h'+R.pos]){R['h'+R.pos]=1;memPress(22,'kb')}});ct.push([R.ok,R.hints])}
 o.chainFails=ct;p=awPick();o.chainRe=[lbl(p),p.a,p.b,C()[0].a,C()[2].b];R=run();o.chainReOk=[R.ok,!!v().re];p=awPick();o.afterChainRe=lbl(p);
 /* 6. Rest perfekt bis zum ganzen Song – Reihenfolge merken */
 const seq=[];let g=0;while(g++<60){p=awPick();if(!p||p.mode==='whole')break;seq.push(lbl(p));R=run()}o.seq=seq;o.whole=p&&p.mode;
 o.twin=[C().map(P=>P.twin),seq.some(x=>x==='learn(5)'||x==='head(5)'),seq.includes('snowk(3-5)'),v().ch[4].st,!v().ch[4].tk];
 /* 7. ganzer Song Tag 1 → morgen; nächster Tag: Wiederholungen gebündelt, dann ganzer Song → sitzt */
 R=run();o.w1=[R.ok,new Set(v().whole.days).size,awPick()];
 window.AW_NOW=T0+DAY+2*36e5;openMem(it);const seq2=[];g=0;let failed=-1;
 while(g++<40){p=awPick();if(!p)break;seq2.push(lbl(p));if(p.mode==='rev'&&failed<0){failed=p.k;const pr0=awProg().total;awNext();R=MEM.run;R=runWait(R=>{if([R.a+2,R.a+4,R.a+6].includes(R.pos)&&!R['x'+R.pos]){R['x'+R.pos]=1;memPress(wrongKeyOf(R.pos),'kb')}});o.revFail=[R.ok,v().ch[failed].st,awProg().total<pr0];continue}run()}
 o.seq2=seq2;o.sits=awSongSits(v());
 window.AW_NOW+=30*DAY;o.midSess=awPick();
 /* 8. Hand-Filter */
 window.AW_NOW=T0;const lr=JSON.stringify(v());awSetHand('L');o.hand=[MEM.hand,awKey(),MEM.gs.every(G=>[...G.hands.values()].every(h=>h==='L'))];awSetHand('LR');o.handBack=JSON.stringify(v())===lr;
 /* 9. Übernahme aus v5.31: Häppchen 1+2 „sitzt“ (im Fluss), Kette 1–2 nur aus dem Kopf (sk) → sitzt; Häppchen 3 sitzt ohne Kette → aus dem Kopf (Kette fehlt) */
 const st31=MEM.C.map((P,k)=>({sig:P.sig,a:P.a,b:P.b,st:k<3?3:0,box:k<3?1:0,due:T0+DAY,reps:1,fails:0,last:0}));MEMS.aw.v10={cv:2,n:st31.length,ch:st31,sn:[],sk:[undefined,1],fd:[],whole:{days:[],due:0,n:0},lat:0,spot:{k:2,a:1,b:4}};memSaveAll();openMem(it);
 o.mig=[v().m5,v().ch.slice(0,4).map(c=>c.st).join(''),!!v().spot,lbl(awPick())];
 /* 10. langer Formteil (> 3 Häppchen) → einmal ganz am Stück, nach der Kette */
 MEMS.aw={};openMem(it);MEM.F=[{s:0,e:4,lab:'A',t0:0,t1:0},{s:5,e:C().length-1,lab:'B',t0:0,t1:0}];C().forEach((P,k)=>P.f=k<=4?0:1);v().ch.forEach((c,k)=>{if(k<=4)c.st=3});
 o.form=[lbl(awPick()),awNeedForm(0),awNeedForm(1)];awNext();o.formRun=[MEM.run.timed,MEM.run.dark,MEM.run.anchor];
 return o}
