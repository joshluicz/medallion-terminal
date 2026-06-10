'use client'

import { watchlistMock } from '@/lib/mockData'
import { badges, colors } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

export function Watchlist() {
  return (
    <TerminalPanel title="Watchlist">
      <table className="w-full text-xxs">
        <thead>
          <tr style={{ color: colors.dim }}>
            <th className="pb-2 text-left font-normal">Ticker</th>
            <th className="pb-2 text-right font-normal">Price</th>
            <th className="pb-2 text-right font-normal">1D%</th>
            <th className="pb-2 text-right font-normal">
              VAM <span style={{ color: colors.cyan }}>↓</span>
            </th>
            <th className="pb-2 text-right font-normal">Signal</th>
          </tr>
        </thead>
        <tbody>
          {watchlistMock.map((row) => {
            const up = row.change1d >= 0
            const badge = badges[row.signal]
            return (
              <tr key={row.ticker} style={{ borderTop: `1px solid ${colors.border}` }}>
                <td className="py-1.5 font-mono" style={{ color: colors.cyan }}>
                  {row.ticker}
                </td>
                <td className="py-1.5 text-right font-mono" style={{ color: colors.white }}>
                  {row.price.toFixed(2)}
                </td>
                <td
                  className="py-1.5 text-right font-mono"
                  style={{ color: up ? colors.positive : colors.negative }}
                >
                  {up ? '+' : ''}
                  {row.change1d.toFixed(2)}%
                </td>
                <td className="py-1.5 text-right font-mono" style={{ color: colors.gold }}>
                  {row.vam.toFixed(3)}
                </td>
                <td className="py-1.5 text-right">
                  <span
                    className="px-1 font-mono uppercase"
                    style={{ color: badge.color, fontSize: '9px' }}
                  >
                    {badge.label}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </TerminalPanel>
  )
}
