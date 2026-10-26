# Reel maker

This repository is a video tool, not a code project. The person using it is
probably a beginner who wants a finished reel, not code changes.

When they send a Google Drive link and a short brief (or ask for a reel), follow
`.claude/skills/brief-to-reel/SKILL.md` from step 1: pickers, storyboard,
render, coaching report, then offer the extras. Work in `work/` (ignored by git).
Never change the tool's own files unless they ask you to.

If the setup script did not run (for example `faster_whisper` or `gdown` is
missing), run `bash setup.sh` once before starting. If a download is blocked by
the network, tell them which domain to add to their environment's allowed
domains (see README.md, step 3) and that they need to start a new session after.

## Showing pictures and giving them files

**Inside a Claude project** (the folder `/mnt/project-files/` exists): save every
picture and deliverable under `/mnt/project-files/reels/<short-name>/` and attach
them to your reply, so they appear in the project's Library. Don't commit reels to
git. Skip the steps below.

**Otherwise** the person can't open files on this machine, so:

1. **Pictures to choose from** (style, colour and font sheets, storyboard frames)
   and **the finished reel**: if the Artifact tool is available, publish one simple
   page that shows them (pictures inline; the reel as a `<video controls>` with a
   download link; re-encode a copy under 15 MB for the page if needed). Keep the
   same page and republish it as things change.
2. **Always also save deliverables to git** so they can download the full-quality
   files: copy the reel, coaching report, carousel slides and story/trial reels to
   `reels/<short-name>/`, commit and push the session branch, then give a direct
   link for each file in this form:
   `https://github.com/<owner>/<repo>/raw/<branch>/reels/<short-name>/<file>`
   (get owner/repo from `git remote -v`). Tell them: "Open the link in Chrome
   while signed in to GitHub and the video downloads; then save it to your phone."
3. Don't open a pull request unless they ask.

Write the coaching report in the chat as well as in the file, short enough to
read on a phone.
