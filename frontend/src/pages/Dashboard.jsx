import { useCallback, useEffect, useRef, useState } from 'react'

import { useNavigate } from 'react-router-dom'

import AlertPanel from '../components/AlertPanel'
import CameraFeed from '../components/CameraFeed'
import CameraStatus from '../components/CameraStatus'
import EventTimeline from '../components/EventTimeline'
import StatisticsCards from '../components/StatisticsCards'
import SurveillanceControls from '../components/SurveillanceControls'
import TopBar from '../components/TopBar'

import { useSurveillance } from '../hooks/useSurveillance'
import { useWebcam } from '../hooks/useWebcam'
import { wsService } from '../services/websocket'

export default function Dashboard() {
  const navigate = useNavigate()

  const {
    videoRef,
    status: cameraStatus,
    error: cameraError,
    start: startCamera,
    stop: stopCamera,
    captureFrame,
  } = useWebcam()

  const {
    sessionStatus,
    sessionId,
    events,
    alerts,
    stats,
    border,
    detections,
    wsConnected,
    backendOnline,
    aiPipeline,
    error: surveillanceError,
    setSessionStatus,
    notifyCameraReady,
    saveBorder,
    clearBorder,
    startSurveillance,
    stopSurveillance,
    resetSession,
  } = useSurveillance()

  const [isDrawingBorder, setIsDrawingBorder] = useState(false)
  const [loading, setLoading] = useState(false)

  // Frame processing state.
  const frameTimerRef = useRef(null)
  const frameIdRef = useRef(0)
  const frameBusyRef = useRef(false)

  const effectiveStatus =
    cameraStatus === 'camera_offline' && sessionStatus === 'idle'
      ? 'idle'
      : cameraStatus === 'camera_ready' && sessionStatus === 'idle'
        ? 'camera_ready'
        : sessionStatus

  // --------------------------------------------------
  // Send webcam frames to backend while surveillance
  // is active.
  // --------------------------------------------------
  useEffect(() => {
    const shouldCapture =
      sessionStatus === 'surveillance_active' &&
      sessionId &&
      wsConnected &&
      cameraStatus === 'camera_ready'

    if (!shouldCapture) {
      if (frameTimerRef.current) {
        clearInterval(frameTimerRef.current)
        frameTimerRef.current = null
      }

      frameBusyRef.current = false
      return
    }

    // Prevent duplicate timers.
    if (frameTimerRef.current) {
      clearInterval(frameTimerRef.current)
    }

    frameTimerRef.current = setInterval(() => {
      // Do not queue another frame while the previous
      // frame is still being processed.
      if (frameBusyRef.current) {
        return
      }

      const image = captureFrame()

      if (!image) {
        return
      }

      frameBusyRef.current = true
frameIdRef.current += 1

if (frameIdRef.current % 5 === 0) {
  console.log(
    '[IBVAP] Sending AI frame:',
    frameIdRef.current,
  )
}

wsService.send({
        type: 'frame',
        session_id: sessionId,
        frame_id: frameIdRef.current,
        image,
      })
    }, 200)

    return () => {
      if (frameTimerRef.current) {
        clearInterval(frameTimerRef.current)
        frameTimerRef.current = null
      }

      frameBusyRef.current = false
    }
  }, [
    sessionStatus,
    sessionId,
    wsConnected,
    cameraStatus,
    captureFrame,
  ])

  // --------------------------------------------------
// Receive YOLO detection results
// --------------------------------------------------
useEffect(() => {
  const unsubscribe = wsService.on('detections', (data) => {
    frameBusyRef.current = false

    if (data?.frame_id % 5 === 0) {
      console.log(
        '[IBVAP] Detection response:',
        data?.detections?.length ?? 0,
        data?.detections,
      )
    }
  })

  return unsubscribe
}, [])

  // --------------------------------------------------
  // Camera
  // --------------------------------------------------
  const handleEnableCamera = useCallback(async () => {
    const ok = await startCamera()

    if (ok) {
      setSessionStatus('camera_ready')
      await notifyCameraReady(true)
    }
  }, [
    startCamera,
    setSessionStatus,
    notifyCameraReady,
  ])

  // --------------------------------------------------
  // Border
  // --------------------------------------------------
  const handleDefineBorder = () => {
    setIsDrawingBorder(true)
  }

  const handleBorderComplete = useCallback(
    async (borderData) => {
      setIsDrawingBorder(false)
      await saveBorder(borderData)
    },
    [saveBorder],
  )

  const handleClearBorder = useCallback(async () => {
    setIsDrawingBorder(false)
    await clearBorder()
  }, [clearBorder])

  const handleRedrawBorder = () => {
    clearBorder()
    setIsDrawingBorder(true)
  }

  // --------------------------------------------------
  // Start surveillance
  // --------------------------------------------------
  const handleStart = async () => {
    setLoading(true)

    try {
      await startSurveillance()
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Stop surveillance
  // --------------------------------------------------
  const handleStop = async () => {
    setLoading(true)

    try {
      const session = await stopSurveillance()

      if (session?.id) {
        navigate(`/report/${session.id}`)
      }
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Reset
  // --------------------------------------------------
  const handleReset = async () => {
    setLoading(true)

    try {
      stopCamera()
      await resetSession()
    } finally {
      setLoading(false)
    }
  }

  const displayError =
    cameraError || surveillanceError

    console.log('[IBVAP DASHBOARD STATE]', {
      detections,
      persons: detections.filter(
        (d) => d.object_type === 'PERSON',
      ).length,
      vehicles: detections.filter(
        (d) => d.object_type === 'VEHICLE',
      ).length,
    })
  return (
    <div className="min-h-screen p-4 space-y-4">
      <TopBar
        backendOnline={backendOnline}
        wsConnected={wsConnected}
        aiPipeline={aiPipeline}
      />

      {displayError && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-2 rounded text-sm font-mono">
          {displayError}
        </div>
      )}

      {!backendOnline && (
        <div className="bg-amber-500/10 border border-amber-500/30 text-amber-400 px-4 py-2 rounded text-sm">
          Backend unavailable. Start the FastAPI server on port 8000.
        </div>
      )}

      <div className="grid grid-cols-12 gap-4">
        {/* Left column */}
        <div className="col-span-12 lg:col-span-3 space-y-4">
          <CameraStatus
            status={effectiveStatus}
            sessionId={sessionId}
            onEnableCamera={handleEnableCamera}
            cameraError={cameraError}
          />

          <SurveillanceControls
            sessionStatus={effectiveStatus}
            border={border}
            isDrawingBorder={isDrawingBorder}
            onDefineBorder={handleDefineBorder}
            onClearBorder={handleClearBorder}
            onRedrawBorder={handleRedrawBorder}
            onStart={handleStart}
            onStop={handleStop}
            onReset={handleReset}
            loading={loading}
          />
        </div>

        {/* Center — video feed */}
        <div className="col-span-12 lg:col-span-6">
          <CameraFeed
            videoRef={videoRef}
            sessionStatus={effectiveStatus}
            border={border}
            isDrawingBorder={isDrawingBorder}
            onBorderComplete={handleBorderComplete}
            tracks={detections}
            aiPipeline={aiPipeline}
            cameraError={cameraError}
          />
        </div>

        {/* Right — alerts */}
        <div className="col-span-12 lg:col-span-3 h-[400px] lg:h-auto lg:min-h-[480px]">
          <AlertPanel alerts={alerts} />
        </div>
      </div>

      {/* Bottom */}
      <StatisticsCards
        stats={stats}
        sessionStatus={effectiveStatus}
      />

      <EventTimeline events={events} />
    </div>
  )
}