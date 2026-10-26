# Reel maker: simple steps

## Do this once. Use a computer.

**1. Get Claude Pro.**
Go to claude.ai. Click your name (bottom left). Click Settings. Click Billing. Click Upgrade. Pick Pro.

**2. Make a GitHub account.**
Go to github.com/signup. Follow the steps. It's free.

**3. Copy the tool.**
Go to github.com/heytherejenae-afk/reel-maker.
Click the green button **Use this template**.
Click **Create a new repository**.
Type the name: `reel-maker`
Click **Private**.
Click **Create repository**.

**4. Link Claude to GitHub.**
Go to claude.ai. Click **Customise**. Click **Connectors**.
Search for **GitHub**. Click it, then click **Connect**.
GitHub opens. Click **Authorize**.
If it says **Install**: click **Only select repositories**, pick **reel-maker**, click **Install**.

**5. Add the settings.**
Go to claude.ai/code (type it in the address bar at the top of the browser).
In the middle of the page there is a big box where you type a message to Claude. That's the typing box.
Just below it is a row of small buttons. One of them says **Default**. Click it.
Click **New environment**.
Name: type `Reel maker`
Network access: pick **Custom**. Paste these 6 lines in the box:

```
drive.google.com
drive.usercontent.google.com
huggingface.co
*.huggingface.co
*.hf.co
incompetech.com
```

Tick the box that says **Also include default list**.
Setup script: open this link in a new tab:
raw.githubusercontent.com/heytherejenae-afk/reel-maker/main/setup.sh
Copy all the text. Paste it into the Setup script box.
Click **Add environment**.

Setup is done.

## Do this for every reel. Your phone is fine.

**6. Put your clips in Google Drive.**
Make a folder. Put your videos in it.
Tap the 3 dots next to the folder. Tap **Share**.
Change **Restricted** to **Anyone with the link**.
Tap **Copy link**.

**7. Open claude.ai/code.**
Check it says **reel-maker** and **Reel maker** under the typing box.

**8. Send one message.**
Paste the link. Add one sentence about the reel.
Example: *(link) 30 second reel about what to plant in December. Fun.*

**9. Answer Claude.**
Pick a look, or say `you choose`.
Look at the plan. Say `build it`.

**10. Get your reel.**
Wait about 15 minutes.
Tap the link Claude gives you. The video downloads to your phone.
