#!/usr/bin/env python3
"""Save the look from a plan to a brand kit, so every future reel matches.

Usage: brand.py PLAN.json OUT/brand-kit.json [--name Butter] [--default] [--handle NAME]
                [--avatar PATH] [--autopilot on|off]

--name adds the look to the kit's lookbook under that name (use it for each look they
love: "Butter", "Playful"...); --default makes it the one used when none is picked.
--autopilot on means future reels skip the questions and storyboard and go straight to
the finished reel in the default look.

Put brand-kit.json in the person's Drive clips folder (Google Drive connector
create_file, or give them the file to add). fetch_drive.py downloads it with the clips,
and the plan uses it with "look": {"brand": "work/clips/brand-kit.json"}.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import looks  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("plan")
ap.add_argument("out")
ap.add_argument("--name")
ap.add_argument("--default", action="store_true")
ap.add_argument("--handle")
ap.add_argument("--avatar")
ap.add_argument("--autopilot", choices=["on", "off"])
a = ap.parse_args()
req = dict(json.load(open(a.plan)).get("look") or {})
if a.handle:
    req["handle"] = a.handle
if a.avatar:
    req["avatar"] = a.avatar
extra = {}
if a.default and a.name:
    extra["default"] = a.name
if a.autopilot:
    extra["autopilot"] = a.autopilot == "on"
path = looks.save_brand(a.out, req, a.name, extra)
kit = json.load(open(path))
print("saved", path, "| lookbook:", ", ".join(kit.get("looks", {})) or "-", "| autopilot:", kit.get("autopilot", False))
