"""v4.83: Teile nach der Musik (Analyse 13.11.: Wake Me Up war in 53 starre 16er-Schnipsel zerlegt, oft mitten in klingenden Tönen).
Song mit Struktur Strophe(8 Takte) Refrain(8) Strophe(8) Refrain(8), linke Hand hält Akkorde H–G–D–A, Phrasen à 4 Takte (8 s).
Prüft: kein Schnitt, solange noch ein Ton klingt; Teile 6–16 s; Schnitte auf Phrasenanfängen; Wiederholungen als Zwillinge erkannt;
sitzt das Original, startet der Zwilling bei „Aus dem Kopf“; Anlauf (2 Anschläge davor, grau, von der App gespielt, zählen nicht);
alter Lernstand (starre Abschnitte) wird übernommen."""
import sys,asyncio,json
from playwright.async_api import async_playwright
JS=r"""async()=>{const w=ms=>new Promise(z=>setTimeout(z,ms));const o={};let tones=[];window.playTone=(m)=>tones.push(m);window.__instantEnd=true;
 const LH=[47,43,50,45],SA=[74,71,69,71, 74,76,74,71, 69,66,69,71, 74,71,69,0],SB=[66,69,71,74, 76,74,71,69, 71,69,66,64, 66,69,71,0];
 const notes=[];let t=0;const phrase=(P)=>{for(let bar=0;bar<4;bar++){notes.push({m:LH[bar],start:t,dur:1.98,hand:'L'});for(let q=0;q<4;q++){const m=P[bar*4+q];if(m)notes.push({m,start:t+q*0.5,dur:q===2&&bar===3?0.95:0.45,hand:'R'})}t+=2}};
 for(const part of ['A','A','B','B','A','A','B','B'])phrase(part==='A'?SA:SB);
 const it={id:'tt',type:'midi',title:'Teile',artist:'x',data:b64FromBuf(writeMidi(notes))};LIB=[it];
 /* alter Stand: mit starrer Aufteilung, erster alter Abschnitt sitzt */
 const gs0=memGroups(songFromMidi(bufFromB64(it.data),'x').notes),old=memSplit(gs0);MEMS['tt']={sig:gs0.length+':'+old.length,v6:1,secs:old.map((_,k)=>k===0?{lvl:3,box:1,due:Date.now()+864e5,runs:6,passed:1,watched:true}:{lvl:1,box:0,due:0,runs:0,passed:0})};
 openMem(it);const gs=MEM.gs,secs=MEM.secs;o.n=secs.length;o.oldN=old.length;
 const me=[];let m=-1;for(const g of gs){m=Math.max(m,g.end);me.push(m)}
 o.clean=secs.slice(0,-1).every(([a,b])=>gs[b+1].start-me[b]>=-0.06);
 o.durs=secs.map(([a,b])=>+(gs[b].end-gs[a].start).toFixed(1));o.starts=secs.map(([a])=>+gs[a].start.toFixed(2));
 o.twin=MEM.twin.slice();o.sig=MEMS['tt'].sig;o.mig=MEMS['tt'].secs.map(r=>r.passed>0?'P':r.lvl+':'+(r.fe||0));
 /* Zwilling: Original sitzt → Zwilling startet bei Aus dem Kopf */
 const rs=MEM.rec.secs;const ti=MEM.twin.findIndex(x=>x>=0);o.ti=ti;if(ti>=0){const orig=MEM.twin[ti];rs.forEach((r,i)=>{if(i!==ti){r.passed=1;r.box=1;r.due=Date.now()+864e5;r.chained=true}}); /* v4.84: schon verbunden, sonst käme zuerst „Verbinden“ */rs[orig].passed=1;rs[orig].box=1;rs[ti].passed=0;rs[ti].box=0;rs[ti].lvl=1;rs[ti].runs=0;rs[ti].tw=0;
   const nx=memPickNext(Date.now());o.twNext=nx&&nx.i===ti;o.twLvl=rs[ti].lvl;memHome();o.here=$('#memHere').textContent}
 /* Anlauf bei Abschnitt 2 */
 rs[1].watched=true;rs[1].runs=1;rs[1].lvl=1;rs[1].passed=0;rs[1].box=0;tones=[];memStart(1,false);const R=MEM.run;o.lead=(R.leadNs||[]).length;o.vt0=+(R.vt).toFixed(2);o.secStart=+gs[R.a].start.toFixed(2);
 await w(2600);o.leadTones=tones.length;o.posAfterLead=R.pos===R.a&&R.errors===0;o.range=R.lo<=Math.min(...R.leadNs.map(n=>n.midi));
 memStop();return o}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await br.new_page(viewport={'width':753,'height':360});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+sys.argv[1]);await pg.wait_for_timeout(3500);await pg.evaluate("localStorage.clear()")
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        ph=all(abs(s/8-round(s/8))<0.02 for s in r['starts'])
        c={'kein Schnitt in klingende Töne':r['clean'],'Teile 6–16 s':all(6<=d<=16 for d in r['durs']),
           'Schnitte auf Phrasenanfängen (alle 8 s)':ph,'nur 2 verschiedene Teile zu lernen (Strophe, Refrain)':sum(1 for x in r['twin'] if x<0)==2,
           'Wiederholungen als Zwillinge':sum(1 for x in r['twin'] if x>=0)>=r['n']//2,
           'Zwilling startet bei Schritt 1 (v4.85)':r.get('twNext') and r.get('twLvl')==1,
           'Anlauf: 2 Anschläge, früher Start':r['lead']>=2 and r['vt0']<r['secStart']-1,
           'Anlauf wird gespielt, zählt nicht':r['leadTones']>=2 and r['posAfterLead'],'Anlauf im Tastenbereich':r['range'],
           'neue Aufteilung gespeichert':r['sig'].startswith('p2:'),'alter Stand übernommen (Anfang sitzt)':r['mig'][0]=='P' and 'P' not in r['mig'][2:],
           'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await br.close()
asyncio.run(main())
