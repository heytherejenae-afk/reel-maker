"""Polish pass (Meg-style finish): one big word at a time with key words in the brand
italic, a title tucked behind the person, Canva/PNG overlay pages that pop in, pop-up
photo/video cards, a hand-written note with an arrow. Writes final.mp4 plus see-through
layers (ProRes 4444 .mov) that all start at 0:00. Normally run by script_reel.py build.
usage: python3 polish.py plan.json base.mp4 outdir   (LIMIT=5 env renders only 5 s, for a quick check)
"""
import json, math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

plan = json.load(open(sys.argv[1])); BASE = sys.argv[2]; OUT = sys.argv[3]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
B = plan["brand"]
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
F = {k: v for k, v in plan["fonts"].items()}
_fc = {}
def font(k, size):
    if (k, size) not in _fc: _fc[(k, size)] = ImageFont.truetype(F[k], size)
    return _fc[(k, size)]
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', BASE]))
N = int(float(os.environ.get("LIMIT", dur)) * FPS)

def ease_back(x):  # 0..1 with a small overshoot
    x = max(0, min(1, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def shadowed(img, blur=14, alpha=.45, dy=5):
    a = np.array(img)[..., 3].astype(np.float32)
    pad = blur * 3
    big = Image.new('L', (img.width + pad * 2, img.height + pad * 2), 0)
    big.paste(Image.fromarray(a.astype(np.uint8)), (pad, pad + dy))
    sh = big.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    out.putalpha(sh.point(lambda v: int(v * alpha)))
    out.alpha_composite(img, (pad, pad))
    return out

def text_img(parts, gap=0.22, sh=(14, .45, 5)):
    """parts: list of (text, fontkey, size, colour) laid out on one line."""
    fs = [font(k, s) for _, k, s, _ in parts]
    asc = max(f.getmetrics()[0] for f in fs); desc = max(f.getmetrics()[1] for f in fs)
    widths = [f.getlength(t) for (t, *_), f in zip(parts, fs)]
    sp = [s * gap for _, _, s, _ in parts]
    w = int(sum(widths) + sum(sp[1:]) + 40); h = asc + desc + 40
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img); x = 20
    for i, ((t, k, s, c), f) in enumerate(zip(parts, fs)):
        if i: x += sp[i]
        d.text((x, 20 + asc), t, font=f, fill=rgb(c) + (255,), anchor='ls')
        x += widths[i]
    return shadowed(img, *sh)

class Layer:
    def __init__(s): s.img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); s.used = False
    def put(s, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
        if alpha <= 0.01 or scale <= 0.01: return
        if scale != 1: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
        if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
        if alpha < 1:
            a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
        s.img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2))) if (
            0 <= int(cx - im.width / 2) and 0 <= int(cy - im.height / 2) and int(cx - im.width / 2) + im.width <= W and int(cy - im.height / 2) + im.height <= H) else s._safe(im, int(cx - im.width / 2), int(cy - im.height / 2))
        s.used = True
    def _safe(s, im, x, y):
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.paste(im, (x, y)); s.img.alpha_composite(c)

# ---------- captions: one word at a time ----------
words = json.load(open(plan["words"]))
KEY = set(w.lower() for w in plan["key_words"])
cap = plan["captions"]
FIX = {k.lower(): v for k, v in plan.get('fixes', {}).items()}
def clean(w):
    w = w.strip().strip('.,?!').strip()
    return FIX.get(w.lower(), w)
merged = []
for w in words:
    if merged and w['w'].strip().startswith('-'): merged[-1] = dict(merged[-1], w=merged[-1]['w'] + w['w'].strip(), e=w['e'])
    else: merged.append(dict(w))
words = merged
caps = []
for i, w in enumerate(words):
    t = clean(w['w'])
    if not t: continue
    nxt = words[i + 1]['s'] if i + 1 < len(words) else w['e'] + .4
    end = min(nxt, w['e'] + .5)
    if any(a <= w['s'] < b for a, b in plan.get("no_caption", [])): continue
    raw = w['w'].strip().strip('.,?!').lower()
    key = t.lower().replace('-', '') in KEY or t.lower() in KEY or raw in KEY
    caps.append(dict(t=t.lower() if not key else t.lower(), s=w['s'], e=max(end, w['s'] + .18), key=key))
_wc = {}
def word_img(c):
    k = (c['t'], c['key'])
    if k not in _wc:
        if c['key']: _wc[k] = shadowed(text_img([(c['t'], 'key', cap['key_size'], B['key'])], sh=(9, .8, 3)), 26, .35, 6)
        else: _wc[k] = text_img([(c['t'], 'word', cap['size'], B['text'])], sh=(11, .6, 4))
    return _wc[k]

# ---------- titles ----------
def title_img(lines, max_w=1010):
    ims = []
    for t, k, s, c, _ in lines:  # shrink a long line until it fits the screen
        im = text_img([(t, k, s, c)])
        while im.width > max_w and s > 40:
            s = int(s * .93); im = text_img([(t, k, s, c)])
        ims.append(im)
    return ims

# ---------- cards ----------
def rounded(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    im = im.convert('RGBA'); im.putalpha(m); return im
def load_card_frames(c):
    cw, ch = c['w'], int(c['w'] * 4 / 3)
    n = int((c['end'] - c['start']) * FPS) + 2
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(c['src_start']), '-i', c['src'], '-frames:v', str(n),
                          '-vf', f'scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},fps={FPS}',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    fr = [Image.frombuffer('RGB', (cw, ch), raw[i:i + cw * ch * 3]) for i in range(0, len(raw) - cw * ch * 3 + 1, cw * ch * 3)]
    bw = 12; lab = None
    if c.get('label'):
        lab = text_img([(c['label'], 'key', 64, B['card_label'])], gap=0)
    out = []
    for f in fr:
        card = Image.new('RGBA', (cw + bw * 2, ch + bw * 2), (0, 0, 0, 0))
        border = Image.new('RGBA', card.size, rgb(B['card']) + (255,))
        card.alpha_composite(rounded(border, 44)); card.alpha_composite(rounded(f, 34), (bw, bw))
        if lab:
            pill_w = int(lab.width * .78); pill = Image.new('RGBA', (pill_w, 86), (0, 0, 0, 0))
            ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill_w - 1, 85), 43, fill=rgb(B['card']) + (255,))
            full = Image.new('RGBA', (card.width, card.height + 50), (0, 0, 0, 0)); full.alpha_composite(card)
            full.alpha_composite(pill, ((card.width - pill_w) // 2, card.height - 50))
            full.alpha_composite(lab, ((card.width - lab.width) // 2, card.height - 50 + 43 - lab.height // 2 + 4))
            card = full
        out.append(shadowed(card, blur=22, alpha=.4, dy=10))
    return out
for c in plan['cards']: c['frames'] = load_card_frames(c)

# ---------- hand-written note + arrow ----------
def note_img(n):
    f = font('hand', n['size']); lines = n['text'].split('\n')
    w = int(max(f.getlength(l) for l in lines) + 60); lh = int(n['size'] * 1.05)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x0, y0 = n['x'], n['y']
    for i, l in enumerate(lines): d.text((x0, y0 + i * lh), l, font=f, fill=rgb(B['note']) + (255,))
    # curved arrow from under the text to the target
    ax, ay = n['arrow_from']; bx, by = n['arrow_to']
    pts = []
    for k in range(41):
        t = k / 40; cx_, cy_ = (ax + bx) / 2 + n.get('bend', 120), (ay + by) / 2
        pts.append(((1 - t) ** 2 * ax + 2 * (1 - t) * t * cx_ + t * t * bx, (1 - t) ** 2 * ay + 2 * (1 - t) * t * cy_ + t * t * by))
    d.line(pts, fill=rgb(B['note']) + (255,), width=7, joint='curve')
    (px, py), (qx, qy) = pts[-4], pts[-1]; ang = math.atan2(qy - py, qx - px)
    for s in (-1, 1):
        a = ang + math.pi - s * .5
        d.line([(qx, qy), (qx + 38 * math.cos(a), qy + 38 * math.sin(a))], fill=rgb(B['note']) + (255,), width=7)
    return shadowed(img.crop(img.getbbox()), blur=8, alpha=.35, dy=3), img.getbbox()
notes = []
for n in plan.get('notes', []):
    im, bb = note_img(n); notes.append((n, im, bb))

# ---------- Canva overlay pages ----------
pngs = []
for p in plan.get('pngs', []):
    im = Image.open(p['png']).convert('RGBA'); bb = im.getbbox(); im = im.crop(bb)
    if p.get('backing'):
        pad = 36; bg = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        ImageDraw.Draw(bg).rounded_rectangle((0, 0, bg.width - 1, bg.height - 1), 40, fill=rgb(p['backing']) + (235,))
        bg.alpha_composite(im, (pad, pad)); im = bg
    pngs.append((p, im, ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)))

# ---------- person mask (only where a behind-title shows over a talking shot) ----------
from ai_edge_litert.interpreter import Interpreter
it = Interpreter(model_path=plan['seg_model']); it.allocate_tensors()
ii, oo = it.get_input_details()[0], it.get_output_details()[0]; mh, mw = ii['shape'][1:3]
def person_mask(frame):
    x = np.asarray(Image.fromarray(frame).resize((mw, mh), Image.BILINEAR), np.float32)[None] / 255.
    it.set_tensor(ii['index'], x); it.invoke(); m = it.get_tensor(oo['index'])[0, :, :, 0]
    m = np.clip((m - .35) / .3, 0, 1)
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)), np.float32) / 255.

# ---------- encoders ----------
def enc_alpha(name):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'prores_ks', '-profile:v', '4', '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0', '-qscale:v', '11',
                             os.path.join(OUT, name)], stdin=subprocess.PIPE)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', BASE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
fin = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', BASE, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                        '-c:a', 'copy', '-shortest', '-movflags', '+faststart', os.path.join(OUT, 'final.mp4')], stdin=subprocess.PIPE)
L_TITLE, L_TEXT = enc_alpha('2-title-behind-you.mov'), enc_alpha('3-captions.mov')
class _Null:
    class stdin:
        write = staticmethod(lambda b: None); close = staticmethod(lambda: None)
    wait = staticmethod(lambda: None)
L_CARDS = enc_alpha('4-overlays.mov')
EMPTY = bytes(W * H * 4)
talk = plan['talk_ranges']
def is_talk(t): return any(a <= t < b for a, b in talk)
titles = [(tt, title_img(tt['lines'])) for tt in plan['titles']]

def comp(base, layer):  # base float32 HxWx3, layer RGBA uint8
    a = layer[..., 3:4].astype(np.float32) / 255.
    return base * (1 - a) + layer[..., :3].astype(np.float32) * a

for fi in range(N):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    t = fi / FPS
    frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    lt, lx, lc = Layer(), Layer(), Layer()
    # titles
    behind_any = False
    for tt, ims in titles:
        if not (tt['start'] <= t < tt['end']): continue
        out_a = min(1, (tt['end'] - t) / .2)
        for k, (im, y) in enumerate(zip(ims, [l[4] for l in tt['lines']])):
            p = (t - tt['start'] - k * .18) / .32
            if p <= 0: continue
            L = lt if tt.get('behind') else lx
            L.put(im, W / 2, y + (1 - min(1, p)) * 40, scale=.9 + .1 * ease_back(p), alpha=min(1, p * 1.5) * out_a)
        behind_any |= bool(tt.get('behind'))
    for p, im, (cx, cy) in pngs:
        if p['start'] <= t < p['end']:
            pin = (t - p['start']) / .35; pout = (p['end'] - t) / .2
            lc.put(im, cx, p.get('y', cy / H) * H + (1 - min(1, pin)) * 30, scale=p.get('scale', 1) * (.8 + .2 * ease_back(pin)), alpha=min(1, pin * 2, pout))
    if lt.used and is_talk(t):
        m = person_mask(frame)
        arr = np.array(lt.img); arr[..., 3] = (arr[..., 3] * (1 - m)).astype(np.uint8); lt.img = Image.fromarray(arr)
    # notes
    for n, im, bb in notes:
        if n['start'] <= t < n['end']:
            p = min(1, (t - n['start']) / .55); a = min(1, (n['end'] - t) / .2)
            im2 = im.crop((0, 0, max(1, int(im.width * p)), im.height)) if p < 1 else im
            c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x0 = bb[0] - (im.width - (bb[2] - bb[0])) // 2; y0 = bb[1] - (im.height - (bb[3] - bb[1])) // 2
            if a < 1: im2 = im2.copy(); im2.putalpha(im2.getchannel('A').point(lambda v: int(v * a)))
            c.paste(im2, (x0, y0)); lx.img.alpha_composite(c); lx.used = True
    # captions
    for c in caps:
        if c['s'] <= t < c['e']:
            p = (t - c['s']) / .14
            lx.put(word_img(c), W / 2, cap['y'] * H, scale=.82 + .18 * ease_back(p), alpha=min(1, p * 2))
    # cards
    for c in plan['cards']:
        if c['start'] <= t < c['end']:
            k = min(len(c['frames']) - 1, int((t - c['start']) * FPS))
            pin = (t - c['start']) / .35; pout = (c['end'] - t) / .18
            sc = (.55 + .45 * ease_back(pin)) * (min(1, .7 + .3 * pout))
            lc.put(c['frames'][k], c['x'] * W, c['y'] * H, scale=sc, alpha=min(1, pin * 2, pout), rot=c.get('tilt', 0))
    # composite: base, title (behind), cards, text
    out = frame.astype(np.float32)
    for L, e in ((lt, L_TITLE), (lc, L_CARDS), (lx, L_TEXT)):
        if L.used:
            arr = np.array(L.img); out = comp(out, arr); e.stdin.write(arr.tobytes())
        else: e.stdin.write(EMPTY)
    fin.stdin.write(out.clip(0, 255).astype(np.uint8).tobytes())
    if fi % 150 == 0: print(f'{t:5.1f}s', flush=True)
for e in (fin, L_TITLE, L_TEXT, L_CARDS): e.stdin.close(); e.wait()
print('done', N)
