"""
aggressive_executor.py — 30-min trade executor with pyramiding.

Higher trade frequency than the standard intraday bot. Tighter stops,
tighter drawdown halt, more max positions. Operates on a completely
separate capital pool and state Gist.

Required environment variables:
    HL_PRIVATE_KEY / HL_ACCOUNT_ADDRESS / HL_TESTNET
    GIST_TOKEN / AGGRESSIVE_GIST_ID    (separate from daily & intraday Gists)
    AGGRESSIVE_CAPITAL                  (capital pool, e.g. 3000)
    AGGRESSIVE_MAX_POSITIONS            (defaults to 4)
    AGGRESSIVE_DD_PCT                   (defaults to 3 — tighter than others)
    AGGRESSIVE_KILL_SWITCH              ("OFF" halts aggressive only)
    GMAIL_USER / GMAIL_APP_PASSWORD / NOTIFY_EMAILS
    TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
"""

import json
import os
import sys
import datetime as dt

import requests

from intraday_data_loader import fetch_all_intraday, HL_SYMBOL_MAP
from aggressive_strategy import generate_aggressive_signals, classify_aggressive_signal
from hyperliquid_executor import (
    ASSETS,
    entry_size,
    execution_summary,
    get_client,
    get_account_equity,
    get_open_positions,
    get_mid_price,
    get_size_decimals,
    round_size,
    _parse_response,
    _send_email,
    _send_telegram,
)
from backtester import get_asset_profile


STATE_FILENAME = "aggressive_state.json"
POSITION_SIZE_PCT = 0.015  # 1.5% per trade — higher than standard intraday
PYRAMID_SIZE_PCT = 0.005   # 0.5% extra per pyramid add (max 2 adds)


# ── State persistence (separate Gist) ───────────────────────────────────────

def load_state() -> dict:
    gist_token = os.environ.get("GIST_TOKEN")
    gist_id = os.environ.get("AGGRESSIVE_GIST_ID")
    if not gist_token or not gist_id:
        raise RuntimeError("Aggressive state credentials are required")
    resp = requests.get(
        f"https://api.github.com/gists/{gist_id}",
        headers={"Authorization": f"token {gist_token}"},
        timeout=15,
    )
    resp.raise_for_status()
    files = resp.json().get("files", {})
    if STATE_FILENAME not in files:
        raise RuntimeError("Aggressive state file is missing; refusing to trade")
    try:
        state = json.loads(files[STATE_FILENAME]["content"])
        if not isinstance(state, dict):
            raise ValueError("Expected a state object")
        return state
    except (ValueError, TypeError, KeyError) as exc:
        raise RuntimeError("Cannot read Aggressive state; refusing to trade") from exc


def save_state(state: dict):
    gist_token = os.environ.get("GIST_TOKEN")
    gist_id = os.environ.get("AGGRESSIVE_GIST_ID")
    if not gist_token or not gist_id:
        raise RuntimeError("Aggressive state credentials are required")
    resp = requests.patch(
        f"https://api.github.com/gists/{gist_id}",
        headers={"Authorization": f"token {gist_token}"},
        json={"files": {STATE_FILENAME: {"content": json.dumps(state, indent=2)}}},
        timeout=15,
    )
    resp.raise_for_status()


def adopt_open_positions(state, positions, adoption_id):
    """One-time bookkeeping only: never place orders or change leverage."""
    if not adoption_id or state.get("position_adoption", {}).get("id") == adoption_id:
        return False
    supported = {HL_SYMBOL_MAP[t] for t in ASSETS}
    unsupported = set(positions) - supported
    if unsupported:
        raise RuntimeError(f"Cannot manage unsupported positions: {sorted(unsupported)}")
    previous = set(state.get("owned_coins", []))
    newly_owned = set(positions) - previous
    pyramids = {c: n for c, n in state.get("pyramid_state", {}).items() if c in positions}
    # Imported positions have unknown add-on history; don't add more exposure.
    for coin in newly_owned:
        pyramids[coin] = 2
    state["owned_coins"] = sorted(positions)
    state["open_positions"] = {c: dict(p) for c, p in positions.items()}
    state["pyramid_state"] = pyramids
    state["position_adoption"] = {
        "id": adoption_id,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "coins": sorted(positions),
        "newly_owned": sorted(newly_owned),
    }
    return True


# ── Signal computation ─────────────────────────────────────────────────────

def compute_aggressive_signals() -> dict:
    """Fetch 30-min candles and compute aggressive signals per asset."""
    all_data = fetch_all_intraday(list(ASSETS.keys()), interval="30m", lookback_hours=1000)
    current = {}

    for ticker in ASSETS:
        try:
            df = all_data.get(ticker)
            if df is None or df.empty or len(df) < 50:
                continue

            profile = get_asset_profile(ticker)
            sig = generate_aggressive_signals(df, allow_short=profile["allow_short"])

            last = int(sig["Signal"].iloc[-1])
            prev = int(sig["Signal"].iloc[-2]) if len(sig) >= 2 else last
            action = classify_aggressive_signal(last, prev)
            price = float(df["Close"].iloc[-1])
            osc = float(sig["TwoPole_Osc"].iloc[-1]) if "TwoPole_Osc" in sig.columns else 0.0
            pyramid = int(sig["Pyramid"].iloc[-1]) if "Pyramid" in sig.columns else 0
            prev_pyramid = int(sig["Pyramid"].iloc[-2]) if len(sig) >= 2 and "Pyramid" in sig.columns else pyramid

            current[ticker] = {
                "signal": last,
                "action": action,
                "price": price,
                "osc": osc,
                "pyramid": pyramid,
                "pyramid_added": pyramid > prev_pyramid,  # fresh pyramid this bar
            }
        except Exception as e:
            print(f"Error on {ticker}: {e}")

    return current


# ── Trade decisions ─────────────────────────────────────────────────────────

def decide_trades(signals: dict, open_positions: dict, max_positions: int,
                  pyramid_state: dict) -> list[dict]:
    """Decide trades, including pyramid adds on existing winners."""
    trades = []

    # Close out positions that should exit
    for ticker, info in signals.items():
        hl_coin = HL_SYMBOL_MAP[ticker]
        pos = open_positions.get(hl_coin)
        if pos is None:
            continue
        is_long = pos["size"] > 0
        is_short = pos["size"] < 0

        action = info["action"]
        if (action == "sell_exit" and is_long) or \
           (action == "cover_short" and is_short) or \
           (action == "buy" and is_short) or \
           (action == "enter_short" and is_long):
            trades.append({
                "ticker": ticker, "hl_coin": hl_coin,
                "action": "close",
                "side": "long" if is_long else "short",
                "reason": f"{action} signal",
            })

    closes = {t["hl_coin"] for t in trades if t["action"] == "close"}
    remaining = {c: p for c, p in open_positions.items() if c not in closes}

    # Pyramid adds on existing winners — these don't count toward max_positions
    for ticker, info in signals.items():
        hl_coin = HL_SYMBOL_MAP[ticker]
        if hl_coin not in remaining:
            continue
        if not info.get("pyramid_added"):
            continue
        # Limit pyramid count
        current_pyramid = pyramid_state.get(hl_coin, 0)
        if current_pyramid >= 2:
            continue
        side = "long" if remaining[hl_coin]["size"] > 0 else "short"
        trades.append({
            "ticker": ticker, "hl_coin": hl_coin,
            "action": f"pyramid_{side}",
            "side": side,
            "reason": f"pyramid add #{current_pyramid + 1} (osc re-entry)",
        })

    slots = max(0, max_positions - len(remaining))

    # Open new positions, prioritized by oscillator magnitude
    candidates = []
    for ticker, info in signals.items():
        hl_coin = HL_SYMBOL_MAP[ticker]
        if hl_coin in remaining:
            continue
        action = info["action"]
        if action in ("buy", "hold_long"):
            reason = "buy signal" if action == "buy" else "sync to hold_long"
            candidates.append({
                "ticker": ticker, "hl_coin": hl_coin,
                "action": "open_long", "side": "long",
                "reason": reason,
                "priority": abs(info["osc"]),
            })
        elif action in ("enter_short", "hold_short"):
            reason = "enter_short signal" if action == "enter_short" else "sync to hold_short"
            candidates.append({
                "ticker": ticker, "hl_coin": hl_coin,
                "action": "open_short", "side": "short",
                "reason": reason,
                "priority": abs(info["osc"]),
            })

    candidates.sort(key=lambda c: c["priority"], reverse=True)
    trades.extend(candidates[:slots])
    return trades


def execute_trade(info, exchange, trade: dict, capital: float, leverage: float) -> dict:
    coin = trade["hl_coin"]
    if trade["action"] == "close":
        resp = exchange.market_close(coin)
        return _parse_response(trade, resp, info, coin)

    try:
        size = entry_size(info, exchange, coin, capital, leverage, PYRAMID_SIZE_PCT if trade["action"].startswith("pyramid_") else POSITION_SIZE_PCT)
    except (ValueError, KeyError, TypeError, ArithmeticError) as e:
        return {**trade, "status": "skipped", "reason": str(e)}

    # Do not open at an unintended leverage if the exchange rejects the setting.
    try:
        leverage_result = exchange.update_leverage(int(leverage), coin, True)
        if not isinstance(leverage_result, dict) or leverage_result.get("status") != "ok":
            return {**trade, "status": "error", "error": f"Leverage update rejected: {leverage_result}"}
    except Exception as e:
        return {**trade, "status": "error", "error": f"Leverage update failed: {e}"}

    is_buy = trade["action"] in ("open_long", "pyramid_long")
    resp = exchange.market_open(coin, is_buy, size)
    return _parse_response(trade, resp, info, coin)


# ── Guardrails ──────────────────────────────────────────────────────────────

def kill_switch_off() -> bool:
    return os.environ.get("AGGRESSIVE_KILL_SWITCH", "ON").upper() == "OFF"


def check_daily_drawdown(state: dict, equity: float, threshold: float) -> tuple[bool, dict]:
    today = dt.date.today().isoformat()
    key = f"day_start_{today}"
    start = state.get(key)
    update = {}
    if start is None:
        update[key] = equity
        return False, update
    dd = (equity - start) / start * 100 if start > 0 else 0
    if dd <= -threshold:
        update["halted_today"] = today
        update["halt_reason"] = f"Aggressive DD {dd:.2f}% exceeded {-threshold}%"
        return True, update
    return False, update


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f"Aggressive executor started at {dt.datetime.now(dt.UTC).isoformat()}")

    if kill_switch_off():
        print("Aggressive KILL_SWITCH is OFF — halting")
        sys.exit(0)

    try:
        info, exchange, address = get_client()
    except Exception as e:
        print(f"Client init failed: {e}")
        _send_email([], f"AGGRESSIVE CLIENT INIT FAILED: {e}")
        sys.exit(1)

    state = load_state()
    adoption_id = os.environ.get("AGGRESSIVE_ADOPT_EXISTING_ID", "")
    if adoption_id and state.get("position_adoption", {}).get("id") != adoption_id:
        positions = get_open_positions(info, address)
        adopt_open_positions(state, positions, adoption_id)
        save_state(state)
        verified = load_state()
        if verified.get("position_adoption") != state["position_adoption"] or \
           verified.get("owned_coins") != state["owned_coins"]:
            raise RuntimeError("Position adoption could not be verified")
        print(f"Adopted existing positions: {state['owned_coins']}; no orders submitted")
        print("Normal Aggressive management resumes on the next run")
        return
    if os.environ.get("AGGRESSIVE_HANDOVER_ONLY", "").lower() == "true":
        print(f"Adoption already recorded for {state.get('owned_coins', [])}; no orders submitted")
        return
    equity = get_account_equity(info, address)
    threshold = float(os.environ.get("AGGRESSIVE_DD_PCT", "3"))
    halted, state_update = check_daily_drawdown(state, equity, threshold)
    state.update(state_update)

    if halted:
        msg = f"Aggressive halted: {state_update.get('halt_reason')}"
        print(msg)
        _send_email([], msg)
        save_state(state)
        sys.exit(0)

    today = dt.date.today().isoformat()
    if state.get("halted_today") == today:
        print(f"Already halted today: {state.get('halt_reason')}")
        sys.exit(0)

    signals = compute_aggressive_signals()
    open_positions = get_open_positions(info, address)
    capital = float(os.environ.get("AGGRESSIVE_CAPITAL", "3000"))
    max_positions = int(os.environ.get("AGGRESSIVE_MAX_POSITIONS", "4"))

    # Filter assets to those listed on this Hyperliquid environment
    available = set(info.all_mids().keys())
    signals = {t: s for t, s in signals.items() if HL_SYMBOL_MAP[t] in available}
    skipped = [t for t in ASSETS if t not in signals]
    if skipped:
        print(f"Skipping unavailable assets on this env: {skipped}")

    # Ownership tracking with stale-position reconciliation
    owned_coins = set(state.get("owned_coins", []))
    stale_owned = owned_coins - set(open_positions.keys())
    if stale_owned:
        print(f"Dropping stale owned coins (no position on exchange): {stale_owned}")
        owned_coins -= stale_owned

    managed_positions = {c: p for c, p in open_positions.items() if c in owned_coins}

    # Per-coin pyramid state (persisted across runs)
    pyramid_state = state.get("pyramid_state", {})

    trades = decide_trades(signals, managed_positions, max_positions, pyramid_state)
    print(f"Decided on {len(trades)} aggressive trade(s) (own {len(owned_coins)} position(s))")

    results = []
    for trade in trades:
        # Aggressive leverage: 4x for large cap (capped at 3x by HL), 1.5x for mid cap
        profile = get_asset_profile(trade["ticker"])
        leverage = min(4.0, profile["max_bull_leverage"] * 1.33)  # bumped from standard
        result = execute_trade(info, exchange, trade, capital, leverage)
        results.append(result)
        print(f"  {result['ticker']} {result['action']}: {result.get('status')}")

        if result.get("status") == "filled":
            coin = result["hl_coin"]
            if result["action"] == "close":
                owned_coins.discard(coin)
                pyramid_state.pop(coin, None)
            elif result["action"].startswith("pyramid_"):
                pyramid_state[coin] = pyramid_state.get(coin, 0) + 1
            else:
                owned_coins.add(coin)
                pyramid_state[coin] = 0

    history = state.get("history", [])
    for r in results:
        history.append({
            "timestamp": dt.datetime.now(dt.UTC).isoformat(),
            **{k: v for k, v in r.items() if k != "raw"},
        })
    state["history"] = history[-500:]
    state["last_equity"] = equity
    state["last_run"] = dt.datetime.now(dt.UTC).isoformat()
    state["owned_coins"] = sorted(owned_coins)
    state["pyramid_state"] = pyramid_state
    latest = get_open_positions(info, address)
    state["open_positions"] = {c: p for c, p in latest.items() if c in owned_coins}
    state["last_signals"] = signals
    save_state(state)

    summary = execution_summary(results, equity)
    if results:
        _send_email(results, summary)
        _send_telegram(results, summary)
    for result in results:
        if result.get("status") in ("error", "unknown", "skipped"):
            print(f"Execution detail: {result.get('ticker')} {result.get('status')}: {result.get('error', result.get('reason', ''))}")
    print("Done")
    if any(r.get("status") in ("error", "unknown") for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()

