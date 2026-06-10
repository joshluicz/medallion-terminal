'use client'

import { regimeMock, signalScoresMock } from '@/lib/mockData'
import { badges, colors } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

function tierBadge(tier: 'qualified' | 'watch' | 'neutral') {
  const b = badges[tier]
  return (
    <span
      className="px-1.5 py-0.5 font-mono text-xxs uppercase"
      style={{
        color: b.color,
        border: `1px solid ${b.color}55`,
        background: `${b.color}11`,
      }}
    >
      {b.label}
    </span>
  )
}

export function SignalScores() {
  const riskOn = regimeMock.status === 'RISK_ON'

  return (
    <TerminalPanel
      title="Signal Scores"
      headerRight={
        <div className={`text-xxs regime-badge ${riskOn ? 'regime-on' : 'regime-off'}`}>
          <span className="live-dot" />◆ {regimeMock.status}
        </div>
      }
    >
      <table className="w-full text-left text-xxs">
        <thead>
          <tr style={{ color: colors.dim }}>
            <th className="pb-2 font-normal">Ticker</th>
            <th className="pb-2 font-normal">VAM</th>
            <th className="pb-2 font-normal">Pct</th>
            <th className="pb-2 font-normal">Entry</th>
            <th className="pb-2 font-normal">Tier</th>
          </tr>
        </thead>
        <tbody>
          {signalScoresMock.map((row) => (
            <tr key={row.ticker} style={{ borderTop: `1px solid ${colors.border}` }}>
              <td className="py-2 font-mono" style={{ color: colors.cyan }}>
                {row.ticker}
              </td>
              <td className="py-2 font-mono" style={{ color: colors.gold }}>
                {row.vam.toFixed(3)}
              </td>
              <td className="py-2 font-mono" style={{ color: colors.white }}>
                {row.percentile.toFixed(1)}
              </td>
              <td className="py-2" style={{ color: colors.dim }}>
                {row.entryMode}
              </td>
              <td className="py-2">{tierBadge(row.tier)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </TerminalPanel>
  )
}
