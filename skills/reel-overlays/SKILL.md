---
name: reel-overlays
description: Stage 5 of the reel creator - make one on-screen overlay page per script beat (price tags, taped notes, numbered cards, pills, sticker cards, banners) in Canva or with the built-in styles, exported as transparent 1080x1920 PNGs. Use when someone wants reel overlays, text cards or Canva graphics for a script.
---

# Stage 5: Overlays

One overlay page per script beat, using that beat's `on_screen` lines from
`script.json`. Pages are 1080x1920 with a see-through background; the edit places
them below the face, in front of the video.

## 1. Pick a style

Send `overlay-styles.jpg` (in this folder; remake it in their brand with
`python3 overlay_pages.py --sheet work/<slug>/styles.jpg --brand work/brand-kit.json`)
and ask: "Which overlay style? 1 Price tag · 2 Taped note · 3 Numbered card ·
4 Clean pills · 5 Sticker card · 6 Bold banner · or **mix** (I'll pick per beat)".

Good defaults per beat when mixing: hook with a price or number → Price tag; tips →
Numbered card (1, 2, 3); a warning or "the hard part" → Taped note with the title
crossed out (`"strike": true`); a list of names → Clean pills; the CTA → Bold banner.

Then ask: "Make them in **Canva** (you can change them in the Canva app) or
**built-in** (fastest, no Canva needed)?" Default: Canva if the Canva connector is
connected, else built-in.

## 2a. Built-in

Write `work/<slug>/overlays.json` (format at the top of `overlay_pages.py`): one page
per beat in script order, `title` = first on-screen line, `lines` = the rest,
`number` for tips, `emoji` for sticker cards. Then
```
python3 overlay_pages.py work/<slug>/overlays.json work/<slug>/ov --brand work/brand-kit.json
```
Look at every PNG before sending (text fits, nothing cut off).

## 2b. Canva

1. Make one design with one page per beat. Use `create-design` if the Canva
   connector offers it, otherwise `generate-design` with `design_type: "your_story"`
   (1080x1920). In the query give: every page's exact words in order, the chosen
   style described in words (e.g. "a cream price tag with a hole and string, tilted
   slightly, forest-green serif text"), the brand colours as hex codes, "transparent
   background, graphic sits in the lower-middle third, nothing near the top or the
   edges", and "no photos, no faces". If they have a Canva Brand Kit, ask whether to
   use it (`list-brand-kits`).
2. Show the candidates; they pick one (`create-design-from-candidate`).
3. Export with `export-design`: `type: "png"`, `transparent_background: true`,
   `width: 1080`, `height: 1920`, all pages. Download to `work/<slug>/ov/p1.png ...`.
4. Look at every page. If the words don't match the script exactly, fix them with
   `edit-design` (or tell them which page to fix in Canva) before going on.
5. Canva's connector can't set fonts. Tell them: "To use your brand fonts, open the
   design in the Canva app, tap a text box, tap the font name at the bottom, and pick
   your font. Then tell me **done** and I'll export again."
6. A canva.com/d/ link that won't open through the connector: find the design with `search-designs`.

Save the design link and the PNG paths to `reel-project.json` (`overlays`), and add
`canva_link` + `overlay_tip` to `script.json` and republish the script page.

Then: "Overlays done. When your clips are in a Google Drive folder, send me the
link and I'll make the first edit." Go to `reel-edit`.
