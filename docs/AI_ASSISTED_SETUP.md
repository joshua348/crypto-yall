# AI-Assisted Setup

Don't want to read the full setup guide? Use an AI assistant (ChatGPT, Claude, Gemini, etc.) to walk you through it step-by-step.

---

## How It Works

1. Open ChatGPT (https://chat.openai.com) or Claude (https://claude.ai) — both have free tiers
2. Copy the prompt below
3. Paste it into the chat
4. Follow the AI's instructions
5. Ask questions whenever you get stuck

The AI will ask you for one piece of information at a time, walk you through each setup step, and help debug if anything goes wrong.

---

## The Setup Prompt (Copy Everything Below)

Copy from the line `=== START COPYING ===` to `=== STOP COPYING ===` and paste into ChatGPT or Claude.

```
=== START COPYING ===

I want to set up my own personal copy of the Crypto Y'all trading bot. The repo is at https://github.com/aicodepathways/crypto-yall. I am NOT a developer. Please walk me through the setup ONE STEP AT A TIME. After each step, wait for me to confirm I completed it before moving to the next.

Important rules for you:
1. Ask me for one thing at a time. Don't dump a wall of instructions.
2. After each step, say "Done? Reply 'done' or paste me the result before we move on."
3. If a step has me copy a value (a key, a token, an ID), explicitly remind me to save it.
4. If I tell you a step failed, help me debug before continuing.
5. Be patient. Some of these steps require navigating crypto exchanges and GitHub which I may not be familiar with.
6. NEVER ask me to share private keys, passwords, or tokens with you. Tell me to save them to my notes, not paste them to you.

Here's what we're setting up:
- A forked GitHub repo of the bot code
- 3 trading bots (daily, intraday, aggressive) running on my own Hyperliquid testnet account
- Email alerts via my own Gmail
- Optional Telegram alerts via a bot I'll create
- 4 GitHub Gists for state storage
- ~12 GitHub Secrets and ~13 GitHub Variables configured

The setup has these phases:
1. Fork the GitHub repo and enable Actions
2. Set up Hyperliquid (connect wallet, $5 mainnet activation, claim testnet faucet, generate API wallet on testnet)
3. Create a GitHub personal access token + 4 private Gists for state
4. Set up Gmail app password
5. (Optional) Create a Telegram bot and get my chat ID
6. Add all secrets and variables to my forked repo
7. Run a test trade to verify everything works
8. Trigger each of the 3 bots manually to confirm they run

Start with phase 1, step 1. Wait for my confirmation between each step. Let's go.

=== STOP COPYING ===
```

---

## What to Expect

The AI will:

1. **Ask if you have a GitHub account.** Help you sign up if needed.
2. **Walk you through forking the repo.** Click by click.
3. **Pause and wait** for you to say "done" before moving on.
4. **Ask you for the result of each step.** For example, after you create a Gist, it'll ask you to paste the Gist URL so it can extract the ID.
5. **Remind you to save important values** (private keys, tokens, app passwords) to your own notes.
6. **Debug with you** if something fails. You can paste error messages and it'll help.

A typical conversation looks like this:

> **You:** *(paste the prompt)*
>
> **AI:** Great, let's start. First, do you already have a GitHub account, or do you need to create one?
>
> **You:** I have one
>
> **AI:** Perfect. Step 1: visit https://github.com/aicodepathways/crypto-yall and click the "Fork" button in the top right. Done? Reply 'done' when you've forked the repo.
>
> **You:** done
>
> **AI:** Step 2: in your forked repo, click the "Actions" tab. You'll see a yellow banner. Click the green button that says "I understand my workflows, go ahead and enable them." Done?
>
> *... and so on*

---

## Security Notes

When using an AI assistant for setup, follow these rules:

### Things you CAN share with the AI:
- Your GitHub username
- Public Gist URLs (so it can extract the ID)
- Your Hyperliquid main wallet address (it's public on the blockchain anyway)
- Error messages from failed steps
- Screenshots of confusing UI

### Things you should NEVER share with the AI:
- **Private keys** (API wallet private key, your main wallet seed phrase)
- **Passwords** (Gmail password, anything else)
- **API tokens** (GitHub PAT, Telegram bot token, Gmail app password)
- **Anything labeled "secret"**

The AI should never ask for these. If it does, the prompt is being misused — refuse and re-paste the original prompt.

The reason: any private value you paste into an AI chat could theoretically be logged, leaked, or seen by support staff at the AI company. There's no reason the AI needs these to help you — it just needs to know where to put them in the GitHub settings page.

### How to handle "secret" values:

When the AI says something like "now go add `HL_PRIVATE_KEY` to your GitHub Secrets":

1. You go to the GitHub Secrets page
2. You paste the value directly into GitHub (NOT into the chat)
3. You tell the AI "done" without showing it the value
4. The AI moves on

---

## What If the AI Gets Something Wrong?

AI assistants are great at walking through this kind of setup, but they can occasionally hallucinate details (especially around Hyperliquid UI specifics, which change over time).

If the AI tells you something that doesn't match what you see, or if a step fails:

1. **Don't panic.** Most issues are easy to fix.
2. **Refer to [USER_SETUP_GUIDE.md](USER_SETUP_GUIDE.md)** — the authoritative manual version of this guide
3. **Tell the AI what you actually see** — paste error messages, describe the screen
4. **If you're really stuck**, contact Josh or the original developer with:
   - Which step failed
   - Your AI conversation history
   - Any error messages

---

## Tips for Better Results

### Be specific when stuck

Instead of: "it didn't work"

Try: "I clicked Run Workflow and got this error in the logs: 'private key must be exactly 32 bytes'. Here's a screenshot."

### Verify critical values

After the setup is done, double-check these by hand:
- All 12 GitHub Secrets are present (count them at https://github.com/your-username/crypto-yall/settings/secrets/actions)
- All 13 GitHub Variables are present (at https://github.com/your-username/crypto-yall/settings/variables/actions)
- The test trade workflow ran successfully (at your Actions tab)

### Use the same AI thread throughout

Don't start over partway through. The AI remembers what you've already done. Stay in the same chat from start to finish.

### Don't multitask

If you start the setup, finish the setup. Pausing for a few hours and coming back tends to make the AI lose context and re-ask questions.

---

## After Setup is Complete

Once you've finished the AI-guided setup:

1. **Save the AI conversation** — it's a useful reference if something breaks later
2. **Bookmark these URLs:**
   - Your forked repo: `https://github.com/<your-username>/crypto-yall`
   - Your Actions tab: `https://github.com/<your-username>/crypto-yall/actions`
   - Your Secrets: `https://github.com/<your-username>/crypto-yall/settings/secrets/actions`
   - Your Variables: `https://github.com/<your-username>/crypto-yall/settings/variables/actions`
3. **Read [QUICKSTART.md](QUICKSTART.md)** — the daily operations guide
4. **Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — for when issues come up later

---

## Sample Follow-Up Prompts

Once setup is done, you can keep using the AI for ongoing operations. Some useful prompts:

### "My bot stopped sending alerts. Help me debug."

Just paste that into a new chat with the AI and describe what you're seeing.

### "I want to pause the Aggressive bot for the weekend."

The AI can walk you through which variable to change.

### "I'm ready to go from testnet to mainnet. Walk me through it."

Reference [MAINNET_LAUNCH.md](MAINNET_LAUNCH.md) and ask the AI to be your guide.

### "I want to add my friend's email to the alerts list."

The AI can walk you through updating the `NOTIFY_EMAILS` secret.

---

## Frequently Asked Questions

**Q: Which AI should I use — ChatGPT or Claude?**

A: Both work. Claude tends to be slightly better at long, multi-step instructional tasks. ChatGPT is fine. Use whichever you're comfortable with.

**Q: Do I need a paid plan?**

A: No. Free tier of either should be enough for this setup.

**Q: Can I do this on my phone?**

A: Technically yes, but it's much easier on a computer because you'll be navigating GitHub UI a lot.

**Q: What if my AI conversation gets too long and the AI starts forgetting context?**

A: Summarize where you are: "We've completed Parts 1-4. We just finished setting up Gmail. Now we're starting Part 5 (Telegram)." Then continue.

**Q: Is this setup really safe?**

A: As long as you follow the security notes above (never paste private values to the AI), yes. The bot itself runs on your own GitHub account, trades only your own money, and you have full kill-switch control.

**Q: Can I skip the AI and just do it manually?**

A: Yes — [USER_SETUP_GUIDE.md](USER_SETUP_GUIDE.md) has the same content in manual click-by-click form.
