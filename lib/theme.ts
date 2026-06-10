/** Cyberpunk terminal design tokens — single source of truth */

export const colors = {
  bg: '#080b12',
  bgPanel: '#0c1019',
  bgElevated: '#111827',
  cyan: '#00d4ff',
  cyanDim: 'rgba(0, 212, 255, 0.45)',
  violet: '#9d00ff',
  violetDim: 'rgba(157, 0, 255, 0.5)',
  positive: '#00ff88',
  negative: '#ff2d55',
  gold: '#f0c040',
  white: '#e8ecf4',
  dim: '#6b7a94',
  muted: '#3d4a5c',
  border: 'rgba(0, 212, 255, 0.22)',
  borderGlow: 'rgba(0, 212, 255, 0.15)',
  riskOff: '#ff2d55',
} as const

export const fonts = {
  display: 'var(--font-display), Orbitron, sans-serif',
  body: 'var(--font-inter), Inter, system-ui, sans-serif',
  mono: 'var(--font-mono), JetBrains Mono, monospace',
} as const

export const spacing = {
  panelPadding: '12px',
  panelGap: '8px',
  gridGap: '6px',
} as const

export const effects = {
  panelShadow: `0 0 8px ${colors.borderGlow}`,
  panelBorder: `1px solid ${colors.border}`,
  scanlineOpacity: 0.03,
} as const

export const badges = {
  qualified: { label: 'QUALIFIED', color: colors.gold },
  watch: { label: 'WATCH', color: colors.cyan },
  neutral: { label: 'NEUTRAL', color: colors.dim },
} as const
