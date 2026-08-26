import { AlertTriangle, Info, ShieldAlert } from 'lucide-react'

const SEVERITY_ICON = {
  CRITICAL: ShieldAlert,
  WARNING: AlertTriangle,
  INFO: Info,
}

const SEVERITY_CLASS = {
  CRITICAL: 'severity-critical',
  WARNING: 'severity-warning',
  INFO: 'severity-info',
}

function formatTime(timestamp) {
  if (!timestamp) return '--:--:--'
  return new Date(timestamp).toLocaleTimeString('en-GB', { hour12: false })
}

export default function AlertPanel({ alerts, onAlertClick }) {
  return (
    <div className="panel flex flex-col h-full overflow-hidden">
      <div className="px-4 py-2 border-b border-ibvap-border">
        <h2 className="text-sm font-semibold tracking-wider uppercase text-gray-300">
          Real-Time Alerts
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {alerts.length === 0 && (
          <div className="text-center text-gray-500 text-sm py-8">
            No alerts yet
          </div>
        )}

        {alerts.map((alert) => {
          const Icon = SEVERITY_ICON[alert.severity] || Info
          const cls = SEVERITY_CLASS[alert.severity] || 'severity-info'

          return (
            <button
              key={alert.event_id}
              onClick={() => onAlertClick?.(alert)}
              className={`w-full text-left p-3 rounded ${cls} hover:bg-white/5 transition-colors`}
            >
              <div className="flex items-start gap-2">
                <Icon className="w-4 h-4 mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-mono font-bold">{alert.severity}</span>
                    <span className="text-xs font-mono text-gray-500">
                      {formatTime(alert.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm font-medium mt-0.5">{alert.event_type}</p>
                  <p className="text-xs text-gray-400 mt-0.5 truncate">{alert.message}</p>
                  {alert.track_id && (
                    <span className="text-xs font-mono text-cyan-400">{alert.track_id}</span>
                  )}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
