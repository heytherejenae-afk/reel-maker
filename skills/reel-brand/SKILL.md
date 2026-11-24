---
name: reel-brand
description: Stage 4 of the reel creator - set up or update the person's brand kit (colours with jobs, title/caption/key-word fonts, caption style) with the Brand Kit page, and save it as brand-kit.json for every reel. Use when someone has no brand kit, wants to change their brand, or pastes a BRAND KIT block.
---

# Stage 4: Brand kit

Always ask first: **"Do you need to update your brand information?"**
Keep my saved brand kit / Yes, change something / I don't have one yet.
Find their saved kit BEFORE asking, so you can name it in the question
("Keep my saved Hey There Jenae kit"). A person should only ever paste their kit once.
Look in this order and stop at the first one you find (see "Where the kit lives" below),
then copy it to `work/brand-kit.json`, which every later stage reads:
1. `work/brand-kit.json` (this thread already has it)
2. `/mnt/project-files/brand/brand-kit.json` (the project's shared files, kept forever)
3. `brand-kit.json` at the top of their repository
4. Project memory: a memory named `brand-kit` holding the kit's JSON
5. `brand-kit.json` in their Google Drive clips folder
6. A `BRAND KIT` block earlier in this chat

- **Keep:** use the kit you found. Never ask them to paste it again.
- **Change / don't have one:** use the Brand Kit page.
- **Found nothing but they said Keep:** say you couldn't find it, send the Brand Kit
  page, and tell them this is the last time they'll need it.

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

Their message contains `BRAND KIT (save as brand-kit.json)` + JSON. Save it
everywhere below, straight away, without asking (`work/` is wiped when the thread ends,
so saving only there is why people got asked to paste their kit again):

1. `work/brand-kit.json` for this reel.
2. `/mnt/project-files/brand/brand-kit.json` if `/mnt/project-files/` exists. Every
   future thread in their project can read it.
3. Project memory: one file named `brand-kit` (type `project`) with the brand name,
   the date, and the whole JSON. Replace an older one rather than adding a second.
4. If neither 2 nor 3 is possible (for example a plain Claude Code folder), save
   `brand-kit.json` at the top of their project folder instead.

Then tell them in one line: "Saved your brand kit. I'll use it for every reel, so you
won't need to paste it again. Say 'change my brand' any time to update it."

### Where the kit lives

These places outlive a single chat: the project's shared files, project memory, the
repository and their Drive folder. `work/` does not. Never tell them to pin or star a
chat to keep the kit: a new chat can't read an old one.

The kit's `colors`: `light` = background/cards, `primary` = ink, `highlight` = key
words, `soft`/`second`/`accent` = extra. Fonts: `display_font` (titles), `font`
(captions), `key_font` (key words). Every later stage reads this file: the script
page, the overlay pages and the edit.

No brand yet and they say "you choose": use cream `#F6EFDF`, forest `#2F4A35`,
terracotta `#E8875A`, sage `#9CAF88`, DM Serif Display / Inter Display / DM Serif
Display Italic, and tell them they can change it any time.
