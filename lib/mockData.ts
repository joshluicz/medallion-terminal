/** MOCK — replace with live feeds in Phase 4 */

export const portfolioMock = {
  nlv: 'SGD 5,598',
  vsVooPct: 2.3,
  buyingPower: 'SGD 412',
  buckets: [
    { id: 'B1', label: 'B1 — FD', target: 40, actual: 38, color: '#00d4ff' },
    { id: 'B2', label: 'B2 — REITs', target: 20, actual: 19, color: '#9d00ff' },
    { id: 'B3', label: 'B3 — Growth', target: 40, actual: 43, color: '#f0c040' },
  ],
}

export const benchmarkMock = {
  ticker: 'VOO',
  ytdPct: 23.9,
}

export const regimeMock = {
  status: 'RISK_ON' as const,
}

export const signalScoresMock = [
  { ticker: 'BK', vam: 1.994, percentile: 91.2, entryMode: 'STAGED', tier: 'qualified' as const },
  { ticker: 'NVDA', vam: 1.412, percentile: 78.4, entryMode: 'STAGED', tier: 'watch' as const },
  { ticker: 'MU', vam: 1.287, percentile: 72.1, entryMode: 'FULL', tier: 'watch' as const },
  { ticker: 'AMD', vam: 0.984, percentile: 68.5, entryMode: 'STAGED', tier: 'watch' as const },
  { ticker: 'META', vam: 0.721, percentile: 61.3, entryMode: 'STAGED', tier: 'watch' as const },
]

export const fundamentalMock = {
  BK: {
    forwardPe: 12.4,
    trailingPe: 14.8,
    evEbitda: 9.2,
    epsTtm: 4.12,
    nextEarnings: '2026-07-15',
    analystTarget: 118.0,
    high52w: 112.4,
    low52w: 78.2,
    volume90d: '4.2M',
  },
}

export const watchlistMock = [
  { ticker: 'BK', price: 108.42, change1d: 1.24, vam: 1.994, signal: 'qualified' as const },
  { ticker: 'NVDA', price: 142.18, change1d: 2.87, vam: 1.412, signal: 'watch' as const },
  { ticker: 'MU', price: 98.65, change1d: -0.42, vam: 1.287, signal: 'watch' as const },
  { ticker: 'VOO', price: 548.32, change1d: 0.31, vam: 0.412, signal: 'neutral' as const },
  { ticker: 'AMD', price: 124.55, change1d: 1.12, vam: 0.984, signal: 'watch' as const },
  { ticker: 'META', price: 678.9, change1d: -0.88, vam: 0.721, signal: 'watch' as const },
  { ticker: 'QQQ', price: 528.14, change1d: 0.55, vam: 0.388, signal: 'neutral' as const },
  { ticker: 'CRWV', price: 42.18, change1d: 3.21, vam: 0.654, signal: 'neutral' as const },
]

export const newsMock = [
  { ticker: 'BK', headline: 'Custody flows surge as institutional rebalancing accelerates', source: 'Bloomberg', minsAgo: 12 },
  { ticker: 'MU', headline: 'HBM supply tightens; analysts raise FY26 margin estimates', source: 'Reuters', minsAgo: 28 },
  { ticker: 'NVDA', headline: 'Data-centre capex guidance beats consensus for Q3', source: 'CNBC', minsAgo: 45 },
  { ticker: 'VOO', headline: 'S&P 500 extends rally as mega-cap earnings season kicks off', source: 'WSJ', minsAgo: 67 },
  { ticker: 'BK', headline: 'Fed stress-test preview: large banks show improved capital buffers', source: 'FT', minsAgo: 89 },
  { ticker: 'MU', headline: 'Memory spot prices firm for third consecutive week', source: 'Digitimes', minsAgo: 120 },
]

export const tradeStagingMock = {
  recommendation: 'BUY BK',
  signal: 'VAM 1.994 | Percentile 91.2',
  entry: 'STAGED (RSI 64.3 > 50)',
  tranche1: 'USD 82 (half booster)',
  stopLoss: 'USD 101.25 (-25%)',
  rationale:
    '8 consecutive earnings beats. Wide moat custody bank. Momentum confirmed.',
  tradeLog: [
    '2026-06-08  REJECT  NVDA  booster veto — EXTREME_FWD_PE',
    '2026-06-03  APPROVE  MU  tranche 1 filled @ 94.20',
    '2026-05-27  STAGED  QQQ  DCA B3 weekly — auto',
  ],
}

export const cashFlowMock = {
  fdMaturityDate: '2026-09-12',
  daysRemaining: 94,
  dcaSchedule: [
    { month: 'Jun 2026', investable: 900, b1: 360, b2: 180, b3: 360 },
    { month: 'Jul 2026', investable: 900, b1: 360, b2: 180, b3: 360 },
    { month: 'Aug 2026', investable: 900, b1: 360, b2: 180, b3: 360 },
  ],
  bucketProgress: [
    { label: 'B1 Tuition', target: 40, actual: 38 },
    { label: 'B2 SGX Income', target: 20, actual: 19 },
    { label: 'B3 Growth', target: 40, actual: 43 },
  ],
}

export const chartTickers = ['VOO', 'MU', 'NVDA', 'BK'] as const
export type ChartTicker = (typeof chartTickers)[number]

/** Generate 60 days of realistic-looking OHLCV */
export function generateMockOHLCV(seed = 42) {
  const days = 60
  let price = 100 + (seed % 20)
  const data: {
    time: string
    open: number
    high: number
    low: number
    close: number
  }[] = []

  const start = new Date()
  start.setDate(start.getDate() - days)

  for (let i = 0; i < days; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const drift = (Math.sin(i * 0.3 + seed) * 0.004 + (seed % 7) * 0.0003)
    const vol = 0.012 + (i % 5) * 0.002
    const open = price
    const change = (Math.random() - 0.48) * vol + drift
    const close = Math.max(10, open * (1 + change))
    const high = Math.max(open, close) * (1 + Math.random() * 0.008)
    const low = Math.min(open, close) * (1 - Math.random() * 0.008)
    price = close
    data.push({
      time: d.toISOString().slice(0, 10),
      open: +open.toFixed(2),
      high: +high.toFixed(2),
      low: +low.toFixed(2),
      close: +close.toFixed(2),
    })
  }
  return data
}

export function computeMA(data: { close: number }[], period: number): (number | null)[] {
  return data.map((_, i) => {
    if (i < period - 1) return null
    const slice = data.slice(i - period + 1, i + 1)
    return +(slice.reduce((s, b) => s + b.close, 0) / period).toFixed(2)
  })
}

export function computeRSI(data: { close: number }[], period = 14): (number | null)[] {
  const rsi: (number | null)[] = [null]
  const gains: number[] = []
  const losses: number[] = []

  for (let i = 1; i < data.length; i++) {
    const diff = data[i].close - data[i - 1].close
    gains.push(diff > 0 ? diff : 0)
    losses.push(diff < 0 ? -diff : 0)

    if (i < period) {
      rsi.push(null)
      continue
    }

    const avgGain = gains.slice(-period).reduce((a, b) => a + b, 0) / period
    const avgLoss = losses.slice(-period).reduce((a, b) => a + b, 0) / period
    if (avgLoss === 0) {
      rsi.push(100)
    } else {
      const rs = avgGain / avgLoss
      rsi.push(+(100 - 100 / (1 + rs)).toFixed(2))
    }
  }
  return rsi
}
