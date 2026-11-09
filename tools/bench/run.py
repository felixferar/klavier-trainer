"""Run the app's video-file conversion on bench videos and score it.
usage: run.py DIR SEED... [--par N]"""
import json, sys, asyncio, collections
from playwright.async_api import async_playwright
import os
APP = os.environ.get('APP') or 'http://127.0.0.1:8765/' + os.path.relpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'web', 'index.html'), '/')
args = sys.argv[1:]; par = 4
if '--par' in args: i = args.index('--par'); par = int(args[i + 1]); del args[i:i + 2]
D = args[0]; seeds = args[1:]
TOL = 0.07

def score(truth, got):
    exp = sorted(truth['notes'], key=lambda n: n['s'])
    if not got: return dict(exp=len(exp), got=0, hit=0, recall=0, extra=0, prec=0)
    oct_ = 0
    if truth['style']['hi'] - truth['style']['lo'] < 60:  # partial keyboard: octave may be estimated
        c = collections.Counter(g[0] - e['m'] for g in got for e in exp if (g[0] - e['m']) % 12 == 0)
        oct_ = c.most_common(1)[0][0]
    def cnt(sh): return sum(any(g[0] - oct_ == e['m'] and abs(g[1] - sh - e['s']) < TOL for g in got) for e in exp)
    cands = collections.Counter(round(g[1] - e['s'], 2) for g in got for e in exp if g[0] - oct_ == e['m'])
    shift = max([c for c, _ in cands.most_common(12)] or [0], key=cnt)
    # refine shift
    shift = max([shift + k * 0.005 for k in range(-8, 9)], key=cnt)
    durl=[]; used = set(); hit = 0; derr = []; hand_ok = 0; miss = []; serr = []
    for e in exp:
        cs = [i for i, g in enumerate(got) if i not in used and g[0] - oct_ == e['m'] and abs(g[1] - shift - e['s']) < TOL]
        if cs:
            i = min(cs, key=lambda i: abs(got[i][1] - shift - e['s'])); used.add(i); hit += 1
            derr.append(abs(got[i][2] - e['d']));
            if abs(got[i][2]-e['d'])>0.12: durl.append((e['m'],e['s'],e['d'],round(got[i][2],2)))
            serr.append(abs(got[i][1] - shift - e['s']))
            if got[i][3] == e['h'] or truth['style']['one_color']: hand_ok += 1
        else: miss.append((e['m'], e['s'], e['d']))
    extra = [(g[0] - oct_, round(g[1] - shift, 2), round(g[2], 2)) for i, g in enumerate(got) if i not in used]
    return dict(exp=len(exp), got=len(got), hit=hit, recall=round(hit / len(exp), 3), extra=len(extra), prec=round(hit / max(1, len(got)), 3),
                dur_err=round(sum(derr) / max(1, len(derr)), 3), dur_bad=sum(1 for x in derr if x > 0.12), start_err=round(max(serr or [0]), 3),
                hands=round(hand_ok / max(1, hit), 3), durl=durl[:6], oct=oct_, miss=miss[:8], extras=extra[:8])

async def one(br, seed, sem, res):
    async with sem:
        truth = json.load(open(f'{D}/{seed}.json'))
        ctx = await br.new_context(viewport={'width': 400, 'height': 800}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(400)
        await pg.evaluate('''()=>{const o=scanCore;window._rec=[];window.scanCore=function(px,w,n,f){const a=new Uint8Array(w*n*3);for(let r=0;r<n;r++)for(let x=0;x<w;x++){const p=px(r,x),i=(r*w+x)*3;a[i]=p[0];a[i+1]=p[1];a[i+2]=p[2]}
          if(!window._recMeta)window._recMeta={keys:SCAN.keys.map(k=>({m:k.m,x:k.x,black:k.black,rest:k.rest})),kw:SCAN.kw,start:SCAN.start,w,n};let s='';for(let i=0;i<a.length;i+=8192)s+=String.fromCharCode.apply(null,a.subarray(i,i+8192));window._rec.push([f,btoa(s)]);return o(px,w,n,f)}}''')
        await pg.set_input_files('#vidFile', f'{D}/{seed}.mp4')
        st = None
        for _ in range(240):
            await pg.wait_for_timeout(500)
            st = await pg.evaluate("()=>({done:!!(LIB[0]&&LIB[0].video),err:document.querySelector('#convErr').classList.contains('on')?document.querySelector('#convErrTxt').textContent:null})")
            if st['done'] or st['err']: break
        if st and st['done']:
            got = await pg.evaluate("()=>songForItem(LIB[0]).notes.map(n=>[n.midi,n.start,n.dur,n.hand0])")
            r = score(truth, got)
            rec = await pg.evaluate("()=>({meta:window._recMeta,frames:window._rec})")
            json.dump(rec, open(f'{D}/{seed}.rec.json', 'w'))
        else: r = dict(error=(st or {}).get('err') or 'timeout')
        r['style'] = truth['style']; r['js'] = errs[:2]; res[seed] = r
        await ctx.close()

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
        sem = asyncio.Semaphore(par); res = {}
        await asyncio.gather(*[one(br, s, sem, res) for s in seeds])
        await br.close()
    tot = dict(exp=0, hit=0, got=0, extra=0)
    for s in seeds:
        r = res[s]; st = r['style']
        tag = f"{s:>4} {st['lo']}-{st['hi']} fps{st['fps']} res{st['lowres']} crf{st['crf']} glow{int(st['glow'])} spk{int(st['sparkle'])} lab{int(st['labels'])} 1c{int(st['one_color'])} lit{st['lit_part']}"
        if 'error' in r: print(tag, 'ERROR', r['error'][:90], r['js']); continue
        for k in tot: tot[k] += r[k]
        print(tag, f"recall {r['recall']} prec {r['prec']} extra {r['extra']} durbad {r['dur_bad']} hands {r['hands']} serr {r['start_err']}", r['js'] or '')
        if r['recall'] < 1 or r['extra']: print('      miss', r['miss'], '\n      extra', r['extras'])
    print('TOTAL recall', round(tot['hit'] / max(1, tot['exp']), 3), 'precision', round(tot['hit'] / max(1, tot['got']), 3), 'extra', tot['extra'])
    json.dump(res, open(f'{D}/result.json', 'w'))
asyncio.run(main())
