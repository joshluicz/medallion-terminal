import { TopBar } from '@/components/TopBar'
import { CashFlowTracker } from '@/components/panels/CashFlowTracker'
import { ChartPanel } from '@/components/panels/ChartPanel'
import { FundamentalSnapshot } from '@/components/panels/FundamentalSnapshot'
import { NewsFeed } from '@/components/panels/NewsFeed'
import { PortfolioPnL } from '@/components/panels/PortfolioPnL'
import { SignalScores } from '@/components/panels/SignalScores'
import { TradeStagingPanel } from '@/components/panels/TradeStagingPanel'
import { Watchlist } from '@/components/panels/Watchlist'

export default function Home() {
  return (
    <div className="terminal-shell flex min-h-screen flex-col">
      <TopBar />
      <main className="grid flex-1 grid-cols-12 gap-1.5 p-1.5">
        {/* Row 1 */}
        <div className="col-span-12 lg:col-span-3">
          <PortfolioPnL />
        </div>
        <div className="col-span-12 lg:col-span-6">
          <ChartPanel />
        </div>
        <div className="col-span-12 lg:col-span-3">
          <SignalScores />
        </div>

        {/* Row 2 */}
        <div className="col-span-12 md:col-span-6 lg:col-span-4">
          <Watchlist />
        </div>
        <div className="col-span-12 md:col-span-6 lg:col-span-4">
          <FundamentalSnapshot />
        </div>
        <div className="col-span-12 lg:col-span-4">
          <NewsFeed />
        </div>

        {/* Row 3 */}
        <div className="col-span-12 lg:col-span-5">
          <TradeStagingPanel />
        </div>
        <div className="col-span-12 lg:col-span-7">
          <CashFlowTracker />
        </div>
      </main>
    </div>
  )
}
