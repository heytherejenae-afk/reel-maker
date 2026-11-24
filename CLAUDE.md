# Reel creator

This repository is a reel-making tool, not a code project. The person using it is
probably a beginner who wants a finished reel, not code changes. All
instructions to them are click by click, naming every button, menu and box.

**The tool is used on a computer** (claude.ai in Chrome, Mac or Windows). Filming
happens on their phone, and only the Edits / phone CapCut step (stage 7) goes back to
the phone. Write steps for a computer (click, not tap) except in stage 7's phone steps.

**Start every request at `skills/reel-creator/SKILL.md`.** It lists the 7 stages and
which skill file runs each one:

1. `skills/reel-ideas/SKILL.md`: outlier research and hook ideas (vidIQ)
2. `skills/reel-transcribe/SKILL.md`: transcribe the winning reels (Eden, Get Transcript backup)
3. `skills/reel-script/SKILL.md`: the script page
4. `skills/reel-brand/SKILL.md`: brand kit
5. `skills/reel-overlays/SKILL.md`: overlays (Canva or built-in)
6. `skills/reel-edit/SKILL.md`: the first edit (engine in `skills/reel-edit/scripts/`)
7. `skills/reel-handoff/SKILL.md`: CapCut / Edits hand-off

Work in `work/` (ignored by git). Never change the tool's own files unless asked.
If `faster_whisper` or `gdown` is missing, run `bash setup.sh` once. If a download is
blocked by the network, name the domain to add (INSTALL.md, Part 4C) and say they need
to start a new chat after.

## Giving them files

They download files on their **computer**: attachments in claude.ai download with
one click (no size limit like the Google Drive connector's ~3 MB). So:
1. **Inside a Claude project** (`/mnt/project-files/` exists): save deliverables
   under `/mnt/project-files/reels/<slug>/` and attach them to your reply.
2. Tell them how to download on a computer: "Click the file under my message, then
   click **Download**. It saves to your **Downloads** folder." For Edits (phone):
   open the same chat in the Claude phone app, tap the file, tap **Download**
   (tested on Android 2026-11-24; going via Google Drive did not work).
3. Pictures to choose from and pages to fill in: publish with the Artifact tool and
   keep the same file path so the link stays the same.

## Pages look the same every time

Every page the person sees (Brand Kit, Reel Setup, script page, script editor, reel
editor) comes from a fixed file in this repo and is black and white, with one system
font. Publish those files as they are and only fill in their data (links, brand names,
script, shots). Never write a page from scratch, restyle one, or colour it with the
person's brand. Brand colours and fonts belong in previews of the reel itself (the
phone mock-up, font and colour samples), never in the page's own buttons, headings or
backgrounds. Keep each page's file path the same so its link stays the same.
