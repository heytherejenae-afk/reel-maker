# Reel maker: simple steps

## Part 1. Do this once. Use a computer. (About 15 minutes)

**Step 1. Get Claude Pro.**
Go to claude.ai. Click your name (bottom left). Click **Settings**. Click **Billing**. Click **Upgrade**. Pick **Pro**.

**Step 2. Make a GitHub account.**
Go to github.com/signup. Follow the steps. It's free.

**Step 3. Copy the tool.**
Go to github.com/heytherejenae-afk/reel-maker
Click the green button **Use this template**.
Click **Create a new repository**.
Type the name: `reel-maker`
Click **Private**.
Click **Create repository**.

**Step 4. Link Claude to GitHub.**
Go to claude.ai.
Click **Customise**. Click **Connectors**.
Search for **GitHub**. Click it. Click **Connect**.
GitHub opens. Click **Authorize**.
If it asks you to **Install**: pick **reel-maker**, then click **Install**.

**Step 5. Make a project.**
Go to claude.ai.
Under the big typing box, click **Project ⌄**.
Click **+ New project**.
Name: type `Reel maker`
Goal: type `Make reels from my video clips`
Next to **Context**, click **+**. Click **Add repository**. Click **reel-maker**.
Click **Create project**.

**Step 6. Add the settings.**
In your new project, click **⋯** (top right). Click **Settings**.
Click **Environment** (on the left).
Next to **Cloud environment**, click **Select a cloud environment ⌄**.
Click **+ Add cloud environment**.
Name: type `Reel maker`

Click **Network access**.
Leave it on **Limited**.
Click in the **Allowed domains** box. Paste these 8 lines:

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

Leave **Allow package managers** ticked.
Click the **<** arrow (top left) to go back.

Click **Setup script**.
Click in the box. Paste all of this:

```
#!/bin/bash
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg) || true
pip install -q --break-system-packages faster-whisper gdown ai-edge-litert opencv-python-headless || pip install -q faster-whisper gdown ai-edge-litert opencv-python-headless || true
node -e "require('playwright')" 2>/dev/null || (npm install -g playwright && npx playwright install --with-deps chromium) || true
python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')" || true
exit 0
```

Click **Add environment**.
Check that **Cloud environment** now says **Reel maker**.
Click **X** (top right) to close settings.

Setup is done. You never need to do Part 1 again.

## Part 2. Do this for every reel. Your phone is fine.

**Step 7. Put your clips in Google Drive.**
Open the Google Drive app. Make a folder. Put your videos in it.
Tap the **3 dots** next to the folder. Tap **Share**.
Change **Restricted** to **Anyone with the link**.
Tap **Copy link**.

**Step 8. Open your project.**
Open claude.ai (or the Claude app).
Under the typing box, tap **Project ⌄**. Tap **Reel maker**.

**Step 9. Send one message.**
Paste the link. Add one sentence about the reel.
Example: *(link) 30 second reel about what to plant in December. Fun.*

**Step 10. Answer Claude.**
Pick a look, or say `you choose`.
Look at the plan. Say `build it`.
Wait about 15 minutes. Your reel appears in the chat. Tap it to download.
