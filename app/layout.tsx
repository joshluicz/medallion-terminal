import type { Metadata } from 'next'
import { Inter, JetBrains_Mono, Orbitron, Space_Grotesk } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
})

const orbitron = Orbitron({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['500', '600', '700'],
})

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space',
  weight: ['400', '500', '600'],
})

export const metadata: Metadata = {
  title: 'Medallion Terminal',
  description: 'AI-assisted cyberpunk trading terminal',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} ${orbitron.variable} ${spaceGrotesk.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  )
}
