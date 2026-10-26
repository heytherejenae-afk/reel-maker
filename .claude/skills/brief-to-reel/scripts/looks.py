"""Editing styles and colour themes: everything that sets the *feel* of a reel.

A plan picks a look with:
  "look": {"style": "editorial",          # clean | editorial | lofi | creator | bold
           "theme": "forest",             # optional colour theme (THEMES below)
           "colors": {"primary": "#1F4D3A"},  # optional single-colour overrides
           "font": "Lilita One",          # optional caption font (render.FONTS name or .ttf path)
           "caption_box": true,           # optional: any STYLES key can be overridden
           "caption_mode": "karaoke"}     # words (default) | karaoke | punch
Older plans with "style": {"font", "highlight_color"} still work.

Brand kit: "look": {"brand": "/path/brand-kit.json", ...} loads a saved look (same keys,
plus "handle" and "avatar" for the Follow card and DM reply). Anything set in the plan
wins over the brand kit. Save one with save_brand() / brand.py.
Lookbook: a brand kit can hold several named looks ("looks": {"Butter": {...}, ...},
"default": "Butter"); pick one with "look": {"brand": ..., "lookbook": "Playful"}.
"""
import json
import os

# Colour roles: primary = boxes, 3D title depth, buttons; light = text on primary and
# title faces; highlight = key words in captions.
THEMES = {
    "forest":   {"primary": "#1F4D3A", "light": "#F4EDE1", "highlight": "#A9C9A4"},
    "sunshine": {"primary": "#111111", "light": "#FFFFFF", "highlight": "#FFD60A"},
    "ocean":    {"primary": "#0B3C5D", "light": "#F2F7FA", "highlight": "#7FD1F5"},
    "blush":    {"primary": "#8E3B5B", "light": "#FFF1F3", "highlight": "#FFB3C6"},
    "terracotta": {"primary": "#9C4A2F", "light": "#FBF1E6", "highlight": "#F4B183"},
    "mono":     {"primary": "#000000", "light": "#FFFFFF", "highlight": "#BDBDBD"},
    "pop":      {"primary": "#E63946", "light": "#FFFFFF", "highlight": "#FFD60A"},
    "vintage":  {"primary": "#3B2F2F", "light": "#FFF6E9", "highlight": "#FFB4A2"},
    "butter":   {"primary": "#B3261E", "light": "#FFFFFF", "highlight": "#F6E27A"},
}

STYLES = {
    # Simple and readable: white captions, yellow key words, nothing fancy.
    "clean": {
        "label": "Clean", "theme": "sunshine", "font": None,
        "caption_box": False, "caption_case": "upper", "caption_words": 3, "caption_mode": "words",
        "display_font": "Archivo Black", "title_3d": False,
        "grade": "", "punch_in": False,
    },
    # Polished creator look: serif boxed captions, big 3D serif titles, UI overlays.
    "editorial": {
        "label": "Editorial (Hi-fi)", "theme": "forest", "font": "Instrument Serif",
        "caption_box": True, "caption_case": "sentence", "caption_words": 4,
        "display_font": "DM Serif Display", "title_3d": True,
        "grade": "eq=contrast=1.05:saturation=0.92", "punch_in": False,
    },
    # Raw and warm: handwritten lower-case captions, film grain, vintage colour.
    "lofi": {
        "label": "Lo-fi", "theme": "vintage", "font": "Permanent Marker",
        "caption_box": False, "caption_case": "lower", "caption_words": 3,
        "display_font": "Permanent Marker", "title_3d": False,
        "grade": "curves=preset=vintage,noise=alls=10:allf=t,vignette=PI/5", "punch_in": False,
    },
    # Talking-head creator look: big one-or-two-word captions, key words in a yellow
    # italic serif, hand-written headlines.
    "creator": {
        "label": "Creator", "theme": "butter", "font": "Poppins",
        "caption_box": False, "caption_case": "sentence", "caption_words": 2, "caption_mode": "punch",
        "display_font": "Instrument Serif", "title_3d": False, "script_font": "Caveat Brush",
        "grade": "eq=saturation=1.05", "punch_in": False,
    },
    # High energy: chunky captions, bright colours, punch-in zooms on alternate shots.
    "bold": {
        "label": "Bold", "theme": "pop", "font": "Luckiest Guy",
        "caption_box": False, "caption_case": "upper", "caption_words": 2,
        "display_font": "Luckiest Guy", "title_3d": True,
        "grade": "eq=contrast=1.1:saturation=1.25", "punch_in": True,
    },
}


def resolve(plan):
    """Merge the chosen style, theme and overrides into one flat look dict."""
    req = dict(plan.get("look") or {})
    if req.get("brand") and os.path.exists(req["brand"]):
        kit = json.load(open(req["brand"]))
        book = kit.pop("looks", {})
        name = req.get("lookbook") or kit.pop("default", None)
        if name in book:  # a saved look from the lookbook sits on top of the kit basics
            kit = {**kit, **book[name], "colors": {**kit.get("colors", {}), **book[name].get("colors", {})}}
        kit_colors = kit.get("colors", {})
        req = {**kit, **req, "colors": {**kit_colors, **(req.get("colors") or {})}}
    old = plan.get("style") or {}  # backwards compatible keys
    if old.get("font") and "font" not in req:
        req["font"] = old["font"]
    look = dict(STYLES.get(req.get("style", "clean"), STYLES["clean"]))
    look["style"] = req.get("style", "clean") if req.get("style") in STYLES else "clean"
    for k, v in req.items():
        if (k in look or k in ("handle", "avatar", "script_font", "caption_mode")) and k != "style":
            look[k] = v
    colors = dict(THEMES.get(req.get("theme") or look["theme"], THEMES["sunshine"]))
    if old.get("highlight_color"):
        colors["highlight"] = old["highlight_color"]
    colors.update(req.get("colors") or {})
    look["colors"] = colors
    return look


def save_brand(path, look_request, name=None, extra=None):
    """Write or update a brand kit. With a name, the look is added to the lookbook
    (and becomes the default if it's the first); without one it's the kit's main look."""
    kit = json.load(open(path)) if os.path.exists(path) else {}
    look = {k: v for k, v in look_request.items() if k not in ("brand", "lookbook")}
    if name:
        kit.setdefault("looks", {})[name] = {k: v for k, v in look.items() if k not in ("handle", "avatar")}
        kit.setdefault("default", name)
        for k in ("handle", "avatar"):
            if look.get(k):
                kit[k] = look[k]
    else:
        kit.update(look)
    kit.update(extra or {})
    with open(path, "w") as f:
        json.dump(kit, f, indent=1)
    return path
