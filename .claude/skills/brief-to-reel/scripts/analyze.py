#!/usr/bin/env python3
"""Analyse a folder of raw clips so Claude can pick the best moments.

For every clip it records basic metadata, scores each second for brightness,
sharpness and motion, writes a contact sheet of frames to look at, and (when a
Whisper model is available) a word-timed transcript.

Usage: analyze.py CLIPS_DIR OUT_DIR [--no-transcribe] [--model base]
Writes OUT_DIR/analysis.json and OUT_DIR/sheets/<clip>.jpg
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".webm", ".mkv", ".3gp"}
SAMPLE_FPS = 2  # frames per second analysed


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json",
               "-show_streams", "-show_format", path])
    info = json.loads(out.stdout or "{}")
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        return None
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    rot = int(v.get("tags", {}).get("rotate", rot))
    if abs(rot) % 180 == 90:
        w, h = h, w  # phone clips shot upright but stored sideways
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    dur = float(info.get("format", {}).get("duration") or v.get("duration") or 0)
    return {"width": w, "height": h, "fps": round(fps, 3), "duration": round(dur, 3),
            "has_audio": a is not None,
            "orientation": "vertical" if h > w else ("square" if h == w else "landscape")}


def frame_stats(path):
    """Per-sample brightness (YAVG), blur and scene-change score."""
    vf = (f"fps={SAMPLE_FPS},scale=320:-2,signalstats,blurdetect,"
          "select='gte(scene,0)',metadata=print:file=-")
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vf", vf,
               "-an", "-f", "null", "-"])
    samples, cur = [], None
    for line in out.stdout.splitlines():
        m = re.match(r"frame:\s*\d+\s+pts:\s*\S+\s+pts_time:([\d.]+)", line)
        if m:
            cur = {"t": float(m.group(1))}
            samples.append(cur)
            continue
        if cur is None or "=" not in line:
            continue
        k, val = line.strip().split("=", 1)
        try:
            val = float(val)
        except ValueError:
            continue
        if math.isnan(val):
            continue  # e.g. blurdetect on a flat black frame
        if k.endswith("YAVG"):
            cur["brightness"] = val
        elif k.endswith("blur"):
            cur["blur"] = val
        elif k.endswith("scene_score"):
            cur["motion"] = val
    return samples


def audio_loudness(path, duration):
    """Momentary loudness per second, used to find moments with speech/action."""
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
               "ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-",
               "-vn", "-f", "null", "-"])
    per_sec = {}
    t = None
    for line in out.stdout.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1))
        elif "lavfi.r128.M=" in line and t is not None:
            v = float(line.split("=", 1)[1])
            per_sec.setdefault(int(t), []).append(v)
    return {s: max(v) for s, v in per_sec.items()}


def score_seconds(samples, loud, duration):
    secs = []
    for s in range(int(math.ceil(duration))):
        pts = [x for x in samples if s <= x["t"] < s + 1]
        if not pts:
            continue
        b = sum(p.get("brightness", 0) for p in pts) / len(pts)
        blur = sum(p.get("blur", 0) for p in pts) / len(pts)
        motion = max(p.get("motion", 0) for p in pts)
        l = loud.get(s, -70.0)
        # 0..1 sub-scores
        light = max(0.0, 1 - abs(b - 125) / 125)          # well exposed ~ mid grey
        sharp = max(0.0, min(1.0, 1 - (blur - 2) / 8))     # blurdetect: lower is sharper
        energy = min(1.0, motion * 8)                      # something is happening
        sound = max(0.0, min(1.0, (l + 50) / 35))          # -50..-15 LUFS
        total = 0.35 * sharp + 0.25 * light + 0.25 * energy + 0.15 * sound
        flags = []
        if b < 40:
            flags.append("too_dark")
        if b > 225:
            flags.append("blown_out")
        if blur > 8:
            flags.append("blurry")
        if motion > 0.6:
            flags.append("hard_cut_or_shake")
        secs.append({"t": s, "score": round(total, 3), "brightness": round(b, 1),
                     "blur": round(blur, 2), "motion": round(motion, 3),
                     "loudness": round(l, 1), "flags": flags})
    return secs


def best_windows(secs, length=3, top=3):
    """Highest scoring stretches of `length` seconds, non-overlapping."""
    cands = []
    for i in range(len(secs) - length + 1):
        win = secs[i:i + length]
        if win[-1]["t"] - win[0]["t"] != length - 1:
            continue
        cands.append((sum(x["score"] for x in win) / length, win[0]["t"]))
    cands.sort(reverse=True)
    picked = []
    for sc, start in cands:
        if all(abs(start - p["start"]) >= length for p in picked):
            picked.append({"start": start, "end": start + length, "score": round(sc, 3)})
        if len(picked) == top:
            break
    return picked


def contact_sheet(path, duration, out_jpg, cols=4, rows=3):
    n = cols * rows
    step = max(duration / n, 0.1)
    vf = (f"fps=1/{step:.3f},scale=320:-2,"
          f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
          f"text='%{{pts\\:hms}}':x=6:y=6:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6,"
          f"tile={cols}x{rows}")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf", vf,
         "-frames:v", "1", "-q:v", "4", out_jpg])
    return os.path.exists(out_jpg)


def transcribe(path, model):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, "faster-whisper not installed"
    try:
        m = transcribe.cache.get(model) or WhisperModel(model, device="cpu", compute_type="int8")
        transcribe.cache[model] = m
        # Decode with ffmpeg ourselves: newer PyAV releases break faster-whisper's own decoder.
        import numpy as np
        pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-vn", "-ac", "1",
                              "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
        audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
        # The prompt nudges Whisper to keep "um"s so the rough cut can remove them.
        segs, _ = m.transcribe(audio, word_timestamps=True, vad_filter=True,
                               initial_prompt="Umm, uh, so, like, you know, I mean, er.")
        words = []
        for seg in segs:
            for w in seg.words or []:
                words.append({"start": round(w.start, 2), "end": round(w.end, 2),
                              "word": w.word.strip()})
        return words, None
    except Exception as e:  # model download blocked, no audio, etc.
        return None, str(e).splitlines()[0][:200]


transcribe.cache = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--model", default="base")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.out_dir, "sheets"), exist_ok=True)
    clips = []
    for name in sorted(os.listdir(args.clips_dir)):
        if os.path.splitext(name)[1].lower() not in VIDEO_EXT:
            continue
        path = os.path.join(args.clips_dir, name)
        meta = probe(path)
        if not meta:
            print(f"skip {name}: no video stream", file=sys.stderr)
            continue
        print(f"analysing {name} ({meta['duration']}s)", file=sys.stderr)
        samples = frame_stats(path)
        loud = audio_loudness(path, meta["duration"]) if meta["has_audio"] else {}
        secs = score_seconds(samples, loud, meta["duration"])
        sheet = os.path.join(args.out_dir, "sheets", os.path.splitext(name)[0] + ".jpg")
        contact_sheet(path, meta["duration"], sheet)
        words, err = (None, "skipped")
        if meta["has_audio"] and not args.no_transcribe:
            words, err = transcribe(path, args.model)
        overall = round(sum(s["score"] for s in secs) / len(secs), 3) if secs else 0
        flag_counts = {}
        for s in secs:
            for f in s["flags"]:
                flag_counts[f] = flag_counts.get(f, 0) + 1
        clips.append({
            "file": name, "path": os.path.abspath(path), **meta,
            "overall_score": overall, "flag_seconds": flag_counts,
            "best_windows": best_windows(secs),
            "seconds": secs, "contact_sheet": os.path.abspath(sheet),
            "transcript": words, "transcript_error": err if words is None else None,
        })
    clips.sort(key=lambda c: c["overall_score"], reverse=True)
    out = os.path.join(args.out_dir, "analysis.json")
    with open(out, "w") as f:
        json.dump({"clips": clips}, f, indent=1)
    for c in clips:
        print(f"{c['overall_score']:.2f}  {c['file']}  {c['orientation']}  "
              f"{c['duration']}s  best={c['best_windows'][:1]}  flags={c['flag_seconds']}")
    print(out)


if __name__ == "__main__":
    main()
