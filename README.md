# 🏅 Medallion Terminal

> An AI-assisted trading terminal for systematic signal generation, portfolio management, and discretionary trade execution. Named after Renaissance Technologies' Medallion Fund.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/medallion-terminal)

---

## What This Is

A personal Bloomberg-style trading terminal that combines:

- **Multi-factor signal engine** — RSI, MACD, momentum, fundamental filters, EPS revisions
- **Live portfolio tracking** — IBKR integration, real-time P&L vs VOO benchmark
- **AI trade recommendations** — Claude LLM analyses signal output and stages orders
- **One-click execution** — approve Claude's recommendation → routes to IBKR

Built for a total-return mandate targeting >10% annualised vs VOO/SPY.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Medallion Terminal                  │
│                  (Next.js + Vercel)                  │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
    ┌──────▼──────┐            ┌──────▼──────┐
    │  Data Layer │            │  AI Layer   │
    │  yfinance / │            │  Claude API │
    │  Polygon.io │            │  (Sonnet)   │
    └──────┬──────┘            └──────┬──────┘
           │                          │
    ┌──────▼──────┐            ┌──────▼──────┐
    │   Supabase  │            │ Trade Stage │
    │  (OHLCV +   │            │  → IBKR     │
    │  signals)   │            │  Client API │
    └─────────────┘            └─────────────┘
```

---

## Signal Library

| Signal | Type | Weight |
|---|---|---|
| RSI(14) | Technical | 15% |
| MACD crossover | Technical | 15% |
| 50/200 MA cross | Technical | 10% |
| 12-1 month momentum | Quantitative | 25% |
| Forward P/E vs sector | Fundamental | 20% |
| EPS revision direction | Fundamental | 15% |

Composite score 0–100. Entry threshold: >65.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Charts | TradingView Lightweight Charts |
| Database | Supabase |
| Auth | Clerk |
| AI | Anthropic Claude API |
| Brokerage | IBKR Client Portal API |
| Deployment | Vercel |

---

## Portfolio Context

See `CLAUDE.md` for full investor profile, mandate, and architecture decisions.

Notion workspace: [Master Hub](https://app.notion.com/p/37ae57d4d5da812c9cddf9328460a37b)

---

## Build Roadmap

- [x] Phase 0 — Foundation (repo, CLAUDE.md, env setup)
- [ ] Phase 1 — Data layer
- [ ] Phase 2 — Signal engine + backtest
- [ ] Phase 3 — Terminal UI
- [ ] Phase 4 — Claude integration + IBKR routing
- [ ] Phase 5 — Hardening + CV polish

---

## Disclaimer

This terminal is built for personal use. Nothing here constitutes financial advice. All trade execution requires explicit human approval.
