"""Zieht aus dem privaten Diagnose-Archiv den neuesten Handy-Scan je Video (nur die Noten) für den Fingersatz-Prüfstand.
Schreibt tools/bench/fixtures/finger_handy.json – die Datei bleibt lokal (.gitignore), weil das Archiv privat ist.
usage: python3 tools/bench/fingerhandy.py [DIAG-ORDNER]     (Standard: $KLAVIER_DIAG oder /home/claude/klavier-diagnose)"""
import gzip, json, glob, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
root = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('KLAVIER_DIAG', '/home/claude/klavier-diagnose')
out = {}
for p in sorted(glob.glob(os.path.join(root, 'diag', '*_done.ktd.gz'))):
    try:
        f = gzip.open(p); h = f.read(8)
        if h[:4] != b'KTD1': continue
        meta = json.loads(f.read(struct.unpack_from('<I', h, 4)[0])); f.close()
    except Exception as e:
        print('übersprungen', os.path.basename(p), e); continue
    n = meta.get('notes')
    if not n or len(n) < 40: continue
    out[meta.get('videoId') or os.path.basename(p)] = {'datei': os.path.basename(p), 'app': meta.get('app', '')[:14], 'oneColor': bool(meta.get('oneColor')), 'notes': n}
dst = os.path.join(HERE, 'fixtures', 'finger_handy.json')
json.dump(out, open(dst, 'w'), separators=(',', ':'))
print(len(out), 'Songs →', dst)
