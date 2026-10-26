#!/usr/bin/env python3
"""Render a vertical reel from an edit plan (JSON) with ffmpeg.

Usage: render.py PLAN.json [--analysis analysis.json] [--workdir DIR]

Plan format (times in seconds, relative to each source clip):
{
  "output": "reel.mp4",
  "width": 1080, "height": 1920, "fps": 30,
  "segments": [
    {"clip": "/path/a.mp4", "start": 3.2, "end": 5.0,
     "framing": "auto" | "fill" | "fit-blur",   # optional, default auto
     "focus_x": 0.5,                             # optional, 0=left 1=right when cropping
     "speed": 1.0,                               # optional, 0.5..2
     "audio": true}                              # optional, keep clip sound
  ],
  "hook":    {"text": "You won't believe this", "duration": 2.0},   # optional
  "end_text": {"text": "Follow for part 2", "duration": 1.8},       # optional
  "captions": {"enabled": true},       # word-by-word, from analysis transcripts
  "captions_manual": [{"start": 0, "end": 1.5, "text": "..."}],     # optional, reel time
  "music": {"path": "/path/song.mp3", "volume": 0.35, "duck": true, "start": 0},  # optional
            # or {"track": "Carefree"} from the music library in audio.py (credit it!)
  "sfx": true,                            # optional: pops/whooshes/clicks synced to overlays
  "sfx_events": [{"t": 3.2, "sound": "ding"}],  # optional extra sounds: pop|whoosh|ding|click
  "style": {"font": "Poppins",            # optional, a name in FONTS below, or a path to
                                          # the person's own .ttf/.otf font file
            "highlight_color": "#FFD60A"}, # optional, colour for key words
  "cut_words": ["you know"],              # optional: words to cut everywhere (or "cut" per segment)
  "blur_faces": "all" | "others",         # optional privacy blur (others = keep the speaker)
  "highlight_words": ["zucchini", "50"]   # optional; key words to pop in colour.
                                          # Numbers are always highlighted. If empty,
                                          # one long word per caption card is picked.
}
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import looks  # noqa: E402

FONT_DIRS = ["/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/dejavu"]
FONT_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
# Free Google Fonts (OFL or Apache licence, fine for commercial use): name -> (family, download url).
# FONT_SCALE evens out how big each font looks at the same point size.
FONTS = {
    "Poppins": ("Poppins ExtraBold", GF + "poppins/Poppins-ExtraBold.ttf"),
    "Anton": ("Anton", GF + "anton/Anton-Regular.ttf"),
    "Bebas Neue": ("Bebas Neue", GF + "bebasneue/BebasNeue-Regular.ttf"),
    "Archivo Black": ("Archivo Black", GF + "archivoblack/ArchivoBlack-Regular.ttf"),
    "Luckiest Guy": ("Luckiest Guy", GF.replace("ofl/", "apache/") + "luckiestguy/LuckiestGuy-Regular.ttf"),
    "Bangers": ("Bangers", GF + "bangers/Bangers-Regular.ttf"),
    "Permanent Marker": ("Permanent Marker", GF.replace("ofl/", "apache/") + "permanentmarker/PermanentMarker-Regular.ttf"),
    "Lilita One": ("Lilita One", GF + "lilitaone/LilitaOne-Regular.ttf"),
    "DM Serif Display": ("DM Serif Display", GF + "dmserifdisplay/DMSerifDisplay-Regular.ttf"),
    "Instrument Serif": ("Instrument Serif", GF + "instrumentserif/InstrumentSerif-Regular.ttf"),
    "Caveat Brush": ("Caveat Brush", GF + "caveatbrush/CaveatBrush-Regular.ttf"),
    "Instrument Serif Italic": ("Instrument Serif", GF + "instrumentserif/InstrumentSerif-Italic.ttf"),
}
FONT_SCALE = {"Poppins": 1.3, "Anton": 1.45, "Bebas Neue": 1.5, "Bangers": 1.6, "Instrument Serif": 1.35}
STOPWORDS = set("""a an the and or but so to of in on at for from with by is are was were be been it its
it's this that these those you you're your i i'm i've i'll we they they're he she my me our their
there here what when where which who how not just only also very really going gonna get got
have has had do does did can will would could should about into than then some any more most""".split())


def custom_font(path):
    """The person's own .ttf/.otf (e.g. a font they bought): (family, dir) or None."""
    r = subprocess.run(["fc-scan", "--format", "%{family[0]}\n", path], capture_output=True, text=True)
    family = r.stdout.strip().splitlines()[0] if r.returncode == 0 and r.stdout.strip() else None
    if not family:
        print(f"couldn't read font file {path}, using the default", file=sys.stderr)
        return None
    os.makedirs(FONT_CACHE, exist_ok=True)  # one fonts folder, so captions can mix fonts
    if not os.path.exists(os.path.join(FONT_CACHE, os.path.basename(path))):
        shutil.copy(path, FONT_CACHE)
    return family, os.path.abspath(FONT_CACHE)


def pick_font(name=None):
    if name and name.lower().endswith((".ttf", ".otf")) and os.path.exists(name):
        found = custom_font(name)
        if found:
            return found
    if name in FONTS:
        family, url = FONTS[name]
        os.makedirs(FONT_CACHE, exist_ok=True)
        dest = os.path.join(FONT_CACHE, os.path.basename(url))
        if not os.path.exists(dest):
            r = subprocess.run(["curl", "-sSfL", "-m", "30", "-o", dest, url], capture_output=True)
            if r.returncode != 0:
                print(f"couldn't download font {name}, using the default", file=sys.stderr)
                if os.path.exists(dest):
                    os.remove(dest)
        if os.path.exists(dest):
            return family, os.path.abspath(FONT_CACHE)
    if os.path.exists("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"):
        return "Inter Display Black", "/usr/share/fonts/opentype/inter"
    if os.path.exists("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"):
        return "Inter Display", "/usr/share/fonts/opentype/inter"
    return "DejaVu Sans", "/usr/share/fonts/truetype/dejavu"


def font_file(name):
    """Path to a font file for the HTML graphics (downloads Google Fonts on first use)."""
    if name and name.lower().endswith((".ttf", ".otf")) and os.path.exists(name):
        return os.path.abspath(name)
    if name in FONTS:
        pick_font(name)
        p = os.path.join(FONT_CACHE, os.path.basename(FONTS[name][1]))
        if os.path.exists(p):
            return os.path.abspath(p)
    return "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd) + "\n" + r.stderr[-3000:])
        raise SystemExit(f"ffmpeg failed ({r.returncode})")
    return r


def probe(path):
    r = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", path])
    st = json.loads(r.stdout)["streams"]
    v = next(s for s in st if s["codec_type"] == "video")
    w, h = int(v["width"]), int(v["height"])
    rot = int(v.get("tags", {}).get("rotate", 0))
    for sd in v.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", rot))
    if abs(rot) % 180 == 90:
        w, h = h, w
    return w, h, any(s["codec_type"] == "audio" for s in st)


def segment_filter(seg, W, H, fps, src_w, src_h):
    framing = seg.get("framing", "auto")
    if framing == "auto":
        # Upright clips fill the frame; landscape clips keep everything over a blurred copy.
        framing = "fill" if src_h / src_w >= 1.2 else "fit-blur"
    speed = float(seg.get("speed", 1.0))
    pre = f"setpts=PTS/{speed}," if speed != 1.0 else ""
    if framing == "fill":
        fx = float(seg.get("focus_x", 0.5))
        z = float(seg.get("zoom", 1.0))  # punch-in: crop tighter, same output size
        v = (f"[0:v]{pre}scale={int(W * z)}:{int(H * z)}:force_original_aspect_ratio=increase,"
             f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})/2,setsar=1,fps={fps},format=yuv420p[v]")
    else:
        v = (f"[0:v]{pre}split[a][b];"
             f"[a]scale={W//4}:{H//4}:force_original_aspect_ratio=increase,crop={W//4}:{H//4},"
             f"boxblur=10:2,scale={W}:{H},eq=brightness=-0.08[bg];"
             f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
             f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={fps},format=yuv420p[v]")
    return v, speed


def atempo_chain(speed):
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0"); s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5"); s /= 0.5
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)


def render_segment(i, seg, W, H, fps, workdir):
    src = seg["clip"]
    src_w, src_h, has_audio = probe(src)
    start, end = float(seg["start"]), float(seg["end"])
    dur = end - start
    vf, speed = segment_filter(seg, W, H, fps, src_w, src_h)
    out = os.path.join(workdir, f"seg_{i:03d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", src]
    keep_audio = seg.get("audio", True) and has_audio
    if keep_audio:
        af = "[0:a]aresample=48000,aformat=channel_layouts=stereo"
        if speed != 1.0:
            af += "," + atempo_chain(speed)
        fc = vf + ";" + af + "[a]"
    else:
        cmd += ["-f", "lavfi", "-t", f"{dur / speed:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc = vf + ";[1:a]acopy[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-t", f"{dur / speed:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(fps),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out]
    sh(cmd)
    return out, dur / speed


def ass_time(t):
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_escape(text):
    return text.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def build_captions(plan, analysis, offsets, per_card=3):
    """Word-timed caption events in reel time, a few words per card."""
    by_path = {}
    for c in (analysis or {}).get("clips", []):
        by_path[os.path.abspath(c["path"])] = c.get("transcript") or []
    events = []
    for seg, (off, out_dur) in zip(plan["segments"], offsets):
        words = by_path.get(os.path.abspath(seg["clip"]), [])
        speed = float(seg.get("speed", 1.0))
        s0, s1 = float(seg["start"]), float(seg["end"])
        inside = [w for w in words if w["start"] >= s0 - 0.05 and w["end"] <= s1 + 0.05]
        chunks, chunk = [], []
        for w in inside:
            chunk.append(w)
            if len(chunk) == per_card or w["word"].endswith((".", ",", "!", "?")):
                chunks.append(chunk); chunk = []
        if chunk:
            chunks.append(chunk)
        for ch in chunks:  # source time -> reel time
            a = off + (ch[0]["start"] - s0) / speed
            b = off + (ch[-1]["end"] - s0) / speed
            events.append({"start": max(off, a), "end": min(off + out_dur, b),
                           "text": " ".join(x["word"] for x in ch),
                           "words": [(x["word"], off + (x["start"] - s0) / speed, off + (x["end"] - s0) / speed)
                                     for x in ch]})
    events.sort(key=lambda e: e["start"])
    # hold each card until the next one (max 0.6s gap) so text doesn't flicker
    for a, b in zip(events, events[1:]):
        if 0 < b["start"] - a["end"] < 0.6:
            a["end"] = b["start"]
    return events


def ass_colour(hexstr):
    h = hexstr.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


def is_key(word, wanted):
    w = word.strip(".,!?\"'").lower()
    return any(ch.isdigit() for ch in w) or w in wanted


def caption_text(words, wanted, colour, case="upper", base="&H00FFFFFF&"):
    """Upper-case card text with key words in the highlight colour."""
    keys = [is_key(w, wanted) for w in words]
    if not wanted and not any(keys):  # auto mode: pop the longest meaningful word
        cands = [(len(w), i) for i, w in enumerate(words)
                 if len(w.strip(".,!?")) >= 5 and w.strip(".,!?\"'").lower() not in STOPWORDS]
        if cands:
            keys[max(cands)[1]] = True
    out = []
    for w, k in zip(words, keys):
        t = ass_escape(w.upper() if case == "upper" else w.lower() if case == "lower" else w)
        out.append(f"{{\\c{colour}}}{t}{{\\c{base}}}" if k else t)
    return " ".join(out)


def write_ass(path, plan, events, total, W, H, look=None):
    look = look or looks.resolve(plan)
    c = look["colors"]
    font, _ = pick_font(look.get("font"))
    colour = ass_colour(c["highlight"])
    wanted = {w.lower() for w in plan.get("highlight_words", [])}
    scale = FONT_SCALE.get(look.get("font"), 1.0) if font != pick_font()[0] else 1.0
    st = lambda hx: ass_colour(hx).rstrip("&")  # style lines take &HAABBGGRR without the closing &
    if look.get("caption_box"):
        # solid box in the theme colour, light text (BorderStyle 3 = box in OutlineColour)
        base = ass_colour(c["light"])
        cap_style = (f"Style: Cap,{font},{int(H * 0.042 * scale)},{st(c['light'])},&H0000FFFF,{st(c['primary'])},"
                     f"&H00000000,0,0,0,0,100,100,0,0,3,{int(H * 0.008)},0,2,90,90,{int(H * 0.30)},1")
    else:
        base = "&H00FFFFFF&"
        cap_style = None
    cap_size = int(H * 0.05 * scale)
    hook_size = int(H * 0.05 * scale)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        # Captions sit in the lower-middle, clear of the app buttons and description.
        cap_style or (f"Style: Cap,{font},{cap_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,"
                      f"-1,0,0,0,100,100,0,0,1,{max(4, cap_size // 9)},2,2,90,90,{int(H * 0.30)},1"),
        # Hook / end text: boxed, near the top third.
        f"Style: Hook,{font},{hook_size},{st(c['primary']) if look['style'] != 'clean' else '&H00000000'},"
        f"&H00000000,{st(c['light']) if look['style'] != 'clean' else '&H00FFFFFF'},&H00FFFFFF,"
        f"-1,0,0,0,100,100,0,0,3,{hook_size // 3},0,8,80,80,{int(H * 0.16)},1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    mode = look.get("caption_mode", "words")
    case = look.get("caption_case", "upper")
    fix = lambda w: ass_escape(w.upper() if case == "upper" else w.lower() if case == "lower" else w)
    if mode == "karaoke":
        # a box in the highlight colour jumps from word to word: measured with the real
        # font so the box sits exactly behind the word being said
        from PIL import ImageFont
        ff = font_file(look.get("font"))
        probe = ImageFont.truetype(ff, 200)
        asc, desc = probe.getmetrics()
        em = cap_size * 200 / (asc + desc)  # libass sizes fonts by ascent + descent
        kfont = ImageFont.truetype(ff, max(1, int(em)))
        bottom = H - int(H * 0.30)
    if mode == "punch":
        # one or two big words at a time; key words switch to an italic serif in the highlight colour
        pick_font("Instrument Serif Italic")
        size = int(H * 0.068 * scale)
        lines.insert(-3, f"Style: Punch,{font},{size},&H00FFFFFF,&H0000FFFF,&H00000000,&H50000000,"
                         f"-1,0,0,0,100,100,0,0,1,{max(3, size // 14)},3,2,70,70,{int(H * 0.40)},1")
    for e in events:
        txt = caption_text(e["text"].split(), wanted, colour, case, base)
        if mode == "karaoke" and e.get("words"):
            ws = e["words"]
            texts = [fix(x) for x, _, _ in ws]
            widths = [kfont.getlength(t) for t in texts]
            space = kfont.getlength(" ")
            total_w = sum(widths) + space * (len(ws) - 1)
            plain = " ".join(texts)
            fit = min(1.0, (W - 160) / total_w)  # shrink a long card to fit one line
            if fit >= 0.7:  # one line: box behind the word being said, that word in dark text
                widths, space, total_w = [w * fit for w in widths], space * fit, total_w * fit
                sc = f"\\fscx{fit * 100:.0f}\\fscy{fit * 100:.0f}\\q2"
                x = (W - total_w) / 2
                pad = cap_size * fit * 0.18
                dark = ass_colour(c["primary"]) if look["style"] != "clean" else "&H00111111&"
                for i, (w, a, b) in enumerate(ws):
                    b = ws[i + 1][1] if i + 1 < len(ws) else e["end"]
                    a = max(a, e["start"]) if i else e["start"]
                    x0, x1 = x - pad, x + widths[i] + pad
                    y0, y1 = bottom - cap_size * fit * 0.98 - pad * 0.4, bottom + pad * 0.3
                    box = f"m {x0:.0f} {y0:.0f} l {x1:.0f} {y0:.0f} {x1:.0f} {y1:.0f} {x0:.0f} {y1:.0f}"
                    lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,"
                                 f"{{\\an7\\pos(0,0)\\bord0\\shad0\\1c{colour}\\p1}}{box}")
                    parts = [f"{{\\c{dark}\\3c{colour}\\shad0}}{t}{{\\c{base}\\3c&H000000&\\shad2}}"
                             if j == i else t for j, t in enumerate(texts)]
                    lines.append(f"Dialogue: 1,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{{{sc}}}{' '.join(parts)}")
                    x += widths[i] + space
            else:  # too wide for one line: colour the spoken word instead
                for i, (w, a, b) in enumerate(ws):
                    b = ws[i + 1][1] if i + 1 < len(ws) else e["end"]
                    parts = [f"{{\\c{colour}}}{t}{{\\c{base}}}" if j == i else t for j, t in enumerate(texts)]
                    lines.append(f"Dialogue: 1,{ass_time(max(a, e['start']))},{ass_time(b)},Cap,,0,0,0,,{' '.join(parts)}")
            continue
        if mode == "punch":
            words = e["text"].split()
            keys = [any(ch.isdigit() for ch in w) or w.strip(".,!?\"'").lower() in wanted for w in words]
            out = []
            for w, k in zip(words, keys):
                t = ass_escape(w.strip(".,") if k else w.strip(".,").lower())
                out.append(f"{{\\fnInstrument Serif\\i1\\b0\\c{colour}\\fscx118\\fscy118}}{t}"
                           f"{{\\fn{font}\\i0\\b1\\c&H00FFFFFF&\\fscx100\\fscy100}}" if k else t)
            lines.append(f"Dialogue: 0,{ass_time(e['start'])},{ass_time(e['end'])},Punch,,0,0,0,,"
                         f"{{\\fad(40,0)\\fscx125\\fscy125\\t(0,90,\\fscx100\\fscy100)}}{' '.join(out)}")
            continue
        if look.get("caption_box"):
            lines.append(f"Dialogue: 0,{ass_time(e['start'])},{ass_time(e['end'])},Cap,,0,0,0,,{txt}")
        else:  # quick pop-in: 112% -> 100% over 80ms
            lines.append(f"Dialogue: 0,{ass_time(e['start'])},{ass_time(e['end'])},Cap,,0,0,0,,"
                         f"{{\\fscx112\\fscy112\\t(0,80,\\fscx100\\fscy100)}}{txt}")
    hook = plan.get("hook")
    if hook and hook.get("text"):
        d = float(hook.get("duration", 2.0))
        lines.append(f"Dialogue: 1,{ass_time(0)},{ass_time(min(d, total))},Hook,,0,0,0,,"
                     f"{ass_escape(hook['text'])}")
    end = plan.get("end_text")
    if end and end.get("text"):
        d = float(end.get("duration", 1.8))
        lines.append(f"Dialogue: 1,{ass_time(max(0, total - d))},{ass_time(total)},Hook,,0,0,0,,"
                     f"{ass_escape(end['text'])}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--analysis")
    ap.add_argument("--workdir")
    args = ap.parse_args()
    plan = json.load(open(args.plan))
    analysis = json.load(open(args.analysis)) if args.analysis else None
    W, H, fps = int(plan.get("width", 1080)), int(plan.get("height", 1920)), int(plan.get("fps", 30))
    workdir = args.workdir or os.path.join(os.path.dirname(os.path.abspath(args.plan)), "work")
    os.makedirs(workdir, exist_ok=True)

    if plan.get("cut_words") or any(sg.get("cut") for sg in plan["segments"]):
        import roughcut
        plan = roughcut.apply_cuts(plan, analysis)
    look = looks.resolve(plan)
    seg_files, offsets, t = [], [], 0.0
    for i, seg in enumerate(plan["segments"]):
        if look.get("punch_in") and i % 2 == 1 and "zoom" not in seg:
            seg = dict(seg, zoom=1.15)
        f, d = render_segment(i, seg, W, H, fps, workdir)
        seg_files.append(f); offsets.append((t, d)); t += d
        print(f"segment {i}: {os.path.basename(seg['clip'])} {seg['start']}-{seg['end']}s -> {d:.2f}s",
              file=sys.stderr)
    total = t

    listfile = os.path.join(workdir, "concat.txt")
    with open(listfile, "w") as f:
        f.writelines(f"file '{p}'\n" for p in seg_files)
    joined = os.path.join(workdir, "joined.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listfile,
        "-c", "copy", joined])

    if plan.get("blur_faces"):
        import privacy
        joined = privacy.blur_faces(joined, os.path.join(workdir, "joined_blur.mp4"), W, H, fps,
                                    plan["blur_faces"])

    events = []
    if plan.get("captions", {}).get("enabled", True):
        per_card = 2 if look.get("caption_mode") == "punch" and "caption_words" not in (plan.get("look") or {}) \
            else int(look.get("caption_words", 3))
        events = build_captions(plan, analysis, offsets, per_card)
    events += plan.get("captions_manual", [])
    ass = os.path.join(workdir, "overlay.ass")
    write_ass(ass, plan, events, total, W, H, look)
    _, fontdir = pick_font(look.get("font"))

    out = plan.get("output", "reel.mp4")
    if not os.path.isabs(out):
        out = os.path.join(os.path.dirname(os.path.abspath(args.plan)), out)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", joined]
    overlays = plan.get("overlays", [])
    if overlays or look.get("grade"):
        import effects
        import graphics
        fonts = {"display": font_file(look.get("display_font")), "body": font_file("Poppins"),
                 "script": font_file(look.get("script_font", "Caveat Brush"))}
        built = graphics.build(overlays, look, fonts, workdir)
        extra, graph = effects.apply(joined, built, look, W, H, fps, workdir, total)
        cmd += extra
        vf = f"{graph};[fx]ass={ass}:fontsdir={fontdir}[v]"
    else:
        vf = f"[0:v]ass={ass}:fontsdir={fontdir}[v]"
    music = plan.get("music")
    parts, mix = [], []
    if music and music.get("track") and not music.get("path"):
        import audio
        music = dict(music, path=audio.track_path(music["track"]))
        print(audio.credit(music["track"]))
    if music and music.get("path"):
        mi = cmd.count("-i")  # music comes after the video and any overlay inputs
        cmd += ["-ss", str(music.get("start", 0)), "-stream_loop", "-1", "-i", music["path"]]
        vol = float(music.get("volume", 0.35))
        fade_at = max(0.0, total - 1.0)
        parts.append(f"[{mi}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},"
                     f"atrim=0:{total:.3f},afade=t=in:d=0.3,afade=t=out:st={fade_at:.3f}:d=1[m]")
        if music.get("duck", True):
            # Music dips automatically whenever the clips have speech or sound.
            parts.append("[0:a]asplit[voice][key];"
                         "[m][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md]")
            mix += ["[voice]", "[md]"]
        else:
            mix += ["[0:a]", "[m]"]
    else:
        mix.append("[0:a]")
    sfx_events = list(plan.get("sfx_events", []))
    if plan.get("sfx"):
        import audio
        sfx_events += audio.auto_events(overlays)
    if sfx_events:
        import audio
        wav = audio.sfx_track(sfx_events, total, os.path.join(workdir, "sfx.wav"))
        si = cmd.count("-i")
        cmd += ["-i", wav]
        parts.append(f"[{si}:a]aformat=channel_layouts=stereo[sx]")
        mix.append("[sx]")
    if len(mix) > 1:
        parts.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,"
                     f"loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    else:
        parts.append(f"{mix[0]}loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    af = ";".join(parts)
    cmd += ["-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", "-t", f"{total:.3f}", out]
    sh(cmd)
    print(f"wrote {out} ({total:.1f}s, {W}x{H})")


if __name__ == "__main__":
    main()
