#!/usr/bin/env python3
"""
Medallion Terminal -- Phase 2 skeleton: signal engine backtest harness.

Sanity check: 12-1 month momentum on VOO vs buy-and-hold.
Expand in Phase 2 to cover the full Signal Library v1:
  - RSI(14)            weight 15%
  - MACD crossover     weight 15%
  - 50/200 MA cross    weight 10%
  - 12-1m momentum     weight 25%  <-- implemented here
  - Forward P/E rank   weight 20%
  - EPS revision dir   weight 15%

Usage:
    python scripts/backtest.py
    python scripts/backtest.py --ticker QQQ --cash 50000
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "medallion.db"

TRADING_DAYS_1M = 21
TRADING_DAYS_12M = 252


# ---- Data -------------------------------------------------------------------

def load_prices(ticker: str) -> pd.Series:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DB not found at {DB_PATH}. Run scripts/fetch_data.py first."
        )

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, close FROM prices WHERE ticker = ? ORDER BY date",
        conn,
        params=(ticker,),
        parse_dates=["date"],
        index_col="date",
    )
    conn.close()

    if df.empty:
        raise ValueError(f"No price data for {ticker} in local DB.")

    return df["close"].rename(ticker)


# ---- Signal: 12-1 month momentum --------------------------------------------

def momentum_signal(price: pd.Series) -> pd.Series:
    """
    12-1 month momentum: 12-month return minus 1-month return.
    Positive -> bullish; negative -> bearish.
    """
    ret_12m = price.pct_change(TRADING_DAYS_12M)
    ret_1m = price.pct_change(TRADING_DAYS_1M)
    return (ret_12m - ret_1m).rename("momentum")


def momentum_regime(mom: pd.Series) -> pd.Series:
    """True when the momentum signal is bullish (above zero)."""
    return (mom > 0).rename("in_market")


def regime_changes(regime: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Entry/exit booleans on regime flips (no look-ahead)."""
    prev = regime.shift(1)
    prev = prev.where(prev.notna(), False).astype(bool)
    entries = regime & ~prev
    exits = ~regime & prev
    return entries, exits


# ---- Backtest ---------------------------------------------------------------

def run(ticker: str, init_cash: float) -> None:
    try:
        import vectorbt as vbt
    except ImportError:
        print("[!!] vectorbt not installed. Run: pip install -r requirements.txt")
        print("     Falling back to pandas-only stats.\n")
        _run_pandas_fallback(ticker, init_cash)
        return

    price = load_prices(ticker)
    mom = momentum_signal(price).dropna()
    price = price.loc[mom.index]

    regime = momentum_regime(mom)
    entries, exits = regime_changes(regime)

    pf = vbt.Portfolio.from_signals(
        price,
        entries,
        exits,
        init_cash=init_cash,
        freq="D",
        fees=0.0,       # zero-commission IBKR US ETFs
        slippage=0.001, # 0.1% slippage estimate
    )
    bh = vbt.Portfolio.from_holding(price, init_cash=init_cash, freq="D")

    _print_results(ticker, price, pf, bh, regime)


def _stat(stats: pd.Series, key: str, default=0):
    val = stats.get(key, default)
    if pd.isna(val):
        return default
    return val


def _print_results(ticker, price, pf, bh, regime) -> None:
    strat_stats = pf.stats()
    bh_stats = bh.stats()

    print(f"\n{'=' * 60}")
    print(f"  Medallion Terminal -- Backtest: {ticker}")
    print(f"  Signal  : 12-1 month momentum (long when > 0, else cash)")
    print(f"  Period  : {price.index[0].date()} -> {price.index[-1].date()}")
    print(f"  Days    : {len(price)}")
    print(f"  In mkt  : {regime.mean() * 100:.1f}% of days")
    print(f"{'=' * 60}")

    def _pct(val):
        try:
            return f"{float(val):.2f}%"
        except (TypeError, ValueError):
            return str(val)

    def _f2(val):
        try:
            return f"{float(val):.4f}"
        except (TypeError, ValueError):
            return str(val)

    rows = [
        (
            "Total Return",
            _pct(_stat(strat_stats, "Total Return [%]")),
            _pct(_stat(bh_stats, "Total Return [%]")),
        ),
        (
            "Annualised Ret",
            _pct(_stat(strat_stats, "Annualized Return [%]")),
            _pct(_stat(bh_stats, "Annualized Return [%]")),
        ),
        (
            "Sharpe Ratio",
            _f2(_stat(strat_stats, "Sharpe Ratio")),
            _f2(_stat(bh_stats, "Sharpe Ratio")),
        ),
        (
            "Max Drawdown",
            _pct(_stat(strat_stats, "Max Drawdown [%]")),
            _pct(_stat(bh_stats, "Max Drawdown [%]")),
        ),
        (
            "Win Rate",
            _pct(_stat(strat_stats, "Win Rate [%]")),
            "N/A",
        ),
        (
            "# Trades",
            str(int(_stat(strat_stats, "Total Trades", 0))),
            "1",
        ),
    ]

    print(f"  {'Metric':<20}  {'Strategy':>12}  {'Buy & Hold':>12}")
    print(f"  {'-' * 20}  {'-' * 12}  {'-' * 12}")
    for label, strat_val, bh_val in rows:
        print(f"  {label:<20}  {strat_val:>12}  {bh_val:>12}")

    print(f"\n  Benchmark hurdle : 3.55% (MYR FD rate)")
    print(f"  Target           : >10% annualised vs VOO")
    print(f"{'=' * 60}\n")


def _run_pandas_fallback(ticker: str, init_cash: float) -> None:
    """Minimal stats without vectorbt, so the skeleton runs in all envs."""
    price = load_prices(ticker)
    mom = momentum_signal(price).dropna()
    price = price.loc[mom.index]
    regime = momentum_regime(mom)

    daily_ret = price.pct_change().fillna(0)
    strat_ret = daily_ret * regime.shift(1).fillna(0)

    total_days = len(price)
    years = total_days / 252
    total_return = (1 + strat_ret).prod() - 1
    bh_return = price.iloc[-1] / price.iloc[0] - 1
    ann_return = (1 + total_return) ** (1 / years) - 1
    ann_bh_return = (1 + bh_return) ** (1 / years) - 1
    sharpe = (
        (strat_ret.mean() / strat_ret.std()) * np.sqrt(252)
        if strat_ret.std()
        else float("nan")
    )
    drawdown = (price / price.cummax() - 1).min()

    print(f"\n{'=' * 60}")
    print(f"  Medallion Terminal -- Backtest: {ticker} (pandas fallback)")
    print(f"  Signal  : 12-1 month momentum")
    print(f"  Period  : {price.index[0].date()} -> {price.index[-1].date()}")
    print(f"  In mkt  : {regime.mean() * 100:.1f}% of days")
    print(f"{'=' * 60}")
    print(f"  {'Metric':<20}  {'Strategy':>12}  {'Buy & Hold':>12}")
    print(f"  {'-' * 20}  {'-' * 12}  {'-' * 12}")
    print(f"  {'Total Return':<20}  {total_return * 100:>11.2f}%  {bh_return * 100:>11.2f}%")
    print(f"  {'Annualised Ret':<20}  {ann_return * 100:>11.2f}%  {ann_bh_return * 100:>11.2f}%")
    print(f"  {'Sharpe Ratio':<20}  {sharpe:>12.4f}  {'N/A':>12}")
    print(f"  {'Max Drawdown':<20}  {drawdown * 100:>11.2f}%  {'':>12}")
    print(f"\n  Benchmark hurdle : 3.55% (MYR FD rate)")
    print(f"  Target           : >10% annualised vs VOO")
    print(f"{'=' * 60}\n")


# ---- Entry ------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Medallion Terminal backtest runner")
    parser.add_argument(
        "--ticker",
        default="VOO",
        help="Ticker to backtest (must be in local DB)",
    )
    parser.add_argument(
        "--cash",
        default=10_000,
        type=float,
        help="Starting portfolio cash",
    )
    args = parser.parse_args()
    run(args.ticker.upper(), args.cash)


if __name__ == "__main__":
    main()
