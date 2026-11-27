"""v5.71/v5.73 „Hand zeigen“ im Auswendig-Modus (v5.73 abgespeckt: nur Farben, Zahl auf jedem Ton, Klammer – keine Schilder, Pfeile, Dreiecke, Streifen). Felix 27.11.: „Ich weiß nicht, wo meine Hände hin müssen.“ Eine Zahl auf jedem Ton beantwortet das nicht.
Prüft: Lage aus dem Fingersatz (fünf weiße Tasten unter der Hand), Klammer L/R auf der Klaviatur, Schild „… Hand hierher“ nur für das NÄCHSTE Versetzen,
Zahlen auf den Balken nur am Anfang einer Lage / bei neuem Akkord / am Zeilenanfang (auf der Zieltaste immer), EIN Warnzeichen mit Grund (brechen/springen/zuviel),
kein Hinweis bei „anders“, Stufe „Aus dem Kopf“: Klammer nur mit sichtbarem Griff, Schalter „Hand zeigen“ aus = jede Zahl wie v5.67.
usage: python3 tools/bench/handzeigentest.py $PWD/web/index.html"""
import sys, os, asyncio
from playwright.async_api import async_playwright
app = 'file://' + os.path.abspath(sys.argv[1])
JS = r"""async()=>{const o={};const ns=[];let t=1.5;
 for(let r=0;r<3;r++){for(const m of [60,62,64,65,67,65,64,62])ns.push({m,start:(t+=0.5),dur:0.4,hand:'R'});   // Fünftonlage C–G
   for(const m of [72,74,76,77,79])ns.push({m,start:(t+=0.5),dur:0.4,hand:'R'});                                  // eine Oktave höher: Hand versetzt
   t+=0.5;for(let q=0;q<2;q++){for(const m of [60,64,67])ns.push({m,start:t,dur:0.4,hand:'R'});t+=0.6}             // Akkord zweimal
   ns.push({m:48,start:t-6,dur:1,hand:'L'});ns.push({m:43,start:t-3,dur:1,hand:'L'})}
 ns.sort((a,b)=>a.start-b.start||a.m-b.m);
 const it={id:'hz',type:'midi',title:'T',artist:'x',data:b64FromBuf(writeMidi(ns)),video:{v:2}};LIB=[it];S.fingers=true;S.handShow=undefined;S.fingShow=undefined;window.AW_NOLOOP=1;
 openMem(it);zlStart({k:0,stage:1,t:0});let R=MEM.run;if(R.demo)zlDemoEnd(R);
 const cv=document.querySelector('#zlCv');
 let KL=0;const texts=()=>{const c=cv.getContext('2d'),ft=c.fillText.bind(c),st=c.stroke.bind(c),T=[];KL=0;c.fillText=(s,x,y)=>{T.push(String(s));return ft(s,x,y)};
   c.stroke=(...a)=>{const col=String(c.strokeStyle).toLowerCase();if(c.lineWidth===4&&(col===ZL.col.lh.toLowerCase()||col===ZL.col.rh.toLowerCase()))KL++;return st(...a)};zlDraw();c.fillText=ft;c.stroke=st;return T};   // KL = gezeichnete Klammern
 const L=zlLagen();o.nR=L.R.length;const s0=L.R[0];o.first=[s0.lo,s0.hi];
 const rn=MEM.notes.filter(n=>n.hand==='R');o.fingers5=rn.slice(0,5).map(n=>n.fing).join('');
 o.showFirst=rn[0].fShow===true;o.hideInside=rn.slice(1,8).every(n=>n.fShow===false);
 const up=rn.find(n=>n.midi===72);o.showAfterMove=up.fShow===true&&up.lgNeu===true;
 const ch=rn.filter(n=>n.midi===67&&Math.abs(n.dur-0.4)<0.05&&rn.some(q=>q!==n&&Math.abs(q.start-n.start)<0.01&&q.midi===60));o.chord1=ch[0]&&ch[0].fShow===true;o.chord2=ch[1]&&ch[1].fShow===false;
 // Zeichnung am Zeilenanfang
 let T=texts();o.klammer=KL;o.keinSchild=!T.includes('L')&&!T.includes('R');o.digits=T.filter(x=>/^[1-5]$/.test(x)).length;{const sv=MEM.notes.map(n=>n.fShow);MEM.notes.forEach(n=>n.fShow=false);o.digitsOhne=texts().filter(x=>/^[1-5]$/.test(x)).length;MEM.notes.forEach((n,i)=>n.fShow=sv[i])}
 // kurz vor dem Versetzen: Schild sichtbar, genau eines je Hand
 const j=MEM.gs.findIndex(g=>g.mids.has(72));R.pos=Math.max(R.a,j-2);R.vt=MEM.gs[R.pos].start-0.15;o.inLine=j<=R.b;T=texts();o.hier=T.filter(x=>/hierher/.test(x)).length;
 // Warnzeichen: Marke am aktuellen Griff → Grund als Text; „anders“ → nichts
 const cur=MEM.notes.filter(n=>MEM.gs[R.pos].mids.has(n.midi)&&Math.abs(n.start-MEM.gs[R.pos].start)<0.2);cur.forEach(n=>n.fingMark='brechen');T=texts();o.warn=T.some(x=>/Weiter Griff|Sprung|Zu viele/.test(x))||T.includes('!')||T.includes('⚠');
 cur.forEach(n=>n.fingMark='anders');T=texts();o.anders=!T.some(x=>/Weiter Griff|Sprung|Zu viele/.test(x))&&!T.includes('⚠');cur.forEach(n=>n.fingMark='');
 // Schalter aus: keine Klammer, jede Zahl
 R.pos=R.a;R.vt=MEM.gs[R.pos].start-0.15;const dOn=texts().filter(x=>/^[1-5]$/.test(x)).length;S.handShow=false;T=texts();o.offLab=KL===0;o.offDigits=T.filter(x=>/^[1-5]$/.test(x)).length;o.onDigits=dOn;S.handShow=undefined;
 // Stufe „Aus dem Kopf“: keine Klammer, kein Schild
 zlStart({k:0,stage:3,t:0});R=MEM.run;if(R.demo)zlDemoEnd(R);R=MEM.run;o.goldStage=R.stage;o.goldDemo=!!R.demo;T=texts();o.goldVis=zlVis(R,R.pos);o.goldStart=!!o.goldVis===(KL>0);   // der Startgriff ist als Anker sichtbar → Klammer dazu
 R.pos=R.a+2;R.vt=MEM.gs[R.pos].start-0.15;o.goldHidden=!zlVis(R,R.pos);T=texts();o.goldLab=KL===0;
 // Einstellung
 const sw=document.querySelector('#handShow');o.sw=!!sw;if(sw){sw.checked=false;sw.dispatchEvent(new Event('change'));o.saved=S.handShow===false&&(load('kt_settings',{})||{}).handShow===false;sw.checked=true;sw.dispatchEvent(new Event('change'));o.saved2=S.handShow===true}
 o.ver=document.querySelector('#verTxt').textContent;return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(app); await pg.wait_for_timeout(400); r = await pg.evaluate(JS); await br.close()
    c = {'Fünftonlage C–G: Finger 1-2-3-4-5, Lage deckt C bis G': r['fingers5'] == '12345' and r['first'][0] <= 60 and r['first'][1] >= 67 and r['first'][1] - r['first'][0] <= 9,
         'Hand versetzt eine Oktave höher: neue Lage': r['nR'] >= 2 and r['showAfterMove'],
         'Zahl auf jedem Balken: die frühere Regel „nur am Anfang einer Lage“ blendet nichts mehr aus': r['digits'] >= 4 and r['digitsOhne'] == r['digits'],
         'Klammer je Hand auf der Klaviatur, kein L/R-Schild': r['klammer'] >= 1 and r['keinSchild'],
         'kein Schild „… Hand hierher“ mehr, auch nicht vor dem Versetzen': r['inLine'] and r['hier'] == 0,
         'kein Warnzeichen und kein Warntext mehr, auch an markierten Griffen': not r['warn'],
         '„hier anders“ zeigt keinen Hinweis': r['anders'],
         'Schalter aus: keine Klammer, gleich viele Zahlen': r['offLab'] and r['offDigits'] == r['onDigits'],
         'Stufe „Aus dem Kopf“: Klammer nur zusammen mit einem sichtbaren Griff (Startgriff, Hilfe), sonst nichts': r['goldStage'] >= 3 and r['goldStart'] and r['goldHidden'] and r['goldLab'],
         'Einstellung „Hand zeigen“ da und wird gespeichert': r['sw'] and r.get('saved') and r.get('saved2'),
         'Version 5.75': r['ver'].startswith('Version 5.75'),
         'keine JS-Fehler': not errs}
    for k, v in c.items(): print(('OK   ' if v else 'FEHL ') + k)
    if not all(c.values()): print(r, errs)
    sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
