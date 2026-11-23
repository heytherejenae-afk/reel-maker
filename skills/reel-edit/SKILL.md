---
name: reel-edit
description: Stage 6 of the reel creator - make the first edit of the reel from the person's script, Google Drive clips (talking head + b-roll) and overlay pages - one-word captions with key words in a second font, title behind the head, overlays, cuts by script beat - then an editor page for changes. Use when someone sends a Drive folder of clips to edit, or pastes a REEL CHANGES block.
---

# Stage 6: The first edit

The engine is this folder: `scripts/`, `fonts/`, `models/`, `assets/`.
`reference.md` holds every option of the older all-in-one reel skill (looks,
font pairs, colour themes, stickers, music, privacy blur, carousel/story extras):
read the part you need when the person asks for something not covered here.

Setup, once per session: `pip install faster-whisper gdown ai-edge-litert opencv-python-headless`
(or `bash setup.sh` at the plugin root). ffmpeg, Node and Playwright Chromium are usually pre-installed.

## Script mode (the standard route)

Inputs: `script.json` (stage 3), overlay PNGs (stage 5), `brand-kit.json` (stage 4),
and a Google Drive folder with one talking-head clip (them saying the script) plus
b-roll clips (no talking).

1. **Get the clips:** `python3 scripts/fetch_drive.py "<drive link>" work/<slug>/clips`.
   If it fails: "Open the folder in the Google Drive app, tap the three dots next to
   it, tap **Share**, tap **Restricted** and change it to **Anyone with the link**,
   tap **Copy link**, and send me the link again." Videos with no sound are b-roll.
2. **Write `reel.json`** (schema at the top of `scripts/script_reel.py`;
   `example-reel.json` is the approved apple reel). From the brand kit: `brand.text`
   white, `brand.key` = `highlight`, `brand.card` = `light`, `brand.card_label` =
   `primary`; fonts: `word` Inter Display SemiBold (or their caption font), `key` =
   their key-word font. `key_words`: 1-2 per sentence from the script. Add
   `"screens": ["pink", "green"]` if they want the Edits hand-off.
3. `python3 scripts/script_reel.py transcribe reel.json`, then
   `python3 scripts/script_reel.py sheets reel.json` and **look at every contact sheet**.
   Map each script beat to the talking-head seconds that say it (`say`; trim pauses
   and retakes, use the last good take). Pick b-roll that shows exactly what that
   beat says (the script's shot list). Long process footage: speed 1.5-2x.
   **Never use the same b-roll moment twice.** Show the talking head for the first
   1-2 s of each beat.
4. Overlay page N goes on beat N. Overlays sit in front, below the face
   (`overlay_place` y 0.735, scale 0.85); a page with no box of its own gets
   `"backing"`. Title behind the head only where there's clear sky above the head.
5. `python3 scripts/script_reel.py build reel.json` (about 6 min for 70 s). Check a
   contact sheet of the result (`ffmpeg -i reel.mp4 -vf fps=1/1.5,scale=270:-2,tile=6x4 sheet.jpg`):
   words readable, overlays not over the face, the right b-roll for each beat.
6. `python3 scripts/script_reel.py editor reel.json` and publish `out/editor.html`
   with the Artifact tool (same file each round keeps the same link). Send the reel
   MP4 and the editor link with:
   > 1. Tap the reel to watch it.
   > 2. Want changes? Tap the editor link. Change words, swap shots or move overlays.
   > 3. Tap **Copy my changes**, come back here, press and hold in the message box,
   >    tap **Paste**, then send. Happy? Reply **done**.
   Flag any caption word that looks misheard.
7. They paste `REEL CHANGES`: save it to a file, `script_reel.py apply reel.json FILE`,
   build again, republish the editor. Their "note" field is free text: act on it.

When they say done, go to `reel-handoff`.

## No script? (clips + a one-line brief)

Use the brief-to-reel route in `reference.md` (steps 1-5): setup questions, rough
cut, storyboard, render, coaching report.
