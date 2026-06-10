import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'terminal': {
          'black':   '#080b12',
          'surface': '#0c1019',
          'border':  'rgba(0, 212, 255, 0.22)',
          'muted':   '#3d4a5c',
          'white':   '#e8ecf4',
          'dim':     '#6b7a94',
          'gold':    '#f0c040',
          'red':     '#ff2d55',
          'green':   '#00ff88',
          'blue':    '#00d4ff',
          'purple':  '#9d00ff',
        },
      },
      fontFamily: {
        sans:  ['var(--font-inter)', 'system-ui', 'sans-serif'],
        display: ['var(--font-display)', 'Orbitron', 'sans-serif'],
        space: ['var(--font-space)', 'Space Grotesk', 'sans-serif'],
        mono:  ['var(--font-mono)', 'JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        'xxs': ['10px', { lineHeight: '1.4', letterSpacing: '0.08em' }],
      },
      borderRadius: {
        'terminal': '2px',
      },
    },
  },
  plugins: [],
}

export default config
