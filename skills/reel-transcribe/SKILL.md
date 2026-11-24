---
name: reel-transcribe
description: Stage 2 of the reel creator - transcribe the outlier reels found in research (Eden first, Get Transcript as the free backup) and break each into hook, beats and call to action. Use after outlier research, or when someone pastes reel links and wants to know what they say or why they worked.
---

# Stage 2: Transcribe the winning reels

Take the top 3-5 reels from `reel-project.json` `research` (or links the person
pasted). Never transcribe more than 5 without asking.

## 1. Eden first

Use `eden_read_social_post` with `url` = the reel link. It returns the spoken
`transcript` and, for Instagram reels and TikToks, `onScreenText` (the captions and
text burned into the video), which matters because many reels carry the hook on screen.

- `upgradeRequired` / "research comes with Eden Discover": their Eden plan doesn't
  include research. Tell them once: "Eden's reel reading needs Eden Discover
  (US$5 a month). I'll use the free backup instead." Then use the backup for all
  the remaining reels; don't retry Eden.
- `status: "queued"`: wait a moment and try once more, then use the backup.
- Eden not connected at all: use the backup.

## 2. Backup: Get Transcript

1. `gettranscribe_create_transcription_job` with `url` (and `language` if not English).
2. Wait the `suggested_first_poll_after_seconds` it gives, then
   `gettranscribe_get_transcription_job` until `completed` (don't busy-loop).
3. `gettranscribe_get_transcription` with the `transcription_id`.
Its free plan is only 2 videos in total; on "free plan limit" stop and say so once.
It gives spoken words only, no on-screen text. If the reel is text-only (music, no
talking), say so and use its caption instead.

## 2b. When both are locked

Don't download YouTube videos yourself: YouTube blocks Claude's cloud ("confirm you're
not a bot"). Instagram reels do download with `yt-dlp` and can be transcribed with
faster-whisper. Otherwise skip this stage: the titles are the hooks. Never stall here.

## 3. Break each one down

For each reel, save to `research[i]`: `transcript`, `on_screen`, and a breakdown:
- **Hook (0-3 s):** the exact words + what's on screen.
- **Beats:** one line each, with rough seconds (count ~2.5 spoken words per second).
- **Re-hook:** where they win attention back mid-way, if they do.
- **Call to action:** exact words.
- **Why it works:** one or two sentences (curiosity gap, a number, a strong opinion, a payoff).

Show the person a short summary (not the full transcripts): one block per reel,
then 2-3 lessons for their reel. Then: "Next I'll write your script using these
lessons. Tap **Next**, or tell me what to change." Go to `reel-script`.

Never copy a creator's script word for word into theirs. Borrow the structure and
the hook pattern, not the words.
