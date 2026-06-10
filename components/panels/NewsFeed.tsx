'use client'

import { newsMock } from '@/lib/mockData'
import { colors } from '@/lib/theme'
import { TerminalPanel } from '@/components/ui/TerminalPanel'

export function NewsFeed() {
  return (
    <TerminalPanel title="News Feed">
      <ul className="max-h-[220px] space-y-0 overflow-y-auto text-xxs">
        {newsMock.map((item, i) => (
          <li
            key={`${item.ticker}-${i}`}
            className="py-2"
            style={{ borderBottom: i < newsMock.length - 1 ? `1px solid ${colors.border}` : undefined }}
          >
            <span
              className="mr-2 inline-block px-1 font-mono"
              style={{
                color: colors.cyan,
                border: `1px solid ${colors.cyan}44`,
                background: `${colors.cyan}0a`,
              }}
            >
              {item.ticker}
            </span>
            <span style={{ color: colors.white }}>{item.headline}</span>
            <span className="mt-1 block" style={{ color: colors.dim }}>
              {item.source} · {item.minsAgo}m ago
            </span>
          </li>
        ))}
      </ul>
    </TerminalPanel>
  )
}
