import { Download, FileText, Shield } from 'lucide-react'
import { api } from '../services/api'
import EvidenceGallery from './EvidenceGallery'

const RISK_COLORS = {
  LOW: 'text-green-400 bg-green-500/10 border-green-500/30',
  MEDIUM: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  HIGH: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
  CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/30',
}

function formatDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

function formatDuration(seconds) {
  if (!seconds) return '—'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}m ${s}s`
}

export default function ReportViewer({ report }) {
  if (!report) return null

  const { header, session, detection_summary, event_summary, incident_timeline, risk_summary, final_summary } = report

  const handleDownload = () => {
    window.open(api.downloadReport(session.session_id), '_blank')
  }

  const handlePrint = () => window.print()

  return (
    <div className="max-w-5xl mx-auto space-y-6 print:text-black print:bg-white">
      {/* Header */}
      <div className="panel p-8 text-center print:border-black">
        <Shield className="w-12 h-12 mx-auto text-cyan-400 mb-4 print:text-black" />
        <h1 className="text-3xl font-bold tracking-widest">{header.title}</h1>
        <p className="text-sm text-gray-400 mt-1 tracking-wide print:text-gray-600">{header.subtitle}</p>
        <p className="text-lg font-semibold mt-4 text-cyan-400 tracking-wider print:text-black">
          {header.report_type}
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-3 print:hidden">
        <button onClick={handleDownload} className="btn-primary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Download Report
        </button>
        <button onClick={handlePrint} className="btn-secondary flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Print Report
        </button>
      </div>

      {/* Session Info */}
      <div className="panel p-6">
        <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-4">Session Information</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 font-mono text-sm">
          <div><span className="text-gray-500">Session ID:</span> {session.session_id}</div>
          <div><span className="text-gray-500">Date:</span> {session.date}</div>
          <div><span className="text-gray-500">Start:</span> {formatDateTime(session.start_time)}</div>
          <div><span className="text-gray-500">End:</span> {formatDateTime(session.end_time)}</div>
          <div><span className="text-gray-500">Duration:</span> {formatDuration(session.duration_seconds)}</div>
          <div><span className="text-gray-500">Camera:</span> {session.camera_source}</div>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="panel p-4 text-center">
          <div className="text-3xl font-bold font-mono text-blue-400">{detection_summary.unique_persons}</div>
          <div className="text-xs text-gray-500 uppercase mt-1">Persons Detected</div>
        </div>
        <div className="panel p-4 text-center">
          <div className="text-3xl font-bold font-mono text-purple-400">{detection_summary.unique_vehicles}</div>
          <div className="text-xs text-gray-500 uppercase mt-1">Vehicles Detected</div>
        </div>
        <div className="panel p-4 text-center">
          <div className="text-3xl font-bold font-mono text-cyan-400">{event_summary.total_events}</div>
          <div className="text-xs text-gray-500 uppercase mt-1">Total Events</div>
        </div>
        <div className={`panel p-4 text-center border ${RISK_COLORS[risk_summary.level] || ''}`}>
          <div className="text-3xl font-bold font-mono">{risk_summary.level}</div>
          <div className="text-xs uppercase mt-1 opacity-70">Risk Level (Score: {risk_summary.score})</div>
        </div>
      </div>

      {/* Event summary */}
      <div className="panel p-6">
        <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-4">Event Summary</h2>
        <div className="grid grid-cols-4 gap-4 font-mono text-sm">
          <div className="text-blue-400">INFO: {event_summary.info_events}</div>
          <div className="text-amber-400">WARNING: {event_summary.warning_events}</div>
          <div className="text-red-400">CRITICAL: {event_summary.critical_events}</div>
          <div className="text-gray-300">TOTAL: {event_summary.total_events}</div>
        </div>
        <p className="text-xs text-gray-500 mt-3 italic">{risk_summary.disclaimer}</p>
      </div>

      {/* Incident timeline */}
      <div className="panel p-6">
        <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-4">Incident Timeline</h2>
        {incident_timeline.length === 0 ? (
          <p className="text-gray-500 text-sm">No warning or critical incidents recorded.</p>
        ) : (
          <div className="space-y-3">
            {incident_timeline.map((item, i) => (
              <div key={i} className="flex gap-4 text-sm font-mono border-b border-gray-800 pb-2">
                <span className="text-gray-500 w-20 shrink-0">
                  {item.time ? new Date(item.time).toLocaleTimeString('en-GB', { hour12: false }) : '—'}
                </span>
                <span className={
                  item.severity === 'CRITICAL' ? 'text-red-400 w-20' :
                  item.severity === 'WARNING' ? 'text-amber-400 w-20' : 'text-gray-400 w-20'
                }>{item.severity}</span>
                <span className="text-gray-300 flex-1">{item.description}</span>
                {item.track_id && <span className="text-cyan-400">{item.track_id}</span>}
                {item.confidence && <span className="text-gray-500">{Math.round(item.confidence * 100)}%</span>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Evidence gallery */}
      <EvidenceGallery items={report.evidence_gallery || []} />

      {/* Final summary */}
      <div className="panel p-6 border-l-4 border-cyan-500">
        <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-2">Final Summary</h2>
        <p className="text-gray-200">{final_summary}</p>
      </div>
    </div>
  )
}
