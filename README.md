# Reel maker: clips + one sentence in, finished reel out

Send Claude a Google Drive folder of your raw phone clips and one sentence about
what the reel is for. Claude picks the best moments, cuts out the ums, adds
captions with highlighted key words, titles, stickers and music, and gives you a
vertical reel (30 to 45 seconds) ready for Instagram, TikTok or YouTube Shorts.
You also get a short coaching report: what worked, what to fix, and which shots
to film next time. It can also make a carousel, a story and three test reels from
the same clips.

You don't need to know anything about video editing or code. Claude asks you
at most three things: your clips, what the reel is for, and how you want it to
look (or "you choose").

---

## What you need and what it costs

| You need | Cost | Why |
|---|---|---|
| A **Claude Pro** plan (or Max) | US$20 a month, or US$17 a month paid yearly. Your local price shows in the app | The tool runs in "Claude Code", which isn't on the free plan |
| A **GitHub** account | Free | Holds your own copy of the tool and your finished reels |
| A **Google Drive** account | Free (15 GB) | Where you put your clips so Claude can fetch them |
| A **computer** for the one-time setup (about 15 minutes) | | Some settings only show on a computer. After that, everything works from your phone |

Everything inside the tool is free: the video tools, speech-to-text, the fonts and the music
(the music just needs a credit line in your caption, which Claude gives you).

**Usage limits:** one reel is a big job, so it uses a large share of your Pro
plan's usage. If Claude says you've hit your limit, wait for it to reset (the
message tells you when) and carry on in the same chat.

---

## One-time setup

Do these steps once, in order, on a computer. Each step says what you should see
when it's done.

### Step 1. Get the accounts

1. Sign up for Claude Pro at [claude.ai](https://claude.ai) (Settings > Billing, or the upgrade button).
2. Make a free GitHub account at [github.com/signup](https://github.com/signup) if you don't have one.

### Step 2. Make your own private copy of the tool

1. Open **https://github.com/heytherejenae-afk/reel-maker** (the link you were given).
2. Click the green **Use this template** button, then **Create a new repository**.
3. Repository name: `reel-maker`. Choose **Private** (so your reels stay private).
4. Click **Create repository**.

Done when: you see `github.com/<your-name>/reel-maker` with a list of files.

### Step 3. Connect Claude and set up the reel environment

1. Go to [claude.ai/code](https://claude.ai/code) and sign in.
2. When it asks, click **Connect GitHub** and approve. If it asks you to install
   the **Claude GitHub App**, install it and pick **Only select repositories >
   reel-maker**. (If you skipped this, do it at
   [github.com/apps/claude](https://github.com/apps/claude/installations/new).)
3. Under the message box, click the **environment** selector (it probably says
   **Default**) and choose **New environment** at the bottom.
4. Fill in the form:
   - **Name:** `Reel maker`
   - **Network access:** choose **Custom**. In **Allowed domains**, paste these
     lines exactly:
     ```
     drive.google.com
     drive.usercontent.google.com
     huggingface.co
     *.huggingface.co
     *.hf.co
     incompetech.com
     ```
     and **tick "Also include default list of common package managers"**.
   - **Setup script:** open [setup.sh](setup.sh) in your copy on GitHub, copy
     everything in it, and paste it into the box.
5. Click **Add environment**. Make sure the selector now shows **Reel maker**.

Done when: the environment selector under the message box says **Reel maker**.

> Why: Claude works in a private computer in the cloud that can only reach
> websites you allow. These ones let it download your clips from Google Drive,
> the speech-to-text model, and the free music. The setup script installs the
> video tools once, so later reels start quickly.

### Step 4. Make a Google Drive folder for your clips

1. In Google Drive, make a folder (for example "Reel 1").
2. Put your video clips in it. You can also add your own font file (`.ttf` or
   `.otf`), GIFs or a music track.
3. Share it so Claude can open it. On a phone: open the folder > the three dots
   > **Share** > **Manage access** > **General access** > **Anyone with the link**
   (Viewer). On a computer: right-click the folder > **Share** > **General
   access** > **Anyone with the link**.
4. Tap **Copy link**.

Done when: you have a link that starts with `https://drive.google.com/drive/folders/`.

---

## Making a reel (every time, works on your phone)

1. Open [claude.ai/code](https://claude.ai/code) (or the **Code** tab in the Claude app).
2. Check the repository picker says **reel-maker** and the environment says **Reel maker**.
3. Send **one message** with your Drive link and one sentence about the reel. For example:

   > https://drive.google.com/drive/folders/abc123 — 30 second reel for beginner
   > gardeners: what to plant in December. Fun and upbeat.

4. Claude sends you picture sheets of styles, colours and fonts. Reply with your
   picks ("style 2, colour 5, font 3") or "you choose".
5. Claude shows you a **storyboard** (the plan, shot by shot). Change anything you
   like ("cut the word basically", "swap shots 2 and 3"), then say **build it**.
6. Wait 10 to 20 minutes. You can close the app; Claude keeps working.
7. You get the reel, the coaching report and posting tips. Say yes if Claude offers
   a carousel, story and trial reels.

### Getting your reel onto your phone

Claude gives you a link for each file. Open it in **Chrome**, signed in to
GitHub, and the video downloads. Then post it from your phone's gallery or
Downloads folder. If Claude also shows a preview page, you can watch and
download it there.

Your reels are saved in the `reels/` folder of your private copy. Delete old ones
now and then to keep it tidy.

**Save your look:** when you're happy, say "save my look". Claude makes a
`brand-kit.json` file. Put it in your Drive clips folder each time, and every
reel matches. Say "turn on autopilot" and Claude will stop asking questions.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| "Nothing downloaded" or "can't open the folder" | The Drive folder isn't shared publicly. Redo Step 4.3 and send the link again |
| "Blocked" or "403" when downloading | A website isn't on the allowed list. Recheck Step 3.4, save, then **start a new chat** (old chats keep the old settings) |
| No **Reel maker** environment to choose | Redo Step 3, on a computer |
| Can't find **reel-maker** in the repository picker | Install the Claude GitHub App on it (Step 3.2) |
| The **+** button on your phone only shows photos | Don't upload clips in the chat; use the Drive folder |
| "You've hit your usage limit" | Wait until the time it shows, then say "carry on" |

---

## Questions people ask

- **Do I need Adobe, CapCut or any editing app?** No. Everything happens in Claude.
  If you like, open the finished MP4 in CapCut or Instagram Edits for final touches.
- **Can I upload clips straight into the chat?** Not reliably; videos are too big.
  Use the Drive folder.
- **Can I choose the fonts?** Yes. Claude shows a numbered font sheet. You can also
  add a font you bought: put the `.ttf` or `.otf` file in the Drive folder. Check
  its licence covers social media video. Adobe Fonts can't be used (Adobe doesn't
  let you download the files).
- **Can I see the plan before it's made?** Yes, the storyboard. Nothing is made until you say "build it".
- **Are key words highlighted?** Yes, in yellow by default, or your brand colour.
- **What overlays can it add?** Big titles (including 3D), number badges, do/don't cards,
  "save this" cards, comment and DM pop-ups, a Follow button, emoji stickers (left,
  centre or right), picture-in-picture and before/after cards.
- **Is the music free?** Yes. It's by Kevin MacLeod (CC BY 4.0). Paste the credit line
  Claude gives you into your caption. You can also swap in a trending sound in
  Instagram or TikTok before posting.
- **Can it hide my kids' faces?** Yes. Ask it to blur everyone except you, or pick
  which faces to blur.
- **How long are the reels?** Usually 30 to 45 seconds, or whatever length you ask for.
- **Can I use it on my phone?** Yes, after the one-time setup on a computer.

---

## Credits

Fonts are from Google Fonts (SIL Open Font License). Music is by Kevin MacLeod,
incompetech.com, CC BY 4.0. Face detection uses OpenCV's YuNet and SFace models;
the person cut-out uses Google's MediaPipe selfie segmenter. Speech-to-text uses
faster-whisper.
