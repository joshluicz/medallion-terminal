'use client'

import { useEffect, useState } from 'react'
import { cashFlowMock } from '@/lib/mockData'
import { colors, fonts } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

export function CashFlowTracker() {
  const [days, setDays] = useState(cashFlowMock.daysRemaining)

  useEffect(() => {
    const id = setInterval(() => {
      setDays((d) => (d > 0 ? d - 1 : 0))
    }, 86400000)
    return () => clearInterval(id)
  }, [])

  return (
    <TerminalPanel title="Cash Flow">
      <div className="mb-4 text-center">
        <p className="text-xxs uppercase tracking-[0.2em]" style={{ color: colors.dim }}>
          FD matures in
        </p>
        <p
          className="countdown-tick text-4xl font-bold tabular-nums"
          style={{ fontFamily: fonts.display, color: colors.cyan }}
        >
          {days}
        </p>
        <p className="font-mono text-xxs" style={{ color: colors.cyanDim }}>
          DAYS — {cashFlowMock.fdMaturityDate}
        </p>
      </div>

      <table className="mb-4 w-full text-xxs">
        <thead>
          <tr style={{ color: colors.dim }}>
            <th className="pb-1 text-left font-normal">Month</th>
            <th className="pb-1 text-right font-normal">Investable</th>
            <th className="pb-1 text-right font-normal">B1</th>
            <th className="pb-1 text-right font-normal">B2</th>
            <th className="pb-1 text-right font-normal">B3</th>
          </tr>
        </thead>
        <tbody>
          {cashFlowMock.dcaSchedule.map((row) => (
            <tr key={row.month} style={{ borderTop: `1px solid ${colors.border}` }}>
              <td className="py-1" style={{ color: colors.white }}>
                {row.month}
              </td>
              <td className="py-1 text-right font-mono">{row.investable}</td>
              <td className="py-1 text-right font-mono">{row.b1}</td>
              <td className="py-1 text-right font-mono">{row.b2}</td>
              <td className="py-1 text-right font-mono">{row.b3}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="space-y-2">
        {cashFlowMock.bucketProgress.map((b) => (
          <div key={b.label}>
            <div className="mb-1 flex justify-between text-xxs">
              <span style={{ color: colors.dim }}>{b.label}</span>
              <span className="font-mono" style={{ color: colors.white }}>
                {b.actual}% / {b.target}%
              </span>
            </div>
            <div className="h-1" style={{ background: colors.muted }}>
              <div
                className="h-full"
                style={{
                  width: `${(b.actual / b.target) * 100}%`,
                  maxWidth: '100%',
                  background: colors.cyan,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </TerminalPanel>
  )
}
