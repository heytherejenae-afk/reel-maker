---
name: reel-creator
description: Start here for making an Instagram/TikTok reel end to end - idea and outlier research, transcribing winning reels, script, brand kit, Canva overlays, first edit, and hand-off to CapCut or Instagram Edits. Use when someone says "make a reel", "I need reel ideas", "help me plan a reel" or wants to jump to any stage.
---

# Reel creator: the whole journey

The person is probably a beginner on a phone. Every instruction you give them is
tap by tap, naming every button, menu and box, and saying what they will see next.
Never ask them about codecs, settings or file formats.

## The 7 stages (each is its own skill in this plugin)

| # | Stage | Skill | Needs | Gives them |
|---|---|---|---|---|
| 1 | Ideas + outlier research | `reel-ideas` | vidIQ connector | 5-8 outlier reels in their niche, hook ideas, 3 reel ideas to pick from |
| 2 | Transcribe the outliers | `reel-transcribe` | Eden connector (Discover plan), else Get Transcript connector | What the winners actually say, beat by beat, and why it works |
| 3 | Script | `reel-script` | nothing extra | Their script page: beats (Say / On screen), shot list, caption, fill-ins |
| 4 | Brand | `reel-brand` | nothing extra | `brand-kit.json` (colours, fonts, caption style), saved for every reel |
| 5 | Overlays | `reel-overlays` | Canva connector (optional) | One overlay page per beat, in one of 6 styles, as transparent PNGs |
| 6 | First edit | `reel-edit` | Google Drive folder of clips | The finished reel MP4 + an editor page to ask for changes |
| 7 | Hand-off | `reel-handoff` | CapCut or Edits app on their phone | MP4 + separate layers + tap-by-tap stacking steps |

Sibling skills live next to this folder: `../reel-ideas/SKILL.md` and so on. The
editing engine (scripts, fonts, models) is in `../reel-edit/`.

## How to run it (the order a new person expects)

1. **Brand first, once.** "Do you need to update your brand information?" If there's
   no `brand-kit.json` (or they want changes), run `reel-brand`: publish their own Brand
   Kit page and wait for the pasted BRAND KIT. Save its link to memory.
2. **Reel Setup page, every reel.** Publish `../reel-edit/pages/reel-setup.html` with
   the Artifact tool (icon "clipboard"), after replacing `BRAND_KIT_LINK` in it with THEIR
   Brand Kit link (never someone else's private link). Keep the same file path so the
   link stays the same. It asks: brand keep/change, **How do you want to start?**
   (`search` = find a winning idea · `idea` = I have an idea · `script` = I have my
   script and clips), topic, length, feel, music, extras (incl. special effects).
   Wait for the pasted REEL SETUP block, then jump by `start`:
   `search` -> `reel-ideas` (+ `reel-transcribe`) -> `reel-script`;
   `idea` -> `reel-script`; `script` -> `reel-overlays` or straight to `reel-edit`.
   Never make them redo earlier stages.
3. Then: script page (with a Special effect per beat) -> overlays -> film + Drive
   folder -> edit -> hand-off. At the end of each stage, show the result and ask
   "Happy with this? Tap **Next** to go on to <next stage>, or tell me what to change."
4. Keep everything for one reel in one project file, `work/<reel-slug>/reel-project.json`:
   ```json
   {"niche": "beginner gardening, Australia", "audience": "...", "idea": "...",
    "research": [{"url": "...", "views": 0, "outlier": 0, "hook": "...", "transcript": "...", "why": "..."}],
    "script": "work/<slug>/script.json", "script_page": "<artifact link>",
    "brand": "work/brand-kit.json", "overlays": {"style": "tag", "canva_design": "...", "pngs": ["ov/p1.png"]},
    "drive_folder": "...", "reel": "<mp4 path>", "editor_page": "<artifact link>", "handoff": ["capcut", "edits"]}
   ```
   Each stage reads what it needs from here and writes its result back, so a later
   chat can pick up where they left off.
5. **Where files go.** Inside a Claude project (`/mnt/project-files/` exists): save
   deliverables under `/mnt/project-files/reels/<slug>/` and attach them to your
   reply. Otherwise follow the delivery rules in the repository's `CLAUDE.md`.

## Missing connectors

If a stage needs a connector that isn't connected, don't stop the whole journey.
Say which connector, what it costs, and give the tap-by-tap steps from `INSTALL.md`
(Part 3) at the plugin root. Offer the fallback in the same message:
- No vidIQ: they paste 3-5 reel links they've noticed doing well; go to stage 2.
- No Eden plan: use the Get Transcript connector; if that's missing too, read the
  reels' captions and describe the hook from the first frame they screenshot.
- No Canva: make the overlays with the built-in styles (`reel-overlays` does both).
