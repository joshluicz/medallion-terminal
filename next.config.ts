import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Allow IBKR Client Portal API (self-signed cert in local dev)
  async rewrites() {
    return [
      {
        source: '/api/ibkr/:path*',
        destination: `${process.env.IBKR_GATEWAY_URL}/:path*`,
      },
    ]
  },
}

export default nextConfig
