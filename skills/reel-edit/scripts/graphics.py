"""Overlay graphics (3D titles, Instagram-style UI, cards, picture-in-picture frames...).

Each overlay in plan["overlays"] becomes one or more transparent PNG frames, drawn as
HTML in headless Chromium (html2png.js). effects.py then animates them onto the video.

Overlay types (times are in reel seconds; every type takes start, end and optional
"y" = top edge as a fraction of the frame height):
  title      {"text": "ZUCCHINI", "sub": "50 DAYS", "behind": true}  big keyword title;
             3D in Editorial/Bold styles; "behind": true tucks it behind the person
  headline   {"lines": [{"text": "15 ways", "font": "script"}, {"text": "Claude edits my reels,"},
                        {"text": "and not my creative voice.", "font": "script"}]}
             mixed-font headline: bold lines plus hand-written lines in the highlight colour
  sticker    {"emoji": "🧠", "size": 260, "side": "centre"}  or  {"image": "/path/reaction.gif"}
             pops in with a bounce (emoji get little burst lines); GIFs keep playing.
             "side": "left" | "centre" | "right" (default right); "x" in pixels still wins
  badge      {"text": "#1 ZUCCHINI · 50 days"}                       pill label
  card       {"lines": ["✅ Seedlings", "❌ Seeds"], "title": "Tomatoes"} tip card
  comments   {"text": "CHRISTMAS", "count": 8}        stack of comment bubbles popping in
  comment_box {"text": "CHRISTMAS"}                   "Add a comment..." box typing a word
  dm_reply   {"comment": "CHRISTMAS", "reply": "Sending it over!", "handle": "jenae"}
  follow     {"handle": "heytherejenae", "avatar": "/path/face.jpg"}   Follow card that taps
  pip        {"clip": "/path.mp4", "clip_start": 12.0, "title": "BEFORE"}  video in a card
  fan        {"clip": "/path.mp4", "times": [5, 9, 15, 20, 27]}   fanned thumbnails + timestamps
  styles     {"cards": [{"label": "LOFI", "clip": "/a.mp4", "t": 3}, ...]}  up to 3 compare cards
"""
import html
import json
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920


def esc(s):
    return html.escape(str(s))


def font_face(name, path):
    if not path:
        return ""
    return f"@font-face{{font-family:'{name}';src:url('file://{path}');}}"


def page(body, css, fonts, w, h):
    faces = "".join(font_face(n, p) for n, p in fonts.items())
    return (f"<html><head><style>{faces}html,body{{margin:0;background:transparent;width:{w}px;"
            f"height:{h}px;overflow:hidden}}*{{box-sizing:border-box}}{css}</style></head>"
            f"<body>{body}</body></html>")


def frame_png(clip, t, out, width):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", clip, "-frames:v", "1",
                    "-vf", f"scale={width}:-2", out], check=True)
    return out


# --- one builder per overlay type: returns (list of (html, w, h)), (x, y) placement ---

WIDE_FONTS = {"Archivo Black": 0.8, "Luckiest Guy": 0.9, "Permanent Marker": 0.9}


def title(o, look, F):
    c = look["colors"]
    text = o["text"]
    nlines = max(1, -(-len(text) // 14))  # long hooks wrap onto 2-3 lines
    size = int(o.get("size") or min(320 if nlines == 1 else 150, 1480 / max(3, len(text) / nlines)))
    if not o.get("size"):  # wide fonts need a smaller size to fit the same word
        size = int(size * WIDE_FONTS.get(look.get("display_font"), 1.0))
    if look.get("title_3d"):
        depth = max(14, size // 7)
        shadow = ",".join(f"{k * 0.55:.1f}px {k}px 0 {c['primary']}" for k in range(1, depth + 1))
        shadow += f",{depth * 0.55 + 6:.0f}px {depth + 10}px 18px rgba(0,0,0,.35)"
        face = f"color:{c['light']};text-shadow:{shadow};"
    else:
        face = (f"color:{c['light'] if look['style'] != 'clean' else '#fff'};"
                f"-webkit-text-stroke:{max(4, size // 30)}px {c['primary']};paint-order:stroke fill;"
                f"text-shadow:0 8px 24px rgba(0,0,0,.35)")
    sub = (f"<div class=s>{esc(o['sub'])}</div>" if o.get("sub") else "")
    h = int(size * 1.12 * nlines + size * 0.15 + (90 if sub else 0) + 40)
    css = (f".t{{font-family:D;font-size:{size}px;line-height:1.05;text-align:center;{face};"
           f"letter-spacing:-0.01em;padding:10px 50px 0;white-space:{'nowrap' if nlines == 1 else 'normal'}}}"
           f".s{{font-family:B;font-size:46px;letter-spacing:.45em;text-align:center;color:{c['light']};"
           f"text-shadow:0 2px 8px rgba(0,0,0,.5);margin-top:6px}}")
    return [(page(f"<div class=t>{esc(text)}</div>{sub}", css, F, W, h), W, h)], 0, o.get("y", 0.1)


def headline(o, look, F):
    c = look["colors"]
    rows, h = "", 40
    for ln in o.get("lines", []):
        script = ln.get("font") == "script"
        size = int(ln.get("size") or (100 if script else 92))
        cls = "sc" if script else "bd"
        rows += f"<div class={cls} style='font-size:{size}px'>{esc(ln['text'])}</div>"
        per_line = max(1, int(1000 / (0.55 * size)))  # rough wrap estimate
        h += int(size * 1.15) * max(1, -(-len(ln["text"]) // per_line))
    css = (f".w{{text-align:center;padding:20px 40px}}.bd{{font-family:B;font-weight:800;color:#fff;"
           f"line-height:1.1;letter-spacing:-0.02em;text-shadow:0 4px 18px rgba(0,0,0,.45)}}"
           f".sc{{font-family:S;color:{c['highlight']};line-height:1.1;text-shadow:0 3px 12px rgba(0,0,0,.4)}}")
    return [(page(f"<div class=w>{rows}</div>", css, F, W, h), W, h)], 0, o.get("y", 0.5)


def sticker_x(o, box):
    if "x" in o:
        return o["x"]
    side = str(o.get("side", "right")).lower()
    if side in ("centre", "center", "middle"):
        return (W - box) // 2
    return 60 if side == "left" else W - box - 60


def sticker(o, look, F):
    size = int(o.get("size", 260))
    box = int(size * 1.6)
    if o.get("image"):
        o["_gif"] = o["image"]  # effects.py plays the file itself (GIF, PNG or video)
        body = f"<img src='file://{o['image']}' style='width:{size}px;height:{size}px;object-fit:contain;" \
               f"border-radius:18px;margin:{(box - size) // 2}px'>"
        return [(page(body, "", F, box, box), box, box)], sticker_x(o, box), o.get("y", 0.3)
    frames = []
    for k, sc in enumerate((0.35, 0.8, 1.18, 0.94, 1.0)):
        burst = ""
        if k >= 2:  # little burst lines around the emoji
            r = size * (0.62 + 0.08 * k)
            for ang in (-60, -20, 20):
                burst += (f"<div style='position:absolute;left:50%;top:50%;width:10px;height:{size // 6}px;"
                          f"background:#fff;border-radius:5px;transform:translate(-50%,-50%) rotate({ang}deg) "
                          f"translateY(-{r:.0f}px);opacity:{1 if k < 4 else 0.6}'></div>")
        body = (f"<div style='position:relative;width:{box}px;height:{box}px'>{burst}"
                f"<div style='position:absolute;inset:0;display:flex;align-items:center;justify-content:center;"
                f"font-size:{int(size * sc)}px;line-height:1;font-family:\"Noto Color Emoji\"'>{esc(o['emoji'])}</div></div>")
        frames.append((page(body, "", F, box, box), box, box))
    return frames, sticker_x(o, box), o.get("y", 0.3)


def badge(o, look, F):
    c = look["colors"]
    css = (f".b{{display:inline-block;font-family:D;font-size:64px;color:{c['light']};"
           f"background:{c['primary']};border-radius:28px;padding:18px 40px;"
           f"box-shadow:0 10px 0 rgba(0,0,0,.25)}}.w{{text-align:center;padding:10px}}")
    return [(page(f"<div class=w><span class=b>{esc(o['text'])}</span></div>", css, F, W, 170), W, 170)], \
        0, o.get("y", 0.14)


def card(o, look, F):
    c = look["colors"]
    lines = "".join(f"<div class=l>{esc(x)}</div>" for x in o.get("lines", []))
    head = f"<div class=h>{esc(o['title'])}</div>" if o.get("title") else ""
    n = len(o.get("lines", [])) + (1 if head else 0)
    h = 120 + n * 110
    css = (f".c{{margin:20px auto;width:760px;background:{c['light']};border-radius:36px;padding:34px 46px;"
           f"box-shadow:0 14px 0 {c['primary']},0 24px 40px rgba(0,0,0,.3)}}"
           f".h{{font-family:D;font-size:70px;color:{c['primary']};margin-bottom:8px}}"
           f".l{{font-family:B;font-size:66px;color:#222;line-height:1.5}}")
    return [(page(f"<div class=c>{head}{lines}</div>", css, F, W, h), W, h)], 0, o.get("y", 0.12)


def bubble(text, c, scale=1.0):
    return (f"<div class=bb style='transform:scale({scale});'><div class=av></div>"
            f"<div class=tx><div class=nm></div><div class=wd>{esc(text)}</div></div>"
            f"<div class=now>· now</div><div class=ht>♡</div></div>")


def comments(o, look, F):
    c = look["colors"]
    n = int(o.get("count", 8))
    css = (f".st{{position:relative;width:{W}px;height:900px}}"
           f".bb{{position:absolute;right:120px;width:640px;height:118px;background:#fff;border-radius:26px;"
           f"display:flex;align-items:center;padding:0 30px;gap:22px;transform-origin:right center;"
           f"box-shadow:0 10px 0 #cfcfcf,0 16px 30px rgba(0,0,0,.25)}}"
           f".av{{width:72px;height:72px;border-radius:50%;background:{c['primary']};flex:none;"
           f"box-shadow:inset 0 -18px 0 rgba(255,255,255,.35)}}.tx{{flex:1}}"
           f".nm{{width:240px;height:14px;border-radius:7px;background:#ddd;margin-bottom:10px}}"
           f".wd{{font-family:D;font-size:52px;color:#111;font-style:italic;font-weight:900}}"
           f".now{{font-family:B;color:#999;font-size:30px;align-self:flex-start;margin-top:22px}}"
           f".ht{{font-size:48px;color:#333}}")
    frames = []
    for k in range(1, n + 1):
        items = ""
        for i in range(k):  # newest at the bottom, older ones shrink upwards
            age = k - 1 - i
            s = max(0.55, 1 - age * 0.06)
            top = 760 - sum(max(0.55, 1 - a * 0.06) * 100 for a in range(age))
            items += f"<div style='position:absolute;top:{top:.0f}px;width:100%'>{bubble(o['text'], c, s)}</div>"
        frames.append((page(f"<div class=st>{items}</div>", css, F, W, 900), W, 900))
    return frames, 0, o.get("y", 0.3)


def comment_box(o, look, F):
    c = look["colors"]
    word = o["text"]
    css = (f".bx{{margin:30px auto;width:900px;height:120px;background:#fff;border-radius:60px;display:flex;"
           f"align-items:center;padding:0 40px;box-shadow:0 14px 0 {c['primary']},0 22px 36px rgba(0,0,0,.3)}}"
           f".p{{flex:1;font-family:B;font-size:50px;color:#999}}.v{{color:#111;font-family:D}}"
           f".go{{width:76px;height:76px;border-radius:50%;background:#ccc;color:#fff;font-size:44px;"
           f"display:flex;align-items:center;justify-content:center}}.on{{background:{c['primary']}}}")
    frames = [(page("<div class=bx><div class=p>Add a comment…</div><div class=go>↑</div></div>", css, F, W, 200),
               W, 200)]
    for i in range(1, len(word) + 1):
        on = " on" if i == len(word) else ""
        frames.append((page(f"<div class=bx><div class='p v'>{esc(word[:i])}</div><div class='go{on}'>↑</div></div>",
                            css, F, W, 200), W, 200))
    return frames, 0, o.get("y", 0.3)


def dm_reply(o, look, F):
    c = look["colors"]
    css = (f".w{{width:820px;margin:20px auto}}"
           f".cm{{background:rgba(245,245,245,.92);border-radius:28px;height:116px;display:flex;align-items:center;"
           f"padding:0 34px;font-family:B;font-size:50px;color:#333;justify-content:space-between}}"
           f".up{{width:70px;height:70px;border-radius:50%;background:#555;color:#fff;display:flex;"
           f"align-items:center;justify-content:center;font-size:40px}}"
           f".rp{{margin:12px 0 0 20px;background:rgba(245,245,245,.92);border-radius:28px;padding:20px 30px;"
           f"display:flex;gap:22px;align-items:center}}.av{{width:76px;height:76px;border-radius:50%;"
           f"background:{c['primary']} center/cover}}.hd{{font-family:B;font-size:30px;color:#555}}"
           f".hd span{{color:#aaa}}.msg{{font-family:D;font-size:52px;color:#111}}")
    avatar = f"style=\"background-image:url('file://{o['avatar']}')\"" if o.get("avatar") else ""
    cm = f"<div class=cm><b>{esc(o['comment'])}</b><div class=up>↑</div></div>"
    rp = (f"<div class=rp><div class=av {avatar}></div><div><div class=hd>{esc(o.get('handle', ''))} "
          f"<span>now</span></div><div class=msg>{esc(o.get('reply', 'Sending it over!'))}</div></div></div>")
    return [(page(f"<div class=w>{cm}</div>", css, F, W, 330), W, 330),
            (page(f"<div class=w>{cm}{rp}</div>", css, F, W, 330), W, 330)], 0, o.get("y", 0.16)


def follow(o, look, F):
    c = look["colors"]
    avatar = f"background-image:url('file://{o['avatar']}');" if o.get("avatar") else ""
    css = (f".cd{{margin:24px auto;width:930px;height:170px;background:#fff;border-radius:40px;display:flex;"
           f"align-items:center;padding:0 34px;gap:28px;box-shadow:0 18px 40px rgba(0,0,0,.3)}}"
           f".av{{flex:none;width:112px;height:112px;border-radius:50%;background:{c['primary']} center/cover;{avatar}}}"
           f".h{{flex:1;font-family:B;font-size:56px;color:#111;font-weight:800}}"
           f".f{{font-family:B;font-size:46px;border-radius:40px;padding:22px 54px;color:#fff;"
           f"background:{c['primary']}}}.p{{transform:scale(.92);filter:brightness(.8)}}"
           f".d{{background:#e6e6e6;color:#333}}")
    frames = []
    for cls, label in (("f", "Follow"), ("f p", "Follow"), ("f d", "Following")):
        frames.append((page(f"<div class=cd><div class=av></div><div class=h>{esc(o['handle'])}</div>"
                            f"<div class='{cls}'>{label}</div></div>", css, F, W, 220), W, 220))
    return frames, 0, o.get("y", 0.12)


def pip(o, look, F):
    """Card frame with a title; effects.py puts the video in the hole (x 40..470, y 150..900)."""
    c = look["colors"]
    w, h = 520, 960
    css = (f".c{{position:absolute;inset:0;border-radius:40px;background:{c['primary']};"
           f"box-shadow:0 20px 40px rgba(0,0,0,.35)}}.t{{position:absolute;top:34px;left:40px;right:30px;"
           f"font-family:D;font-size:78px;color:{c['light']};line-height:1}}"
           f".hole{{position:absolute;left:40px;top:150px;width:440px;height:780px;border-radius:24px;"
           f"background:#000}}")
    o["_hole"] = (40, 150, 440, 780)
    return [(page(f"<div class=c></div><div class=t>{esc(o.get('title', ''))}</div><div class=hole></div>",
                  css, F, w, h), w, h)], o.get("x", W - w - 20), o.get("y", 0.45)


def fan(o, look, F, tmp):
    times = o.get("times", [])[:7]
    css = (".f{position:relative;width:1080px;height:640px}.th{position:absolute;border-radius:10px;"
           "overflow:hidden;box-shadow:0 10px 24px rgba(0,0,0,.35);background:#000 center/cover}"
           ".ts{position:absolute;font-family:'DejaVu Sans Mono',monospace;font-size:34px;color:#fff;"
           "background:rgba(0,0,0,.75);padding:4px 10px;border-radius:6px}")
    items, x = "", 250
    for i, t in enumerate(times):
        s = 1 - i * 0.13
        w, h = int(220 * s), int(390 * s)
        img = frame_png(o["clip"], t, os.path.join(tmp, f"fan{i}_{id(o)}.jpg"), 300)
        items = (f"<div class=th style=\"left:{x}px;top:{40 + i * 6}px;width:{w}px;height:{h}px;z-index:{20 - i};"
                 f"background-image:url('file://{img}')\"></div>"
                 f"<div class=ts style='left:{x + w // 2 - 50}px;top:{40 + i * 6 + h + 10}px;z-index:30'>"
                 f"{int(t) // 60}:{int(t) % 60:02d}</div>") + items
        x += int(w * 0.62)
    return [(page(f"<div class=f>{items}</div>", css, F, W, 640), W, 640)], 0, o.get("y", 0.18)


def styles(o, look, F, tmp):
    c = look["colors"]
    css = (f".g{{display:flex;justify-content:center;gap:26px;padding:20px}}.cd{{width:300px;height:520px;"
           f"border-radius:16px;border:5px solid {c['light']};background:#000 center/cover;position:relative;"
           f"box-shadow:0 14px 30px rgba(0,0,0,.35)}}.lb{{position:absolute;top:16px;left:16px;"
           f"font-family:'DejaVu Sans Mono',monospace;font-weight:bold;font-size:40px;background:{c['light']};"
           f"color:{c['primary']};padding:6px 14px;border-radius:8px}}")
    items = ""
    for i, cd in enumerate(o.get("cards", [])[:3]):
        img = frame_png(cd["clip"], cd.get("t", 1), os.path.join(tmp, f"sty{i}_{id(o)}.jpg"), 400)
        items += (f"<div class=cd style=\"background-image:url('file://{img}');"
                  f"filter:{cd.get('css_filter', 'none')}\"><div class=lb>{esc(cd['label'])}</div></div>")
    return [(page(f"<div class=g>{items}</div>", css, F, W, 580), W, 580)], 0, o.get("y", 0.25)


BUILDERS = {"title": title, "headline": headline, "sticker": sticker, "badge": badge, "card": card, "comments": comments, "comment_box": comment_box,
            "dm_reply": dm_reply, "follow": follow, "pip": pip}
NEEDS_TMP = {"fan": fan, "styles": styles}


def build(overlays, look, font_files, workdir):
    """Render every overlay's frames. Returns overlays with "_frames", "_x", "_y" (pixels)."""
    F = {"D": font_files["display"], "B": font_files["body"], "S": font_files.get("script")}
    tmp = tempfile.mkdtemp(dir=workdir)
    jobs, out = [], []
    for n, o in enumerate(overlays):
        o = dict(o)
        for k in ("handle", "avatar"):  # brand kit fills these in for UI overlays
            if look.get(k) and not o.get(k):
                o[k] = look[k]
        kind = o.get("type")
        if kind in BUILDERS:
            frames, x, y = BUILDERS[kind](o, look, F)
        elif kind in NEEDS_TMP:
            frames, x, y = NEEDS_TMP[kind](o, look, F, tmp)
        else:
            print(f"unknown overlay type {kind!r}, skipped")
            continue
        o["_frames"] = []
        for k, (doc, w, h) in enumerate(frames):
            png = os.path.join(tmp, f"ov{n:02d}_{k:02d}.png")
            jobs.append({"html": doc, "out": png, "width": w, "height": h})
            o["_frames"].append(png)
        o["_size"] = (frames[0][1], frames[0][2])
        o["_x"] = int(x)
        o["_y"] = int(y * H) if isinstance(y, float) and y <= 1 else int(y)
        out.append(o)
    if jobs:
        jf = os.path.join(tmp, "jobs.json")
        json.dump(jobs, open(jf, "w"))
        subprocess.run(["node", os.path.join(HERE, "html2png.js"), jf], check=True)
    return out
