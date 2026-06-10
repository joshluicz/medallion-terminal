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
          'black':   '#0a0a0f',
          'surface': '#111118',
          'border':  '#1e1e2e',
          'muted':   '#2a2a3a',
          'white':   '#e8e8f0',
          'dim':     '#6e6e8a',
          'gold':    '#f0b429',
          'red':     '#ff4d6a',
          'green':   '#00d68f',
          'blue':    '#4da6ff',
          'purple':  '#9d7aff',
        },
      },
      fontFamily: {
        sans:  ['var(--font-inter)', 'system-ui', 'sans-serif'],
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
