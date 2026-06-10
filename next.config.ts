import type { NextConfig } from 'next'

const ibkrGatewayUrl = process.env.IBKR_GATEWAY_URL

const nextConfig: NextConfig = {
  // Allow IBKR Client Portal API (self-signed cert in local dev)
  async rewrites() {
    if (!ibkrGatewayUrl) return []

    return [
      {
        source: '/api/ibkr/:path*',
        destination: `${ibkrGatewayUrl}/:path*`,
      },
    ]
  },
}

export default nextConfig
