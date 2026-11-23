"""Effect pack (from the Arcads-style reel, 2026-11-23): orbit cards, glass widgets,
black-and-white glowing title, comment box. Each effect can sit BEHIND the person
(selfie segmenter mask) so the head and hands pass in front of it.

usage: python3 fx_pack.py fx.json base.mp4 out.mp4
fx.json = {"seg_model": ".../selfie_segmenter.tflite",
           "fonts": {"black": InterDisplay-Black.otf, "semi": InterDisplay-SemiBold.ttf, "serif": DMSerifDisplay-Italic.ttf},
           "brand": {"accent": "#E8875A", "accent2": "#EDBE3A", "green": "#2F4A35", "cream": "#F6EFDF"},
           "fx": [ {type: orbit|glass|mono|comment, start, end, ...}, ... ]}
See SKILL.md "Effect pack" for every field.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
plan = json.load(open(sys.argv[1])); BASE, OUT = sys.argv[2], sys.argv[3]
B = plan['brand']; FONTS = plan['fonts']
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
_fc = {}
def font(k, s):
    if (k, s) not in _fc: _fc[(k, s)] = ImageFont.truetype(FONTS[k], s)
    return _fc[(k, s)]
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease_back(x):
    x = clamp(x); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def with_alpha(im, a):
    if a >= .999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a))); return im

def shadow(img, blur=18, alpha=.4, dy=8, colour=(0, 0, 0)):
    pad = blur * 3
    out = Image.new('RGBA', (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    m = Image.new('L', out.size, 0); m.paste(img.getchannel('A'), (pad, pad + dy))
    m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    sh = Image.new('RGBA', out.size, colour + (0,)); sh.putalpha(m)
    out.alpha_composite(sh); out.alpha_composite(img, (pad, pad)); return out

def rounded_mask(w, h, r):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

class Canvas:
    def __init__(s): s.img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); s.used = False
    def put(s, im, cx, cy, scale=1., alpha=1., rot=0.):
        if alpha <= .01 or scale <= .01: return
        if abs(scale - 1) > .002: im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.BICUBIC)
        if abs(rot) > .05: im = im.rotate(rot, Image.BICUBIC, expand=True)
        im = with_alpha(im, alpha)
        x, y = int(cx - im.width / 2), int(cy - im.height / 2)
        if x >= 0 and y >= 0 and x + im.width <= W and y + im.height <= H: s.img.alpha_composite(im, (x, y))
        else:
            c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.paste(im, (x, y)); s.img.alpha_composite(c)
        s.used = True

# ---------------- text helpers ----------------
def text(t, k, s, colour, stroke=0, stroke_col=(0, 0, 0), track=0):
    f = font(k, s); asc, desc = f.getmetrics()
    w = int(f.getlength(t) + track * max(0, len(t) - 1) + stroke * 2 + 20); h = asc + desc + stroke * 2 + 20
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if track:
        x = 10 + stroke
        for ch in t:
            d.text((x, 10 + stroke), ch, font=f, fill=colour, stroke_width=stroke, stroke_fill=stroke_col); x += f.getlength(ch) + track
    else: d.text((10 + stroke, 10 + stroke), t, font=f, fill=colour, stroke_width=stroke, stroke_fill=stroke_col)
    return im.crop(im.getbbox())

def glow(im, radius=28, strength=1.6, colour=(255, 255, 255)):
    pad = radius * 3
    out = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = Image.new('L', out.size, 0); a.paste(im.getchannel('A'), (pad, pad))
    for r, k in ((radius, strength * .55), (radius // 3, strength * .5)):
        g = a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, k=k: int(min(255, v * k)))
        layer = Image.new('RGBA', out.size, colour + (0,)); layer.putalpha(g); out.alpha_composite(layer)
    out.alpha_composite(im, (pad, pad)); return out

# ---------------- 1. orbit cards ----------------
def card_img(path, w):
    src = Image.open(path).convert('RGB'); h = int(w * 4 / 3)
    sc = max(w / src.width, h / src.height); src = src.resize((math.ceil(src.width * sc), math.ceil(src.height * sc)), Image.LANCZOS)
    src = src.crop(((src.width - w) // 2, (src.height - h) // 2, (src.width - w) // 2 + w, (src.height - h) // 2 + h))
    bw = max(6, w // 36)
    card = Image.new('RGBA', (w + bw * 2, h + bw * 2), rgb(B['cream']) + (255,)); card.putalpha(rounded_mask(card.width, card.height, w // 10))
    ph = src.convert('RGBA'); ph.putalpha(rounded_mask(w, h, w // 10 - bw)); card.alpha_composite(ph, (bw, bw))
    return shadow(card, blur=16, alpha=.45, dy=10)

def prep_orbit(e):
    e['_cards'] = [card_img(p, e.get('card_w', 300)) for p in e['images']]
def draw_orbit(e, t, front, back):
    lt = t - e['start']; dur = e['end'] - e['start']; n = len(e['_cards'])
    cx, cy = e.get('cx', .5) * W, e.get('cy', .30) * H; rx, ry = e.get('rx', .40) * W, e.get('ry', .07) * H
    spin = e.get('speed', .22) * 2 * math.pi           # turns per second
    out_a = clamp((e['end'] - t) / .3)
    for i, im in enumerate(e['_cards']):
        p = ease_back((lt - i * .07) / .45)              # staggered pop-in
        if p <= 0: continue
        ang = i / n * 2 * math.pi + lt * spin
        depth = math.sin(ang)                            # +1 front, -1 back
        x = cx + rx * math.cos(ang) * (.6 + .4 * p); y = cy + ry * depth + 18 * math.sin(lt * 2.1 + i) - (i % 2) * 120 + 60
        sc = (.62 + .38 * (depth + 1) / 2) * (.4 + .6 * p) * e.get('scale', 1)
        rot = -math.cos(ang) * 14 + (i % 3 - 1) * 4
        a = min(1, p * 1.5) * out_a * (.85 + .15 * (depth + 1) / 2)
        (front if depth > 0 else back).append((depth, im, x, y, sc, a, rot))

# ---------------- 2. glass widgets ----------------
def glass_panel(bg_frame, x, y, w, h, tint=(255, 255, 255)):
    r = 44
    crop = Image.fromarray(bg_frame).crop((int(x), int(y), int(x + w), int(y + h))).filter(ImageFilter.GaussianBlur(26))
    arr = np.asarray(crop, np.float32); arr = arr * .62 + np.array(tint, np.float32) * .38   # frosted + brighter
    im = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert('RGBA')
    hl = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(hl)
    for k in range(h // 2):  # soft top highlight
        d.line([(0, k), (w, k)], fill=(255, 255, 255, int(46 * (1 - k / (h / 2)))))
    im.alpha_composite(hl)
    im.putalpha(rounded_mask(w, h, r))
    ImageDraw.Draw(im).rounded_rectangle((1, 1, w - 2, h - 2), r, outline=(255, 255, 255, 150), width=3)
    return im

def widget_content(wd, w, h, prog):
    """Draws the inside of a widget. prog 0..1 animates bars / rings / counters."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ink, soft = (34, 30, 28, 255), (34, 30, 28, 170); acc = rgb(wd.get('colour', B['accent'])) + (255,)
    pad = 34; kind = wd['kind']
    if wd.get('label'): d.text((pad, pad - 4), wd['label'], font=font('semi', 38), fill=soft)
    sub_col = rgb(wd.get('sub_colour', B['green'])) + (255,)
    if kind == 'number':
        val = wd['value']; num = ''.join(ch for ch in val if ch.isdigit() or ch == '.')
        shown = val
        if num and prog < 1:  # count up
            v = float(num) * ease_out(prog); dec = len(num.split('.')[1]) if '.' in num else 0
            shown = val.replace(num, f'{v:.{dec}f}')
        d.text((pad - 4, pad + 36), shown, font=font('black', wd.get('size', 120)), fill=ink)
        if wd.get('sub'): d.text((pad, h - pad - 44), wd['sub'], font=font('semi', 38), fill=sub_col)
    elif kind == 'bars':
        vals = wd['values']; n = len(vals); top = pad + 70; bot = h - pad - 10; gw = (w - pad * 2) / n
        for i, v in enumerate(vals):
            q = ease_out(prog * 1.6 - i * .12); bh = (bot - top) * v * q
            d.rounded_rectangle((pad + i * gw + 6, bot - bh, pad + (i + 1) * gw - 6, bot), 8,
                                fill=acc if i == n - 1 else (34, 30, 28, 90))
    elif kind == 'ring':
        cxr, cyr, rr = w / 2, pad + 50 + (h - pad * 2 - 100) / 2, min(w - pad * 2, h - pad * 2 - 120) / 2 - 10
        d.ellipse((cxr - rr, cyr - rr, cxr + rr, cyr + rr), outline=(34, 30, 28, 60), width=18)
        d.arc((cxr - rr, cyr - rr, cxr + rr, cyr + rr), -90, -90 + 360 * wd.get('value', .75) * ease_out(prog), fill=acc, width=18)
        f = font('black', int(rr * .62)); d.text((cxr, cyr), wd['centre'], font=f, fill=ink, anchor='mm')
        if wd.get('sub'): d.text((w / 2, h - pad - 4), wd['sub'], font=font('semi', 34), fill=sub_col, anchor='ms')
    elif kind == 'progress':
        d.text((pad, pad + 48), wd['title'], font=font('black', wd.get('size', 52)), fill=ink)
        y = h - pad - 26; d.rounded_rectangle((pad, y, w - pad, y + 22), 11, fill=(34, 30, 28, 50))
        d.rounded_rectangle((pad, y, pad + max(22, (w - pad * 2) * wd.get('value', 1) * ease_out(prog)), y + 22), 11, fill=acc)
    return im

def draw_glass(e, t, frame, back, front):
    lt = t - e['start']; out_a = clamp((e['end'] - t) / .3)
    for i, wd in enumerate(e['widgets']):
        p = (lt - wd.get('delay', i * .18)) / .5
        if p <= 0: continue
        w, h = wd['w'], wd['h']; cx, cy = wd['x'] * W, wd['y'] * H + 10 * math.sin(lt * 1.6 + i * 1.3)
        x0, y0 = int(clamp(cx - w / 2, 0, W - w)), int(clamp(cy - h / 2, 0, H - h))
        panel = glass_panel(frame, x0, y0, w, h)
        panel.alpha_composite(widget_content(wd, w, h, clamp((lt - wd.get('delay', i * .18)) / 1.1)))
        panel = shadow(panel, blur=20, alpha=.28, dy=10)
        (front if wd.get('front') else back).put(panel, x0 + w / 2, y0 + h / 2, scale=.7 + .3 * ease_back(p), alpha=min(1, p * 2) * out_a)

# ---------------- 3. black-and-white + glowing title behind ----------------
def prep_mono(e):
    t = text(e['title'], 'black', e.get('size', 300), (255, 255, 255), track=e.get('track', -6))
    if t.width > W * .9: t = t.resize((int(W * .9), int(t.height * W * .9 / t.width)), Image.LANCZOS)   # always fits the screen
    e['_title'] = glow(t, 30, 1.5)
    e['_sub'] = shadow(text(e['sub'], 'black', e.get('sub_size', 84), (255, 255, 255)), 12, .6, 4) if e.get('sub') else None
def mono_grade(frame, amt):
    f = frame.astype(np.float32)
    g = f @ np.array([.299, .587, .114], np.float32)
    g = np.clip((g - 128) * 1.28 + 118, 0, 255)                     # punchy contrast
    return f * (1 - amt) + g[..., None] * amt
def draw_mono(e, t, back, front):
    lt = t - e['start']; out_a = clamp((e['end'] - t) / .25)
    tin = lt - e.get('title_at', 0)
    if tin > 0:
        p = tin / .5
        back.put(e['_title'], W / 2, e.get('y', .2) * H + (1 - ease_out(p)) * 60, scale=1.18 - .18 * ease_out(p), alpha=min(1, p * 1.6) * out_a)
    if e['_sub'] is not None:
        sin_ = lt - e.get('sub_at', .3)
        if sin_ > 0:
            p = sin_ / .35
            front.put(e['_sub'], W / 2, e.get('sub_y', .72) * H, scale=.85 + .15 * ease_back(p), alpha=min(1, p * 2) * out_a)

# ---------------- 4. comment box ----------------
def heart(d, x, y, s, fill):
    d.ellipse((x, y, x + s * .55, y + s * .55), fill=fill); d.ellipse((x + s * .45, y, x + s, y + s * .55), fill=fill)
    d.polygon([(x + s * .03, y + s * .38), (x + s * .97, y + s * .38), (x + s / 2, y + s * .95)], fill=fill)
def comment_panel(e, lt):
    w, h = e.get('w', 860), e.get('h', 560)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 46, fill=(24, 24, 27, 238), outline=(255, 255, 255, 40), width=2)
    d.rounded_rectangle((w / 2 - 50, 18, w / 2 + 50, 28), 5, fill=(255, 255, 255, 90))
    d.text((w / 2, 74), 'Comments', font=font('black', 40), fill=(255, 255, 255), anchor='mm')
    d.line((0, 116, w, 116), fill=(255, 255, 255, 30), width=2)
    word = e['word']; ts, te = e['type_at'], e['type_at'] + .14 * len(word)
    typed = word[:int(clamp((lt - ts) / (te - ts)) * len(word))] if lt >= ts else ''
    posted = lt >= te + e.get('post_gap', .35)
    rows = list(e.get('others', []))
    yrow = 150
    avatar_cols = [(232, 135, 90), (47, 74, 53), (237, 190, 58), (120, 160, 140)]
    nrows = max(1, (h - 150 - 130) // 104)                    # rows that fit above the input bar
    show_rows = (rows + ([[e.get('handle', 'you'), word]] if posted else []))[-nrows:]
    for i, (who, msg) in enumerate(show_rows):
        mine = posted and i == len(show_rows) - 1
        pa = clamp((lt - te - e.get('post_gap', .35)) / .25) if mine else 1
        yy = yrow + i * 104 + (1 - ease_out(pa)) * 30
        c = avatar_cols[i % 4] + (int(255 * pa),)
        d.ellipse((40, yy, 112, yy + 72), fill=c)
        d.text((76, yy + 36), who[0].upper(), font=font('black', 34), fill=(255, 255, 255, int(255 * pa)), anchor='mm')
        d.text((134, yy + 4), who, font=font('semi', 30), fill=(170, 170, 175, int(255 * pa)))
        d.text((134, yy + 36), msg, font=font('black' if mine else 'semi', 38), fill=(255, 255, 255, int(255 * pa)))
        heart(d, w - 84, yy + 18, 34, (237, 73, 86, int(255 * pa)) if mine else (120, 120, 125, int(255 * pa)))
    # input bar
    iy = h - 110
    d.line((0, iy - 18, w, iy - 18), fill=(255, 255, 255, 30), width=2)
    d.ellipse((36, iy, 100, iy + 64), fill=rgb(B['accent']) + (255,))
    d.text((68, iy + 32), e.get('handle', 'you')[0].upper(), font=font('black', 30), fill=(255, 255, 255), anchor='mm')
    d.rounded_rectangle((120, iy + 2, w - 40, iy + 62), 30, outline=(255, 255, 255, 70), width=2)
    if typed and not posted:
        d.text((150, iy + 32), typed, font=font('black', 36), fill=(255, 255, 255), anchor='lm')
        cx_ = 150 + font('black', 36).getlength(typed) + 4
    else:
        d.text((150, iy + 32), 'Add a comment...', font=font('semi', 32), fill=(150, 150, 155), anchor='lm'); cx_ = 150
    if not posted and int(lt * 2.4) % 2 == 0: d.line((cx_, iy + 14, cx_, iy + 50), fill=(255, 255, 255), width=3)
    pressed = te <= lt < te + e.get('post_gap', .35)
    d.text((w - 70, iy + 32), 'Post', font=font('black', 32), fill=(0, 149, 246) if typed else (0, 95, 160), anchor='rm')
    if pressed: d.rounded_rectangle((w - 160, iy + 6, w - 48, iy + 58), 26, outline=(0, 149, 246), width=3)
    return shadow(im, blur=26, alpha=.5, dy=12)
def prep_comment(e):
    big = e.get('cta', [])
    e['_cta'] = [shadow(text(l, 'black', e.get('cta_size', 150), (255, 255, 255), stroke=9), 14, .55, 6) for l in big]
def draw_comment(e, t, back, front):
    lt = t - e['start']; out_a = clamp((e['end'] - t) / .25)
    p = lt / .5
    back.put(comment_panel(e, lt), W / 2, e.get('y', .17) * H + (1 - ease_out(p)) * 80, scale=.86 + .14 * ease_back(p), alpha=min(1, p * 2) * out_a)
    for i, im in enumerate(e['_cta']):
        q = (lt - e.get('cta_at', 0) - i * .3) / .28
        if q > 0:
            front.put(im, W / 2, (e.get('cta_y', .6) + i * .085) * H, scale=.6 + .4 * ease_back(q), alpha=min(1, q * 2) * out_a)

# ---------------- person mask ----------------
from ai_edge_litert.interpreter import Interpreter
it = Interpreter(model_path=plan['seg_model']); it.allocate_tensors()
ii, oo = it.get_input_details()[0], it.get_output_details()[0]; mh, mw = ii['shape'][1:3]
_prev = [None]
def person_mask(frame):
    x = np.asarray(Image.fromarray(frame).resize((mw, mh), Image.BILINEAR), np.float32)[None] / 255.
    it.set_tensor(ii['index'], x); it.invoke(); m = it.get_tensor(oo['index'])[0, :, :, 0]
    m = np.clip((m - .35) / .3, 0, 1)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)), np.float32) / 255.
    if _prev[0] is not None: m = np.maximum(m, _prev[0] * .5)   # steadier edges between frames
    _prev[0] = m; return m

def comp(base, layer):
    a = layer[..., 3:4].astype(np.float32) / 255.
    return base * (1 - a) + layer[..., :3].astype(np.float32) * a

for e in plan['fx']:
    {'orbit': prep_orbit, 'mono': prep_mono, 'comment': prep_comment}.get(e['type'], lambda e: None)(e)

dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', BASE]))
N = int(float(os.environ.get('LIMIT', dur)) * FPS)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', BASE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', BASE, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                        '-c:a', 'copy', '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for fi in range(N):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    t = fi / FPS
    frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    out = frame.astype(np.float32)
    back, front = Canvas(), Canvas(); orb_f, orb_b = [], []
    for e in plan['fx']:
        if not (e['start'] <= t < e['end']): continue
        if e['type'] == 'mono':
            lt = t - e['start']
            amt = clamp(lt / .2) * clamp((e['end'] - t) / .2)
            out = mono_grade(frame, amt)
            if lt < .12: out = out + (255 - out) * (.35 * (1 - lt / .12))   # quick white flash on the switch
            draw_mono(e, t, back, front)
        elif e['type'] == 'orbit': draw_orbit(e, t, orb_f, orb_b)
        elif e['type'] == 'glass': draw_glass(e, t, frame, back, front)
        elif e['type'] == 'comment': draw_comment(e, t, back, front)
    for depth, im, x, y, sc, a, rot in sorted(orb_b): back.put(im, x, y, sc, a, rot)
    for depth, im, x, y, sc, a, rot in sorted(orb_f): front.put(im, x, y, sc, a, rot)
    if back.used:
        arr = np.array(back.img); m = person_mask(frame)
        arr[..., 3] = (arr[..., 3] * (1 - m)).astype(np.uint8); out = comp(out, arr)
    else: _prev[0] = None
    if front.used: out = comp(out, np.array(front.img))
    enc.stdin.write(out.clip(0, 255).astype(np.uint8).tobytes())
    if fi % 90 == 0: print(f'{t:5.1f}s', flush=True)
enc.stdin.close(); enc.wait(); print('done', OUT)
