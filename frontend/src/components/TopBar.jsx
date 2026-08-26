import { Shield, Wifi, WifiOff } from 'lucide-react'

export default function TopBar({ backendOnline, wsConnected, aiPipeline }) {
  return (
    <header className="panel px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <Shield className="w-8 h-8 text-cyan-400" />
        <div>
          <h1 className="text-xl font-bold tracking-wider text-white">IBVAP</h1>
          <p className="text-xs text-gray-400 tracking-wide">
            Intelligent Border Video Analytics Platform
          </p>
        </div>
      </div>

      <div className="flex items-center gap-6 text-sm font-mono">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">SYSTEM STATUS:</span>
          <span className={`status-dot ${backendOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className={backendOnline ? 'text-green-400' : 'text-red-400'}>
            {backendOnline ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>

        <div className="flex items-center gap-2 text-gray-400">
          {wsConnected ? (
            <Wifi className="w-4 h-4 text-green-400" />
          ) : (
            <WifiOff className="w-4 h-4 text-red-400" />
          )}
          <span>WS {wsConnected ? 'CONNECTED' : 'DISCONNECTED'}</span>
        </div>

        <div className="px-3 py-1 rounded bg-gray-800 border border-gray-700">
          <span className="text-gray-400">AI: </span>
          <span className={aiPipeline === 'stub' ? 'text-amber-400' : 'text-green-400'}>
            {aiPipeline === 'stub' ? 'NOT ACTIVE (Phase 3)' : aiPipeline.toUpperCase()}
          </span>
        </div>
      </div>
    </header>
  )
}
