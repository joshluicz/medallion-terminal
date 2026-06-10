export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="w-full max-w-xl rounded-terminal border border-terminal-border bg-terminal-surface p-8">
        <p className="font-mono text-xxs uppercase tracking-widest text-terminal-gold">
          Medallion Terminal
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-terminal-white">
          Phase 0 — Foundation
        </h1>
        <p className="mt-4 text-sm text-terminal-dim">
          Dev server is running. Terminal UI panels arrive in Phase 3.
        </p>
      </div>
    </main>
  )
}
