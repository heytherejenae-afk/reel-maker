---
name: reel-script
description: Stage 3 of the reel creator - write the reel script (timed beats of what to say and what shows on screen, shot list, caption) and publish it as the person's editable script page. Use when someone has an idea and needs a script, or pastes a SCRIPT CHANGES block.
---

# Stage 3: The script page

## 1. Write `script.json`

Read `reel-project.json`: the idea, the outlier breakdowns, the brand kit (`about`,
`principles`, handle). Write `work/<slug>/script.json` (format at the top of
`script_page.py` in this folder; `example-script.json` is a full example).

Rules:
- **Length:** 30-50 s unless they asked otherwise. About 2.5 spoken words a second
  (45 s ≈ 110-140 words). Put the total in `glance`.
- **Hook beat first** (`"kind": "hook"`, 0-3 s): a curiosity gap, number or strong
  claim, built on a hook pattern from the research. On-screen text repeats the hook
  in fewer words.
- 5-8 beats. Each beat: `name`, `time`, `say` (their words, in their voice, short
  sentences), `on_screen` (1-2 short lines; these become the overlay pages in stage 5).
- `effect` per beat (optional; at most 2-3 in a reel): `behind` (title behind the head), `orbit`
  (a list of things), `glass` (numbers), `mono` (one dramatic word), `comment` (the CTA),
  `glasstype` (one big word/number), `phone` (show a result/profile), `checklist` (steps),
  `doodle` (fun/emotion), `background`, `papercut` (= background paper + border + stickies),
  `stickies` (labels), `framebreak`, `vertigo` (a twist), `cover` (topic title), `chart` (growth),
  `polaroids` (memories/varieties), `prompt` (a sentence), `zoom`, `zoomcut` (between beats),
  `pullback` (the ending).
  Suggest one where it fits; they can change it on the page. reel-edit adds them
  (fx_pack.py, reference.md 4b).
- A re-hook in the middle (a twist, "the hard part?", a number).
- **Last beat** `"kind": "cta"`: one clear action (comment a word, follow, save).
- Anything you're unsure of (a size, price, variety, local store) goes in
  `[square brackets]` in `say` and is listed in `fill_in`.
- `shots`: what to film for each beat, in order. Mark which ones are new to film.
  The talking-take note always says: "Put your script right under the camera lens (or use a
  free teleprompter app) so you look into the lens. Leave a hand's width of wall or sky above
  your head if any beat has a title behind your head." Screen recordings: "Turn on Do not
  disturb first, and don't show your email."
- `caption`: the hook again, 3-6 short value lines with emoji bullets, the CTA, a
  question to drive comments, 5-10 hashtags.
- `research`: the 3-5 outliers it learns from (label = "@creator · views · Nx usual").
- `template` + `next_ideas`: the reusable beat pattern and 4-6 follow-up episodes.

## 2. Make and publish the page

```
python3 script_page.py work/<slug>/script.json work/<slug>/script.html --brand work/brand-kit.json
```
(Leave out `--brand` if there's no kit yet.) Publish `script.html` with the Artifact
tool (icon "script"). Keep the same file path for every version so the link stays the same.
If there's no Artifact tool, send the script as a message: one block per beat.

Send the link with these steps:
> 1. Tap the link. Your script opens.
> 2. Tap any words to change them (Say or On screen).
> 3. Under each beat, tap the **Special effect** box and pick one, or leave **No effect**.
> 4. When you're done, tap **Copy my changes**.
> 5. Come back here, press and hold in the message box, tap **Paste**, then send.
> Happy with it as it is? Just reply **looks good**.

## 3. Changes

They paste a block starting `SCRIPT CHANGES (for Claude)` + JSON (`title`, `beats`
with `name`, `time`, `say`, `on_screen`). Copy those into `script.json`, keep
everything else. If they changed a number or name in `say`, update the same thing in
`on_screen`, `glance` and `caption` too (they often fill in [brackets] in Say only), remake the page, republish to the same link. Repeat until they say
it's good.

Then: "Next: your brand (if not done) and the overlays. Film the shot list whenever
you're ready and put the clips in one Google Drive folder." Go to `reel-brand` or
`reel-overlays`.
