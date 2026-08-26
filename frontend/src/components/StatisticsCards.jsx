import { Activity, AlertTriangle, Car, ShieldAlert, Users } from 'lucide-react'

export default function StatisticsCards({ stats, sessionStatus }) {
  const cards = [
    { label: 'Persons', value: stats.persons, icon: Users, color: 'text-blue-400' },
    { label: 'Vehicles', value: stats.vehicles, icon: Car, color: 'text-purple-400' },
    { label: 'Events', value: stats.total_events, icon: Activity, color: 'text-cyan-400' },
    { label: 'Critical', value: stats.critical_events, icon: ShieldAlert, color: 'text-red-400' },
    { label: 'Warnings', value: stats.warning_events, icon: AlertTriangle, color: 'text-amber-400' },
  ]

  return (
    <div className="panel p-4">
      <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-3">
        Session Statistics
      </h2>

      {sessionStatus === 'idle' && (
        <p className="text-xs text-gray-500 mb-3">Statistics available during surveillance</p>
      )}

      <div className="grid grid-cols-5 gap-3">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-gray-800/50 rounded-lg p-3 text-center border border-gray-700/50">
            <Icon className={`w-4 h-4 mx-auto mb-1 ${color}`} />
            <div className="text-2xl font-bold font-mono">{value}</div>
            <div className="text-xs text-gray-500 uppercase tracking-wide">{label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
