# Quickstart Guide (For Non-Technical Users)

This guide is for daily operations — pausing the bots, checking on them, and handling alerts. No coding required.

---

## What You Need

- A web browser
- Access to the GitHub repo: https://github.com/aicodepathways/crypto-yall
- Access to the dashboard: https://crypto-yall-8s3evlspcczux5ztdmat9e.streamlit.app/
- Email and Telegram set up for alerts (already done if you've been getting notifications)

---

## How to Check on the Bots

### Option 1: The Dashboard (recommended for daily checks)

1. Open https://crypto-yall-8s3evlspcczux5ztdmat9e.streamlit.app/
2. Scroll down past the "Live Market Status" cards
3. You'll see three sections:
   - **Live Trading (Hyperliquid)** — Daily bot
   - **Intraday Trading (1h)** — Intraday Standard bot
   - **Aggressive Trading (30m)** — Aggressive bot
4. Each section shows:
   - **Status:** ACTIVE (green) or PAUSED (red)
   - **Account equity:** current value
   - **Open positions:** what the bot is currently holding
   - **Recent trades:** last 20-25 trades

**If you don't see those sections**, the dashboard config needs the Gist secrets re-added — contact Brendan.

### Option 2: Email and Telegram alerts

You already get notifications whenever a bot places a trade. These are the real-time pulse of the system. If you stop getting them for over 24 hours, something might be wrong.

### Option 3: Hyperliquid directly

The authoritative source of truth for actual positions and PnL:

1. Visit https://app.hyperliquid.xyz (or testnet equivalent)
2. Connect the wallet (Josh's Coinbase wallet)
3. See all open positions across all bots

---

## How to Pause a Bot

You might want to pause a bot if:
- The market is doing something extreme
- You're going on vacation and want to be cautious
- A bot is behaving oddly and you want to investigate

### Step-by-step (uses GitHub web UI — no coding)

1. Go to https://github.com/aicodepathways/crypto-yall/settings/variables/actions
2. You'll see a list of "Variables" — these control the bots' settings
3. Find the kill switch you want to flip:
   - **KILL_SWITCH** → controls the Daily bot
   - **INTRADAY_KILL_SWITCH** → controls the Intraday Standard bot
   - **AGGRESSIVE_KILL_SWITCH** → controls the Aggressive bot
4. Click the pencil icon next to the variable name to edit it
5. Change the value from **ON** to **OFF**
6. Click "Update variable"

The bot will skip its next scheduled run and won't place any new trades. Existing positions stay open. You'll get one email confirming the pause.

### To resume:

Same steps, but change **OFF** back to **ON**.

### To pause ALL bots at once:

Repeat the steps above for all three kill switch variables.

---

## How to Pause Everything Immediately (Emergency)

If the market is moving fast and you need to halt everything:

1. **Web UI:** Set all three kill switches to OFF (steps above)
2. **Manually close positions on Hyperliquid** if you want to exit existing trades
3. **Email Brendan** so he knows you intervened

**Important:** The kill switch only prevents NEW orders. To close existing positions, do it manually on https://app.hyperliquid.xyz.

---

## How to Change the Bot Capital Allocation

If you want to give a bot more or less money to play with:

1. Go to https://github.com/aicodepathways/crypto-yall/settings/variables/actions
2. Find the capital variable:
   - **SEGREGATED_CAPITAL** → Daily bot (currently $10,000 on testnet)
   - **INTRADAY_CAPITAL** → Intraday Standard (currently $5,000)
   - **AGGRESSIVE_CAPITAL** → Aggressive bot (currently $3,000)
3. Edit, change the number, save

**Important caveat:** This is just an accounting variable. The actual money is in the Hyperliquid account. Changing this number affects how big each trade is (1% of this value per trade), not how much actual money the bot can spend. If you set it to $50,000 but the Hyperliquid account only has $1,000, you'd quickly hit margin limits.

---

## Understanding the Alerts

Each email and Telegram alert tells you:

- **Asset** (BTC, ETH, SOL, etc.)
- **Action**:
  - `BUY` / `open_long` — opened a long position
  - `ENTER SHORT` / `open_short` — opened a short position
  - `SELL / EXIT` / `close` — closed an existing position
  - `HOLD LONG` / `HOLD SHORT` — keeping the current position open
- **Mode** (Standard or Aggressive)
- **Regime** (Bull, Bear, or Chop) and confidence
- **Price** at the time of the alert
- **Previous action** (what was it before this change)

You don't need to do anything on these alerts. They're informational. The bot has already placed the trade.

---

## What to Do If You Don't Get Alerts for a Long Time

### Possible causes:

1. **The market hasn't done anything significant** — quiet markets = quiet alerts. This is normal and good.
2. **A bot is paused** — check the kill switch variables
3. **Email going to spam** — check your spam folder, mark as "not spam"
4. **Telegram bot was blocked or deleted** — open https://t.me/Crypto_yall_bot and message it again
5. **GitHub Actions stopped running** — only happens if the repo got disabled or out of free credits. Contact Brendan.

### To check if the bots are still running:

1. Go to https://github.com/aicodepathways/crypto-yall/actions
2. Look at the "Execute Aggressive" workflow — it runs every 30 minutes, so the most recent run should be within the last hour
3. Look at "Execute Intraday" — runs hourly
4. Look at "Execute Trades" — runs daily at ~00:15 UTC (might show as 4 hours later due to GitHub delays)

Green checkmarks ✓ = healthy. Red X = something broke; contact Brendan.

---

## What to Do If You Get an "Error" or "Failed" Email

The system sends error emails when:
- The Hyperliquid API rejected an order
- The drawdown limit was hit (auto-pause)
- The kill switch was flipped to OFF

Most errors self-recover on the next scheduled run. Only worry if:
- You get the same error 3+ times in a row
- The error mentions "API wallet" — could mean key rotated or de-authorized
- The error mentions "insufficient balance" — account ran out of margin

When in doubt: pause all bots and email Brendan.

---

## When to Email Brendan

- The system did something you didn't expect and you can't figure out why
- You want to change something not covered in this guide
- You want to add a new community member to the system
- You want to migrate from testnet to mainnet
- Multiple consecutive error alerts
- Major market event (regulatory action, exchange hack, etc.)

Brendan: `nocodepathways@gmail.com`

---

## Quick Reference Card

| What you want to do | How |
|---------------------|-----|
| Check current positions | https://crypto-yall-8s3evlspcczux5ztdmat9e.streamlit.app/ |
| Verify trades on exchange | https://app.hyperliquid.xyz |
| Pause Daily bot | GitHub repo → Settings → Variables → KILL_SWITCH = OFF |
| Pause Intraday Standard | INTRADAY_KILL_SWITCH = OFF |
| Pause Aggressive | AGGRESSIVE_KILL_SWITCH = OFF |
| Resume any bot | Change OFF back to ON |
| Check if bots are running | https://github.com/aicodepathways/crypto-yall/actions |
| See trade history | Dashboard → bot section → "Recent Trades" |
