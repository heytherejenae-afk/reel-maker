"""Put colour grading, animated overlays and picture-in-picture onto the joined reel.

Overlays slide up and fade in, then fade out. Multi-frame overlays (comment stacks,
typing, the Follow tap) step through their frames: the first frames play quickly and
the last one holds. "behind": true titles go between the background and the person,
using a person cut-out mask from models/selfie_segmenter.tflite.
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "..", "models", "selfie_segmenter.tflite")
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/"
             "selfie_segmenter/float16/latest/selfie_segmenter.tflite")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd)[:2000] + "\n" + r.stderr[-3000:])
        raise SystemExit("ffmpeg failed in effects")


def frames_clip(o, workdir, n):
    """Turn an overlay's PNG frames into one short transparent .mov."""
    frames, dur = o["_frames"], o["end"] - o["start"]
    if o.get("_gif"):  # a GIF/image/video sticker: scale it into its box and loop it
        size, box = int(o.get("size", 260)), o["_size"][0]
        out = os.path.join(workdir, f"ov{n}.mov")
        run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", o["_gif"], "-t", f"{dur:.3f}",
             "-vf", f"fps=30,scale={size}:{size}:force_original_aspect_ratio=decrease,format=rgba,"
                    f"pad={box}:{box}:(ow-iw)/2:(oh-ih)/2:color=0x00000000",
             "-c:v", "png", out])
        return out
    if len(frames) == 1:
        steps = [dur]
    else:  # step through quickly (max ~0.15s each, within the first 60%), hold the last
        quick = {"follow": 0.5, "sticker": 0.06}.get(o["type"], 0.15)
        step = min(quick, dur * 0.6 / (len(frames) - 1))
        steps = [step] * (len(frames) - 1) + [dur - step * (len(frames) - 1)]
    lst = os.path.join(workdir, f"ov{n}.txt")
    with open(lst, "w") as f:
        for p, d in zip(frames, steps):
            f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{frames[-1]}'\n")
    out = os.path.join(workdir, f"ov{n}.mov")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-vf", "fps=30,format=rgba", "-c:v", "png", "-t", f"{dur:.3f}", out])
    return out


def person_mask(video, workdir, W, H, fps):
    """Grey-scale mask video (white = person) for the whole reel."""
    if not os.path.exists(MODEL):
        os.makedirs(os.path.dirname(MODEL), exist_ok=True)
        subprocess.run(["curl", "-sSfL", "-m", "60", "-o", MODEL, MODEL_URL], check=True)
    from ai_edge_litert.interpreter import Interpreter
    from PIL import Image, ImageFilter
    it = Interpreter(model_path=MODEL)
    it.allocate_tensors()
    i, o = it.get_input_details()[0], it.get_output_details()[0]
    mh, mw = i["shape"][1:3]
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", video, "-vf", f"scale={mw}:{mh}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    out = os.path.join(workdir, "mask.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                            "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "16",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    size = mw * mh * 3
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        x = np.frombuffer(buf, np.uint8).reshape(mh, mw, 3).astype(np.float32)[None] / 255.0
        it.set_tensor(i["index"], x)
        it.invoke()
        m = it.get_tensor(o["index"])[0, :, :, 0]
        m = np.clip((m - 0.35) / 0.3, 0, 1)  # firm up the edge
        img = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        enc.stdin.write(img.filter(ImageFilter.GaussianBlur(3)).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()
    return out


def apply(joined, overlays, look, W, H, fps, workdir, total):
    """Returns (extra ffmpeg inputs, filter graph text ending in [fx]) for the final pass."""
    inputs, chain, cur = [], [], "[0:v]"
    nxt = [1]

    def add_input(args):
        inputs.extend(args)
        k = nxt[0]
        nxt[0] += 1
        return k

    if look.get("grade"):
        chain.append(f"{cur}{look['grade']},format=yuv420p[g]")
        cur = "[g]"
    behind = [o for o in overlays if o.get("behind")]
    front = [o for o in overlays if not o.get("behind")]
    if behind:
        chain.append(f"{cur}split[gb][gp]")
        cur, person_src = "[gb]", "[gp]"
    for n, o in enumerate(behind + front):
        s, e = float(o["start"]), float(o["end"])
        if o["type"] == "pip":  # video inside the card
            k = add_input(["-ss", str(o.get("clip_start", 0)), "-t", f"{e - s:.3f}", "-i", o["clip"]])
            hx, hy, hw, hh = o["_hole"]
            chain.append(f"[{k}:v]scale={hw}:{hh}:force_original_aspect_ratio=increase,crop={hw}:{hh},"
                         f"setpts=PTS-STARTPTS+{s}/TB,format=rgba,fade=t=in:st={s}:d=0.25:alpha=1,"
                         f"fade=t=out:st={e - 0.2:.3f}:d=0.2:alpha=1[pv{n}]")
        mov = frames_clip(o, workdir, n)
        k = add_input(["-i", mov])
        chain.append(f"[{k}:v]setpts=PTS-STARTPTS+{s}/TB,format=rgba,fade=t=in:st={s}:d=0.25:alpha=1,"
                     f"fade=t=out:st={e - 0.2:.3f}:d=0.2:alpha=1[o{n}]")
        x, y = o["_x"], o["_y"]
        ymove = f"{y}+max(0\\,1-(t-{s})/0.3)*60"  # slide up into place
        chain.append(f"{cur}[o{n}]overlay=x={x}:y='{ymove}':enable='between(t,{s},{e})':eof_action=pass[c{n}]")
        cur = f"[c{n}]"
        if o["type"] == "pip":
            hx, hy, hw, hh = o["_hole"]
            chain.append(f"{cur}[pv{n}]overlay=x={x + hx}:y='{ymove}+{hy}':enable='between(t,{s},{e})'"
                         f":eof_action=pass[cp{n}]")
            cur = f"[cp{n}]"
        if behind and o is behind[-1]:
            # person back on top of the behind-titles
            mask = person_mask(joined, workdir, W, H, fps)
            km = add_input(["-i", mask])
            on = "+".join(f"between(t,{b['start']},{b['end']})" for b in behind)
            chain.append(f"[{km}:v]format=gray[mk];{person_src}format=rgba[pp];[pp][mk]alphamerge[cut]")
            chain.append(f"{cur}[cut]overlay=0:0:enable='{on}'[pb]")
            cur = "[pb]"
    chain.append(f"{cur}format=yuv420p[fx]")
    return inputs, ";".join(chain)
