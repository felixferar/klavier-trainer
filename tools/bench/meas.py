"""Messung D2-Nachfolger: spielt eine Aufnahme mit instrumentierter Kopie (meas.html) nach und
speichert alle Ereignisse vor dem Geisterfilter + Farbprotokoll pro Taste.
usage: meas.py phone DIAGDIR OUT.json   |   meas.py bench REC.json OUT.json"""
import json, sys, os, glob, base64, asyncio
from playwright.async_api import async_playwright
import tempfile, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(tempfile.mkdtemp(), 'instr.html')
subprocess.check_call([sys.executable, os.path.join(HERE, 'instrument.py'), TMP])
APP = 'file://' + TMP
mode, src, outf = sys.argv[1:4]

async def go():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(300)
        handy = False
        if mode == 'phone':
            rec = json.load(open(src + '/rec.json')); meta = json.load(open(src + '/meta.json'))
            enc = lambda f: 'data:image/jpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
            searches = sorted(glob.glob(src + '/search*_*.jpg'), key=lambda f: int(os.path.basename(f)[6:].split('_')[0]))
            rel = {'img': enc(src + '/still.jpg'), 'rows': meta['scanRows'], 'search': [{'t': float(os.path.basename(f).rsplit('_', 1)[1][:-4]), 'img': enc(f)} for f in searches]}
            info = await pg.evaluate("""async (o)=>{const load=s=>new Promise(r=>{const i=new Image();i.onload=()=>{const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);r(x.getImageData(0,0,i.width,i.height))};i.src=s});
              const img=await load(o.img),fr=[];for(const s of o.search){const im=await load(s.img);im.t=s.t;fr.push(im)}
              scanImg=img;scanRows=o.rows;scanDet=detectKeys(img,o.rows.yA);if(!scanDet)return null;scanOct=0;scanFrames=fr;
              const keys=keyLayout(scanDet,0);restColors(keys,[img,...fr.slice(-5)],o.rows);window.__handy=true;return {keys,kw:scanDet.w/scanDet.W}}""", rel)
            rec['meta']['keys'] = info['keys']; rec['meta']['kw'] = info['kw']; handy = True
        else:
            rec = json.load(open(src))
        M = rec['meta']
        await pg.evaluate("""([M,h])=>{const keys=M.keys.map(k=>({...k}));
          Object.assign(SCAN,{oddR:[],normF:0,gapMin:null,lrow:null,fi:0,laneGap:null,laneBg:null,keyPx:null,barDelay:null,kw:M.kw,fromFile:!h,hole:false,lastF:null,on:true,keys,rest:null,state:null,lane:null,events:[],frames:0,vtMap:[],lastVt:0,scene:0,cut:null,okF:0,okT:null,oneColor:false,start:M.start,flog:null})}""", [M, handy])
        fr = rec['frames']
        for i in range(0, len(fr), 300):
            await pg.evaluate("""([M,frames])=>{for(const [f,b] of frames){if(!SCAN.on)break;const raw=atob(b),w=M.w;scanCore((r,x)=>{const i=(r*w+x)*3;return [raw.charCodeAt(i),raw.charCodeAt(i+1),raw.charCodeAt(i+2)]},w,M.n,f)}}""", [M, fr[i:i + 300]])
        res = await pg.evaluate("""()=>{SCAN.on=false;const fin=finishScan();const pg=SCAN.preGhost||[];
          return {start:SCAN.start,barDelay:SCAN.barDelay,keys:SCAN.keys.map(k=>({m:k.m,x:k.x,black:k.black})),
            notes:fin.map(n=>[n.m,n.start,n.dur,n.hand]),
            pre:pg.map(e=>({m:e.m,s:e.start,e:e.end,bar:!!e.bar,clean:!!e.clean,early:!!e.early,hue:e.hue})),
            flog:SCAN.flog.map(a=>a.map(r=>r.map(v=>Math.round(v*1000)/1000))),raw:SCAN.events.map(e=>({m:e.m,s:e.start,e:e.end,clean:!!e.clean})),found:SCAN.dbgFound||[],early:SCAN.dbgEarly||[],yT:scanRows.yT,laneHigh:laneHigh(scanRows,scanDet,scanFrames[0]),H:scanFrames[0].height,firstNote:SCAN.firstNote,dbg:SCAN.dbg,lane:SCAN.lane.map(l=>({ons:l.ons,offs:l.offs}))}}""")
        # which pre-ghost events survived: same as the ghost filter
        pre = res['pre']
        def has(e, f): return f is not e and f['bar'] and abs(f['m'] - e['m']) <= 2 and abs(f['s'] - e['s']) < 0.15
        for e in pre: e['kept'] = e['bar'] or (not any(has(e, f) for f in pre) and e['e'] - e['s'] >= 0.1)
        res['errs'] = errs
        json.dump(res, open(outf, 'w'))
        print(outf, len(res['notes']), 'Noten,', len(pre), 'vor Filter,', sum(not e['kept'] for e in pre), 'gefiltert', errs[:1])
        await br.close()
asyncio.run(go())
