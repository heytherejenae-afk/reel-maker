"""Sound effects and the music library.

Sound effects are synthesised (no downloads, no licences): pop, whoosh, ding, click.
  plan "sfx": true            -> automatic: whoosh on titles, pop on badges/cards/stickers,
                                 clicks while a comment types, ding on the DM reply
  plan "sfx_events": [{"t": 3.2, "sound": "ding", "volume": 0.6}]   extra hand-placed sounds

Music library: Kevin MacLeod tracks from incompetech.com, licensed CC BY 4.0. They are
free to use in reels as long as the caption credits them (credit() gives the line).
  plan "music": {"track": "Carefree"}  (or "path" for the person's own file)
"""
import os
import subprocess
import urllib.parse
import wave

import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(HERE, "..", "assets", "music")
BASE = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"

LIBRARY = {  # name: mood
    "Wallpaper": "chill lo-fi",
    "Airport Lounge": "chill lounge",
    "Lobby Time": "chill jazzy",
    "Bossa Antigua": "chill bossa nova",
    "Carefree": "happy upbeat",
    "Life of Riley": "happy playful",
    "Happy Alley": "happy acoustic",
    "Monkeys Spinning Monkeys": "funny bouncy",
    "Fluffing a Duck": "funny quirky",
    "Inspired": "inspiring warm",
    "Easy Lemon": "inspiring gentle",
    "Hyperfun": "energetic",
    "Funky Chunk": "energetic funky",
    "Daily Beetle": "energetic pop",
    "Jingle Bells": "christmas",
}


def track_path(name):
    """Download a library track once and return its local path."""
    os.makedirs(MUSIC_DIR, exist_ok=True)
    dest = os.path.join(MUSIC_DIR, name.replace(" ", "_") + ".mp3")
    if not os.path.exists(dest):
        subprocess.run(["curl", "-sSfL", "-m", "120", "-o", dest, BASE + urllib.parse.quote(name) + ".mp3"],
                       check=True)
    return os.path.abspath(dest)


def credit(name):
    return f'Music: "{name}" by Kevin MacLeod (incompetech.com), licensed CC BY 4.0'


# --- synthesised sound effects ---

def _env(n, attack=0.005, decay=0.08):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)


def sound(name):
    if name == "pop":
        n = int(0.09 * SR)
        t = np.arange(n) / SR
        f = 900 * np.exp(-t * 30) + 180  # quick downward sweep
        return 0.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.03)
    if name == "whoosh":
        n = int(0.45 * SR)
        noise = np.random.default_rng(1).standard_normal(n)
        k = np.linspace(0.02, 0.25, n)  # sweeping one-pole low-pass
        out, y = np.zeros(n), 0.0
        for i in range(n):
            y += k[i] * (noise[i] - y)
            out[i] = y
        shape = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
        return 1.6 * out * shape
    if name == "ding":
        n = int(0.7 * SR)
        t = np.arange(n) / SR
        tone = np.sin(2 * np.pi * 1318.5 * t) + 0.6 * np.sin(2 * np.pi * 1760 * t) + 0.2 * np.sin(2 * np.pi * 2637 * t)
        return 0.35 * tone * _env(n, 0.002, 0.22)
    if name == "click":
        n = int(0.025 * SR)
        noise = np.random.default_rng(2).standard_normal(n)
        return 0.35 * noise * _env(n, 0.0005, 0.006)
    raise ValueError(f"unknown sound {name!r}")


def auto_events(overlays):
    ev = []
    for o in overlays:
        s, kind = float(o["start"]), o["type"]
        if kind in ("title", "headline", "fan", "styles", "pip"):
            ev.append({"t": s, "sound": "whoosh", "volume": 0.5})
        elif kind in ("badge", "card", "sticker", "follow"):
            ev.append({"t": s + 0.05, "sound": "pop", "volume": 0.7})
        elif kind == "comment_box":
            n = len(o.get("text", ""))
            step = min(0.15, (float(o["end"]) - s) * 0.6 / max(1, n))
            ev += [{"t": s + step * (i + 1), "sound": "click", "volume": 0.6} for i in range(n)]
        elif kind == "dm_reply":
            ev.append({"t": s + 0.15, "sound": "ding", "volume": 0.6})
        elif kind == "comments":
            n = int(o.get("count", 8))
            ev += [{"t": s + 0.15 * i, "sound": "pop", "volume": 0.35} for i in range(n)]
    return ev


def sfx_track(events, total, out):
    """Write a stereo WAV of all sound effects for the whole reel."""
    buf = np.zeros(int(total * SR) + SR)
    for e in events:
        x = sound(e["sound"]) * float(e.get("volume", 0.7))
        i = int(float(e["t"]) * SR)
        if 0 <= i < len(buf):
            j = min(len(buf), i + len(x))
            buf[i:j] += x[: j - i]
    buf = np.clip(buf[: int(total * SR)], -1, 1)
    pcm = (np.repeat(buf[:, None], 2, axis=1) * 32767 * 0.9).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out
