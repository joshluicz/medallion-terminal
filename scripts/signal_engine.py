#!/usr/bin/env python3
"""
Medallion Terminal — TGVM v2 signal engine.

Trend-Gated, Vol-adjusted Momentum with Fundamental Veto.

Usage:
    python scripts/signal_engine.py
    python scripts/signal_engine.py --date 2026-06-09
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

import pandas as pd

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))

from tgvm_core import (  # noqa: E402
    DB_PATH,
    EARNINGS_WINDOW,
    REGIME_MA,
    compute_regime_series,
    compute_signals_for_date,
    init_signal_tables,
    load_all_closes,
    load_fundamentals,
    load_stock_tickers,
    now_utc,
    store_regime,
    store_signals,
)
from universe import REGIME_TICKER  # noqa: E402


def _print_top15(signals, regime_status: str, as_of: str, spy_close, spy_ma) -> None:
    print(f"\n{'=' * 110}")
    print(f"  TGVM v2 Signal Engine — {as_of}")
    print(f"  Layer 0 Regime: {regime_status}  |  SPY close={spy_close:.2f}  200d SMA={spy_ma:.2f}")
    print(f"{'=' * 110}")

    ranked = [
        s for s in signals
        if s.vam_score is not None
        and not (s.vam_score != s.vam_score)
        and not s.insufficient_history
    ]
    ranked.sort(key=lambda s: s.vam_score or 0, reverse=True)
    top = ranked[:15]

    header = (
        f"{'#':>2}  {'Ticker':<6} {'VAM':>8} {'PctRank':>8} {'RawMom':>8} {'Vol90d':>8} "
        f"{'RSI':>6} {'Entry':<7} {'Veto':>4}  {'Qual':>4}  VetoReason"
    )
    print(header)
    print("-" * 110)

    for i, s in enumerate(top, 1):
        qual = "YES" if s.qualified else "no"
        veto = "YES" if s.vetoed else "no"
        print(
            f"{i:>2}  {s.ticker:<6} "
            f"{s.vam_score:>8.3f} "
            f"{s.percentile_rank or 0:>8.1f} "
            f"{s.raw_momentum or 0:>8.4f} "
            f"{s.vol_90d or 0:>8.4f} "
            f"{s.rsi or 0:>6.1f} "
            f"{s.entry_mode or '-':<7} "
            f"{veto:>4}  {qual:>4}  "
            f"{s.veto_reason or '-'}"
        )

    insuf = sum(1 for s in signals if s.insufficient_history)
    qualified_n = sum(1 for s in signals if s.qualified)
    print(f"\n  Stocks ranked: {len(ranked)}  |  Insufficient history: {insuf}  |  Qualified: {qualified_n}")
    print(f"{'=' * 110}\n")


def run(as_of: str | None = None) -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found at {DB_PATH}. Run scripts/fetch_data.py first.")

    conn = sqlite3.connect(DB_PATH)
    init_signal_tables(conn)

    spy = load_all_closes(conn, [REGIME_TICKER])
    if spy.empty or REGIME_TICKER not in spy.columns:
        conn.close()
        raise ValueError(f"{REGIME_TICKER} not in DB. Run fetch_data.py (includes SPY).")

    spy_series = spy[REGIME_TICKER].dropna()
    regime_df = compute_regime_series(spy_series)
    store_regime(conn, regime_df)

    if as_of:
        as_of_ts = pd.Timestamp(as_of)
    else:
        as_of_ts = spy_series.index[-1]

    if as_of_ts not in regime_df.index:
        valid = regime_df.index[regime_df.index <= as_of_ts]
        if valid.empty:
            conn.close()
            raise ValueError(f"No regime data on or before {as_of_ts.date()}")
        as_of_ts = valid[-1]

    regime_row = regime_df.loc[as_of_ts]
    regime_status = regime_row["status"]
    spy_close = float(regime_row["spy_close"])
    spy_ma = float(regime_row["spy_200ma"])

    stocks = load_stock_tickers(conn)
    stock_closes = load_all_closes(conn, stocks)
    fundamentals = load_fundamentals(conn)
    calendar = stock_closes.index.union(spy_series.index).sort_values()

    signals = compute_signals_for_date(
        as_of_ts,
        stock_closes,
        regime_status,
        fundamentals,
        calendar,
        earnings_window=EARNINGS_WINDOW,  # 2d window: day-of + day-before earnings
    )

    created = now_utc()
    store_signals(conn, signals, created)
    conn.close()

    _print_top15(
        signals,
        regime_status,
        as_of_ts.strftime("%Y-%m-%d"),
        spy_close,
        spy_ma,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="TGVM v2 signal engine")
    parser.add_argument("--date", help="Signal date YYYY-MM-DD (default: latest)")
    args = parser.parse_args()
    try:
        run(args.date)
    except Exception as exc:
        print(f"[!!] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
