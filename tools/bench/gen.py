"""Random Synthesia-style piano video with exact ground truth.
usage: gen.py SEED OUTDIR  -> OUTDIR/SEED.mp4, OUTDIR/SEED.json"""
import cv2, numpy as np, json, subprocess, sys, random, colorsys, math

seed = int(sys.argv[1]); out = sys.argv[2]
R = random.Random(seed)
WPC = [0, 2, 4, 5, 7, 9, 11]
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'H']

# ---------- style ----------
W, H, FPS = 1280, 720, R.choice([25, 30, 30, 60])
lo, hi = R.choice([(21, 108), (21, 108), (36, 96), (36, 84), (48, 84), (48, 79), (53, 77)])
lowres = R.choice([None, None, 360, 480])
crf = R.choice([20, 24, 28, 32])
kbH = int(H * R.uniform(0.14, 0.30))
kbY = H - kbH - (int(H * R.uniform(0, 0.08)) if R.random() < 0.3 else 0)
bratio_w = R.uniform(0.5, 0.66); bratio_h = R.uniform(0.58, 0.68)
pps = R.uniform(120, 420)
def hue_rgb(h, s=0.75, v=0.95):
    r, g, b = colorsys.hsv_to_rgb(h % 1, s, v); return (int(r * 255), int(g * 255), int(b * 255))
one_color = R.random() < 0.3
hr = R.random(); hl = (hr + R.uniform(0.25, 0.75)) % 1
RC = hue_rgb(hr, R.uniform(0.55, 0.9), R.uniform(0.8, 1)); LC = RC if one_color else hue_rgb(hl, R.uniform(0.55, 0.9), R.uniform(0.8, 1))
black_shade = R.uniform(0.55, 1.0)          # lit black keys darker
bg = R.choice(['solid', 'grad', 'noise'])
bgc = tuple(R.randint(5, 40) for _ in range(3))
labels = R.random() < 0.5
label_dark = R.random() < 0.5
pills = R.random() < 0.25          # short notes drawn as narrow rounded pills
glow = R.random() < 0.5
sparkle = R.random() < 0.4
bar_border = R.random() < 0.4
lit_part = R.choice([1.0, 1.0, 0.6])         # some videos only light the lower part of a key
hitline = R.random() < 0.6
intro = R.choice([0, 2, 3, 4]); outro = R.choice([0, 2, 3])
keys_x_jitter = R.uniform(0, 0.03)           # slightly irregular drawing
style = dict(label_dark=label_dark, pills=pills, seed=seed, fps=FPS, lo=lo, hi=hi, lowres=lowres, crf=crf, kbH=kbH, pps=round(pps), one_color=one_color, labels=labels, glow=glow,
             sparkle=sparkle, bar_border=bar_border, lit_part=lit_part, intro=intro, outro=outro, bg=bg)

whites = [m for m in range(lo, hi + 1) if m % 12 in WPC]; ww = W / len(whites)
pos = {}; wi = 0
for m in range(lo, hi + 1):
    if m % 12 in WPC: pos[m] = (wi * ww, ww, False); wi += 1
    else: pos[m] = (wi * ww - ww * bratio_w / 2 + ww * R.uniform(-keys_x_jitter, keys_x_jitter), ww * bratio_w, True)

# ---------- song (relative to song start) ----------
def inr(m): return max(lo, min(hi, m))
notes = []
first = R.choice([0.15, 0.5, 1.0, 2.0])  # first note can come right when the keyboard appears
t = first; center_r = inr(R.randint(64, 79)); center_l = inr(R.randint(43, 55))
if center_l >= center_r - 7: center_l = inr(center_r - 12)
song_len = R.uniform(10, 16)
m = center_r
while t < song_len:
    kind = R.random()
    if kind < 0.15: step = 0                     # repeated note
    elif kind < 0.35: step = R.choice([-1, 1])     # semitone step (neighbour key!)
    else: step = R.choice([-4, -3, -2, 2, 3, 4, 5, -5, 7])
    m = inr(m + step) if abs(m + step - center_r) < 9 else inr(center_r)
    d = R.choice([0.12, 0.18, 0.25, 0.35, 0.5, 0.75, 1.0])
    gap = R.choice([0.04, 0.06, 0.08, 0.12, 0.2]) if step == 0 else R.choice([0, 0.03, 0.08, 0.15])
    notes.append(dict(m=m, s=round(t, 3), d=round(d, 3), h='R')); t += d + gap
t = first
while t < song_len:
    root = inr(center_l + R.choice([0, 2, 5, 7, -3]))
    shape = R.choice([[0, 7], [0, 4, 7], [0, 7, 12], [0, 3, 7], [0], [0, 1]])  # [0,1] = cluster of two neighbour keys
    d = R.choice([0.5, 1.0, 1.5, 2.2])
    for o in shape:
        mm = inr(root + o)
        if not any(n['m'] == mm and abs(n['s'] - t) < d + 0.1 for n in notes): notes.append(dict(m=mm, s=round(t, 3), d=round(d - 0.08, 3), h='L'))
    t += d
# remove overlaps on the same key (impossible on a piano)
notes.sort(key=lambda n: (n['m'], n['s'])); clean = []
for n in notes:
    if clean and clean[-1]['m'] == n['m'] and n['s'] < clean[-1]['s'] + clean[-1]['d'] + 0.03:
        clean[-1]['d'] = round(max(0.06, n['s'] - clean[-1]['s'] - 0.05), 3)
        if clean[-1]['d'] < 0.06: continue
    clean.append(n)
notes = sorted(clean, key=lambda n: n['s'])
song_dur = max(n['s'] + n['d'] for n in notes) + 1.0
total = intro + song_dur + outro

def shade(c, b): return tuple(int(v * black_shade) for v in c) if b else c
def bgimg(f):
    img = np.zeros((H, W, 3), np.uint8)
    if bg == 'solid': img[:] = bgc
    elif bg == 'grad':
        g = np.linspace(0, 1, H)[:, None, None]; img[:] = (np.array(bgc) * (0.4 + 0.8 * g)).clip(0, 255).astype(np.uint8)
    else:
        rs = np.random.RandomState(7); base = rs.randint(0, 25, (H // 8, W // 8, 3)).astype(np.uint8); img[:] = cv2.resize(base, (W, H)) + np.array(bgc, np.uint8) // 2
    return img
BG = bgimg(0)
name = f'{out}/{seed}.mp4'
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if lowres: cmd += ['-vf', f'scale=-2:{lowres},scale={W}:{H}']
cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), name]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(int(total * FPS)):
    tv = f / FPS
    if tv < intro:
        img = np.zeros((H, W, 3), np.uint8); img[:] = (R.randint(20, 60), 10, 50) if f == 0 else img[:]
        img[:] = (40, 15, 70); cv2.circle(img, (W // 2, H // 2), int(80 + 50 * tv), hue_rgb(seed * 0.13), -1)
        cv2.putText(img, 'CHANNEL', (420, 150), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 6)
    elif tv >= intro + song_dur:
        img = np.zeros((H, W, 3), np.uint8); img[:] = (25, 25, 25); cv2.putText(img, 'SUBSCRIBE', (300, 360), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 60, 60), 7)
    else:
        t = tv - intro; img = BG.copy(); on = {}
        for n in notes:
            c = RC if n['h'] == 'R' else LC; x, w, b = pos[n['m']]
            y1 = kbY - (n['s'] - t) * pps; y0 = y1 - n['d'] * pps
            if y1 > 0 and y0 < kbY:
                inset = w * 0.22 if (pills and n['d'] <= 0.35) else 2
                p0 = (int(x + inset), int(max(0, y0))); p1 = (int(x + w - inset), int(min(kbY - 1, y1)))
                cv2.rectangle(img, p0, p1, shade(c, b), -1)
                if bar_border: cv2.rectangle(img, p0, p1, tuple(int(v * 0.6) for v in c), 2)
                if labels and p1[1] - p0[1] > 22: cv2.putText(img, NAMES[n['m'] % 12], (int(x + w / 2 - 7), p1[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5 if w < 40 else 0.9, (30, 30, 30) if label_dark else (255, 255, 255), 2)
            if n['s'] <= t < n['s'] + n['d']: on[n['m']] = shade(c, b)
        if hitline: cv2.line(img, (0, kbY - 2), (W, kbY - 2), hue_rgb(seed * 0.31, 0.6, 0.9), 3)
        kb = np.zeros((kbH, W, 3), np.uint8)
        for pb in (False, True):
            for mm in range(lo, hi + 1):
                x, w, b = pos[mm]
                if b != pb: continue
                hh = int(kbH * bratio_h) if b else kbH
                base = (20, 20, 20) if b else (240, 240, 240)
                cv2.rectangle(kb, (int(x + 0.5), 0), (int(x + w - 1), hh), base, -1)
                if mm in on:
                    top = int(hh * (1 - lit_part))
                    cv2.rectangle(kb, (int(x + 0.5), top), (int(x + w - 1), hh), on[mm], -1)
                if not b: cv2.line(kb, (int(x), 0), (int(x), kbH), (110, 110, 110), 1)
        img[kbY:kbY + kbH] = kb[:min(kbH, H - kbY)]
        if glow and on:
            y0g = max(0, int(kbY - ww * 4)); y1g = min(H, int(kbY + ww * 4))
            gl = np.zeros((y1g - y0g, W, 3), np.float32)
            for mm, c in on.items():
                x, w, b = pos[mm]; cv2.circle(gl, (int(x + w / 2), kbY - y0g), int(ww * 1.2), c, -1)
            gl = cv2.GaussianBlur(gl, (0, 0), ww * 0.8)
            img[y0g:y1g] = np.clip(img[y0g:y1g].astype(np.float32) + gl * 0.55, 0, 255).astype(np.uint8)
        if sparkle:
            rs = np.random.RandomState(f)
            for mm in on:
                x, w, b = pos[mm]
                for _ in range(6): cv2.circle(img, (int(x + w / 2 + rs.randn() * ww), int(kbY + rs.randn() * kbH * 0.3)), rs.randint(1, 4), (255, 255, 230), -1)
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait()
json.dump(dict(style=style, notes=notes, intro=intro), open(f'{out}/{seed}.json', 'w'))
print(json.dumps(style))
