'use client'

import type { ReactNode } from 'react'
import { colors, effects, fonts } from '@/lib/theme'

type TerminalPanelProps = {
  title: string
  children: ReactNode
  className?: string
  accent?: 'cyan' | 'violet'
  headerRight?: ReactNode
}

export function TerminalPanel({
  title,
  children,
  className = '',
  accent = 'cyan',
  headerRight,
}: TerminalPanelProps) {
  const accentColor = accent === 'violet' ? colors.violet : colors.cyan

  return (
    <section
      className={`terminal-panel ${className}`}
      style={{
        background: colors.bgPanel,
        border: effects.panelBorder,
        boxShadow: effects.panelShadow,
        fontFamily: fonts.body,
      }}
    >
      <header
        className="flex items-center justify-between px-3 py-2"
        style={{ borderBottom: `1px solid ${colors.border}` }}
      >
        <h2
          className="text-xxs uppercase tracking-[0.2em]"
          style={{ fontFamily: fonts.display, color: accentColor }}
        >
          {title}
        </h2>
        {headerRight}
      </header>
      <div className="p-3">{children}</div>
    </section>
  )
}
