#!/usr/bin/env python3
"""
Medallion Terminal — TGVM v2 backtest.

Fundamental vetoes require point-in-time data. Applying a current snapshot
to historical dates introduces unknown bias. Vetoes are live-only controls.
Backtest measures pure VAM + regime performance.

Weekly rebalance: top 4 qualified stocks, equal weight (25% each slot).
Regime gate (RISK_ON only), -25% hard stop per position. No fundamental vetoes.
Benchmark: VOO buy-and-hold.

Usage:
    python scripts/backtest.py
    python scripts/backtest.py --cash 100000
    python scripts/backtest.py --skip-extend   # skip 5y SP100 re-fetch
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPTS = Path(__file__).resolve().parent
_REPO = _SCRIPTS.parent
sys.path.insert(0, str(_SCRIPTS))

from tgvm_core import (  # noqa: E402
    DB_PATH,
    REGIME_MA,
    RISK_FREE_RATE,
    STOP_LOSS,
    TOP_N_HOLDINGS,
    compute_regime_series,
    compute_signals_for_date,
    load_all_closes,
    load_stock_tickers,
)
from universe import REGIME_TICKER  # noqa: E402

BENCHMARK = "VOO"
REPORTS_DIR = _REPO / "reports"
TEARSHEET_PATH = REPORTS_DIR / "tgvm_tearsheet.html"


def weekly_rebalance_dates(calendar: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Last trading day of each week (Friday-aligned)."""
    s = pd.Series(calendar, index=calendar)
    fridays = s.groupby(pd.Grouper(freq="W-FRI")).last().dropna()
    return pd.DatetimeIndex(fridays.values).sort_values()


def run_backtest(init_cash: float = 100_000.0) -> dict:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found at {DB_PATH}. Run scripts/fetch_data.py first.")

    conn = sqlite3.connect(DB_PATH)
    spy = load_all_closes(conn, [REGIME_TICKER])
    voo = load_all_closes(conn, [BENCHMARK])
    stocks = load_stock_tickers(conn)
    stock_closes = load_all_closes(conn, stocks)
    conn.close()

    if spy.empty or voo.empty or stock_closes.empty:
        raise ValueError("Insufficient price data for backtest.")

    spy_s = spy[REGIME_TICKER].dropna()
    voo_s = voo[BENCHMARK].dropna()
    regime_df = compute_regime_series(spy_s)

    calendar = stock_closes.index.intersection(voo_s.index).intersection(spy_s.index).sort_values()
    stock_closes = stock_closes.reindex(calendar).ffill()
    voo_s = voo_s.reindex(calendar).ffill()
    full_closes = stock_closes.copy()

    warmup = max(REGIME_MA, 252)
    if len(calendar) <= warmup:
        raise ValueError(f"Not enough history ({len(calendar)} days); need >{warmup}.")
    bt_calendar = calendar[warmup:]
    bt_closes = stock_closes.loc[bt_calendar]
    voo_s = voo_s.loc[bt_calendar]
    calendar = bt_calendar

    rebal_dates = weekly_rebalance_dates(calendar)
    rebal_set = set(rebal_dates)

    daily_rets = bt_closes.pct_change()
    voo_rets = voo_s.pct_change().fillna(0)

    holdings: dict[str, float] = {}
    entry_prices: dict[str, float] = {}
    trades = 0
    in_market_days = 0

    port_rets = pd.Series(0.0, index=calendar, name="TGVM")
    empty_fundamentals = pd.DataFrame()

    for i, dt in enumerate(calendar):
        if holdings:
            to_exit = []
            for t in list(holdings.keys()):
                if t not in bt_closes.columns:
                    continue
                px = bt_closes.at[dt, t]
                if pd.isna(px):
                    continue
                entry = entry_prices.get(t, px)
                if px <= entry * (1 - STOP_LOSS):
                    to_exit.append(t)
            for t in to_exit:
                holdings.pop(t)
                entry_prices.pop(t, None)
                trades += 1

        if dt in rebal_set:
            regime_status = regime_df.loc[dt, "status"] if dt in regime_df.index else "RISK_OFF"
            signals = compute_signals_for_date(
                dt,
                full_closes,
                regime_status,
                empty_fundamentals,
                full_closes.index,
                disable_fundamental_veto=True,
            )
            qualified = [s for s in signals if s.qualified]
            qualified.sort(key=lambda s: s.vam_score or 0, reverse=True)
            picks = [s.ticker for s in qualified[:TOP_N_HOLDINGS]]

            if regime_status != "RISK_ON" or len(picks) < 1:
                if holdings:
                    trades += len(holdings)
                holdings = {}
                entry_prices = {}
            else:
                slot_w = 1.0 / TOP_N_HOLDINGS
                new_holdings: dict[str, float] = {}
                new_entries: dict[str, float] = {}
                for t in picks[:TOP_N_HOLDINGS]:
                    px = bt_closes.at[dt, t]
                    if pd.isna(px):
                        continue
                    new_holdings[t] = slot_w
                    new_entries[t] = float(px)
                if set(new_holdings.keys()) != set(holdings.keys()):
                    trades += 1
                holdings = new_holdings
                entry_prices = new_entries

        day_ret = 0.0
        invested = 0.0
        for t, w in holdings.items():
            r = daily_rets.at[dt, t] if t in daily_rets.columns else 0.0
            if pd.isna(r):
                r = 0.0
            day_ret += w * r
            invested += w
        port_rets.iloc[i] = day_ret
        if invested > 0.01:
            in_market_days += 1

    years = len(calendar) / 252
    total_ret = (1 + port_rets).prod() - 1
    voo_total = (1 + voo_rets).prod() - 1
    ann_ret = (1 + total_ret) ** (1 / years) - 1 if years > 0 else 0
    voo_ann = (1 + voo_total) ** (1 / years) - 1 if years > 0 else 0

    excess = port_rets - RISK_FREE_RATE / 252
    sharpe = (
        (excess.mean() / excess.std()) * np.sqrt(252)
        if excess.std() and excess.std() > 0
        else float("nan")
    )
    voo_excess = voo_rets - RISK_FREE_RATE / 252
    voo_sharpe = (voo_excess.mean() / voo_excess.std()) * np.sqrt(252) if voo_excess.std() else float("nan")

    cum = (1 + port_rets).cumprod()
    max_dd = (cum / cum.cummax() - 1).min()
    voo_cum = (1 + voo_rets).cumprod()
    voo_max_dd = (voo_cum / voo_cum.cummax() - 1).min()

    win_rate = (port_rets > 0).mean()

    return {
        "calendar": calendar,
        "port_rets": port_rets,
        "voo_rets": voo_rets,
        "total_ret": total_ret,
        "voo_total": voo_total,
        "ann_ret": ann_ret,
        "voo_ann": voo_ann,
        "sharpe": sharpe,
        "voo_sharpe": voo_sharpe,
        "max_dd": max_dd,
        "voo_max_dd": voo_max_dd,
        "win_rate": win_rate,
        "trades": trades,
        "time_in_market_pct": in_market_days / len(calendar) * 100,
        "years": years,
        "trading_days": len(calendar),
    }


def save_tearsheet(port_rets: pd.Series, voo_rets: pd.Series) -> Path | None:
    import quantstats as qs

    if port_rets.std() == 0 or port_rets.abs().sum() == 0:
        print("  [skip] QuantStats tearsheet — strategy had zero variance (no trades).")
        return None

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    qs.reports.html(
        port_rets,
        benchmark=voo_rets,
        output=str(TEARSHEET_PATH),
        title="Medallion Terminal — TGVM v2 Backtest",
        download_filename=TEARSHEET_PATH.name,
    )
    return TEARSHEET_PATH


def print_results(m: dict) -> None:
    cal = m["calendar"]
    print(f"\n{'=' * 72}")
    print("  Medallion Terminal — TGVM v2 Backtest (clean: VAM + regime only)")
    print(f"  Backtest window: {cal[0].date()} to {cal[-1].date()}, {m['trading_days']} trading days")
    print(f"  Benchmark    : {BENCHMARK} buy-and-hold")
    print(f"  Risk-free    : {RISK_FREE_RATE * 100:.2f}% (MYR FD hurdle)")
    print(f"  Positions    : top {TOP_N_HOLDINGS} @ {100 / TOP_N_HOLDINGS:.0f}% each")
    print(f"{'=' * 72}")
    print(f"  {'Metric':<22}  {'TGVM':>12}  {BENCHMARK:>12}")
    print(f"  {'-' * 22}  {'-' * 12}  {'-' * 12}")
    print(f"  {'Annualised Return':<22}  {m['ann_ret'] * 100:>11.2f}%  {m['voo_ann'] * 100:>11.2f}%")
    print(f"  {'Total Return':<22}  {m['total_ret'] * 100:>11.2f}%  {m['voo_total'] * 100:>11.2f}%")
    print(f"  {'Sharpe Ratio':<22}  {m['sharpe']:>12.4f}  {m['voo_sharpe']:>12.4f}")
    print(f"  {'Max Drawdown':<22}  {m['max_dd'] * 100:>11.2f}%  {m['voo_max_dd'] * 100:>11.2f}%")
    print(f"  {'Win Rate (daily)':<22}  {m['win_rate'] * 100:>11.2f}%  {'N/A':>12}")
    print(f"  {'# Rebalance events':<22}  {m['trades']:>12}  {'1':>12}")
    print(f"  {'Time in market':<22}  {m['time_in_market_pct']:>11.1f}%  {'100.0':>11}%")
    print(f"\n  *** CAVEAT: ~{m['years']:.1f}-year sample is a PLUMBING CHECK only.")
    print("  Not statistically valid. Do not infer alpha from this.")
    print(f"{'=' * 72}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="TGVM v2 backtest")
    parser.add_argument("--cash", type=float, default=100_000, help="Starting cash (display only)")
    parser.add_argument(
        "--skip-extend",
        action="store_true",
        help="Skip 5y SP100/SPY/VOO history extension",
    )
    args = parser.parse_args()

    try:
        if not args.skip_extend:
            from extend_sp100_history import extend_sp100_history

            extend_sp100_history()

        m = run_backtest(args.cash)
        print_results(m)
        path = save_tearsheet(m["port_rets"], m["voo_rets"])
        if path:
            print(f"  QuantStats tearsheet: {path}\n")
    except Exception as exc:
        print(f"[!!] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
