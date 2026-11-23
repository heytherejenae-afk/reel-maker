# Reel creator

This repository is a reel-making tool, not a code project. The person using it is
probably a beginner on a phone who wants a finished reel, not code changes. All
instructions to them are tap by tap, naming every button, menu and box.

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

The Claude phone app can't always save attached files to the phone. So:
1. **Inside a Claude project** (`/mnt/project-files/` exists): save deliverables
   under `/mnt/project-files/reels/<slug>/` and attach them to your reply.
2. **Also make files easy to get onto a phone.** Files under about 3 MB (overlay
   cards, short layers): put them in their Google Drive too (Google Drive connector
   `create_file` into a folder named after the reel). Bigger videos: commit them to
   `reels/<slug>/` on the session branch and give the
   `https://github.com/<owner>/<repo>/raw/<branch>/reels/<slug>/<file>` link to open in Chrome.
3. Pictures to choose from and pages to fill in: publish with the Artifact tool and
   keep the same file path so the link stays the same.
