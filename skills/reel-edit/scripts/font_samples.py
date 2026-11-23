#!/usr/bin/env python3
"""Make a numbered sheet showing caption fonts on a frame of the person's own video.

Includes every free font in render.FONTS plus any .ttf/.otf files passed with
--custom (for example fonts the person bought and put in their Drive folder).
The person replies with a number to choose.

Usage: font_samples.py VIDEO OUT.jpg [--time 5] [--custom a.ttf b.otf]
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--time", type=float, default=5.0)
    ap.add_argument("--custom", nargs="*", default=[])
    args = ap.parse_args()

    tmp = tempfile.mkdtemp()
    W, H = 1080, 1920
    bg = os.path.join(tmp, "bg.png")
    # Same framing as the reel: fill a 9:16 frame from the centre.
    render.sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(args.time), "-i", args.video,
               "-frames:v", "1", "-vf",
               f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", bg])

    options = [("Inter Display", None)] + [(n, n) for n in render.FONTS] + \
              [(os.path.splitext(os.path.basename(p))[0], p) for p in args.custom]
    tiles = []
    for i, (label, font) in enumerate(options, 1):
        plan = {"style": {"font": font} if font else {},
                "hook": {"text": f"{i}. {label}", "duration": 5}}
        ass = os.path.join(tmp, f"s{i}.ass")
        render.write_ass(ass, plan, [{"start": 0, "end": 5, "text": "This is how your captions look"}],
                         5, W, H)
        _, fontdir = render.pick_font(font)
        tile = os.path.join(tmp, f"s{i}.png")
        render.sh(["ffmpeg", "-y", "-loglevel", "error", "-i", bg, "-vf",
                   f"ass={ass}:fontsdir={fontdir},scale=360:640", tile])
        tiles.append(tile)

    cols = 3
    while len(tiles) % cols:  # pad the grid with blank tiles
        blank = os.path.join(tmp, f"blank{len(tiles)}.png")
        render.sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                   "color=c=white:s=360x640", "-frames:v", "1", blank])
        tiles.append(blank)
    layout = "|".join(f"{(k % cols) * 360}_{(k // cols) * 640}" for k in range(len(tiles)))
    inputs = sum([["-i", t] for t in tiles], [])
    render.sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
               f"xstack=inputs={len(tiles)}:layout={layout}", "-q:v", "3", args.out])
    for i, (label, font) in enumerate(options, 1):
        print(f"{i}. {label}" + (f"  ->  style.font = {font!r}" if font else "  (default)"))


if __name__ == "__main__":
    main()
