# Reel maker: clips + one sentence in, finished reel out

Send Claude a Google Drive folder of your raw phone clips and one sentence about
what the reel is for. Claude picks the best moments, cuts out the ums, adds
captions with highlighted key words, titles, stickers and music, and gives you a
vertical reel (30 to 45 seconds) ready for Instagram, TikTok or YouTube Shorts.
You also get a short coaching report: what worked, what to fix, and which shots
to film next time.

You don't need to know anything about video editing or code.

---

## Before you start: what you need and what it costs

| You need | Cost |
|---|---|
| A **Claude Pro** plan (Max also works). The free plan can't run this tool | US$20 a month, or US$17 a month if you pay yearly. Your local price shows when you upgrade |
| A **GitHub** account. Think of it as a free online folder that holds your copy of the tool | Free |
| A **Google Drive** account, for your video clips | Free |
| A **computer** (laptop or desktop) for the one-time setup. It takes about 20 minutes. After that you can make reels from your phone | |

Everything inside the tool is free: the video tools, the fonts and the music.

> **Tip:** do the whole setup in one sitting, in the **Chrome** browser on your
> computer. Keep this page open in one tab and do each step in another tab.

---

## Part 1. Get your accounts ready (5 minutes)

### 1A. Claude Pro

1. Go to **claude.ai** and sign in (or sign up).
2. Click your **name or initials** in the bottom-left corner.
3. Click **Settings**, then **Billing**.
4. Click **Upgrade** and choose **Pro**. Pay.

✅ **Done when:** Settings > Billing says **Pro**.

### 1B. A free GitHub account

1. Go to **github.com/signup**.
2. Type your email, make a password and choose a username (anything, for example `sarahgardens`).
3. Do the puzzle, then type the code GitHub emails you.
4. If it asks questions about you, click **Skip personalization** (or **Continue for free**).

✅ **Done when:** you're on github.com and see your picture or initial in the top-right corner.

---

## Part 2. Make your own copy of the tool (3 minutes)

1. In the same browser (still signed in to GitHub), go to:
   **https://github.com/heytherejenae-afk/reel-maker**
2. Near the top-right, click the green **Use this template** button.
   Then click **Create a new repository**.
   (If you can't see the green button, make the window wider, or scroll right.)
3. On the next page:
   - **Owner:** leave it as your username.
   - **Repository name:** type `reel-maker`
   - Click **Private** (so only you can see your reels).
4. Click the green **Create repository** button at the bottom.

✅ **Done when:** the address bar shows `github.com/YOUR-USERNAME/reel-maker`
and you see a list of files (README.md, setup.sh and others).

---

## Part 3. Connect Claude to GitHub (3 minutes)

1. Go to **claude.ai/code** (type it into the address bar).
2. You'll see a welcome screen asking you to connect GitHub. Click
   **Connect GitHub** (it may say **Sign in with GitHub**).
3. GitHub opens and asks "Authorize Claude?". Click the green **Authorize** button.
4. GitHub may then show **Install Claude**. If it does:
   - Click your username.
   - Click **Only select repositories**.
   - Click **Select repositories**, type `reel-maker` and click it.
   - Click the green **Install** button.
5. You're sent back to Claude.

**If step 4 didn't appear**, do it now: go to **github.com/apps/claude**, click
**Install** (or **Configure**), then follow step 4 above.

> Your copy is private, so Claude can only open it once the Claude app is
> installed on it. That's what step 4 does.

✅ **Done when:** at claude.ai/code, you see a message box with a
**repository** button under it, and when you click it, **reel-maker** is in the list.

---

## Part 4. Create the "Reel maker" environment (5 minutes)

This tells Claude which websites it's allowed to use (Google Drive, the
speech-to-text model and the free music), and installs the video tools once.

1. Stay on **claude.ai/code**.
2. Look under the message box. There's a small button that says **Default**
   (it may have a cloud icon). Click it.
3. At the bottom of the menu that opens, click **New environment**.
4. A form opens. Fill it in like this:

   **Name:** type `Reel maker`

   **Network access:** click it and choose **Custom**. A box called
   **Allowed domains** appears. Copy these six lines and paste them in:

   ```
   drive.google.com
   drive.usercontent.google.com
   huggingface.co
   *.huggingface.co
   *.hf.co
   incompetech.com
   ```

   Under the box, **tick** "Also include default list of common package managers".
   This one matters: without it, the setup fails.

   **Setup script:** click it. Then, in a new tab, open this link:
   **https://raw.githubusercontent.com/heytherejenae-afk/reel-maker/main/setup.sh**
   You'll see a page of plain text. Press **Ctrl + A** then **Ctrl + C**
   (on a Mac: **Cmd + A** then **Cmd + C**) to copy it all. Go back to the Claude
   tab, click in the setup script box, and press **Ctrl + V** (Mac: **Cmd + V**)
   to paste.

5. Click **Add environment** at the bottom of the form.

✅ **Done when:** the button under the message box says **Reel maker** instead of **Default**.

> If you ever change these settings later, start a **new** chat afterwards.
> Chats you already started keep the old settings.

---

## Part 5. Put your clips in Google Drive (do this for every reel)

### On an Android phone or iPhone (Google Drive app)

1. Open the **Google Drive** app.
2. Tap the **+ New** button (bottom-right), then **Folder**. Name it, for example
   `December reel`, and tap **Create**.
3. Open the folder. Tap **+ New** > **Upload** and pick your video clips.
   Wait until they finish uploading.
4. Go back one screen so you can see the folder. Tap the **three dots ⋮** next to it.
5. Tap **Share**. Then tap **Manage access** (or **General access**).
6. Under **General access**, tap **Restricted** and change it to
   **Anyone with the link**. Leave the role as **Viewer**.
7. Tap the **link icon** (or **Copy link**). The link is now copied.

### On a computer (drive.google.com)

1. Click **+ New** > **New folder**, name it, click **Create**.
2. Open the folder and drag your clips into it.
3. Go back, **right-click** the folder > **Share** > **Share**.
4. Under **General access**, change **Restricted** to **Anyone with the link**.
5. Click **Copy link**, then **Done**.

✅ **Done when:** you have a link that starts with `https://drive.google.com/drive/folders/`.

**Optional extras for the same folder:** a font file you bought (`.ttf` or
`.otf`), GIFs or PNG stickers, or your own music track.

---

## Part 6. Make a reel (works on your phone)

1. Open **claude.ai/code** in Chrome, or open the **Claude app** and tap the
   **Code** tab.
2. Check the two buttons under the message box:
   - The repository button says **reel-maker**. If not, tap it and choose **reel-maker**.
   - The environment button says **Reel maker**. If not, tap it and choose **Reel maker**.
3. In the message box, paste your Drive link and add one sentence about the reel.
   Send it as **one message**. For example:

   > https://drive.google.com/drive/folders/abc123 Make a 30 second reel for
   > beginner gardeners about what to plant in December. Fun and upbeat.

4. **Pick a look.** Claude sends picture sheets of styles, colours and fonts.
   Reply with numbers, like `style 2, colour 5, font 3`, or just `you choose`.
5. **Check the storyboard.** Claude shows the plan, shot by shot. Ask for changes
   in plain words ("cut the word basically", "swap shots 2 and 3", "make it
   shorter"), then reply **build it**.
6. **Wait 10 to 20 minutes.** You can close the app. Claude keeps working.
7. You get your reel, a coaching report and posting tips. If Claude offers a
   carousel, a story and trial reels, say **yes** if you'd like them.

### Getting the reel onto your phone

1. Claude gives you a link for each file. Tap the link for the video.
2. It opens in Chrome. If GitHub asks you to sign in, sign in.
3. The video downloads. You'll see it in your phone's **Downloads** or **Files**
   app, and usually in your **Gallery** or **Photos**.
4. Post it from Instagram, TikTok or YouTube as normal. Add the music credit
   line Claude gave you to your caption.

### Next time

- **Save your look:** when you love a reel, say `save my look`. Claude makes a
  file called `brand-kit.json`. Put it in your Drive folder each time and every
  reel will match.
- **Autopilot:** say `turn on autopilot` and Claude stops asking questions and
  just makes the reel.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| "Nothing downloaded" or "can't open the folder" | The Drive folder isn't shared. Redo Part 5, steps 4 to 7, and send the link again |
| "Blocked", "403" or "not allowed" when downloading | A website is missing from the list. Redo Part 4 (click **Reel maker** > the ⚙️ gear or **Edit**), check all six lines are there and the tick box is ticked, click **Save changes**, then start a **new chat** |
| No **Reel maker** in the environment menu | Redo Part 4 on a computer |
| **reel-maker** isn't in the repository list | Redo Part 3, step 4 (install the Claude app on your copy) |
| The page only shows a "Sign in with GitHub" button | Redo Part 3 |
| "You've hit your usage limit" | Wait until the time it shows, then type `carry on` in the same chat |
| The phone's **+** button only shows photos | Don't upload videos into the chat. Use the Drive folder |

---

## Questions people ask

- **Do I need Adobe, CapCut or another editing app?** No. If you like, you can
  open the finished video in CapCut or Instagram Edits for final touches.
- **Can I upload clips straight into the chat?** No. Videos are too big. Use the Drive folder.
- **Can I choose the fonts?** Yes, from a numbered sheet. You can add a font you
  bought by putting the `.ttf` or `.otf` file in your Drive folder. Check its
  licence covers social media video. Adobe Fonts can't be used, because Adobe
  doesn't let you download the files.
- **Can I see the plan first?** Yes, the storyboard. Nothing is made until you say `build it`.
- **Are key words highlighted?** Yes, in yellow, or your brand colour.
- **What can it add on screen?** Big titles (including 3D), number badges,
  do/don't cards, "save this" cards, comment and DM pop-ups, a Follow button,
  emoji stickers (left, centre or right) and before/after cards.
- **Is the music free?** Yes. It's by Kevin MacLeod (CC BY 4.0). Paste the credit
  line Claude gives you into your caption. You can also add a trending sound in
  Instagram or TikTok before posting.
- **Can it hide my kids' faces?** Yes. Ask it to blur everyone except you, or pick which faces to blur.
- **Is my video private?** Yes. Your copy of the tool is private, and so are the reels saved in it.
- **Does it cost extra per reel?** No, it's included in Claude Pro. A reel is a
  big job, though, so it uses a good share of your plan's usage limit.

---

## Credits

Fonts are from Google Fonts (SIL Open Font License). Music is by Kevin MacLeod,
incompetech.com, CC BY 4.0. Face detection uses OpenCV's YuNet and SFace models.
The person cut-out uses Google's MediaPipe selfie segmenter. Speech-to-text uses
faster-whisper.
