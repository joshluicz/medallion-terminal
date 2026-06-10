# Medallion Terminal — Claude Code Context

> Load this file at the start of every Claude Code session. This is the single source of truth for project mandate, architecture, and decisions made.

---

## Who This Is For

**Joshua** — Singaporean NS serviceman, NUS matriculation 2028/2029.
Investor profile: total return mandate, benchmark VOO/SPY, target >10% annualised.
Brokerage: IBKR (primary). Stack: Next.js + TypeScript + Node.

**Claude's role:** No-BS portfolio manager + trading system architect.
Frameworks: Warren Buffett fundamentals × quant signal logic (Jane Street / Citadel / HRT style).

---

## Notion Workspace

| Page | URL |
|---|---|
| Master Hub | https://app.notion.com/p/37ae57d4d5da812c9cddf9328460a37b |
| Build Roadmap | https://app.notion.com/p/37ae57d4d5da8143af24d97c506e5236 |
| Trade Log | https://app.notion.com/p/37ae57d4d5da8134b30edd4c86d7a64b |

---

## Portfolio Architecture

### Three-Bucket Structure (deploys 12 Sep 2026 — FD maturity)

| Bucket | Allocation | Instrument | Purpose |
|---|---|---|---|
| B1 — Tuition Reserve | ~40% | Rolling MYR FD ladder @ 3.55% | Fund NUS tuition tranches |
| B2 — SGX Income | ~20% | MIT, CICT (REITs) | Zero-WHT dividend income; monthly DCA |
| B3 — Growth Engine | ~40% | QQQ/SCHG/VUG + Booster (~4%) | Total return; daily/weekly DCA |

### Booster Sleeve Rules
- Size: ~4% of total portfolio
- Can go to zero without affecting tuition bucket
- Conviction required: must pass signal score threshold before entry
- Hard stop: -30% from entry on speculative names

### Key Parameters
- Risk-free hurdle: 3.55% MYR FD rate
- WHT: only relevant for dividend instruments; growth ETFs exempt
- SGX DCA: monthly (commission friction); US ETFs: daily/weekly (zero commission IBKR)

---

## Cash Flow Schedule

| Period | Monthly Allowance | Investable (after SGD 300 living) |
|---|---|---|
| Now | SGD 1,200 | SGD 900 |
| Jan 2027 | SGD 1,400 | SGD 1,100 |
| End 2027 | SGD 1,600 | SGD 1,300 |

**FD maturity: 12 September 2026** — ~SGD 50,000 equivalent. Deployment split TBC (see open decisions).

---

## Signal Library v1

| Signal | Type | Weight |
|---|---|---|
| RSI(14) | Technical | 15% |
| MACD crossover | Technical | 15% |
| 50/200 MA golden/death cross | Technical | 10% |
| 12-1 month momentum vs SPY | Quantitative | 25% |
| Forward P/E vs sector median | Fundamental | 20% |
| EPS revision direction | Fundamental | 15% |

Composite score 0–100. Threshold for booster entry: >65. Exit signal: <40 or hard stop hit.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 14+ (App Router), TypeScript |
| Styling | Tailwind CSS — dark Bloomberg-style theme |
| Charts | TradingView Lightweight Charts or Recharts |
| Data | yfinance (free) → Polygon.io (upgrade path) |
| Database | Supabase (free tier) |
| Auth | Clerk or NextAuth |
| Deployment | Vercel |
| AI | Claude API (claude-sonnet-4-20250514) |
| Brokerage | IBKR Client Portal API |
| CI/CD | GitHub Actions |

---

## Dashboard Panels (Target State)

1. **Portfolio P&L** — live IBKR feed, vs VOO benchmark
2. **Watchlist + Signal Scores** — composite score per ticker
3. **Chart Panel** — candlestick + RSI + MACD + MA overlays
4. **Fundamental Snapshot** — P/E, PEG, EV/EBITDA, EPS trend
5. **News Feed** — filtered by watchlist tickers
6. **Cash Flow Tracker** — DCA schedule, bucket allocation, FD countdown
7. **Trade Staging** — Claude recommendations → approve/reject → IBKR execution
8. **Trade Log** — audit trail of all decisions

---

## Open Decisions

| Decision | Status |
|---|---|
| FD deployment split B1/B2/B3 | Pending clarification session (before 12 Sep 2026) |
| Data provider (free vs Polygon.io) | Decide at Phase 1 start |
| IBKR connection: TWS vs Client Portal API | Client Portal recommended (no local install needed) |
| Booster v1 pick post-FD | Pending signal engine build |

---

## Build Phases

- **Phase 0** — Foundation (repo, CLAUDE.md, env setup) ← YOU ARE HERE
- **Phase 1** — Data layer (fetcher, DB, scheduler)
- **Phase 2** — Signal engine (technicals, momentum, fundamentals, backtest)
- **Phase 3** — Terminal UI (Next.js, Bloomberg dark theme, all panels)
- **Phase 4** — Claude integration (API, trade staging, IBKR routing)
- **Phase 5** — Hardening + CV polish (Sharpe tracker, PDF export, demo video)

---

## Working Principles

- Every trade recommendation must include: signal triggers, Sharpe estimate, entry/exit levels, downside scenario
- No position enters without a defined exit
- Benchmark every decision against VOO total return
- Booster sleeve sized by asymmetric risk logic — upside must justify downside
- No capital sits idle — FD ladder and DCA windows enforce this
