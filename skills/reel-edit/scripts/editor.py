#!/usr/bin/env python3
"""Make the Reel Editor page: the finished reel plus every shot, caption and overlay,
editable by tapping, so the person can ask for changes without knowing any jargon.

Usage: editor.py PLAN.json OUT.html [--analysis analysis.json] [--reel reel.mp4] [--name "Raspberries"]
                 [--stage storyboard|reel]

The same page is the editable storyboard (before rendering, no --reel: "Build my
reel" / "Copy my changes") and the Reel Editor (after rendering, with the reel
playable at the top so they can watch it inside Claude).

The page shows the reel (a small copy is embedded when it fits), then one card per
shot (picture, the words said, tick boxes for "remove this shot" and "show big in the
middle", up/down to move it, key words to highlight), one card per on-screen title or
pop-up (edit the words or remove it), the look and music, and a free-text box.
"Copy my changes" gives a block starting `REEL CHANGES` that the person pastes back
into the chat; apply it to plan.json and render again (see SKILL.md step 5).
Publish the HTML with the Artifact tool (a new page per reel, or republish the same file).
"""
import argparse
import base64
import html
import json
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_KEYS = ("text", "sub", "title", "reply", "comment", "lines")


def b64(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def thumb(clip, t, tmp, n):
    out = os.path.join(tmp, f"s{n}.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(t, 0):.2f}", "-i", clip,
                    "-frames:v", "1", "-vf", "scale=200:-2", "-q:v", "5", out], check=True)
    return b64(out, "image/jpeg")


def small_reel(reel, tmp, limit_mb=9):
    """A phone-sized copy of the reel for the page; None if it won't fit."""
    out = os.path.join(tmp, "reel-small.mp4")
    for crf in (30, 34, 38):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", reel, "-vf", "scale=540:-2",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-c:a", "aac",
                        "-b:a", "64k", "-movflags", "+faststart", out], check=True)
        if os.path.getsize(out) < limit_mb * 1e6:
            return b64(out, "video/mp4")
    return None


def words_for(analysis, clip, start, end):
    for c in (analysis or {}).get("clips", []):
        if os.path.basename(c.get("path") or c.get("file", "")) == os.path.basename(clip):
            ws = [w["word"] for w in (c.get("transcript") or []) if start - 0.05 <= w["start"] < end - 0.1]
            return " ".join(ws).strip()
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("out")
    ap.add_argument("--analysis")
    ap.add_argument("--reel")
    ap.add_argument("--name", default="My reel")
    ap.add_argument("--stage", choices=["storyboard", "reel"], default=None,
                    help="storyboard = before rendering (no video yet); reel = after (default when --reel is given)")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    analysis = json.load(open(a.analysis)) if a.analysis else None
    tmp = tempfile.mkdtemp()

    shots, t = [], 0.0
    for n, s in enumerate(plan.get("segments", []), 1):
        dur = (s["end"] - s["start"]) / float(s.get("speed", 1) or 1)
        shots.append({"n": n, "at": round(t, 1), "len": round(dur, 1),
                      "pic": thumb(s["clip"], (s["start"] + s["end"]) / 2, tmp, n),
                      "words": words_for(analysis, s["clip"], s["start"], s["end"])})
        t += dur
    centre = plan.get("center_lines", [])
    for s in shots:
        s["centre"] = any(c.lower() in s["words"].lower() for c in centre if c)

    overlays = []
    for n, o in enumerate(plan.get("overlays", []), 1):
        fields = {}
        for k in TEXT_KEYS:
            v = o.get(k)
            if isinstance(v, str):
                fields[k] = v
            elif isinstance(v, list):
                fields[k] = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in v)
        if o.get("emoji"):
            fields["emoji"] = o["emoji"]
        overlays.append({"n": n, "type": o.get("type", "title"), "at": round(o.get("start", 0), 1), "fields": fields})

    look = plan.get("look", {})
    music = plan.get("music")
    data = {
        "name": a.name, "stage": a.stage or ("reel" if a.reel else "storyboard"), "length": round(t, 1), "shots": shots, "overlays": overlays,
        "highlight_words": plan.get("highlight_words", []),
        "look": {"style": look.get("style", ""), "font_pair": look.get("font_pair", ""), "theme": look.get("theme", "")},
        "music": (music.get("track") if isinstance(music, dict) else "") if music else "none",
        "video": small_reel(a.reel, tmp) if a.reel else None,
    }
    page = open(os.path.join(HERE, "editor_template.html")).read()
    page = page.replace("__TITLE__", html.escape(a.name)).replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    with open(a.out, "w") as f:
        f.write(page)
    print(a.out, f"{os.path.getsize(a.out) / 1e6:.1f} MB", "video embedded" if data["video"] else "no video")


if __name__ == "__main__":
    main()
