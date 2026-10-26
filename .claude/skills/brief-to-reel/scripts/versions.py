#!/usr/bin/env python3
"""Build three short versions of the opening so the person can pick a favourite.

Usage: versions.py PLAN.json OUT_DIR --analysis analysis.json [--seconds 6]
                   [--looks editorial,creator,bold]  (styles, or lookbook names if the plan has a brand kit)
                   [--hooks "Hook one" "Hook two" "Hook three"]

Each version is the first few seconds of the plan with a different look and/or hook
title. Writes version-1.mp4 .. version-3.mp4 and versions.mp4 (all three side by side,
numbered). Send versions.mp4 and ask "Which one do you like best? 1, 2 or 3".
Then use that look (and hook) for the full reel; offer to save it to their lookbook.
"""
import argparse
import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import looks  # noqa: E402


def cut_to(plan, seconds):
    segs, t = [], 0.0
    for s in plan["segments"]:
        d = (s["end"] - s["start"]) / float(s.get("speed", 1.0))
        if t + d >= seconds:
            segs.append(dict(s, end=round(s["start"] + (seconds - t) * float(s.get("speed", 1.0)), 2)))
            break
        segs.append(s)
        t += d
    plan["segments"] = segs
    plan["overlays"] = [dict(o, end=min(o["end"], seconds)) for o in plan.get("overlays", [])
                        if o["start"] < seconds - 0.5]
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("out_dir")
    ap.add_argument("--analysis")
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--looks", default="editorial,creator,bold")
    ap.add_argument("--hooks", nargs="*", default=[])
    a = ap.parse_args()
    out_dir = os.path.abspath(a.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    base = json.load(open(a.plan))
    names = a.looks.split(",")
    labels, files = [], []
    for i in range(3):
        p = cut_to(copy.deepcopy(base), a.seconds)
        name = names[i % len(names)]
        req = dict(p.get("look") or {})
        if req.get("brand"):
            req["lookbook"] = name
        else:
            req = {k: v for k, v in req.items() if k in ("colors", "handle", "avatar")}
            req["style"] = name
        p["look"] = req
        if i < len(a.hooks):
            p.pop("hook", None)
            titles = [o for o in p.get("overlays", []) if o["type"] in ("title", "headline") and o["start"] < 1]
            if titles:
                titles[0]["text"] = a.hooks[i]
                titles[0]["lines"] = [{"text": a.hooks[i]}]
            else:
                p.setdefault("overlays", []).insert(0, {"type": "title", "text": a.hooks[i], "start": 0.0,
                                                        "end": min(2.6, a.seconds), "y": 0.08})
        p["output"] = os.path.join(out_dir, f"version-{i + 1}.mp4")
        pf = os.path.join(out_dir, f"version-{i + 1}.json")
        json.dump(p, open(pf, "w"), indent=1)
        cmd = [sys.executable, os.path.join(HERE, "render.py"), pf, "--workdir", os.path.join(out_dir, f"_w{i + 1}")]
        if a.analysis:
            cmd += ["--analysis", a.analysis]
        subprocess.run(cmd, check=True)
        label = looks.STYLES.get(name, {}).get("label", name)
        labels.append(f"{i + 1}. {label}" + (f" · {a.hooks[i]}" if i < len(a.hooks) else ""))
        files.append(p["output"])
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    inputs = sum([["-i", f] for f in files], [])
    fc = ";".join(f"[{i}:v]scale=360:640,drawtext=fontfile={font}:text='{i + 1}':x=20:y=20:fontsize=64:"
                  f"fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=12[v{i}]" for i in range(3))
    fc += ";[v0][v1][v2]hstack=inputs=3[v]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[v]",
                    "-map", "0:a?", "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-shortest",
                    os.path.join(out_dir, "versions.mp4")], check=True)
    print("\n".join(labels))


if __name__ == "__main__":
    main()
