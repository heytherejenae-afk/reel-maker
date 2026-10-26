#!/usr/bin/env python3
"""Rough cut from the transcript: drop ums, long pauses and retakes, and cut words by text.

  roughcut.py analysis.json OUT.json [--max-pause 0.45] [--clip NAME]
      Writes the cleaned talk as plan-ready segments plus a numbered transcript
      (OUT.json and OUT.md) and lists what it removed. Use the segments as the
      starting point for plan.json, then trim to the best parts.

Cut by word (used by render.py): a segment can carry "cut": ["you know", "basically"],
or the plan "cut_words": [...]. Those words are removed and the segment is split around
them, so the person can cut any word just by naming it in the storyboard.
"""
import argparse
import difflib
import json
import os
import re

FILLERS = {"um", "umm", "uh", "uhh", "er", "erm", "ah", "hmm", "mm"}


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def sentences(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if w["word"].endswith((".", "!", "?")):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def similar(a, b):
    ta, tb = " ".join(norm(w["word"]) for w in a), " ".join(norm(w["word"]) for w in b)
    if len(ta) < 20 or len(tb) < 20:
        return False
    return difflib.SequenceMatcher(None, ta, tb).ratio() > 0.7 or tb.startswith(ta[: int(len(ta) * 0.6)])


def clean_words(words, max_retake_gap=25.0):
    """Remove fillers and earlier takes of a sentence that gets repeated soon after."""
    removed = []
    kept = [w for w in words if norm(w["word"]) not in FILLERS]
    removed += [("filler", w["start"], w["word"]) for w in words if norm(w["word"]) in FILLERS]
    sents = sentences(kept)
    drop = set()
    for i, s in enumerate(sents):
        for j in range(i + 1, min(i + 4, len(sents))):
            if sents[j][0]["start"] - s[-1]["end"] > max_retake_gap:
                break
            if similar(s, sents[j]):
                drop.add(i)
                removed.append(("retake", s[0]["start"], " ".join(w["word"] for w in s)))
                break
    return [w for i, s in enumerate(sents) if i not in drop for w in s], removed


def to_segments(clip, words, max_pause=0.45, lead=0.08, tail=0.15):
    """Group words into segments, splitting wherever the gap is longer than max_pause."""
    segs, run = [], []
    for w in words:
        if run and w["start"] - run[-1]["end"] > max_pause:
            segs.append(run)
            run = []
        run.append(w)
    if run:
        segs.append(run)
    return [{"clip": clip, "start": round(max(0, r[0]["start"] - lead), 2), "end": round(r[-1]["end"] + tail, 2),
             "text": " ".join(w["word"] for w in r)} for r in segs]


def apply_cuts(plan, analysis):
    """Split plan segments around words the person asked to cut (segment "cut" / plan "cut_words")."""
    by_path = {os.path.abspath(c["path"]): c.get("transcript") or [] for c in (analysis or {}).get("clips", [])}
    global_cut = [p.lower() for p in plan.get("cut_words", [])]
    out = []
    for seg in plan["segments"]:
        phrases = global_cut + [p.lower() for p in seg.get("cut", [])]
        words = [w for w in by_path.get(os.path.abspath(seg["clip"]), [])
                 if w["start"] >= seg["start"] - 0.05 and w["end"] <= seg["end"] + 0.05]
        if not phrases or not words:
            out.append(seg)
            continue
        toks = [norm(w["word"]) for w in words]
        holes = []
        for p in phrases:
            pt = [norm(x) for x in p.split()]
            for i in range(len(toks) - len(pt) + 1):
                if toks[i:i + len(pt)] == pt:
                    holes.append((words[i]["start"], words[i + len(pt) - 1]["end"]))
        if not holes:
            out.append(seg)
            continue
        t = seg["start"]
        for a, b in sorted(holes):
            if a - t > 0.25:
                out.append(dict(seg, start=round(t, 2), end=round(a, 2)))
            t = max(t, b)
        if seg["end"] - t > 0.25:
            out.append(dict(seg, start=round(t, 2)))
    plan["segments"] = [{k: v for k, v in s.items() if k != "cut"} for s in out]
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("out")
    ap.add_argument("--max-pause", type=float, default=0.45)
    ap.add_argument("--clip")
    args = ap.parse_args()
    a = json.load(open(args.analysis))
    result, md = {"segments": [], "removed": []}, ["# Transcript (rough cut)", ""]
    for c in a["clips"]:
        if args.clip and c["file"] != args.clip:
            continue
        words, removed = clean_words(c.get("transcript") or [])
        segs = to_segments(c["path"], words, args.max_pause)
        result["segments"] += segs
        result["removed"] += [{"clip": c["file"], "kind": k, "at": t, "text": x} for k, t, x in removed]
        md.append(f"## {c['file']}")
        for i, s in enumerate(segs, 1):
            md.append(f"{i}. [{s['start']:.1f}s] {s['text']}")
        md.append("")
    talk = sum(s["end"] - s["start"] for s in result["segments"])
    json.dump(result, open(args.out, "w"), indent=1)
    open(os.path.splitext(args.out)[0] + ".md", "w").write("\n".join(md))
    print(f"{len(result['segments'])} segments, {talk:.1f}s of talk kept")
    for r in result["removed"]:
        print(f"removed {r['kind']} at {r['at']:.1f}s: {r['text'][:70]}")


if __name__ == "__main__":
    main()
