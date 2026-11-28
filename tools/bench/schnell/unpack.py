import re, os, sys, glob, subprocess
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import diag
ref={}
for line in open(os.path.join(HERE,'refs/echt/README.md')):
    m=re.match(r'\|\s*([\w.]+\.mid)\s*\|[^|]*\|\s*([\w-]{11})\s*\|', line)
    if m: ref[m.group(2)]=m.group(1)
D=os.path.join(os.environ.get('KLAVIER_DIAG','/home/claude/klavier-diagnose'),'diag')
root=sys.argv[1]
for vid,mid in ref.items():
    fs=sorted(glob.glob(f'{D}/*_{vid}_done.ktd.gz'))
    print(vid, mid, len(fs), [os.path.basename(f)[:19] for f in fs])
    if not fs: continue
    f=fs[-1]
    out=f'{root}/{vid}'
    if os.path.exists(out+'/rec.json'): continue
    meta,frames=diag.load(f)
    diag.write(meta,frames,out)
    open(out+'/SOURCE.txt','w').write(os.path.basename(f)+'\n')
