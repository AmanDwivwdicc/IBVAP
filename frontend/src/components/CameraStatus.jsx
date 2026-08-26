import { Camera, CameraOff, Circle, Square } from 'lucide-react'

const STATUS_CONFIG = {
  idle: { label: 'CAMERA OFFLINE', color: 'text-gray-400', dot: 'bg-gray-500', icon: CameraOff },
  camera_offline: { label: 'CAMERA OFFLINE', color: 'text-gray-400', dot: 'bg-gray-500', icon: CameraOff },
  camera_ready: { label: 'CAMERA READY', color: 'text-green-400', dot: 'bg-green-500', icon: Camera },
  surveillance_active: { label: 'SURVEILLANCE ACTIVE', color: 'text-cyan-400', dot: 'bg-cyan-500 animate-pulse', icon: Circle },
  surveillance_stopped: { label: 'SURVEILLANCE STOPPED', color: 'text-amber-400', dot: 'bg-amber-500', icon: Square },
}

export default function CameraStatus({ status, sessionId, onEnableCamera, cameraError }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.idle
  const Icon = config.icon

  return (
    <div className="panel p-4 space-y-4">
      <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">Camera</h2>

      <div className="flex items-center gap-3">
        <Icon className={`w-5 h-5 ${config.color}`} />
        <span className={`status-dot ${config.dot}`} />
        <span className={`font-mono text-sm font-medium ${config.color}`}>
          {config.label}
        </span>
      </div>

      {sessionId && (
        <div className="text-xs font-mono text-gray-500 break-all">
          Session: {sessionId}
        </div>
      )}

      {(status === 'idle' || status === 'camera_offline') && (
        <button onClick={onEnableCamera} className="btn-primary w-full text-sm">
          Enable Webcam
        </button>
      )}

      {cameraError && (
        <div className="text-xs text-red-400 bg-red-500/10 p-2 rounded border border-red-500/30">
          {cameraError}
        </div>
      )}
    </div>
  )
}
