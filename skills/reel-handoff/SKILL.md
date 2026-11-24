---
name: reel-handoff
description: Stage 7 of the reel creator - hand the finished reel over for polishing in CapCut or Instagram Edits - the finished MP4 plus full-length layers (video, title behind head, captions, overlays) and step-by-step stacking steps (computer download, then phone steps for Edits). Use when someone wants to finish a reel in CapCut or Edits, or asks for the layers.
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

## Getting the files to them (computer first, decided 2026-11-24)

The tool is used on a **computer**. Attach the MP4, the layer files and the steps file
to the reply (from `/mnt/project-files/reels/<slug>/`). Tell them: "Click each file
under my message, then click **Download**. They save to your **Downloads** folder."
Full-size files are fine: there's no size limit on downloading attachments.

Don't send videos through the Google Drive connector: it refuses anything over about
**3.1 MB** (tested 2026-11-24).

**CapCut on a computer** (works on Intel and Apple Macs and Windows): use
`layers-for-computer/` (see-through .mov). No phone needed.

**Edits, or CapCut on a phone:** Edits is a phone app (Edits for Mac needs an Apple
silicon Mac). Tell them to open the same chat in the **Claude** phone app, tap each
file, then **Download** (Step 1 of `edits-steps.md`). Tested on Android 2026-11-24:
downloading attachments straight to the phone works; saving them to Google Drive from
the phone did not. Don't route videos through Drive.
Effects already replaced the cards on their beats, so list only the cards left.

## CapCut steps

On a computer: import `layers-for-computer/` .mov files and stack them from 0:00 (no
colour removal). On a phone: use `capcut-steps-example.md` (in this folder) as the
template: move files to the phone (as in `edits-steps.md`), New project with `1-video`, then for each layer **Overlay** > **Add overlay**
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
