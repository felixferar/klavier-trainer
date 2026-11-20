"""v5.35: Takt-Schnitt (Zeilen an Taktanfängen/Auftakten; Fly Me = die 8 vom Nutzer abgenommenen Zeilen). Vorher v5.28: Standardisierte Aufteilung an echten Noten (Fly Me to the Moon `Wa8fAoJmjQA`, Für Elise `tOpdCxy7N5M`, aus den Diagnosen).
Häppchen nach Last (Einzelton 1,0 · zwei Töne 1,4 · ab 3 Tönen 1,8; Ziel 16, Korridor 12–22, max. 26, weiche Grenze 12 s), Schnitte an Ruheton/Atempause/Harmoniewechsel,
4–6 Formteile mit Buchstaben. Dazu: Übernahme des Lernstands aus v5.26/5.27 (Formteile als Lerneinheit) – was saß, sitzt weiter.
usage: python3 tools/bench/haeppchentest.py $PWD/web/index.html"""
import sys, asyncio, json, os
from playwright.async_api import async_playwright
SONGS = json.load(open(os.path.join(os.path.dirname(__file__), 'fixtures', 'haeppchen_songs.json')))
JS = r"""(S)=>{window.toast=()=>{};window.AW_NOLOOP=true;const o={};
 const load=(id,ns)=>{const it={id,type:'midi',title:id,artist:'x',data:b64FromBuf(writeMidi(ns.map(([m,s,d,h])=>({m,start:s,dur:d,hand:h}))))};LIB=[it];save('kt_lib',LIB);openMem(it);return it};
 for(const k of ['fly_me','fuer_elise']){MEMS={};load(k,S[k]);
   o[k]={F:MEM.F.map(F=>F.lab).join(' '),n:MEM.C.length,first:[MEM.C[0].a,MEM.C[0].b],L:MEM.C.map(P=>P.L),dur:MEM.C.map(P=>+(MEM.gs[P.b].start-P.t0).toFixed(1)),
     mid:MEM.takt?MEM.C.slice(1).filter(P=>!MEM.takt.S.some(x=>Math.abs(x-P.t0)<0.02)).length:99,takt:MEM.takt&&[MEM.takt.beat,MEM.takt.M],cut:MEM.C.slice(0,-1).map(P=>+MEM.gs[P.b+1].start.toFixed(1)),
     twin:MEM.C.map(P=>P.twin)}}
 /* Übernahme v5.27 (cv 1): Fly Me mit Teil 1 sitzt (13 Anschläge), Teil 2 kennengelernt (21 Anschläge), Rest neu */
 MEMS={};load('fly_me',S.fly_me);const gs=MEM.gs,sig=(a,b)=>{const x=[];for(let q=a;q<=b;q++)x.push(awGSig(gs[q]));return x.join('|')},cuts=[[0,12],[13,33],[34,43],[44,60],[61,79],[80,gs.length-1]];
 MEMS.fly_me={v10:{cv:1,n:6,ch:cuts.map(([a,b],i)=>({sig:sig(a,b),st:i===0?3:i===1?1:0,h:null,box:i===0?1:0,due:i===0?Date.now()+5e7:0,reps:1,fails:0,last:0})),sn:[],whole:{days:[],due:0,n:0},lat:0.02}};memSaveAll();
 openMem(LIB[0]);const v=MEMS.fly_me.v10;o.mig=[v.cv,v.ch.map(c=>c.st).join(''),v.lat,v.ch[0].box];o.next=awPick();
 return o}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(viewport={'width': 780, 'height': 360}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(2500); await pg.evaluate("localStorage.clear()")
        r = await pg.evaluate(JS, SONGS); await br.close()
    print(json.dumps(r, ensure_ascii=False), errs)
    f, e = r['fly_me'], r['fuer_elise']
    c = {'Fly Me: Takt erkannt (Schlag 0,667 s, 4/4), 8 Zeilen': f['takt'] == [0.667, 8] and f['n'] == 8,
         'Fly Me: erste Zeile = Anschlag 1–13': f['first'] == [0, 12],
         'Fly Me: Schnitte genau an den abgenommenen Zeilen (0:11,7 · 0:21,6 Auftakt · 0:32,3 Auftakt · 0:43,7 · 0:54,3 · 1:04,4 Auftakt · 1:15,0 Auftakt)': f['cut'] == [11.7, 21.6, 32.3, 43.7, 54.3, 64.4, 75.0],
         'Fly Me: Zeile 5 und 6 sind Zwillinge von 1 und 2': f['twin'][4] == 0 and f['twin'][5] == 1,
         'Fly Me: keine Zeile länger als 12 s, Last ≤ 22': max(f['dur']) <= 12.5 and max(f['L']) <= 22,
         'Für Elise: Takt erkannt, 8 Zeilen, Last ≤ 23': e['takt'] is not None and e['n'] == 8 and max(e['L']) <= 23,
         'jeder Schnitt liegt auf einem Taktanfang oder Auftakt (beide Songs)': f['mid'] == 0 and e['mid'] == 0,
         'Übernahme v5.27: Teil 1 sitzt → Zeile 1 sitzt; Teil 2 kennengelernt → Zeile 2 kennengelernt; zweites A sitzt als Zwilling; Rest neu': r['mig'][0] == 2 and r['mig'][1] == '31003000' and r['mig'][2] == 0.02 and r['mig'][3] == 1,
         'danach geht es mit Zeile 2 aus dem Kopf weiter': r['next'] == {'k': 1, 'mode': 'head'},
         'keine Fehler': not errs}
    for k, v in c.items(): print(('OK  ' if v else 'FAIL') + ' ' + k)
    print('OK' if all(c.values()) else 'FEHLER'); sys.exit(0 if all(c.values()) else 1)
asyncio.run(main())
