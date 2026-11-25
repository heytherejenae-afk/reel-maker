"""Read the editing style of sample reels, so new reels can match it.

    python3 -I skills/reel-edit/scripts/style_sample.py OUT_DIR SOURCE [SOURCE ...]

SOURCE is a video file, or an Instagram / TikTok / YouTube Shorts link (downloaded
with yt-dlp, no login; installed with pip on first use).

Writes to OUT_DIR:
  style_measure.json   numbers per sample + averages (cuts, shot length, length, colours)
  sheet_<n>.jpg        a contact sheet per sample: a frame every ~1.5 s with the time on it
Prints LINK_BLOCKED / DOWNLOAD_FAILED lines for links it couldn't fetch.

What it can't measure (caption font feel, words per screen, caption position and case,
zooms, B roll, hook style), you read from the contact sheets by eye.
"""
import json, os, re, subprocess, sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def ensure_ytdlp():
    try:
        import yt_dlp  # noqa: F401
        return True
    except ImportError:
        r = run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"])
        if r.returncode != 0:
            return False
        import site, importlib
        importlib.invalidate_caches()
        for p in site.getsitepackages() + [site.getusersitepackages()]:
            if p not in sys.path:
                sys.path.append(p)
        try:
            import yt_dlp  # noqa: F401
            return True
        except ImportError:
            return False


def download(url, out_dir, n):
    if not ensure_ytdlp():
        print(f"DOWNLOAD_FAILED {url} (could not install yt-dlp)")
        return None
    import yt_dlp
    tmpl = os.path.join(out_dir, f"sample_{n}.%(ext)s")
    opts = {"outtmpl": tmpl, "format": "mp4/best", "quiet": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=True)
            return y.prepare_filename(info)
    except Exception as e:  # network blocks show up here
        msg = str(e)
        if re.search(r"403|429|Too Many|Forbidden|login|Tunnel|proxy|resolve|Connection", msg, re.I):
            print(f"LINK_BLOCKED {url}")
        else:
            print(f"DOWNLOAD_FAILED {url} ({msg[:160]})")
        return None


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def cuts(path, thresh=0.1):
    # 0.1 catches talking head jump cuts and punch ins (tested: 0.3 missed all of them)
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-an", "-vf",
             f"scale=320:-2,select='gt(scene,{thresh})',showinfo", "-f", "null", "-"])
    out = []
    for t in (float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)):
        if not out or t - out[-1] > 0.4:  # one cut, not a flicker of several frames
            out.append(t)
    return out


def sheet(path, dur, out):
    step = max(1.0, dur / 24.0)
    vf = (f"fps=1/{step:.3f},scale=270:-2,"
          "drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,"
          "tile=6x4:padding=4")
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", path, "-an", "-vf", vf, "-frames:v", "1", out])
    if r.returncode != 0:  # drawtext needs a font; fall back without the time stamp
        vf = f"fps=1/{step:.3f},scale=270:-2,tile=6x4:padding=4"
        run(["ffmpeg", "-hide_banner", "-y", "-i", path, "-an", "-vf", vf, "-frames:v", "1", out])
    return round(step, 2)


def palette(path, dur, k=6):
    try:
        from PIL import Image
    except ImportError:
        return []
    tmp = path + ".pal.png"
    run(["ffmpeg", "-hide_banner", "-y", "-i", path, "-an", "-vf",
         f"fps=1/{max(1.0, dur / 12):.3f},scale=96:-2,tile=12x1", "-frames:v", "1", tmp])
    if not os.path.exists(tmp):
        return []
    im = Image.open(tmp).convert("RGB").quantize(colors=k)
    pal = im.getpalette()[: k * 3]
    counts = sorted(im.getcolors(), reverse=True)
    os.remove(tmp)
    out = []
    for c, idx in counts:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        out.append({"hex": f"#{r:02X}{g:02X}{b:02X}", "share": round(c / (im.width * im.height), 2)})
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out_dir, sources = sys.argv[1], sys.argv[2:]
    os.makedirs(out_dir, exist_ok=True)
    samples = []
    for n, src in enumerate(sources, 1):
        path = download(src, out_dir, n) if re.match(r"https?://", src) else src
        if not path or not os.path.exists(path):
            continue
        d = duration(path)
        c = cuts(path)
        shots = len(c) + 1
        sh = os.path.join(out_dir, f"sheet_{n}.jpg")
        step = sheet(path, d, sh)
        samples.append({
            "sample": n, "source": src, "file": path, "length_s": round(d, 1),
            "cuts": len(c), "avg_shot_s": round(d / shots, 2) if d else None,
            "cuts_per_10s": round(len(c) / d * 10, 1) if d else None,
            "first_cut_s": round(c[0], 2) if c else None,
            "colours": palette(path, d), "sheet": sh, "sheet_every_s": step,
        })
        print(f"SAMPLE {n}: {d:.1f}s, {len(c)} cuts, avg shot {samples[-1]['avg_shot_s']}s, sheet {sh}")
    ok = [s for s in samples if s["avg_shot_s"]]
    avg = {}
    if ok:
        avg = {"length_s": round(sum(s["length_s"] for s in ok) / len(ok), 1),
               "avg_shot_s": round(sum(s["avg_shot_s"] for s in ok) / len(ok), 2),
               "cuts_per_10s": round(sum(s["cuts_per_10s"] for s in ok) / len(ok), 1)}
    json.dump({"samples": samples, "average": avg}, open(os.path.join(out_dir, "style_measure.json"), "w"), indent=1)
    print("AVERAGE", json.dumps(avg))
    if not samples:
        print("NO_SAMPLES")


if __name__ == "__main__":
    main()
