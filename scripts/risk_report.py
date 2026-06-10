#!/usr/bin/env python3
"""
Medallion Terminal -- risk agent output: QuantStats tearsheet generator.

Accepts a daily return series and writes an HTML performance/risk report
to reports/. Intended as the deliverable from the risk analysis agent.

Usage:
    # From a CSV (columns: date, return)
    python scripts/risk_report.py --returns-file returns/strategy.csv

    # Quick sanity check: build returns from a ticker in the local DB
    python scripts/risk_report.py --ticker VOO

    # With benchmark comparison (default benchmark: VOO)
    python scripts/risk_report.py --returns-file returns/strategy.csv --benchmark VOO
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "medallion.db"
REPORTS_DIR = REPO_ROOT / "reports"
DEFAULT_BENCHMARK = "VOO"


# ---- Load returns -----------------------------------------------------------

def _normalise_returns(series: pd.Series, name: str) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        raise ValueError(f"No valid returns found for {name}.")

    if not isinstance(s.index, pd.DatetimeIndex):
        s.index = pd.to_datetime(s.index)

    s = s.sort_index()
    s.name = name
    return s


def load_returns_from_csv(path: Path, name: str = "Strategy") -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Returns file is empty: {path}")

    date_col = next((c for c in df.columns if c.lower() in {"date", "datetime", "time"}), df.columns[0])
    ret_col = next(
        (c for c in df.columns if c.lower() in {"return", "returns", "ret", "daily_return"}),
        None,
    )
    if ret_col is None:
        numeric = [c for c in df.columns if c != date_col and pd.api.types.is_numeric_dtype(df[c])]
        if not numeric:
            raise ValueError(f"Could not find a return column in {path}")
        ret_col = numeric[0]

    df[date_col] = pd.to_datetime(df[date_col])
    series = df.set_index(date_col)[ret_col]
    return _normalise_returns(series, name)


def load_returns_from_json(path: Path, name: str = "Strategy") -> pd.Series:
    raw = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(raw, dict) and "returns" in raw:
        payload = raw["returns"]
    else:
        payload = raw

    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict):
            df = pd.DataFrame(payload)
            date_col = next((c for c in df.columns if c.lower() in {"date", "datetime"}), df.columns[0])
            ret_col = next((c for c in df.columns if c.lower() in {"return", "returns", "ret"}), df.columns[-1])
            df[date_col] = pd.to_datetime(df[date_col])
            series = df.set_index(date_col)[ret_col]
        else:
            series = pd.Series(payload, name=name)
            series.index = pd.date_range(end=pd.Timestamp.today().normalize(), periods=len(series), freq="B")
    else:
        raise ValueError(f"Unsupported JSON returns format in {path}")

    return _normalise_returns(series, name)


def load_returns_from_db(ticker: str) -> pd.Series:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DB not found at {DB_PATH}. Run scripts/fetch_data.py first."
        )

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, close FROM prices WHERE ticker = ? ORDER BY date",
        conn,
        params=(ticker.upper(),),
        parse_dates=["date"],
        index_col="date",
    )
    conn.close()

    if df.empty:
        raise ValueError(f"No price data for {ticker} in local DB.")

    returns = df["close"].pct_change().dropna()
    return _normalise_returns(returns, ticker.upper())


def load_returns(path: Path | None, ticker: str | None, name: str) -> pd.Series:
    if path is not None:
        suffix = path.suffix.lower()
        if suffix == ".json":
            return load_returns_from_json(path, name=name)
        return load_returns_from_csv(path, name=name)

    if ticker is not None:
        return load_returns_from_db(ticker.upper())

    raise ValueError("Provide --returns-file or --ticker.")


def load_benchmark(
    benchmark_file: Path | None,
    benchmark_ticker: str | None,
) -> pd.Series | None:
    if benchmark_file is not None:
        return load_returns_from_csv(benchmark_file, name="Benchmark")
    if benchmark_ticker is None:
        return None
    return load_returns_from_db(benchmark_ticker.upper())


# ---- Report -----------------------------------------------------------------

def default_output_path(label: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in label)
    return REPORTS_DIR / f"risk_report_{safe}_{stamp}.html"


def generate_tearsheet(
    returns: pd.Series,
    output: Path,
    *,
    title: str,
    benchmark: pd.Series | None = None,
) -> Path:
    try:
        import quantstats as qs
    except ImportError as exc:
        raise ImportError(
            "quantstats not installed. Run: pip install -r requirements.txt"
        ) from exc

    output.parent.mkdir(parents=True, exist_ok=True)

    qs.reports.html(
        returns,
        benchmark=benchmark,
        output=str(output),
        title=title,
        download_filename=output.name,
    )

    return output


# ---- CLI --------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a QuantStats HTML tearsheet for a return series"
    )
    parser.add_argument(
        "--returns-file",
        type=Path,
        help="CSV or JSON file with daily returns (date + return columns)",
    )
    parser.add_argument(
        "--ticker",
        help="Build returns from ticker prices in data/medallion.db (sanity-check mode)",
    )
    parser.add_argument(
        "--name",
        default="Strategy",
        help="Label for the return series in the report",
    )
    parser.add_argument(
        "--benchmark",
        nargs="?",
        const=DEFAULT_BENCHMARK,
        default=None,
        help=f"Benchmark ticker from local DB (default when flag given: {DEFAULT_BENCHMARK})",
    )
    parser.add_argument(
        "--benchmark-file",
        type=Path,
        help="Benchmark returns CSV/JSON (overrides --benchmark ticker)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output HTML path (default: reports/risk_report_<name>_<timestamp>.html)",
    )
    args = parser.parse_args()

    try:
        returns = load_returns(args.returns_file, args.ticker, args.name)
        benchmark = load_benchmark(args.benchmark_file, args.benchmark)

        label = returns.name or args.name
        output = args.output or default_output_path(label)
        if not output.is_absolute():
            output = REPO_ROOT / output

        title = f"Medallion Terminal — {label} Risk Report"
        path = generate_tearsheet(returns, output, title=title, benchmark=benchmark)

        print(f"\n{'=' * 60}")
        print("  Medallion Terminal -- Risk Report")
        print(f"  Series    : {label}")
        print(f"  Period    : {returns.index[0].date()} -> {returns.index[-1].date()}")
        print(f"  Days      : {len(returns)}")
        if benchmark is not None:
            print(f"  Benchmark : {benchmark.name}")
        print(f"  Output    : {path}")
        print(f"{'=' * 60}\n")

    except Exception as exc:
        print(f"[!!] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
