import { Eraser, Pencil, Play, RotateCcw, Square } from 'lucide-react'

export default function SurveillanceControls({
  sessionStatus,
  border,
  isDrawingBorder,
  onDefineBorder,
  onClearBorder,
  onRedrawBorder,
  onStart,
  onStop,
  onReset,
  loading,
}) {
  const canStart =
    (sessionStatus === 'camera_ready' || sessionStatus === 'surveillance_stopped') &&
    border &&
    !loading

  const canStop = sessionStatus === 'surveillance_active' && !loading
  const canDefineBorder =
    sessionStatus !== 'surveillance_active' && sessionStatus !== 'idle' && sessionStatus !== 'camera_offline'
  const hasBorder = !!border

  return (
    <div className="panel p-4 space-y-4">
      <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">
        Surveillance Control
      </h2>

      <div className="space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onDefineBorder}
            disabled={!canDefineBorder || isDrawingBorder}
            className="btn-secondary flex items-center justify-center gap-2 text-sm"
          >
            <Pencil className="w-4 h-4" />
            Define Border
          </button>

          {hasBorder ? (
            <button
              onClick={onRedrawBorder}
              disabled={!canDefineBorder}
              className="btn-secondary flex items-center justify-center gap-2 text-sm"
            >
              <Pencil className="w-4 h-4" />
              Redraw Border
            </button>
          ) : (
            <button disabled className="btn-secondary flex items-center justify-center gap-2 text-sm opacity-40">
              <Pencil className="w-4 h-4" />
              Redraw Border
            </button>
          )}
        </div>

        <button
          onClick={onClearBorder}
          disabled={!hasBorder || sessionStatus === 'surveillance_active'}
          className="btn-secondary w-full flex items-center justify-center gap-2 text-sm"
        >
          <Eraser className="w-4 h-4" />
          Clear Border
        </button>
      </div>

      <div className="border-t border-ibvap-border pt-4 space-y-2">
        <button
          onClick={onStart}
          disabled={!canStart}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <Play className="w-4 h-4" />
          Start Surveillance
        </button>

        <button
          onClick={onStop}
          disabled={!canStop}
          className="btn-danger w-full flex items-center justify-center gap-2"
        >
          <Square className="w-4 h-4" />
          Stop Surveillance
        </button>

        <button
          onClick={onReset}
          disabled={sessionStatus === 'idle' || loading}
          className="btn-secondary w-full flex items-center justify-center gap-2 text-sm"
        >
          <RotateCcw className="w-4 h-4" />
          Reset Session
        </button>
      </div>

      {!border && canDefineBorder && (
        <p className="text-xs text-amber-400/80">
          Define a virtual border before starting surveillance.
        </p>
      )}
    </div>
  )
}
