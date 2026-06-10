#!/usr/bin/env python3
"""
Medallion Terminal -- Phase 1 data fetcher.
Pulls 2-year OHLCV + fundamentals for watched tickers into SQLite.

Usage:
    python scripts/fetch_data.py
    python scripts/fetch_data.py --tickers AAPL TSLA   # override ticker list
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))
from universe import get_all_tickers, is_etf  # noqa: E402

# Load .env.local (Next.js convention) then fall back to .env
_repo_root = Path(__file__).resolve().parent.parent
load_dotenv(_repo_root / ".env.local")
load_dotenv(_repo_root / ".env")

try:
    from openbb import obb as _obb
    _fmp_key = os.getenv("FMP_API_KEY")
    if _fmp_key:
        _obb.user.credentials.fmp_api_key = _fmp_key
    _OPENBB_AVAILABLE = True
except ImportError:
    _OPENBB_AVAILABLE = False

DEFAULT_TICKERS = get_all_tickers()

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "medallion.db"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_to_date(ts: int | float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


# ---- Database ---------------------------------------------------------------

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS prices (
            ticker  TEXT    NOT NULL,
            date    TEXT    NOT NULL,   -- ISO-8601 YYYY-MM-DD
            open    REAL,
            high    REAL,
            low     REAL,
            close   REAL,               -- adjusted close
            volume  INTEGER,
            PRIMARY KEY (ticker, date)
        );

        CREATE TABLE IF NOT EXISTS fundamentals (
            ticker                  TEXT PRIMARY KEY,
            forward_pe              REAL,
            trailing_pe             REAL,
            ev_ebitda               REAL,
            eps_trailing            REAL,
            eps_revision_direction  TEXT,   -- 'up' | 'down' | 'flat' | NULL (ETFs)
            next_earnings_date      TEXT,   -- ISO-8601 YYYY-MM-DD, null for ETFs
            updated_at              TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS securities (
            ticker   TEXT PRIMARY KEY,
            is_etf   INTEGER NOT NULL DEFAULT 0   -- 1 = ETF, excluded from momentum ranking
        );
    """)
    # Migrate existing DB: add eps_revision_direction if the column is absent
    existing = {row[1] for row in conn.execute("PRAGMA table_info(fundamentals)")}
    if "eps_revision_direction" not in existing:
        conn.execute("ALTER TABLE fundamentals ADD COLUMN eps_revision_direction TEXT")
    conn.commit()
    # Migration: add new columns to existing DBs without dropping data
    existing = {r[1] for r in conn.execute("PRAGMA table_info(fundamentals)")}
    for col, definition in [("eps_revision_direction", "TEXT")]:
        if col not in existing:
            conn.execute(f"ALTER TABLE fundamentals ADD COLUMN {col} {definition}")
    conn.commit()


def upsert_security(ticker: str, conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO securities (ticker, is_etf) VALUES (?, ?)",
        (ticker, 1 if is_etf(ticker) else 0),
    )
    conn.commit()


# ---- Prices -----------------------------------------------------------------

def upsert_prices(ticker: str, conn: sqlite3.Connection) -> tuple[int, str, str]:
    raw = yf.download(
        ticker,
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False,
    )
    if raw.empty:
        raise ValueError("yfinance returned empty DataFrame")

    df = raw.copy()
    # yfinance >=0.2.18 returns MultiIndex columns (field, ticker) for single-ticker downloads
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


# ---- OpenBB helpers ---------------------------------------------------------

def _openbb_multiples(ticker: str) -> dict[str, float | None]:
    """Fetch forward P/E and EV/EBITDA via OpenBB. Returns {} on any failure."""
    try:
        data = _obb.equity.fundamental.multiples(symbol=ticker).results
        if not data:
            return {}
        m = data[0]
        return {
            "forward_pe": getattr(m, "forward_pe", None),
            "ev_ebitda":  getattr(m, "ev_to_ebitda", None),
        }
    except Exception:
        return {}


def _openbb_eps_revision(ticker: str) -> str | None:
    """
    Return 'up' / 'down' / 'flat' from the 30-day EPS estimate drift.
    Returns None on failure or when data is unavailable (e.g. ETFs).
    """
    try:
        trend = _obb.equity.estimates.eps_trend(symbol=ticker).results
        if not trend:
            return None
        t = trend[0]
        # Field names vary by provider; try the most common variants
        current = getattr(t, "current", None) or getattr(t, "current_estimate", None)
        prior   = (getattr(t, "thirty_days_ago", None) or
                   getattr(t, "prior_30d", None) or
                   getattr(t, "consensus_30d_prior", None))
        if current is None or not prior:
            return None
        pct = (current - prior) / abs(prior)
        if pct > 0.001:
            return "up"
        if pct < -0.001:
            return "down"
        return "flat"
    except Exception:
        return None


# ---- Fundamentals -----------------------------------------------------------

def upsert_fundamentals(ticker: str, conn: sqlite3.Connection) -> str:
    """Populate fundamentals row. Returns the data-source label for the caller."""
    fields: dict[str, object] = {}
    source = "yfinance"

    # OpenBB first — cleaner institutional data
    if _OPENBB_AVAILABLE:
        ob_mult = _openbb_multiples(ticker)
        ob_rev  = _openbb_eps_revision(ticker)
        if ob_mult or ob_rev is not None:
            source = "openbb"
        fields.update(ob_mult)
        if ob_rev is not None:
            fields["eps_revision_direction"] = ob_rev

    # yfinance fallback for any field still missing
    info = yf.Ticker(ticker).info

    if fields.get("forward_pe") is None:
        fields["forward_pe"] = info.get("forwardPE")
    if fields.get("ev_ebitda") is None:
        fields["ev_ebitda"] = info.get("enterpriseToEbitda")

    fields.setdefault("trailing_pe",            info.get("trailingPE"))
    fields.setdefault("eps_trailing",           info.get("trailingEps"))
    fields.setdefault("eps_revision_direction", None)

    # earningsTimestamp = upcoming earnings Unix ts. Falls back to range-start.
    # ETFs return None for both -- stored as NULL, which is correct.
    next_earnings: str | None = None
    for key in ("earningsTimestamp", "earningsTimestampStart"):
        ts = info.get(key)
        if ts and isinstance(ts, (int, float)) and ts > 0:
            next_earnings = _ts_to_date(ts)
            break

    conn.execute(
        "INSERT OR REPLACE INTO fundamentals "
        "(ticker, forward_pe, trailing_pe, ev_ebitda, eps_trailing, "
        " eps_revision_direction, next_earnings_date, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            ticker,
            fields.get("forward_pe"),
            fields.get("trailing_pe"),
            fields.get("ev_ebitda"),
            fields.get("eps_trailing"),
            fields.get("eps_revision_direction"),
            next_earnings,
            _now_utc(),
        ),
    )
    conn.commit()
    return source


# ---- Main -------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Medallion Terminal data fetcher")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS,
                        help="Override the default ticker list")
    args = parser.parse_args()
    tickers: list[str] = [t.upper() for t in args.tickers]

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    ok:   list[tuple[str, int, str, str]] = []
    fail: list[tuple[str, str]]           = []

    provider_tag = "openbb+yfinance" if _OPENBB_AVAILABLE else "yfinance"
    etf_n = sum(1 for t in tickers if is_etf(t))
    print(f"Medallion Terminal -- fetching {len(tickers)} tickers  [{provider_tag}]")
    print(f"  Universe: S&P 100 + holdings + SPY  |  ETFs (no rank): {etf_n}\n")

    for i, ticker in enumerate(tickers, 1):
        try:
            upsert_security(ticker, conn)
            n, d_min, d_max = upsert_prices(ticker, conn)
            src = upsert_fundamentals(ticker, conn)
            ok.append((ticker, n, d_min, d_max))
            tag = "ETF" if is_etf(ticker) else "STK"
            print(f"  [{i:>3}/{len(tickers)}] [OK]  {ticker:<6} {tag}  {n:>4} rows  {d_min} -> {d_max}  [{src}]")
        except Exception as exc:
            fail.append((ticker, str(exc)))
            print(f"  [{i:>3}/{len(tickers)}] [!!]  {ticker:<6}  FAILED: {exc}", file=sys.stderr)

    conn.close()

    print(f"\n{'-'*52}")
    print(f"  DB      : {DB_PATH}")
    print(f"  Success : {len(ok)}/{len(tickers)} tickers")
    if fail:
        print(f"  Failures: {', '.join(t for t, _ in fail)}")
    if ok:
        print(f"  Range   : {min(r[2] for r in ok)} -> {max(r[3] for r in ok)}")
    print(f"  Run at  : {_now_utc()} UTC")

    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
