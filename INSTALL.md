# Reel Creator: install guide

Reel Creator takes you from "I need an idea" to a finished reel, in 7 stages:
**ideas → transcribe winning reels → script → brand → overlays → first edit → CapCut or Edits.**
You can start at any stage.

Do Parts 1 to 4 **once, on a computer**, in the **Chrome** browser. It takes about 30 minutes. You do **not** need anyone else's files: your copy of the tool starts empty, and your brand kits are saved only in your own project.
You also make your reels **on the computer** (claude.ai in Chrome). You only need your phone to film your clips and, if you use Edits, for the last step.

---

## Part 1. What you need and what it costs

| You need | What it does | Cost |
|---|---|---|
| **Claude Pro** (or Max) | Runs the whole tool | US$20 a month (US$17 a month if you pay yearly) |
| **GitHub** account | Holds your copy of the tool | Free |
| **Google Drive** | Where you put your video clips | Free |
| **Google Drive connector** | Lets Claude save your brand kit and small files to your Drive | Free |
| **Canva connector** | Makes your overlay pages (stage 5) | Free Canva works. Canva Pro (about US$15 a month) adds your own brand kit and fonts. *Optional:* the tool has 6 built-in overlay styles too |
| **vidIQ connector** | Finds reels doing far better than usual in your niche (stage 1) | Free plan: 150 credits a month. One search uses 5 credits, so about 30 searches a month. Boost: US$19 a month for 2,000 credits |
| **Eden connector** | Reads the words and on-screen text of those reels (stage 2) | Needs **Eden Discover**, US$5 a month. *Optional:* the free Get Transcript connector is the backup |
| **Get Transcript connector** | Backup for stage 2 (spoken words only) | Only **2 free videos in total**, then a paid plan (from about US$5 a month). *Optional:* without it, ideas still work from the reels' titles |
| **CapCut** (computer or phone) or **Edits** (phone) | Final polish (stage 7) | Free |

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

Do these steps once for **each** of these 5 connectors:
**Google Drive, Canva, vidIQ, Eden, Get Transcript.** (GitHub is different: it's in Part 4B.)

1. In Chrome, go to **claude.ai/customize/connectors**. You see a list called **Connectors**.
   (Or: on claude.ai, click **Customise** in the menu on the left, then **Connectors**.)
2. Click in the **search box** and type the connector's name (for example `vidIQ`).
3. Click it in the list, then click **Connect**.
4. A new tab opens and asks you to sign in to that service. Sign in, or click **Sign up** if you don't have an account yet.
5. Click **Allow** (or **Authorize**). The tab closes and you're back in Claude.
6. The connector now says **Connected**.

Notes for some connectors:
- **Eden:** connecting is free, but reading reels needs **Eden Discover**. To upgrade: go to **app.eden.so**, click **Settings** (bottom left), click **Billing**, then choose **Discover**. Skip this if you're happy with the free backup.
- **vidIQ:** if it asks you to connect a YouTube channel, click **Skip**. Reels research doesn't need one.
- Only **Google Drive** and **Canva** really matter for a first try. The others make the ideas stage better and can be added later.

✅ **Done when:** the Connectors page shows the ones you chose as **Connected**.

---

## Part 4. Make your copy of the tool (15 minutes)

### 4A. Copy the tool
1. Go to **github.com/heytherejenae-afk/reel-maker** (sign in to GitHub first if it asks).
2. Click the green **Use this template** button (top right, above the list of files), then click **Create a new repository**.
3. Under **Owner**, leave your own username. **Repository name:** type `reel-maker`. Click **Private**.
4. Click the green **Create repository** button. Wait about 10 seconds.

✅ **Done when:** the address bar shows `github.com/YOUR-USERNAME/reel-maker` and you see folders called **skills** and **docs**.

### 4B. Let Claude open your copy
1. In Chrome, go to **claude.ai/connect-github**.
2. GitHub asks you to authorise Claude. Click the green **Authorize** button.
3. If GitHub then shows **Install Claude**: click your **username**, click **Only select repositories**, click **Select repositories**, type `reel-maker` and click it, then click **Install**.
4. You land back on claude.ai.

✅ **Done when:** in the next step, **reel-maker** shows in the list of repositories.
If it doesn't: go to **github.com/settings/installations**, click **Configure** next to **Claude**, add **reel-maker** under **Only select repositories**, and click **Save**.

### 4C. Make a Claude project
1. In Chrome, go to **claude.ai/code**. Under the big typing box, click **Project ⌄**.
2. Click **+ New project**.
3. **Name:** type `Reel creator`. **Goal:** type `Make reels from idea to finished video`.
4. Next to **Context**, click **+**, click **Add repository**, then click **YOUR-USERNAME/reel-maker** (your copy, not Jenae's).
5. Click **Create project**.

### 4D. Add the settings
1. In your new project, click **⋯** (top right), then **Settings**.
2. Click **Environment** (on the left).
3. Next to **Cloud environment**, click **Select a cloud environment ⌄**, then **+ Add cloud environment**.
4. **Name:** type `Reel creator`.
5. Click **Network access** and choose **Full**. Click the **<** arrow (top left) to go back.
   *Why Full:* the tool fetches your Google Drive clips, your Canva overlay downloads, fonts, music and reel links from Instagram and YouTube. Those come from many different web addresses, and the tool has only been tested with Full.
   *Prefer Limited?* Choose **Limited**, leave **Allow package managers** ticked, and paste these lines into **Allowed domains**. Canva, Instagram and YouTube links may still be blocked; if Claude names another address, add it here and start a new chat.
   ```
   drive.google.com
   drive.usercontent.google.com
   huggingface.co
   *.huggingface.co
   *.hf.co
   incompetech.com
   storage.googleapis.com
   raw.githubusercontent.com
   *.canva.com
   *.instagram.com
   *.cdninstagram.com
   *.fbcdn.net
   *.youtube.com
   ```
6. Click **Setup script**. In a new tab, open your copy on GitHub (`github.com/YOUR-USERNAME/reel-maker`), click **setup.sh** in the file list, then click the **Copy raw file** button (two overlapping squares, top right of the file). Go back to the settings tab, click in the **Setup script** box and press **Ctrl+V** (Windows) or **Cmd+V** (Mac) to paste.
7. Click **Add environment**. Check that **Cloud environment** now says **Reel creator**. Click **X** to close.

✅ **Done when:** your project's settings show your **reel-maker** repository and the **Reel creator** environment.

### 4E. Check it works (2 minutes)
1. In your **Reel creator** project, type **Make a reel** and send it.
2. The first time, it takes a minute or two to get ready (the setup script is running).
3. Claude replies with a link to **your own Brand Kit page**. Click it, fill it in, click **Copy my brand kit**, come back to the chat, paste and send.
4. Claude says it saved your brand. Next time you say **Make a reel**, it lists your brand by name and doesn't ask again.

If Claude doesn't mention a Brand Kit, or says it can't find the tool, check that 4C step 4 picked **your** reel-maker, then start a new chat in the project.

Setup is finished. You never need to do Parts 1 to 4 again.
**Changed a setting or added a connector later?** Start a **new** chat. Chats that are already open keep the old settings.

---

## Part 5. Make a reel (on your computer)

1. On your computer, open **Chrome** and go to **claude.ai**. Click **Projects** on the left, then click **Reel creator**.
2. Type **Make a reel** and send it.
3. Claude asks where you're starting from: **I need an idea**, **I have an idea**, **I have a script and clips** or **I have a finished reel**. Tap one.
4. Answer each question by tapping a box, or say **you choose**.

**For the first edit (stage 6),** put your clips in a Google Drive folder and share it (do this on your phone, where your clips are):
1. Open the **Google Drive** app. Tap **+ New**, then **Folder**. Name it and tap **Create**.
2. Open the folder. Tap **+ New**, then **Upload**, and pick your clips. Wait for them to finish.
3. Go back one screen. Tap the **three dots ⋮** next to the folder, then **Share**.
4. Tap **Restricted** and change it to **Anyone with the link**. Leave it on **Viewer**.
5. Tap **Copy link**. Paste the link into Claude and send.

**Getting your finished reel:** in the chat, click each file under Claude's message, then click **Download**. It saves to your computer's **Downloads** folder, ready to post or open in CapCut on your computer.

**Finishing in Edits (a phone app)?** On your phone, open the **Claude** app, go to the same chat, tap each file under Claude's message, then tap **Download**. The files save to your phone and Edits can use them.
Claude's Edits steps walk you through the rest.

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
| A download is blocked | In Part 4D, set **Network access** to **Full** (or add the address Claude names), then start a **new** chat (old chats keep old settings) |
| Can't save a file in the Claude phone app | Use a computer: open claude.ai in Chrome, click the file, then **Download** |
