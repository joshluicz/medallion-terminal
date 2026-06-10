'use client'

import { useState } from 'react'
import { fundamentalMock } from '@/lib/mockData'
import { colors } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

const tickers = Object.keys(fundamentalMock)

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="py-1.5">
      <p className="text-xxs uppercase tracking-wider" style={{ color: colors.dim }}>
        {label}
      </p>
      <p className="font-mono text-sm" style={{ color: colors.white }}>
        {value}
      </p>
    </div>
  )
}

export function FundamentalSnapshot() {
  const [selected, setSelected] = useState('BK')
  const data = fundamentalMock[selected as keyof typeof fundamentalMock]

  return (
    <TerminalPanel title="Fundamentals">
      <div className="flex gap-4">
        <div className="w-16 shrink-0 space-y-1">
          {tickers.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setSelected(t)}
              className="block w-full px-2 py-1 text-left font-mono text-xxs"
              style={{
                color: selected === t ? colors.cyan : colors.dim,
                border: selected === t ? `1px solid ${colors.cyan}44` : '1px solid transparent',
                background: selected === t ? `${colors.cyan}11` : 'transparent',
              }}
            >
              {t}
            </button>
          ))}
        </div>
        <div className="grid flex-1 grid-cols-2 gap-x-4">
          <Metric label="Forward P/E" value={data.forwardPe} />
          <Metric label="Trailing P/E" value={data.trailingPe} />
          <Metric label="EV/EBITDA" value={data.evEbitda} />
          <Metric label="EPS (TTM)" value={data.epsTtm} />
          <Metric label="Next Earnings" value={data.nextEarnings} />
          <Metric label="Analyst Target" value={`$${data.analystTarget}`} />
          <Metric label="52W High" value={`$${data.high52w}`} />
          <Metric label="52W Low" value={`$${data.low52w}`} />
          <Metric label="Vol (90d avg)" value={data.volume90d} />
        </div>
      </div>
    </TerminalPanel>
  )
}
