'use client'

import { useEffect, useState } from 'react'
import { benchmarkMock, regimeMock } from '@/lib/mockData'
import { colors, fonts } from '@/lib/theme'

function MedallionLogo() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden>
      <path d="M4 4h8v8H4V4z" fill={colors.cyan} opacity="0.9" />
      <path d="M16 4h8v8h-8V4z" fill={colors.violet} opacity="0.7" />
      <path d="M4 16h20v8H4v-8z" fill={colors.cyan} opacity="0.35" />
      <path d="M2 2h24v24" stroke={colors.cyan} strokeWidth="1" />
    </svg>
  )
}

function formatSGT(date: Date) {
  return date.toLocaleString('en-SG', {
    timeZone: 'Asia/Singapore',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function TopBar() {
  const [clock, setClock] = useState('')

  useEffect(() => {
    const tick = () => setClock(formatSGT(new Date()))
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  const riskOn = regimeMock.status === 'RISK_ON'

  return (
    <header
      className="flex h-11 items-center justify-between px-4"
      style={{
        background: colors.bgElevated,
        borderBottom: `1px solid ${colors.border}`,
        boxShadow: effectsShadow(),
      }}
    >
      <div className="flex items-center gap-3">
        <MedallionLogo />
        <div>
          <span
            className="text-sm font-semibold tracking-[0.25em]"
            style={{ fontFamily: fonts.display, color: colors.cyan }}
          >
            MEDALLION
          </span>
          <span className="ml-3 text-xxs tracking-widest" style={{ color: colors.dim }}>
            TRADING TERMINAL
          </span>
          <span className="ml-2 font-mono text-xxs" style={{ color: colors.muted }}>
            v0.3.0-alpha
          </span>
        </div>
      </div>

      <div className="font-mono text-xs tabular-nums" style={{ color: colors.white }}>
        {clock} <span style={{ color: colors.dim }}>SGT</span>
      </div>

      <div className="flex items-center gap-5 text-xxs uppercase tracking-wider">
        <div className={`regime-badge ${riskOn ? 'regime-on' : 'regime-off'}`}>
          <span className="live-dot" />
          REGIME: {regimeMock.status}
        </div>
        <div style={{ color: colors.dim }}>
          BENCHMARK:{' '}
          <span style={{ color: colors.white }}>
            {benchmarkMock.ticker} +{benchmarkMock.ytdPct}% YTD
          </span>
        </div>
        <div className="claude-shimmer" style={{ color: colors.violet }}>
          ◆ CLAUDE ACTIVE
        </div>
        <div className="flex items-center gap-1.5" style={{ color: colors.cyan }}>
          <span className="live-dot" />
          LIVE
        </div>
      </div>
    </header>
  )
}

function effectsShadow() {
  return `0 0 12px ${colors.borderGlow}`
}
