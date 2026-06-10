'use client'

import { portfolioMock } from '@/lib/mockData'
import { colors, fonts } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

export function PortfolioPnL() {
  const positive = portfolioMock.vsVooPct >= 0

  return (
    <TerminalPanel title="Portfolio P&L">
      <div className="space-y-3">
        <div>
          <p className="text-xxs uppercase tracking-widest" style={{ color: colors.dim }}>
            Net Liquidation Value
          </p>
          <p
            className="text-2xl font-semibold tabular-nums"
            style={{ fontFamily: fonts.mono, color: colors.cyan }}
          >
            {portfolioMock.nlv}
          </p>
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-xxs" style={{ color: colors.dim }}>
            vs VOO
          </span>
          <span
            className="font-mono text-sm font-medium"
            style={{ color: positive ? colors.positive : colors.negative }}
          >
            {positive ? '+' : ''}
            {portfolioMock.vsVooPct}%
          </span>
        </div>

        <div className="space-y-2 pt-1">
          {portfolioMock.buckets.map((b) => (
            <div key={b.id}>
              <div className="mb-1 flex justify-between text-xxs">
                <span style={{ color: colors.dim }}>{b.label}</span>
                <span className="font-mono" style={{ color: colors.white }}>
                  {b.actual}%
                </span>
              </div>
              <div className="h-1.5" style={{ background: colors.muted }}>
                <div
                  className="h-full"
                  style={{
                    width: `${b.actual}%`,
                    background: b.color,
                    boxShadow: `0 0 6px ${b.color}55`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        <div
          className="flex justify-between border-t pt-2 text-xxs"
          style={{ borderColor: colors.border }}
        >
          <span style={{ color: colors.dim }}>Buying Power</span>
          <span className="font-mono" style={{ color: colors.white }}>
            {portfolioMock.buyingPower}
          </span>
        </div>
      </div>
    </TerminalPanel>
  )
}
