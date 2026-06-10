"""
TGVM v2 core — shared signal logic for signal_engine.py and backtest.py.
Trend-Gated, Vol-adjusted Momentum with Fundamental Veto.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from universe import ETF_TICKERS, REGIME_TICKER, is_etf

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "medallion.db"

TRADING_DAYS_1M = 21
TRADING_DAYS_12M = 252
TRADING_DAYS_VOL = 90
RSI_PERIOD = 14
REGIME_MA = 200
EARNINGS_WINDOW = 2  # live signal: day-of and day-before earnings only
STOP_LOSS = 0.25
QUALIFIED_PERCENTILE = 75
TOP_N_HOLDINGS = 4
RISK_FREE_RATE = 0.0355


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_signal_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS regime (
            date        TEXT PRIMARY KEY,
            status      TEXT NOT NULL,
            spy_close   REAL,
            spy_200ma   REAL
        );

        CREATE TABLE IF NOT EXISTS signals_v2 (
            ticker           TEXT NOT NULL,
            date             TEXT NOT NULL,
            regime           TEXT,
            raw_momentum     REAL,
            vol_90d          REAL,
            vam_score        REAL,
            percentile_rank  REAL,
            vetoed           INTEGER,
            veto_reason      TEXT,
            rsi              REAL,
            entry_mode       TEXT,
            qualified        INTEGER,
            created_at       TEXT NOT NULL,
            PRIMARY KEY (ticker, date)
        );
    """)
    conn.commit()


def load_close_series(conn: sqlite3.Connection, ticker: str) -> pd.Series:
    df = pd.read_sql(
        "SELECT date, close FROM prices WHERE ticker = ? ORDER BY date",
        conn,
        params=(ticker.upper(),),
        parse_dates=["date"],
        index_col="date",
    )
    if df.empty:
        return pd.Series(dtype=float, name=ticker.upper())
    return df["close"].astype(float).rename(ticker.upper())


def load_all_closes(conn: sqlite3.Connection, tickers: list[str]) -> pd.DataFrame:
    frames: dict[str, pd.Series] = {}
    for t in tickers:
        s = load_close_series(conn, t)
        if not s.empty:
            frames[t.upper()] = s
    if not frames:
        return pd.DataFrame()
    return pd.DataFrame(frames).sort_index()


def load_fundamentals(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM fundamentals", conn)


def load_stock_tickers(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT ticker FROM securities WHERE is_etf = 0 ORDER BY ticker"
    ).fetchall()
    if rows:
        return [r[0] for r in rows]
    # Fallback if securities table not populated
    all_t = pd.read_sql("SELECT DISTINCT ticker FROM prices", conn)["ticker"].tolist()
    return sorted(t for t in all_t if not is_etf(t))


def compute_rsi(close: pd.Series, period: int = RSI_PERIOD) -> float:
    if len(close) < period + 1:
        return float("nan")
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain.iloc[-1] / avg_loss.iloc[-1] if avg_loss.iloc[-1] else float("inf")
    return float(100 - (100 / (1 + rs)))


def compute_regime_series(spy: pd.Series) -> pd.DataFrame:
    sma = spy.rolling(REGIME_MA, min_periods=REGIME_MA).mean()
    status = np.where(spy > sma, "RISK_ON", "RISK_OFF")
    return pd.DataFrame(
        {
            "status": status,
            "spy_close": spy,
            "spy_200ma": sma,
        },
        index=spy.index,
    )


def trading_days_until(earnings_date: str, as_of: pd.Timestamp, calendar: pd.DatetimeIndex) -> int | None:
    if not earnings_date:
        return None
    try:
        ed = pd.Timestamp(earnings_date)
    except (ValueError, TypeError):
        return None
    future = calendar[(calendar > as_of) & (calendar <= ed)]
    return len(future)


def fundamental_veto(
    ticker: str,
    as_of: pd.Timestamp,
    calendar: pd.DatetimeIndex,
    fund_row: pd.Series | None,
    median_forward_pe: float | None,
    *,
    skip_earnings_veto: bool = False,
    earnings_window: int = EARNINGS_WINDOW,
) -> tuple[bool, str]:
    if fund_row is None:
        return False, ""

    reasons: list[str] = []

    eps = fund_row.get("eps_trailing")
    if eps is not None and not pd.isna(eps) and float(eps) < 0:
        reasons.append("NEG_EPS")

    fwd_pe = fund_row.get("forward_pe")
    if (
        fwd_pe is not None
        and not pd.isna(fwd_pe)
        and median_forward_pe is not None
        and not pd.isna(median_forward_pe)
        and float(fwd_pe) > 3 * float(median_forward_pe)
    ):
        reasons.append("EXTREME_FWD_PE")

    earn = fund_row.get("next_earnings_date")
    if not skip_earnings_veto and earn and not pd.isna(earn):
        days = trading_days_until(str(earn), as_of, calendar)
        if days is not None and 0 <= days <= earnings_window:
            reasons.append("EARNINGS_SOON")

    if reasons:
        return True, "|".join(reasons)
    return False, ""


@dataclass
class StockSignal:
    ticker: str
    date: str
    regime: str
    raw_momentum: float | None
    vol_90d: float | None
    vam_score: float | None
    percentile_rank: float | None
    vetoed: bool
    veto_reason: str
    rsi: float | None
    entry_mode: str | None
    qualified: bool
    insufficient_history: bool = False


def compute_stock_metrics(
    ticker: str,
    close: pd.Series,
    as_of: pd.Timestamp,
) -> tuple[float | None, float | None, float | None, bool]:
    """Return raw_mom, vol_90d, vam_score, insufficient_history."""
    hist = close[close.index <= as_of].dropna()
    if len(hist) < TRADING_DAYS_12M + 1:
        return None, None, None, True

    p_now = hist.iloc[-1]
    p_21 = hist.iloc[-1 - TRADING_DAYS_1M] if len(hist) > TRADING_DAYS_1M else None
    p_252 = hist.iloc[-1 - TRADING_DAYS_12M] if len(hist) > TRADING_DAYS_12M else None

    if p_21 is None or p_252 is None or p_252 == 0:
        return None, None, None, True

    raw_mom = float(p_21 / p_252 - 1)

    rets = hist.pct_change().dropna()
    if len(rets) < TRADING_DAYS_VOL:
        return raw_mom, None, None, True

    vol_90d = float(rets.iloc[-TRADING_DAYS_VOL:].std() * np.sqrt(252))
    if vol_90d <= 0 or np.isnan(vol_90d):
        return raw_mom, vol_90d, None, False

    vam = raw_mom / vol_90d
    return raw_mom, vol_90d, float(vam), False


def compute_signals_for_date(
    as_of: pd.Timestamp,
    stock_closes: pd.DataFrame,
    regime_status: str,
    fundamentals: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    *,
    skip_earnings_veto: bool = False,
    earnings_window: int = EARNINGS_WINDOW,
    disable_fundamental_veto: bool = False,
) -> list[StockSignal]:
    fund_idx = fundamentals.set_index("ticker") if not fundamentals.empty else pd.DataFrame()

    valid_pe = []
    for t in stock_closes.columns:
        if t in fund_idx.index:
            pe = fund_idx.loc[t, "forward_pe"]
            if pe is not None and not pd.isna(pe) and float(pe) > 0:
                valid_pe.append(float(pe))
    median_fwd_pe = float(np.median(valid_pe)) if valid_pe else None

    rows: list[dict] = []
    insufficient: list[StockSignal] = []

    for ticker in stock_closes.columns:
        close = stock_closes[ticker].dropna()
        if as_of not in close.index and len(close.loc[:as_of]) == 0:
            continue

        raw_mom, vol_90d, vam, insuf = compute_stock_metrics(ticker, close, as_of)
        if insuf:
            insufficient.append(
                StockSignal(
                    ticker=ticker,
                    date=as_of.strftime("%Y-%m-%d"),
                    regime=regime_status,
                    raw_momentum=raw_mom,
                    vol_90d=vol_90d,
                    vam_score=vam,
                    percentile_rank=None,
                    vetoed=False,
                    veto_reason="INSUFFICIENT_HISTORY",
                    rsi=None,
                    entry_mode=None,
                    qualified=False,
                    insufficient_history=True,
                )
            )
            continue

        fund_row = fund_idx.loc[ticker] if ticker in fund_idx.index else None
        if disable_fundamental_veto:
            vetoed, veto_reason = False, ""
        else:
            vetoed, veto_reason = fundamental_veto(
                ticker, as_of, calendar, fund_row, median_fwd_pe,
                skip_earnings_veto=skip_earnings_veto,
                earnings_window=earnings_window,
            )

        rsi_val = compute_rsi(close.loc[:as_of])
        entry_mode = "FULL" if not np.isnan(rsi_val) and rsi_val < 50 else "STAGED"

        rows.append(
            {
                "ticker": ticker,
                "raw_momentum": raw_mom,
                "vol_90d": vol_90d,
                "vam_score": vam,
                "vetoed": vetoed,
                "veto_reason": veto_reason,
                "rsi": rsi_val,
                "entry_mode": entry_mode,
            }
        )

    # Percentile rank by vam_score (0–100, higher = stronger momentum)
    ranked = [r for r in rows if r["vam_score"] is not None and not np.isnan(r["vam_score"])]
    if ranked:
        scores = pd.Series(
            [r["vam_score"] for r in ranked],
            index=[r["ticker"] for r in ranked],
        )
        pct_ranks = scores.rank(pct=True) * 100
    else:
        pct_ranks = pd.Series(dtype=float)

    signals: list[StockSignal] = list(insufficient)
    for r in rows:
        ticker = r["ticker"]
        pct = float(pct_ranks[ticker]) if ticker in pct_ranks.index else None
        qualified = (
            regime_status == "RISK_ON"
            and pct is not None
            and pct >= QUALIFIED_PERCENTILE
            and not r["vetoed"]
        )
        signals.append(
            StockSignal(
                ticker=ticker,
                date=as_of.strftime("%Y-%m-%d"),
                regime=regime_status,
                raw_momentum=r["raw_momentum"],
                vol_90d=r["vol_90d"],
                vam_score=r["vam_score"],
                percentile_rank=pct,
                vetoed=r["vetoed"],
                veto_reason=r["veto_reason"] or "",
                rsi=r["rsi"],
                entry_mode=r["entry_mode"],
                qualified=qualified,
            )
        )

    return signals


def store_regime(conn: sqlite3.Connection, regime_df: pd.DataFrame) -> None:
    rows = [
        (
            idx.strftime("%Y-%m-%d"),
            row["status"],
            None if pd.isna(row["spy_close"]) else float(row["spy_close"]),
            None if pd.isna(row["spy_200ma"]) else float(row["spy_200ma"]),
        )
        for idx, row in regime_df.dropna(subset=["spy_200ma"]).iterrows()
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO regime (date, status, spy_close, spy_200ma) VALUES (?,?,?,?)",
        rows,
    )
    conn.commit()


def store_signals(conn: sqlite3.Connection, signals: list[StockSignal], created_at: str) -> None:
    rows = [
        (
            s.ticker,
            s.date,
            s.regime,
            s.raw_momentum,
            s.vol_90d,
            s.vam_score,
            s.percentile_rank,
            1 if s.vetoed else 0,
            s.veto_reason or None,
            s.rsi,
            s.entry_mode,
            1 if s.qualified else 0,
            created_at,
        )
        for s in signals
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO signals_v2 "
        "(ticker, date, regime, raw_momentum, vol_90d, vam_score, percentile_rank, "
        " vetoed, veto_reason, rsi, entry_mode, qualified, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
