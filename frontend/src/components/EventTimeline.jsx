const SEVERITY_DOT = {
  CRITICAL: 'bg-red-500',
  WARNING: 'bg-amber-500',
  INFO: 'bg-blue-500',
}

function formatTime(timestamp) {
  if (!timestamp) return '--:--:--'
  return new Date(timestamp).toLocaleTimeString('en-GB', { hour12: false })
}

export default function EventTimeline({ events }) {
  const timelineEvents = [...events].reverse()

  return (
    <div className="panel p-4">
      <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-3">
        Event Timeline
      </h2>

      <div className="max-h-48 overflow-y-auto space-y-1 font-mono text-xs">
        {timelineEvents.length === 0 && (
          <p className="text-gray-500 py-4 text-center">No events recorded</p>
        )}

        {timelineEvents.map((event) => (
          <div key={event.event_id} className="flex items-start gap-3 py-1.5 border-b border-gray-800/50">
            <span className="text-gray-500 shrink-0 w-16">{formatTime(event.timestamp)}</span>
            <span className={`status-dot mt-1.5 shrink-0 ${SEVERITY_DOT[event.severity] || 'bg-gray-500'}`} />
            <div className="flex-1 min-w-0">
              <span className={
                event.severity === 'CRITICAL' ? 'text-red-400' :
                event.severity === 'WARNING' ? 'text-amber-400' : 'text-gray-300'
              }>
                {event.severity === 'CRITICAL' && 'CRITICAL — '}
                {event.message || event.event_type}
              </span>
              {event.track_id && (
                <span className="text-cyan-400 ml-2">{event.track_id}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
