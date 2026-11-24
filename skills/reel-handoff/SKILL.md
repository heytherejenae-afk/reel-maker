---
name: reel-handoff
description: Stage 7 of the reel creator - hand the finished reel over for polishing in CapCut or Instagram Edits - the finished MP4 plus full-length layers (video, title behind head, captions, overlays) and tap-by-tap Android steps to stack them. Use when someone wants to finish a reel in CapCut or Edits, or asks for the layers.
---

# Stage 7: Hand-off to CapCut or Edits

Be honest about the limit: **neither app can open a ready-made project from us.**
CapCut's project files are locked (encrypted since about version 6) and Edits has
no import format. So the hand-off is:
1. The **finished MP4**, ready to post as it is, or to open in either app to add a
   trending sound, more text or effects.
2. **Layers**, each the full length of the reel and starting at 0:00, so nothing
   needs lining up: `1-video.mp4` (cut video with their voice), `2-title-behind-you`,
   `3-captions`, `4-overlays`. They let them delete or move one part without the others.

Ask: "Which app do you finish reels in? CapCut / Edits / I'll just post it".

## Which layer files

`script_reel.py build` writes them into the reel's output folder:
- `layers-for-phone/` - pink colour screen (`*-pink.mp4`), for **CapCut** on a phone
  (Chroma key removes the pink). Pink, not green, because garden cards and b-roll are green.
- `layers-for-edits/` - for **Instagram Edits**, which has no colour key (tested on
  Android 2026-11-23: its **Cutouts** is Meta AI person cut-out, **Mask** is shapes only):
  `1-video-with-captions.mp4` (title + captions already on) plus one full-screen
  see-through PNG per overlay card, named with its start and end time, and `card-times.txt`.
  Android phones can't open see-through .mov video, so never send .mov to a phone.
- `layers-for-computer/` - see-through `.mov` files (ProRes 4444), for CapCut on a
  computer: no colour removal needed.

Attach the MP4 and the right layer folder's files, plus the steps file below,
filled in with this reel's name and layer names.

**Tested 2026-11-24:** the Google Drive connector refuses any file over about **3.1 MB**,
so only cards, pink caption/title layers and card-times go to Drive. Videos: make phone
versions under 10 MB (2-pass x264, 1500k video + 96k audio, still sharp), attach them to the
reply, and tell them to tap the video, then the three dots / download arrow, then **Download**.
Effects already replaced the cards on their beats, so list only the cards left.

**Getting files onto their phone (older notes):** attachments in the Claude phone app can be hard
to save. Small files (cards, captions layers, test clips under about 3 MB) also go
into a Google Drive folder named after the reel (Google Drive connector
`create_file`, uploaded from the scratchpad folder). Videos over 3 MB can't go
through the connector: commit them to `reels/<slug>/` on the session branch and give
the `https://github.com/<owner>/<repo>/raw/<branch>/reels/<slug>/<file>` link ("open
it in Chrome, the video downloads to your phone"), or point them to the file in the
project's Library.

## CapCut steps

Use `capcut-steps-example.md` (in this folder) as the template: save files to the
phone, New project with `1-video`, then for each layer **Overlay** > **Add overlay**
> pick it > spread to full screen > drag the strip to 0:00 > **Remove BG** >
**Chroma key** > drag the circle onto the pink > **Intensity** about 20-40 > tick.
Then **1080P**, 30 fps, **Export**. Include the "On a computer instead" part.

## Edits steps

Use `edits-steps.md` (in this folder), filled in with this reel's card names.
Confirmed on Android 2026-11-23: see-through PNGs work in Edits via **Overlay**.

## Last message

Lead with the finished MP4. Then: "Want to change something in CapCut/Edits? Here
are the layers and the steps." Offer to save the brand and the script template for
the next episode (the script page's "next episode ideas").
