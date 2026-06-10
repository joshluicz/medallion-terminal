"""
Medallion Terminal — investable universe definitions.

S&P 100 (OEX) constituents as of Q2 2026.
Refresh this list quarterly when index membership changes.
Source: S&P Dow Jones Indices OEX membership (manual snapshot).
"""

from __future__ import annotations

# S&P 100 — 100 large-cap US equities (OEX index)
# NOTE: Quarterly manual refresh required when constituents change.
SP100: list[str] = [
    "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT", "AMZN",
    "AVGO", "AXP", "BA", "BAC", "BK", "BKNG", "BLK", "BMY", "BRK-B", "C",
    "CAT", "CL", "CMCSA", "COF", "COP", "COST", "CRM", "CSCO", "CVS", "CVX",
    "DE", "DHR", "DIS", "DUK", "EMR", "EXC", "F", "FDX", "GD", "GE",
    "GILD", "GM", "GOOG", "GOOGL", "GS", "HD", "HON", "IBM", "INTC", "INTU",
    "ISRG", "JNJ", "JPM", "KO", "LIN", "LLY", "LMT", "LOW", "MA", "MCD",
    "MDLZ", "MDT", "MET", "META", "MMM", "MO", "MRK", "MS", "MSFT", "NEE",
    "NFLX", "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "PM", "PYPL", "QCOM",
    "RTX", "SBUX", "SCHW", "SO", "SPG", "T", "TGT", "TMO", "TMUS", "TSLA",
    "TXN", "UNH", "UNP", "UPS", "USB", "V", "VZ", "WFC", "WMT", "XOM",
]

# Portfolio / benchmark ETFs + booster names outside the S&P 100
HOLDINGS: list[str] = [
    "CRWV", "NBIS", "QQQM", "VXUS", "EWJV", "GLD", "VOO", "QQQ",
]

# SPY used for Layer 0 regime gate (not ranked for momentum)
REGIME_TICKER = "SPY"

# ETFs excluded from cross-sectional momentum ranking (DB + benchmarks only)
ETF_TICKERS: frozenset[str] = frozenset({
    "VOO", "QQQ", "QQQM", "VXUS", "EWJV", "GLD", "SPY",
})


def is_etf(ticker: str) -> bool:
    return ticker.upper() in ETF_TICKERS


def get_all_tickers() -> list[str]:
    """Deduped, sorted universe for fetch_data.py."""
    tickers = set(SP100) | set(HOLDINGS) | {REGIME_TICKER}
    return sorted(tickers)


def get_ranking_universe() -> list[str]:
    """Stocks eligible for TGVM cross-sectional ranking."""
    return sorted(set(SP100) | set(HOLDINGS) - ETF_TICKERS)
