'use client'

import dynamic from 'next/dynamic'
import { useState } from 'react'
import { chartTickers, type ChartTicker } from '@/lib/mockData'
import { colors } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

const ChartPanelInner = dynamic(
  () => import('./ChartPanelInner').then((m) => m.ChartPanelInner),
  { ssr: false, loading: () => <ChartSkeleton /> },
)

function ChartSkeleton() {
  return (
    <div
      className="flex h-[360px] items-center justify-center font-mono text-xxs uppercase tracking-widest"
      style={{ color: colors.cyanDim }}
    >
      Initialising chart feed…
    </div>
  )
}

export function ChartPanel() {
  const [ticker, setTicker] = useState<ChartTicker>('VOO')

  return (
    <TerminalPanel
      title={`Chart — ${ticker}`}
      headerRight={
        <div className="flex gap-1">
          {chartTickers.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTicker(t)}
              className="px-2 py-0.5 font-mono text-xxs"
              style={{
                color: ticker === t ? colors.cyan : colors.dim,
                border: ticker === t ? `1px solid ${colors.cyan}` : `1px solid ${colors.muted}`,
                background: ticker === t ? `${colors.cyan}12` : 'transparent',
              }}
            >
              {t}
            </button>
          ))}
        </div>
      }
    >
      <ChartPanelInner ticker={ticker} />
    </TerminalPanel>
  )
}
