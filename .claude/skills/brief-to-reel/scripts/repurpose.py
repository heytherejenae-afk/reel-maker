#!/usr/bin/env python3
"""Turn one finished reel into a carousel, a story and three trial reels.

Usage: repurpose.py PLAN.json REEL.mp4 OUT_DIR --analysis analysis.json [--only carousel,story,trials]

Uses the same look (style, colours, fonts) as the reel. Optional plan keys:
  "points":      [{"title": "Zucchini", "text": "50 days from seed to plate", "t": 12.0}, ...]
                 one carousel slide each; "t" is the reel second to use as the photo.
                 Without it, the title/badge/card overlays become the slides.
  "cta":         "Comment CHRISTMAS for the free planner"   last slide and story text
  "trial_hooks": ["3 plants that still make it by Christmas", "Stop buying Christmas veg", ...]
                 hook text for the three trial reels (Instagram's "trial reels" test new hooks
                 on non-followers first).
"""
import argparse
import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graphics  # noqa: E402
import looks  # noqa: E402
import render  # noqa: E402

CTA_TYPES = {"comment_box", "dm_reply", "follow", "comments"}


def frame(plan, t, out):
    """A clean 4:5 photo (no captions or overlays) from the source clip behind reel second t."""
    for seg in plan["segments"]:
        d = (seg["end"] - seg["start"]) / float(seg.get("speed", 1.0))
        if t < d or seg is plan["segments"][-1]:
            src_t = seg["start"] + min(t, d) * float(seg.get("speed", 1.0))
            fx = float(seg.get("focus_x", 0.5))
            vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)*{fx}:(ih-1920)/2,"
                  f"crop=1080:1350:0:250")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{src_t:.2f}", "-i", seg["clip"],
                            "-frames:v", "1", "-vf", vf, out], check=True)
            return out
        t -= d


def points_from(plan):
    pts = []
    for o in plan.get("overlays", []):
        if o["type"] in ("title", "badge"):
            pts.append({"title": o["text"].title() if o["text"].isupper() else o["text"],
                        "text": o.get("sub", ""), "t": o["start"] + 0.5})
        elif o["type"] == "card":
            pts.append({"title": o.get("title", ""), "text": " · ".join(o.get("lines", [])), "t": o["start"] + 0.5})
    return pts


def carousel(plan, reel, out_dir, look, fonts):
    c = look["colors"]
    pts = plan.get("points") or points_from(plan)
    hook = plan.get("trial_hooks", [None])[0] or (plan.get("hook") or {}).get("text") or (pts[0]["title"] if pts else "")
    cta = plan.get("cta") or (plan.get("end_text") or {}).get("text") or "Save this for later"
    F = {"D": fonts["display"], "B": fonts["body"]}
    css = (f".s{{position:relative;width:1080px;height:1350px;background:{c['primary']} center/cover;"
           f"font-family:B;color:{c['light']}}}.sh{{position:absolute;inset:0;background:linear-gradient("
           f"180deg,rgba(0,0,0,0) 35%,rgba(0,0,0,.75))}}.t{{position:absolute;left:70px;right:70px;bottom:120px;"
           f"font-family:D;font-size:110px;line-height:1.02}}.x{{position:absolute;left:70px;right:70px;"
           f"bottom:60px;font-size:44px;opacity:.95}}.n{{position:absolute;top:60px;left:70px;font-size:40px;"
           f"background:{c['light']};color:{c['primary']};border-radius:30px;padding:8px 26px;font-weight:800}}"
           f".cta{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;"
           f"text-align:center;padding:100px;font-family:D;font-size:100px;line-height:1.05}}"
           f".sw{{position:absolute;right:70px;top:60px;font-size:36px;font-weight:800;background:{c['light']};"
           f"color:{c['primary']};border-radius:30px;padding:8px 26px}}")
    jobs, slides = [], []
    os.makedirs(out_dir, exist_ok=True)
    total = len(pts) + 2
    cover = frame(plan, 0.6, os.path.join(out_dir, "_f0.jpg"))
    docs = [f"<div class=s style=\"background-image:url('file://{cover}')\"><div class=sh></div>"
            f"<div class=sw>Swipe →</div><div class=t>{graphics.esc(hook)}</div></div>"]
    for i, p in enumerate(pts, 1):
        img = frame(plan, float(p.get("t", 1)), os.path.join(out_dir, f"_f{i}.jpg"))
        docs.append(f"<div class=s style=\"background-image:url('file://{img}')\"><div class=sh></div>"
                    f"<div class=n>{i}/{len(pts)}</div><div class=t style='bottom:{170 if p.get('text') else 120}px'>"
                    f"{graphics.esc(p['title'])}</div><div class=x>{graphics.esc(p.get('text', ''))}</div></div>")
    docs.append(f"<div class=s><div class=cta>{graphics.esc(cta)}</div></div>")
    for k, body in enumerate(docs, 1):
        png = os.path.join(out_dir, f"slide_{k:02d}.png")
        jobs.append({"html": graphics.page(body, css, F, 1080, 1350), "out": png, "width": 1080, "height": 1350})
        slides.append(png)
    jf = os.path.join(out_dir, "_jobs.json")
    json.dump(jobs, open(jf, "w"))
    subprocess.run(["node", os.path.join(HERE, "html2png.js"), jf], check=True)
    for f in os.listdir(out_dir):
        if f.startswith("_") or f.endswith(".html"):
            os.remove(os.path.join(out_dir, f))
    print(f"carousel: {total} slides in {out_dir}")
    return slides


def story(plan, reel, out, look, fonts, workdir):
    """First ~12 s of the reel with a 'New reel' sticker over the last 3 seconds."""
    sticker = {"type": "badge", "text": "New reel ↓ tap to watch", "start": 9.0, "end": 12.0, "y": 0.62}
    built = graphics.build([sticker], look, fonts, workdir)
    png = built[0]["_frames"][0]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-t", "12", "-i", reel, "-i", png, "-filter_complex",
                    f"[0:v][1:v]overlay=0:{built[0]['_y']}:enable='between(t,9,12)'[v]", "-map", "[v]",
                    "-map", "0:a?", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-movflags", "+faststart", out], check=True)
    print(f"story: {out}")
    return out


def trial_plans(plan, offsets_total):
    """Three variants: new hook, a short cut, and the twist moved to the front."""
    hooks = plan.get("trial_hooks") or []
    segs = plan["segments"]
    cta_ovs = [o for o in plan.get("overlays", []) if o["type"] in CTA_TYPES]

    def seg_len(s):
        return (s["end"] - s["start"]) / float(s.get("speed", 1.0))

    def finish(p, segments, hook_text):
        p["segments"] = segments
        total = sum(seg_len(s) for s in segments)
        ovs = []
        if hook_text:
            ovs.append({"type": "title" if looks.resolve(p).get("title_3d") else "headline",
                        "text": hook_text, "lines": [{"text": hook_text}], "start": 0.0, "end": 2.6,
                        "behind": True, "y": 0.08})
        for o in cta_ovs:  # keep the call to action at the end
            d = o["end"] - o["start"]
            back = offsets_total - o["end"]
            ovs.append(dict(o, start=round(total - back - d, 2), end=round(total - back, 2)))
        p["overlays"] = ovs
        p.pop("hook", None)
        return p

    v1 = finish(copy.deepcopy(plan), list(segs), hooks[0] if hooks else None)
    short, t = [segs[0]], seg_len(segs[0])
    for s in segs[1:-1]:
        if t + seg_len(s) > 18:
            break
        short.append(s)
        t += seg_len(s)
    v2 = finish(copy.deepcopy(plan), short + [segs[-1]], hooks[1] if len(hooks) > 1 else None)
    twist = [s for s in segs if s.get("rehook")] or [segs[-2]]
    rest = [s for s in segs if s not in twist]
    v3 = finish(copy.deepcopy(plan), twist + rest, hooks[2] if len(hooks) > 2 else None)
    return [("new-hook", v1), ("short", v2), ("twist-first", v3)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("reel")
    ap.add_argument("out_dir")
    ap.add_argument("--analysis")
    ap.add_argument("--only", default="carousel,story,trials")
    a = ap.parse_args()
    a.out_dir, a.reel = os.path.abspath(a.out_dir), os.path.abspath(a.reel)
    plan = json.load(open(a.plan))
    look = looks.resolve(plan)
    fonts = {"display": render.font_file(look.get("display_font")), "body": render.font_file("Poppins"),
             "script": render.font_file(look.get("script_font", "Caveat Brush"))}
    os.makedirs(a.out_dir, exist_ok=True)
    work = os.path.join(a.out_dir, "_work")
    os.makedirs(work, exist_ok=True)
    todo = a.only.split(",")
    if "carousel" in todo:
        carousel(plan, a.reel, os.path.join(a.out_dir, "carousel"), look, fonts)
    if "story" in todo:
        story(plan, a.reel, os.path.join(a.out_dir, "story.mp4"), look, fonts, work)
    if "trials" in todo:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                    "csv=p=0", a.reel], capture_output=True, text=True).stdout)
        for name, p in trial_plans(plan, dur):
            p["output"] = os.path.abspath(os.path.join(a.out_dir, f"trial-{name}.mp4"))
            pf = os.path.join(work, f"trial-{name}.json")
            json.dump(p, open(pf, "w"), indent=1)
            cmd = [sys.executable, os.path.join(HERE, "render.py"), pf, "--workdir", os.path.join(work, name)]
            if a.analysis:
                cmd += ["--analysis", a.analysis]
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
