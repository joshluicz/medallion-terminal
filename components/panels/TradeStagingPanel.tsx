'use client'

import { tradeStagingMock } from '@/lib/mockData'
import { colors } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

export function TradeStagingPanel() {
  const m = tradeStagingMock

  return (
    <TerminalPanel title="◆ Claude — Trade Staging" accent="violet">
      <div
        className="space-y-2 p-3 text-xxs"
        style={{
          border: `1px solid ${colors.violet}44`,
          background: `${colors.violet}08`,
          boxShadow: `0 0 12px ${colors.violet}18`,
        }}
      >
        <p className="claude-shimmer font-mono uppercase tracking-widest" style={{ color: colors.violet }}>
          Recommendation: {m.recommendation}
        </p>
        <Row label="Signal" value={m.signal} />
        <Row label="Entry" value={m.entry} />
        <Row label="Tranche 1" value={m.tranche1} />
        <Row label="Stop loss" value={m.stopLoss} violet />
        <p className="pt-2 italic leading-relaxed" style={{ color: colors.dim }}>
          &ldquo;{m.rationale}&rdquo;
        </p>
        <div className="flex gap-3 pt-3">
          <button
            type="button"
            className="px-4 py-1.5 font-mono text-xxs uppercase tracking-wider"
            style={{
              color: colors.positive,
              border: `1px solid ${colors.positive}`,
              background: `${colors.positive}15`,
            }}
          >
            Approve
          </button>
          <button
            type="button"
            className="px-4 py-1.5 font-mono text-xxs uppercase tracking-wider"
            style={{
              color: colors.negative,
              border: `1px solid ${colors.negative}`,
              background: `${colors.negative}15`,
            }}
          >
            Reject
          </button>
        </div>
      </div>

      <div className="mt-3 space-y-1">
        <p className="text-xxs uppercase tracking-widest" style={{ color: colors.dim }}>
          Trade Log
        </p>
        {m.tradeLog.map((line) => (
          <p key={line} className="font-mono text-xxs leading-relaxed" style={{ color: colors.muted }}>
            {line}
          </p>
        ))}
      </div>
    </TerminalPanel>
  )
}

function Row({ label, value, violet }: { label: string; value: string; violet?: boolean }) {
  return (
    <div className="flex gap-2">
      <span className="w-20 shrink-0" style={{ color: colors.dim }}>
        {label}
      </span>
      <span className="font-mono" style={{ color: violet ? colors.violet : colors.white }}>
        {value}
      </span>
    </div>
  )
}
