---
name: reel-ideas
description: Stage 1 of the reel creator - find outlier Instagram reels and TikToks in the person's niche with vidIQ, pull out hook patterns, and offer 3 reel ideas. Use when someone needs reel ideas, hooks, trending formats or "what's working" research.
---

# Stage 1: Ideas and outlier research

An **outlier** is a reel that got far more views than that creator usually gets
(3x or more). Outliers show what the audience wants right now, not just which
accounts are big.

## 1. Ask (one message, tap-to-pick where possible)

- What's your niche and who watches? (e.g. "beginner gardeners in Australia")
- Any topic in mind for this reel, or should I find one? (topic / "find one")
- Where do you post? (Instagram / TikTok / both, default both)

Save answers to `reel-project.json` (`niche`, `audience`).

## 2. Search with vidIQ (5 credits per search)

Use `vidiq_instagram_tiktok_outlier_search`:
- `query`: the topic, or the niche if no topic.
- `audienceQuery`: `Culture/Region: <country>; Global: <true|false>; Demographics: <who>;`
- `embeddingType`: `concept` for ideas; run a second search with `hook` only if the
  first one comes back thin.
- `outlierScoreMin`: 3, `resultsPerPlatform`: 5, `durationMax`: 90.
- Leave the date at the default (last 30 days). Widen to 90 days only if you get fewer than 4.

Do at most 2 searches without asking (10 credits). Before a third, ask.
If vidIQ isn't connected, ask them to paste 3-5 reel links they've seen doing well,
and skip to step 3.

## 3. Show what's working

Pick the best 5-8 results that fit their niche (drop off-topic ones). For each:
the creator, views, how many times their usual (outlier score), the link, and the
first line or caption hook. Then name the **patterns** across them, only when 2 or
more outliers share one: hook type (price shock, "stop doing X", POV, number list,
myth bust, before/after), format (talking head + b-roll, voiceover over process,
text-on-screen only), length, call to action.

## 4. Offer 3 ideas

Write 3 reel ideas for *their* niche, each built on a pattern you found:
- **Idea** (one line), **Hook** (the first 3 seconds, word for word), **Why it
  should work** (which outliers it borrows from), **What to film**.
Ask them to pick one (decision card or "1, 2 or 3?"), or mix them.

Save the chosen idea and the outlier list (`research`: url, views, outlier score,
hook) to `reel-project.json`. Then say: "Next I'll get the full words from the top
reels so we can see exactly how they hold attention." Go to `reel-transcribe`.
