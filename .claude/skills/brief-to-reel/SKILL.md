---
name: brief-to-reel
description: Turn raw video clips and a short brief into a finished vertical reel (9:16, captions, styled titles and overlays, music) plus a coaching report, a carousel, a story and trial reels. Use when someone shares clips (Google Drive link or uploads) and wants a Reel, TikTok or Short made from them.
---

# Brief to reel

The person is probably a beginner. Never ask them about codecs, frame rates or
settings. Ask at most for (1) their clips, (2) one or two sentences about what
the reel is for, and (3) once, how they want it to look (or "you choose").
Everything else you decide.

Scripts live in `scripts/` next to this file. Setup, once per session:
`pip install faster-whisper gdown ai-edge-litert opencv-python-headless`.
`ffmpeg`, Node and Playwright Chromium are pre-installed. Small model files
(person cut-out, face detector and matcher), Google Fonts and music-library tracks
download on first use from storage.googleapis.com, huggingface.co,
raw.githubusercontent.com and incompetech.com.

## 1. Get the clips

- **Google Drive link (preferred):** `python3 scripts/fetch_drive.py "<link>" work/clips`.
  If it fails, tell them in plain words: "Open the folder in Drive, tap Share,
  set General access to *Anyone with the link*, and send me the link again."
- **Uploaded in chat:** copy them into `work/clips`.
- **Adobe Creative Cloud Files:** find them with the Adobe connector
  `asset_search` (entityScope CCAsset). Clips inside an Adobe *Express* project
  are not reachable; ask for Drive instead.

If there is no brief, ask once: "What's this reel for, and who's watching? One
sentence is plenty." If they don't answer, assume a fun, upbeat 20-second reel
for Instagram.

**Brand kit:** if `work/clips/brand-kit.json` exists, they've saved their look
before. Use it (`"look": {"brand": "work/clips/brand-kit.json"}`) and skip step 1b.
If the kit has several looks (a lookbook), use its default unless they name one
(`"lookbook": "Playful"`).

**Autopilot:** if the brand kit has `"autopilot": true`, don't ask anything and
skip the storyboard: rough cut, plan in their default look, render, and deliver the
reel with the coaching report. Only ask if there's no brief and the clips don't make
the topic obvious.

## 1b. Customise the look (one message, while analysis runs)

Make the picker sheets from a frame where the person is in shot:

```
python3 scripts/look_samples.py work/clips/<clip> work/looks --time <t> --title <a key word from the brief>
python3 scripts/font_samples.py work/clips/<clip> work/fonts.jpg --time <t>
```

Send `styles.jpg`, `colours.png` and `fonts.jpg` in one message:
"Pick a style (1–4), a colour (1–8, or tell me your brand colour) and a caption
font by number, or just say 'you choose'." Carry on while you wait. If they
don't answer, pick the style that fits the brief (Clean for simple tips,
Editorial for polished creator content, Lo-fi for cosy or behind-the-scenes,
Bold for high energy) and keep its default colours and font.

| Style | Feel | What it sets |
|---|---|---|
| Clean | Simple, readable | White captions with yellow key words, flat titles |
| Editorial (Hi-fi) | Polished creator look | Serif captions in a coloured box, big 3D serif titles, slight grade |
| Lo-fi | Raw, warm, cosy | Hand-written lower-case captions, film grain, vintage colour |
| Creator | Talking-head creator look | One or two big words at a time, key words in a yellow italic serif, hand-written headlines |
| Bold | High energy | Chunky captions, bright 3D titles, punch-in zoom on every other shot |

Caption modes (any style): `"caption_mode": "words"` (default, a few words at a
time), `"karaoke"` (a highlight box jumps from word to word as it's said) or
`"punch"` (one or two big words, key words in italic serif).

**3 versions, pick your favourite:** when they can't decide, or the brief is open,
render three short openings in different looks or hooks and let them choose:
`python3 scripts/versions.py work/plan.json work/versions --analysis work/analysis/analysis.json --looks creator,editorial,bold --hooks "..." "..." "..."`
Send `versions.mp4` (all three side by side, numbered) and ask "1, 2 or 3?".

In the plan: `"look": {"style": "editorial", "theme": "ocean", "font": "Poppins"}`.
Single colours can be overridden with `"colors": {"primary": "#...", "light": "#...",
"highlight": "#..."}` (primary = boxes and title depth, light = text on boxes and
title faces, highlight = key words). Any style key in `scripts/looks.py` can be
overridden too (for example `"caption_box": true`).

**Their own fonts (free or bought):** any `.ttf` or `.otf` file in their Drive
folder downloads with the clips. Add it with `--custom work/clips/<font file>`
so it appears on the font sheet, and set `look.font` to the file's path if
chosen. Remind them to check the font licence covers social media video. Adobe
Fonts can't be used this way, because Adobe doesn't let you download the font files.

**Save it for next time:** after they're happy with a reel, offer to save their
look: `python3 scripts/brand.py work/plan.json work/brand-kit.json --name <a name they like, e.g. Butter> --handle <their handle>`.
Each saved name becomes a look in their **lookbook**; run it again with another
name to add more (`--default` picks the one used automatically). Then offer
autopilot ("Want me to edit your next reels in this style without asking
questions?"); if yes, add `--autopilot on`. Put `brand-kit.json` in their Drive
clips folder (Google Drive connector `create_file` if available, otherwise give
them the file to add), so every future reel matches automatically.

## 2. Analyse and rough cut

```
python3 scripts/analyze.py work/clips work/analysis
python3 scripts/roughcut.py work/analysis/analysis.json work/roughcut.json
```

`analysis.json` holds per-clip metadata, a 0–1 score for every second, the best
3-second windows, problem flags (`too_dark`, `blurry`, `hard_cut_or_shake`) and a
word-timed transcript. One contact sheet per clip goes in `work/analysis/sheets/`.
**Look at every contact sheet**, because the scores only measure technical
quality. You judge what is actually interesting: faces, reactions, reveals, the
product, the "money shot".

`roughcut.py` removes ums, pauses longer than 0.45 s and earlier takes of a line
that gets repeated (the last take wins). It writes plan-ready segments of the
clean talk plus a numbered transcript (`roughcut.md`). For talking videos, build
the plan from these segments and pick the best lines; don't hand-trim pauses.

**Cut by word:** if the person wants a word or phrase gone ("cut 'basically'",
"drop the bit where I say 'you know'"), add it to `"cut_words"` (everywhere) or a
segment's `"cut"` list. `render.py` splits the segment around it.

Before rendering, fix words Whisper mishears (brand names, local slang such as
"Woolies") directly in `analysis.json`. If transcription fails, carry on and use
`captions_manual` for on-screen text.

## 3. Plan the edit, built for reach

Write `work/plan.json` (format at the top of `scripts/render.py`; overlays are
documented at the top of `scripts/graphics.py`). Follow this playbook unless the
brief says otherwise:

| Rule | Why |
|---|---|
| 15–30 s total (7–12 s for a simple show-off); follow the person's length if they give one | Completion rate drives reach |
| **Hook in the first 1 s**: open on the most striking moment, plus a hook title that creates curiosity ("Watch what happens when…", "POV: …", "3 things nobody tells you about…") | Most viewers decide in the first second |
| Cuts every 1–2 s; nothing static longer than 3 s unless someone is talking | Keeps attention |
| Re-hook in the middle (a new angle, a reveal, a big title, a speed change); mark that segment `"rehook": true` | Stops the mid-video drop-off |
| Captions on whenever someone speaks, with 1–2 key words per sentence in `highlight_words` (numbers are automatic) | Most people watch on mute |
| Payoff near the end, then a call to action ("Comment X", "Follow for part 2", "Save this") | Comments, saves and follows boost reach |
| Make the last shot flow back into the first | Loops count as rewatches |
| Upright clips use `fill`; landscape clips use `fit-blur`, or `fill` with `focus_x` | No black bars |
| Skip seconds flagged `too_dark`, `blurry` or `hard_cut_or_shake` unless it's the only shot of something important | Quality signals |
| Use `speed` 1.1 for talking, 1.25–2 for slow process shots | Pace |

**Overlays** (`"overlays": [...]`, reel times in seconds). Use them to make the
key moments land, roughly one every 4–8 seconds, never two at once, kept in the
top half so captions stay clear:

| Moment | Overlay |
|---|---|
| Hook, list items, the twist | `title` (big keyword; 3D in Editorial and Bold; `"behind": true` tucks it behind the person) or `headline` (bold plus hand-written lines) |
| Numbers, quick facts | `badge` ("#1 Zucchini · 50 days") |
| A do/don't or tip | `card` (title plus lines, emoji fine) |
| A reaction or emphasis | `sticker` (an emoji that pops in with burst lines, or their own GIF/PNG from the Drive folder). Place it with `"side": "left"`, `"centre"` or `"right"` (default right); mixing sides keeps it lively. Keep a centre sticker clear of any title or headline on screen at the same time, and off the face |
| "Comment X" call to action | `comment_box` (types the word), then `dm_reply` ("Sending it over!"), or `comments` (a stack of comments pouring in) |
| "Follow for more" | `follow` (Follow card that taps to Following) |
| Showing another clip, before/after | `pip` (video in a titled card) |
| "I filmed for hours", process | `fan` (fanned thumbnails with timestamps) |
| Comparing options or looks | `styles` (up to 3 labelled cards) |

With overlays, drop the plain `hook` and `end_text` and use a `title` and a
call-to-action overlay instead.

**Privacy:** if kids or bystanders appear and the person wants them hidden, set
`"blur_faces": "others"` (keeps the biggest face, usually the speaker) or `"all"`.
To blur only certain people, make the face sheet first
(`python3 scripts/privacy.py work/clips/<clip> work/faces`), send `faces.jpg`
("Which faces should I cover? Face 1, Face 2...") and set
`"blur_faces": {"faces": [2], "sheet": "work/faces/faces.json"}`. Ask once if you
see children in the contact sheets.

**Sound:** set `"sfx": true` for pops, whooshes, typing clicks and a ding synced to
the overlays (made on the fly, no licence needed). For music, use their own track
(`"path"`), or pick from the library in `scripts/audio.py`
(`"music": {"track": "Carefree", "volume": 0.12}`; moods: chill, happy, funny,
inspiring, energetic, Christmas). Library tracks are Kevin MacLeod, CC BY 4.0: put
the credit line `render.py` prints into the posting tips so they add it to the
caption. Loudness is always levelled to -14 LUFS (the social media standard).

Don't license paid Adobe Stock music without asking, because it costs money.
Without music, keep the original sound. If music is used, keep `duck: true` so
speech stays clear and the volume low (0.1–0.15) under talking. Tell them that on
Instagram or TikTok they can swap in a trending sound in the app before posting,
which often helps reach.

### Storyboard first (standard)

Always show a storyboard **before** rendering, so they can see and change the
plan. Make it as a Claude Doc when the Docs connector is available (otherwise a
short Markdown file plus a contact image):

1. One picture per shot: `ffmpeg -ss <start+1> -i <clip> -frames:v 1 -vf scale=216:384 shotNN.jpg`,
   uploaded to the doc and placed in the table.
2. A **Shot list** table: #, picture, time in the reel, what's said (key words
   in bold), text and overlays on screen, and why the shot is there, in plain words.
3. A **Look** table: style, colours, caption font, highlight words, music,
   face blur, length.
4. **How to change it**: edit cells, delete or move rows, write "cut <word>", or
   comment on a row, then say "build it".

Ask them to look it over and say "build it" (or make edits first). Then re-read
the doc, update `plan.json` to match, and render. If they asked you to go ahead
without checking, skip the wait.

## 4. Render and check

`python3 scripts/render.py work/plan.json --analysis work/analysis/analysis.json`

Then pull 4–6 frames (`ffmpeg -ss <t> -i reel.mp4 -frames:v 1 f.png`), including
one during each overlay, and look at them: is the text readable, is the subject
in frame, do overlays and captions stay clear of each other and of the face? Fix
the plan and re-render if not.

## 5. Deliver

Give them the MP4, and with it a **coaching report** in friendly, plain language:

1. **What's working:** 2–3 specific things ("The close-up of the pour at 0:04 is a great hook").
2. **What held this reel back:** the top 2–3 issues you saw in the flags and
   contact sheets, each with a one-line fix (dark → "face a window or film
   before sunset"; shaky → "hold the phone with both hands, elbows tucked in,
   or lean on something"; horizontal → "turn your phone upright"; far away →
   "step closer, fill the frame with the subject"; long static shots → "move the
   camera slowly, or change angle every few seconds").
3. **Shots to get next time:** a numbered list of 4–6 concrete shots tailored to
   the brief and missing from this footage, for example a tight close-up
   opener, a reaction face, a before/after, a POV shot, a 3-second
   "reveal", or a shot of the person talking straight to camera for the hook.
4. **Posting tips:** best caption idea, 3–5 hashtags, the cover frame to choose,
   and a reminder to add a trending sound in the app.

Keep the report short enough to read on a phone.

## 6. Repurpose (offer after delivery)

Offer: "Want a carousel, a story and 3 trial reels from this too?" If yes, add
`"cta"`, three `"trial_hooks"` (different angles on the same idea) and,
optionally, `"points"` (one carousel slide each) to the plan, then:

`python3 scripts/repurpose.py work/plan.json reel.mp4 work/repurposed --analysis work/analysis/analysis.json`

This makes `carousel/slide_NN.png` (4:5 slides: hook, one per point, call to
action), `story.mp4` (first 12 s with a "New reel" sticker) and three trial reels:
`trial-new-hook` (same edit, new hook), `trial-short` (about 20 s) and
`trial-twist-first` (the re-hook moment moved to the start). Explain that
Instagram's trial reels are shown to non-followers first, so they can test which
hook works best before sharing to their main feed.
