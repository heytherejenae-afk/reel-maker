# Reel Creator: install guide

Reel Creator takes you from "I need an idea" to a finished reel, in 7 stages:
**ideas → transcribe winning reels → script → brand → overlays → first edit → CapCut or Edits.**
You can start at any stage.

Do Parts 1 to 4 **once, on a computer**, in the **Chrome** browser. It takes about 30 minutes.
After that you can make reels from your phone.

---

## Part 1. What you need and what it costs

| You need | What it does | Cost |
|---|---|---|
| **Claude Pro** (or Max) | Runs the whole tool | US$20 a month (US$17 a month if you pay yearly) |
| **GitHub** account | Holds your copy of the tool | Free |
| **Google Drive** | Where you put your video clips | Free |
| **Google Drive connector** | Lets Claude save files to your Drive, so you can get them onto your phone | Free |
| **Canva connector** | Makes your overlay pages (stage 5) | Free Canva works. Canva Pro (about US$15 a month) adds your own brand kit and fonts. *Optional:* the tool has 6 built-in overlay styles too |
| **vidIQ connector** | Finds reels doing far better than usual in your niche (stage 1) | Free plan: 150 credits a month. One search uses 5 credits, so about 30 searches a month. Boost: US$19 a month for 2,000 credits |
| **Eden connector** | Reads the words and on-screen text of those reels (stage 2) | Needs **Eden Discover**, US$5 a month. *Optional:* the free Get Transcript connector is the backup |
| **Get Transcript connector** | Backup for stage 2 (spoken words only) | Only **2 free videos in total**, then a paid plan (from about US$5 a month). *Optional:* without it, ideas still work from the reels' titles |
| **CapCut** or **Edits** app | Final polish on your phone (stage 7) | Free |

**Cheapest setup:** Claude Pro + free Canva + free vidIQ = **US$20 a month.** If vidIQ runs out of credits, Claude uses a free YouTube Shorts search instead (no transcripts).
**Full setup:** add Eden Discover = **US$25 a month.**

Prices are in US dollars and were checked in November 2026. Your local price shows when you sign up.

---

## Part 2. Get your accounts ready (5 minutes)

### 2A. Claude Pro
1. Go to **claude.ai** and sign in (or sign up).
2. Click your **name or initials** in the bottom-left corner.
3. Click **Settings**, then **Billing**.
4. Click **Upgrade** and choose **Pro**. Pay.

✅ **Done when:** Settings > Billing says **Pro**.

### 2B. A free GitHub account
1. Go to **github.com/signup**.
2. Type your email, make a password and choose a username.
3. Do the puzzle, then type the code GitHub emails you.
4. If it asks questions about you, click **Skip personalization**.

✅ **Done when:** you see your picture or initial in the top-right corner of github.com.

---

## Part 3. Connect the connectors (10 minutes)

Do these steps once for **each** connector in this list:
**Google Drive, Canva, vidIQ, Eden, Get Transcript, GitHub.**

1. Go to **claude.ai**. In the menu on the left, click **Customise**.
2. Click **Connectors**.
3. Click in the **search box** and type the connector's name (for example `vidIQ`).
4. Click it in the list, then click **Connect**.
5. A new tab opens and asks you to sign in to that service. Sign in, or click **Sign up** if you don't have an account yet (it's free to start).
6. Click **Allow** (or **Authorize**). The tab closes and you're back in Claude.
7. The connector now says **Connected**.

Notes for some connectors:
- **GitHub:** after **Authorize**, GitHub may show **Install Claude**. Click your username, click **Only select repositories**, pick **reel-maker** (you make it in Part 4, so come back and do this step after Part 4), then click **Install**.
- **Eden:** connecting is free, but reading reels needs **Eden Discover**. To upgrade: go to **app.eden.so**, click **Settings** (bottom left), click **Billing**, then choose **Discover**. Skip this if you're happy with the free backup.
- **vidIQ:** if it asks you to connect a YouTube channel, click **Skip**. Reels research doesn't need one.

✅ **Done when:** Customise > Connectors shows all six as **Connected**.

---

## Part 4. Make your copy of the tool (15 minutes)

### 4A. Copy the tool
1. Go to **github.com/heytherejenae-afk/reel-maker**.
2. Click the green **Use this template** button, then click **Create a new repository**.
3. **Repository name:** type `reel-maker`. Click **Private**.
4. Click **Create repository**.
5. Go back to Part 3 and finish the **GitHub** note (pick **reel-maker**, click **Install**).

✅ **Done when:** the address bar shows `github.com/YOUR-USERNAME/reel-maker`.

### 4B. Make a Claude project
1. Go to **claude.ai**. Under the big typing box, click **Project ⌄**.
2. Click **+ New project**.
3. **Name:** type `Reel creator`. **Goal:** type `Make reels from idea to finished video`.
4. Next to **Context**, click **+**, click **Add repository**, then click **reel-maker**.
5. Click **Create project**.

### 4C. Add the settings
1. In your new project, click **⋯** (top right), then **Settings**.
2. Click **Environment** (on the left).
3. Next to **Cloud environment**, click **Select a cloud environment ⌄**, then **+ Add cloud environment**.
4. **Name:** type `Reel creator`.
5. Click **Network access**. Leave it on **Limited**. Click in the **Allowed domains** box and paste these 8 lines:
   ```
   drive.google.com
   drive.usercontent.google.com
   huggingface.co
   *.huggingface.co
   *.hf.co
   incompetech.com
   storage.googleapis.com
   raw.githubusercontent.com
   ```
   Leave **Allow package managers** ticked. Click the **<** arrow (top left) to go back.
6. Click **Setup script**. Open `setup.sh` in your reel-maker repository on GitHub, click the **Copy raw file** button (two squares, top right of the file), click in the Setup script box and paste.
7. Click **Add environment**. Check that **Cloud environment** says **Reel creator**. Click **X** to close.

✅ **Done when:** your project's settings show the **reel-maker** repository and the **Reel creator** environment.

Setup is finished. You never need to do Parts 1 to 4 again.

---

## Part 5. Make a reel (your phone is fine)

1. Open the **Claude** app (or claude.ai in Chrome). Under the typing box, tap **Project ⌄**, then tap **Reel creator**.
2. Type **Make a reel** and send it.
3. Claude asks where you're starting from: **I need an idea**, **I have an idea**, **I have a script and clips** or **I have a finished reel**. Tap one.
4. Answer each question by tapping a box, or say **you choose**.

**For the first edit (stage 6),** put your clips in a Google Drive folder and share it:
1. Open the **Google Drive** app. Tap **+ New**, then **Folder**. Name it and tap **Create**.
2. Open the folder. Tap **+ New**, then **Upload**, and pick your clips. Wait for them to finish.
3. Go back one screen. Tap the **three dots ⋮** next to the folder, then **Share**.
4. Tap **Restricted** and change it to **Anyone with the link**. Leave it on **Viewer**.
5. Tap **Copy link**. Paste the link into Claude and send.

**Getting finished files onto your phone:** Claude puts small files (like overlay cards) in your Google Drive: in the **Drive** app, open the folder, press and hold a file, tap **⋮**, then **Download**. For big videos, Claude gives you a link: tap it, it opens in **Chrome**, and the video downloads to your phone.

---

## Using Claude Code instead (for people comfortable with it)

The tool is also a Claude Code plugin. In Claude Code, type:
```
/plugin marketplace add YOUR-USERNAME/reel-maker
/plugin install reel-creator@reel-creator
```
Then say **make a reel**. You still need the connectors from Part 3.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| "vidIQ isn't connected" | Do Part 3 for vidIQ. Or paste 3-5 reel links you've seen doing well, and Claude carries on |
| "Eden needs Discover" | Nothing. Claude uses Get Transcript instead. Upgrade Eden only if you want on-screen text too |
| "vidIQ has no credits" | Nothing. Claude searches YouTube Shorts for free instead. Credits refill each month |
| "Get Transcript free plan limit" | Nothing. Claude writes ideas from the reels' titles. Or paste the words of a reel you like into the chat |
| "I can't download your Drive folder" | In Drive, set the folder to **Anyone with the link** (Part 5, steps 3 to 5) |
| A download is blocked | Check the 8 allowed domains in Part 4C, then start a **new** chat (old chats keep old settings) |
| Can't save a file from the Claude app to your phone | Ask Claude to put it in your Google Drive, then download it from the Drive app |
