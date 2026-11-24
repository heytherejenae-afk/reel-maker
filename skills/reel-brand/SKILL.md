---
name: reel-brand
description: Stage 4 of the reel creator - set up or update the person's brand kit (colours with jobs, title/caption/key-word fonts, caption style) with the Brand Kit page, and save each brand as brand-kit-<name>.json for every reel (several brands allowed). Use when someone has no brand kit, wants to change or add a brand, or pastes a BRAND KIT block.
---

# Stage 4: Brand kit

A person can have several brands (for example a gardening account and an AI account),
and should only ever paste each brand kit once. Each brand is one file,
`brand-kit-<slug>.json`, where the slug is the `brand_name` in lower case with words
joined by `-` (e.g. `brand-kit-hey-there-jenae-ai.json`).

**Before asking anything, gather every saved brand** from all of these places, keyed by
`brand_name` (if a brand turns up twice, the first place in this list wins):
1. `work/brand-kit-*.json`
2. `/mnt/project-files/brand/brand-kit-*.json` (the project's shared files, kept forever;
   an older single `brand-kit.json` there counts too)
3. `brand-kit-*.json` / `brand-kit.json` at the top of their repository
4. Project memory: memories named `brand-kit-<slug>` (or an older `brand-kit`)
5. `brand-kit*.json` in their Google Drive clips folder
6. `BRAND KIT` blocks earlier in this chat

Then ask: **"Which brand is this reel for?"** with one option per saved brand by name,
plus **Change one of my brands** and **Add a new brand**. With no saved brands, ask
"Do you have a brand kit yet?" instead. (The Reel Setup page asks this for you: fill its
`SAVED_BRANDS` list before publishing, see `reel-creator`.)

- **A saved brand:** copy that kit to `work/brand-kit.json`, which every later stage
  reads, and say its name once ("Using your Hey There Jenae AI brand."). Never ask them
  to paste it again.
- **Change one / Add a new brand:** use the Brand Kit page. A changed kit keeps its
  `brand_name`, so it replaces that brand's file and leaves the others alone.
- **Found nothing for the brand they named:** say so, send the Brand Kit page, and tell
  them this is the last time they'll need it for that brand.

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

1. `work/brand-kit.json` for this reel, and `work/brand-kit-<slug>.json`.
2. `/mnt/project-files/brand/brand-kit-<slug>.json` if `/mnt/project-files/` exists.
   Every future thread in their project can read it. Other brands' files stay as they are.
3. Project memory: one file per brand, named `brand-kit-<slug>` (type `project`), with
   the brand name, the date, and the whole JSON. Replace only that brand's memory.
4. If neither 2 nor 3 is possible (for example a plain Claude Code folder), save
   `brand-kit-<slug>.json` at the top of their project folder instead.

Then tell them in one line: "Saved your <brand name> brand. Next time I'll list it with
your other brands, so you won't need to paste it again."

### Where the kits live

These places outlive a single chat: the project's shared files, project memory, the
repository and their Drive folder. `work/` does not. Never tell them to pin or star a
chat to keep a kit: a new chat can't read an old one.

The kit's `colors`: `light` = background/cards, `primary` = ink, `highlight` = key
words, `soft`/`second`/`accent` = extra. Fonts: `display_font` (titles), `font`
(captions), `key_font` (key words). Every later stage reads this file: the script
page, the overlay pages and the edit.

No brand yet and they say "you choose": use cream `#F6EFDF`, forest `#2F4A35`,
terracotta `#E8875A`, sage `#9CAF88`, DM Serif Display / Inter Display / DM Serif
Display Italic, and tell them they can change it any time.
