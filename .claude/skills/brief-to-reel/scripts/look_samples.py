#!/usr/bin/env python3
"""Make the "choose your look" sheets on a frame of the person's own video.

  look_samples.py VIDEO OUT_DIR [--time 5] [--title WORD]

Writes OUT_DIR/styles.jpg (one tile per editing style, numbered), OUT_DIR/font-pairs.jpg
(one tile per font combination: title font + caption font) and OUT_DIR/colours.png (the
colour themes as numbered swatches). Send all three and let the person reply with a style,
a font combination, a colour theme (or their own brand colour), or "you choose".
Single caption fonts (and fonts they bought) have their own sheet: font_samples.py.
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graphics  # noqa: E402
import looks  # noqa: E402
import render  # noqa: E402

W, H = 1080, 1920


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out_dir")
    ap.add_argument("--time", type=float, default=5.0)
    ap.add_argument("--title", default="WATCH THIS")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    bg = os.path.join(tmp, "bg.png")
    render.sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a.time), "-i", a.video, "-frames:v", "1", "-vf",
               f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", bg])
    tiles = []
    for i, (key, st) in enumerate(looks.STYLES.items(), 1):
        plan = {"look": {"style": key}, "highlight_words": ["captions"]}
        look = looks.resolve(plan)
        fonts = {"display": render.font_file(look["display_font"]), "body": render.font_file("Poppins")}
        ov = graphics.build([{"type": "title", "text": a.title, "start": 0, "end": 5, "y": 0.1}], look, fonts, tmp)[0]
        ass = os.path.join(tmp, f"{key}.ass")
        plan["hook"] = {"text": f"{i}. {st['label']}", "duration": 5}
        render.write_ass(ass, plan, [{"start": 0, "end": 5, "text": "This is how your captions look"}], 5, W, H, look)
        _, fontdir = render.pick_font(look.get("font"))
        grade = (look["grade"] + ",") if look.get("grade") else ""
        tile = os.path.join(tmp, f"{key}.png")
        render.sh(["ffmpeg", "-y", "-loglevel", "error", "-i", bg, "-i", ov["_frames"][0], "-filter_complex",
                   f"[0:v]{grade}format=rgba[b];[b][1:v]overlay=0:{ov['_y'] + 300}[o];"
                   f"[o]ass={ass}:fontsdir={fontdir},scale=360:640", tile])
        tiles.append(tile)
    inputs = sum([["-i", t] for t in tiles], [])
    render.sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
               f"hstack=inputs={len(tiles)}", "-q:v", "3", os.path.join(a.out_dir, "styles.jpg")])

    tiles = []  # font combinations, shown in the Clean style so only the fonts change
    for i, (key, fp) in enumerate(looks.FONT_PAIRS.items(), 1):
        plan = {"look": {"style": "clean", "font_pair": key, "caption_case": "sentence"},
                "highlight_words": ["captions"]}
        look = looks.resolve(plan)
        fonts = {"display": render.font_file(look["display_font"]), "body": render.font_file("Poppins")}
        ov = graphics.build([{"type": "title", "text": a.title, "start": 0, "end": 5, "y": 0.1}], look, fonts, tmp)[0]
        ass = os.path.join(tmp, f"fp_{key}.ass")
        plan["hook"] = {"text": f"{i}. {fp['label']}", "duration": 5}
        render.write_ass(ass, plan, [{"start": 0, "end": 5, "text": "This is how your captions look"}], 5, W, H, look)
        _, fontdir = render.pick_font(look.get("font"))
        tile = os.path.join(tmp, f"fp_{key}.png")
        render.sh(["ffmpeg", "-y", "-loglevel", "error", "-i", bg, "-i", ov["_frames"][0], "-filter_complex",
                   f"[0:v]format=rgba[b];[b][1:v]overlay=0:{ov['_y'] + 300}[o];"
                   f"[o]ass={ass}:fontsdir={fontdir},scale=360:640", tile])
        tiles.append(tile)
    inputs = sum([["-i", t] for t in tiles], [])
    render.sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
               f"xstack=inputs={len(tiles)}:layout=0_0|360_0|720_0|0_640|360_640|720_640", "-q:v", "3",
               os.path.join(a.out_dir, "font-pairs.jpg")])

    sw = "".join(
        f"<div class=t><div class=b style='background:{c['primary']}'><span style='color:{c['light']}'>Aa</span>"
        f"<i style='background:{c['highlight']}'></i></div><div class=n>{i}. {name.title()}</div></div>"
        for i, (name, c) in enumerate(looks.THEMES.items(), 1))
    css = (".g{display:flex;flex-wrap:wrap;gap:24px;padding:30px;background:#fff;width:1080px}"
           ".t{width:234px}.b{height:180px;border-radius:24px;position:relative;display:flex;align-items:center;"
           "justify-content:center;font:900 80px Poppins,sans-serif}.b i{position:absolute;right:16px;bottom:16px;"
           "width:50px;height:50px;border-radius:50%}.n{font:700 34px sans-serif;margin-top:8px;text-align:center}")
    rows = -(-len(looks.THEMES) // 4)
    jf = os.path.join(tmp, "jobs.json")
    import json
    json.dump([{"html": graphics.page(f"<div class=g>{sw}</div>", css, {}, 1080, 60 + rows * 280),
                "out": os.path.join(a.out_dir, "colours.png"), "width": 1080, "height": 60 + rows * 280}],
              open(jf, "w"))
    subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "html2png.js"), jf], check=True)
    for i, (k, st) in enumerate(looks.STYLES.items(), 1):
        print(f"style {i}. {st['label']}  ->  \"look\": {{\"style\": \"{k}\"}}")
    for i, (k, fp) in enumerate(looks.FONT_PAIRS.items(), 1):
        print(f"fonts {i}. {fp['label']} ({fp['display_font']} + {fp['font']})  ->  \"look\": {{\"font_pair\": \"{k}\"}}")
    for i, k in enumerate(looks.THEMES, 1):
        print(f"colour {i}. {k.title()}  ->  \"look\": {{\"theme\": \"{k}\"}}")


if __name__ == "__main__":
    main()
