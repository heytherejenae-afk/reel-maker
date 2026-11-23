---
name: reel-brand
description: Stage 4 of the reel creator - set up or update the person's brand kit (colours with jobs, title/caption/key-word fonts, caption style) with the Brand Kit page, and save it as brand-kit.json for every reel. Use when someone has no brand kit, wants to change their brand, or pastes a BRAND KIT block.
---

# Stage 4: Brand kit

Always ask first: **"Do you need to update your brand information?"**
Keep my saved brand kit / Yes, change something / I don't have one yet.
- **Keep:** load `work/brand-kit.json` (or `brand-kit.json` in their Drive folder).
  If neither exists, say you couldn't find it and offer the page below.
- **Change / don't have one:** use the Brand Kit page.

## The Brand Kit page

`pages/brand-kit-builder.html` in this folder. Publish it once with the Artifact
tool (icon "palette") and save its link in `CLAUDE.md` or project memory so later
reels reuse it. An Artifact is private to its owner, so each person publishes their own copy.

Steps to send:
> 1. Tap the link. The Brand Kit page opens.
> 2. Type your brand name and handle at the top.
> 3. Pick your colours: tap a colour circle, then pick a colour (or type its code, like #2F4A35).
>    Each colour has a job: Background, Ink (words), Pop (key words), Soft, Second pop, Accent.
> 4. Pick 3 fonts from the lists: **Title**, **Captions**, **Key words**.
> 5. Check the phone preview on the right (scroll down on a phone).
> 6. Tap **Copy my brand kit**.
> 7. Come back here, press and hold in the message box, tap **Paste**, then send.

## Saving it

Their message contains `BRAND KIT (save as brand-kit.json)` + JSON. Save the JSON
as `work/brand-kit.json`. Offer to save it into their Google Drive clips folder too
(Google Drive connector `create_file`) so every future reel finds it.

The kit's `colors`: `light` = background/cards, `primary` = ink, `highlight` = key
words, `soft`/`second`/`accent` = extra. Fonts: `display_font` (titles), `font`
(captions), `key_font` (key words). Every later stage reads this file: the script
page, the overlay pages and the edit.

No brand yet and they say "you choose": use cream `#F6EFDF`, forest `#2F4A35`,
terracotta `#E8875A`, sage `#9CAF88`, DM Serif Display / Inter Display / DM Serif
Display Italic, and tell them they can change it any time.
