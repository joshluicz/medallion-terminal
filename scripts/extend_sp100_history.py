#!/usr/bin/env python3
"""
Extend S&P 100 price history to 5 years for backtest depth.

Does not modify fetch_data.py defaults. ETFs (including SPY, VOO) and
short-history names (CRWV, NBIS) are left unchanged.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))

from universe import SP100  # noqa: E402

DB_PATH = _SCRIPTS.parent / "data" / "medallion.db"


def upsert_prices(ticker: str, period: str, conn: sqlite3.Connection) -> tuple[int, str, str]:
    raw = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
    if raw.empty:
        raise ValueError("yfinance returned empty DataFrame")

    df = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    rows: list[tuple] = []
    for dt, row in df.iterrows():
        def _f(col: str) -> float | None:
            v = row.get(col)
            return None if v is None or pd.isna(v) else round(float(v), 6)

        rows.append((
            ticker,
            dt.strftime("%Y-%m-%d"),
            _f("Open"),
            _f("High"),
            _f("Low"),
            _f("Close"),
            None if pd.isna(row.get("Volume", float("nan"))) else int(row["Volume"]),
        ))

    conn.executemany(
        "INSERT OR REPLACE INTO prices "
        "(ticker, date, open, high, low, close, volume) VALUES (?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    dates = [r[1] for r in rows]
    return len(rows), min(dates), max(dates)


def extend_sp100_history() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found at {DB_PATH}. Run scripts/fetch_data.py first.")

    tickers = sorted(SP100)
    conn = sqlite3.connect(DB_PATH)

    print(f"Extending price history to 5y for {len(tickers)} S&P 100 tickers...\n")

    ok = 0
    for i, ticker in enumerate(tickers, 1):
        try:
            n, d_min, d_max = upsert_prices(ticker, "5y", conn)
            print(f"  [{i:>3}/{len(tickers)}] [OK]  {ticker:<6}  {n:>4} rows  {d_min} -> {d_max}")
            ok += 1
        except Exception as exc:
            print(f"  [{i:>3}/{len(tickers)}] [!!]  {ticker:<6}  FAILED: {exc}", file=sys.stderr)

    conn.close()
    print(f"\n  Extended: {ok}/{len(tickers)} tickers\n")


if __name__ == "__main__":
    extend_sp100_history()
