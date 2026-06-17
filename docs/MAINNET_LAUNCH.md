# Mainnet Launch Guide

This guide walks through moving the bots from testnet (fake money) to mainnet (real money). This is a significant step. Read the whole thing before doing anything.

---

## What "Mainnet" Means

Right now, the bots run on **Hyperliquid testnet** — a practice version of the exchange with fake USDC. Every trade is real (real orders, real fills, real PnL calculations) but the money is mock.

**Mainnet** = the actual Hyperliquid exchange with real USDC. Real money in, real money out.

**One variable change** flips the system from testnet to mainnet. But that's the LAST step. Many other things need to happen first.

---

## Before You Even Consider Mainnet

Make sure you can honestly answer "yes" to all of these:

- [ ] The bots have been running on testnet for at least 6 weeks
- [ ] You've watched at least 2 different market conditions (chop + trend, ideally both directions)
- [ ] You've received and understand many trade alerts
- [ ] You've successfully paused and resumed a bot using the kill switch
- [ ] You understand the difference between the three bots (Daily, Intraday, Aggressive)
- [ ] You understand the worst-case scenario (account drained by leverage + bad trade)
- [ ] You've discussed the legal/tax implications with someone qualified (US clients: at minimum a CPA)
- [ ] You have an actual amount of money you're prepared to lose entirely

If any of those are "no," wait. Mainnet can wait.

---

## The Pre-Launch Checklist

Each item below has its own section further down. Don't skip any.

- [ ] **Step 1:** Decide on starting capital amounts (small for first week)
- [ ] **Step 2:** Create Hyperliquid sub-accounts (one per bot) — strongly recommended
- [ ] **Step 3:** Authorize API wallets on mainnet
- [ ] **Step 4:** Bridge real USDC to each sub-account
- [ ] **Step 5:** Tighten safety parameters
- [ ] **Step 6:** Reset bot state Gists to fresh
- [ ] **Step 7:** Run a test trade on mainnet
- [ ] **Step 8:** Flip the testnet flag
- [ ] **Step 9:** Watch first 10 runs manually
- [ ] **Step 10:** Slowly scale up

---

## Step 1: Decide on Starting Capital

The bots are currently sized for testnet ($10k / $5k / $3k). For mainnet week 1, go **much smaller**.

**Recommended starting amounts:**

| Bot | Recommended Capital |
|-----|---------------------|
| Daily | $500 - $1,000 |
| Intraday Standard | $300 - $500 |
| Aggressive | $200 - $300 |
| **Total starting** | **$1,000 - $1,800** |

This is the amount you'd be **comfortable losing entirely**. If something goes wrong, this is the worst case.

**Why so small?**
- Real fills behave slightly differently from testnet (slippage, fees, partial fills)
- The shared-account issue (without sub-accounts) is more visible at small scale
- You learn how the bot actually behaves with real money
- Smaller positions = smaller potential losses while you're verifying

Scale up only after the system runs cleanly for at least a week.

---

## Step 2: Create Hyperliquid Sub-Accounts

**Strongly recommended.** Without this, all three bots share the same Hyperliquid account, which means they can net against each other on the exchange. With sub-accounts, each bot has its own isolated margin account.

### How (Josh needs to do this himself in his Hyperliquid UI):

1. Open https://app.hyperliquid.xyz/portfolio
2. Connect Josh's main Coinbase wallet
3. Look for "Sub-accounts" section
4. Click "Create sub-account"
5. Create 3 sub-accounts:
   - Name: `Crypto Yall Daily`
   - Name: `Crypto Yall Intraday`
   - Name: `Crypto Yall Aggressive`
6. Each sub-account gets its own address (looks like `0xabc...`). Save these addresses.

### Then send Brendan a list of all 3 sub-account addresses.

Brendan will need to update the bot code to use the right sub-account per bot. **This is not yet done in the current code.** It's a 30-60 minute code change he'll handle.

---

## Step 3: Authorize API Wallets on Mainnet

Testnet and mainnet are separate environments. The API wallet that's already authorized on testnet needs to be authorized again on mainnet.

For each of the 3 sub-accounts:

1. Open the sub-account on https://app.hyperliquid.xyz
2. Go to https://app.hyperliquid.xyz/API
3. Click "Generate" or "Authorize Existing API Wallet"
4. Use the same API wallet address that's currently in the GitHub secret `HL_PRIVATE_KEY`. OR generate fresh ones for each sub-account (more secure).
5. Sign the authorization transaction (small gas fee)
6. Note which API wallet is authorized for which sub-account

Send Brendan: the private key + sub-account address for each of the 3 bots.

**If you generate fresh API wallets per sub-account:**
- You'll have 3 different private keys
- Each is only authorized for its specific sub-account
- Safer if any one key leaks

---

## Step 4: Bridge USDC to Hyperliquid

Real money in.

1. Open https://app.hyperliquid.xyz/deposit
2. Choose Arbitrum as the source (cheapest gas)
3. Send USDC from Josh's source wallet (Coinbase, Metamask, etc.) to the Hyperliquid bridge
4. Wait 1-2 minutes for confirmation
5. **Distribute to each sub-account:**
   - Send $X to the Daily sub-account
   - Send $Y to the Intraday sub-account
   - Send $Z to the Aggressive sub-account

Use the recommended starting amounts from Step 1.

---

## Step 5: Tighten Safety Parameters

For mainnet, tighten the drawdown thresholds. Real money should have tighter guardrails.

### Recommended mainnet settings:

Go to https://github.com/aicodepathways/crypto-yall/settings/variables/actions and update:

| Variable | Testnet value | Mainnet value |
|----------|---------------|---------------|
| `DAILY_DD_PCT` | 5 | **3** |
| `INTRADAY_DD_PCT` | 5 | **3** |
| `AGGRESSIVE_DD_PCT` | 3 | **2** |

Update the capital variables to match what you actually bridged:

| Variable | Set to actual USDC amount |
|----------|---------------------------|
| `SEGREGATED_CAPITAL` | $500-$1000 |
| `INTRADAY_CAPITAL` | $300-$500 |
| `AGGRESSIVE_CAPITAL` | $200-$300 |

---

## Step 6: Reset Bot State Gists

The bots remember what positions they "own." But those memories are from testnet. Before mainnet, wipe them so the bots start fresh.

**Important:** This will erase the testnet trade history. Make sure you've exported or noted anything important first.

Brendan needs to do this part (involves Gist API). Tell him: "Ready to reset state for mainnet."

He'll run something like:
```
gh gist edit <DAILY_GIST> -f trading_state.json - <<< '{}'
gh gist edit <INTRADAY_GIST> -f intraday_state.json - <<< '{}'
gh gist edit <AGGRESSIVE_GIST> -f aggressive_state.json - <<< '{}'
```

---

## Step 7: Run a Test Trade on Mainnet (Critical)

Before letting the real bots run, do a manual test trade with a tiny amount.

### How (Brendan does this part):

1. Update HL_TESTNET to false temporarily
2. Trigger the `test-trade.yml` workflow
3. It places a $10 BTC trade and immediately closes it
4. Verifies authentication, order placement, fills, and close all work on mainnet
5. Total expected loss: $0.01-$0.05 in slippage + Hyperliquid fees

If this fails, **do not proceed**. There's a real bug that needs fixing first.

---

## Step 8: Flip the Testnet Flag

This is the actual go-live moment.

1. Go to https://github.com/aicodepathways/crypto-yall/settings/variables/actions
2. Find `HL_TESTNET`
3. Change from `true` to `false`
4. Save

**The bots are now live with real money.** Next scheduled run will place real trades.

---

## Step 9: Watch the First 10 Runs Manually

For the first day:

1. After each scheduled bot run (Aggressive every 30 min, Intraday every hour, Daily once daily), check:
   - Did you get an alert? ✓
   - Does the alert match what shows on the dashboard? ✓
   - Does the dashboard match what shows on Hyperliquid? ✓
   - Are the fill prices reasonable?

2. If you see ANY discrepancy:
   - Pause all bots (kill switches OFF)
   - Don't try to fix it yourself
   - Email Brendan immediately

3. After ~10 clean runs across all three bots, you can relax monitoring.

---

## Step 10: Slowly Scale Up

After **at least 1 week** of clean mainnet operation:

- Bridge more USDC into the sub-accounts
- Update the capital variables to match
- Watch for another week
- Repeat

**Never scale up after a single good day.** A single profitable day isn't validation.

**Recommended scaling schedule:**

| Week | Capital per bot |
|------|-----------------|
| Week 1 | $300-$1000 each |
| Week 2 | If clean, scale up to 2x |
| Week 3-4 | If still clean, scale up to 5x |
| Month 2 | If still clean, target allocation |

Total commitment over 4 weeks: only as much as you'd be willing to lose entirely.

---

## What to Do If Something Goes Wrong on Mainnet

### Mild problem (one weird trade)

- Note what happened
- Email Brendan
- Don't change anything yet

### Moderate problem (recurring errors)

- Pause the specific bot affected
- Email Brendan
- Wait for response before resuming

### Severe problem (unexpected loss, big position, account drained)

1. **Immediately:** Pause ALL bots (all three kill switches to OFF)
2. **Immediately:** Open Hyperliquid and assess actual positions
3. **If positions are running away:** Manually close them on Hyperliquid
4. **Then:** Email Brendan with screenshots of everything
5. **Don't try to "trade out" of a bad situation yourself**

---

## Rolling Back to Testnet

If at any point you want to step back from live trading:

1. Pause all bots (kill switches OFF)
2. Manually close any open mainnet positions on Hyperliquid
3. Optionally withdraw the USDC back to Josh's main wallet
4. Flip `HL_TESTNET` back to `true`
5. Resume bots (kill switches ON)

You're now back on testnet with no real money at risk.

---

## Cost Awareness

### Hyperliquid fees (small but real)

- Maker: 0.01% per trade
- Taker: 0.035% per trade (the bots use market orders, so this is what you pay)
- Funding rates on perpetuals (paid every 8 hours, varies per asset)

On 50 trades per week with $1k capital:
- 50 × $1000 × 1% × 0.035% = ~$1.75/week in fees

This is small but not zero. Over a year of active trading, fees add up.

### GitHub Actions cost

Free for now. Aggressive bot runs 48 times per day = ~22 minutes of compute per day per workflow. Well within free tier.

If usage grows (community members, more bots), this might need a paid plan.

### Streamlit Cloud cost

Free.

### Total monthly cost at current scale: ~$0 outside of trading fees.

---

## Tax and Legal Notice

This guide is operational, not legal advice. **Talk to a CPA / tax professional before trading at meaningful size.**

In the US:
- Every closed trade is a taxable event
- Short-term capital gains (under 1 year) are taxed as ordinary income
- Wash sale rules may or may not apply to crypto depending on classification
- The IRS gets reports from major exchanges
- The bot runs hundreds of trades — that's hundreds of tax events

You will likely need crypto tax software (Koinly, CoinTracker, etc.) to make this manageable at tax time. Set this up before going live.

---

## Summary

Mainnet is one variable flip away. But the preparation is everything:

1. **Sub-accounts** — separate the three bots' margin
2. **Small capital** — start with $1-2k total
3. **Tighter guardrails** — 3% DD halt instead of 5%
4. **Manual verification** — watch the first 10 runs
5. **Slow scaling** — weeks, not days
6. **Tax planning** — get set up before going live

If you've done all of that honestly, you're ready. If you've skipped steps, don't.

When ready: email Brendan and say "Ready to go to mainnet, completed the checklist." He'll do the technical pieces (sub-account code changes, test trade verification) and walk you through the flip.

---

## Final Reminder

The bots have a track record on testnet. Testnet is not mainnet.

Real money introduces:
- Real slippage
- Real fees
- Real emotions
- Real consequences

Take it slow. There's no urgency. The strategies will work next month as well as this month.
