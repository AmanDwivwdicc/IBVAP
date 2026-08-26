import { ShieldAlert, Video, Info } from 'lucide-react'

import VirtualFenceCanvas from './VirtualFenceCanvas'
import DetectionOverlay from './DetectionOverlay'

export default function CameraFeed({
  videoRef,
  sessionStatus,
  border,
  isDrawingBorder,
  onBorderComplete,
  tracks = [],
  aiPipeline,
  cameraError,
}) {
  const isActive = sessionStatus === 'surveillance_active'

  const hasCamera =
    sessionStatus !== 'idle' &&
    sessionStatus !== 'camera_offline'

  return (
    <div className="panel flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-4 py-2 border-b border-ibvap-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Video className="w-4 h-4 text-cyan-400" />

          <span className="text-sm font-semibold tracking-wider uppercase text-gray-300">
            Live Surveillance
          </span>
        </div>

        {isActive && (
          <span className="flex items-center gap-1.5 text-xs font-mono text-red-400">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            REC
          </span>
        )}
      </div>

      {/* Video coordinate surface */}
      <div
        className={`relative bg-black aspect-video overflow-hidden ${
          isActive ? 'ring-2 ring-cyan-500/30' : ''
        }`}
      >
        {/* Camera unavailable */}
        {!hasCamera && !cameraError && (
          <div className="absolute inset-0 flex items-center justify-center z-10 text-center text-gray-500 space-y-2">
            <div>
              <Video className="w-12 h-12 mx-auto opacity-30" />
              <p className="text-sm mt-2">
                Enable webcam to begin
              </p>
            </div>
          </div>
        )}

        {/* Camera error */}
        {cameraError && (
          <div className="absolute inset-0 flex items-center justify-center z-10 text-center text-red-400 space-y-2 p-4">
            <div>
              <ShieldAlert className="w-10 h-10 mx-auto" />
              <p className="text-sm mt-2">{cameraError}</p>
            </div>
          </div>
        )}

        {/* Camera */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`absolute inset-0 w-full h-full object-contain ${
            hasCamera ? 'block' : 'hidden'
          }`}
        />

        {/* Virtual fence */}
        <div className="absolute inset-0 z-20 pointer-events-auto">
          <VirtualFenceCanvas
            videoRef={videoRef}
            border={border}
            isDrawing={isDrawingBorder}
            onBorderComplete={onBorderComplete}
            disabled={sessionStatus === 'surveillance_active'}
          />
        </div>

        {/* YOLO detections */}
        <div className="absolute inset-0 z-50 pointer-events-none">
          <DetectionOverlay tracks={tracks} />
        </div>

        {/* AI status */}
        {aiPipeline === 'stub' && isActive && (
          <div className="absolute bottom-3 left-3 right-3 z-[60] bg-amber-500/20 border border-amber-500/40 rounded px-3 py-2 flex items-center gap-2 text-xs text-amber-300">
            <Info className="w-4 h-4 shrink-0" />
            AI detection not yet active — Phase 3 implementation pending
          </div>
        )}

        {/* Border drawing instruction */}
        {isDrawingBorder && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[70] bg-cyan-600/90 text-white text-xs px-4 py-1.5 rounded font-mono">
            Click two points to define virtual border
          </div>
        )}

        {/* Debug indicator */}
        {isActive && tracks.length > 0 && (
          <div className="absolute top-3 left-3 z-[70] bg-green-500/90 text-black text-xs px-3 py-1 rounded font-mono font-bold">
            AI: {tracks.length} OBJECT{tracks.length !== 1 ? 'S' : ''} DETECTED
          </div>
        )}
      </div>
    </div>
  )
}