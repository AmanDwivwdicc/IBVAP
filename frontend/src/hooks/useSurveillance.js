import { useCallback, useEffect, useState } from 'react'

import { api } from '../services/api'
import { wsService } from '../services/websocket'

const INITIAL_STATS = {
  persons: 0,
  vehicles: 0,
  total_events: 0,
  info_events: 0,
  warning_events: 0,
  critical_events: 0,
  person_detections: 0,
  vehicle_detections: 0,
}

export function useSurveillance() {
  const [sessionStatus, setSessionStatus] = useState('idle')
  const [sessionId, setSessionId] = useState(null)
  const [events, setEvents] = useState([])
  const [alerts, setAlerts] = useState([])
  const [stats, setStats] = useState(INITIAL_STATS)
  const [border, setBorder] = useState(null)

  const [detections, setDetections] = useState([])

  const [wsConnected, setWsConnected] = useState(false)
  const [backendOnline, setBackendOnline] = useState(false)
  const [aiPipeline, setAiPipeline] = useState('stub')
  const [aiStatus, setAiStatus] = useState('unknown')

  const [error, setError] = useState(null)

  // ------------------------------------------
  // Backend health
  // ------------------------------------------
  useEffect(() => {
    let mounted = true
  
    const checkBackend = async () => {
      try {
        const data = await api.health()
  
        if (!mounted) return
  
        setBackendOnline(true)
        setAiPipeline(data.ai_pipeline || 'stub')
        setAiStatus(data.ai_status || 'unknown')
      } catch {
        if (!mounted) return
  
        setBackendOnline(false)
        setAiStatus('offline')
      }
    }
  
    checkBackend()
  
    const interval = setInterval(
      checkBackend,
      10000,
    )
  
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  // ------------------------------------------
  // WebSocket listeners
  // ------------------------------------------
  useEffect(() => {
    wsService.connect()

    const unsubs = [
      wsService.on('connection', ({ status }) => {
        setWsConnected(status === 'connected')
      }),

      wsService.on('connected', (data) => {
        setAiPipeline(data.ai_pipeline || 'stub')
        setAiStatus(data.ai_status || 'unknown')
      }),

      wsService.on('ai_started', () => {
        setAiStatus('active')
        setSessionStatus('surveillance_active')
      }),

      wsService.on('ai_stopped', () => {
        setAiStatus('ready')
        setDetections([])
      }),

      wsService.on('detections', (data) => {
        if (!data?.detections) return
      
        setDetections(data.detections)
      
        const persons = data.detections.filter(
          (d) => d.object_type === 'PERSON',
        ).length
      
        const vehicles = data.detections.filter(
          (d) => d.object_type === 'VEHICLE',
        ).length
      
        setStats((prev) => ({
          ...prev,
      
          // Current frame
          persons,
          vehicles,
      
          // Session totals
          person_detections:
            prev.person_detections + persons,
      
          vehicle_detections:
            prev.vehicle_detections + vehicles,
        }))
      }),

      wsService.on('session_started', (data) => {
        setSessionStatus('surveillance_active')
        setSessionId(data.session_id)
        setDetections([])
      }),

      wsService.on('session_stopped', (data) => {
        setSessionStatus('surveillance_stopped')
        setSessionId(data.session_id)
        setDetections([])
      }),

      wsService.on('session_reset', () => {
        setSessionStatus('idle')
        setSessionId(null)
        setEvents([])
        setAlerts([])
        setStats(INITIAL_STATS)
        setDetections([])
        setBorder(null)
        setAiStatus('ready')
      }),

      wsService.on('event', (data) => {
        const event = {
          event_id: data.event_id,
          session_id: data.session_id,
          event_type: data.event_type,
          severity: data.severity,
          timestamp: data.timestamp,
          track_id: data.track_id,
          message: data.message,
          confidence: data.confidence,
          evidence_path: data.evidence_path,
        }

        setEvents((prev) => [event, ...prev])

        if (
          data.severity === 'WARNING' ||
          data.severity === 'CRITICAL'
        ) {
          setAlerts((prev) => [event, ...prev].slice(0, 50))
        }

        setStats((prev) => ({
          ...prev,
          total_events: prev.total_events + 1,
          info_events:
            data.severity === 'INFO'
              ? prev.info_events + 1
              : prev.info_events,
          warning_events:
            data.severity === 'WARNING'
              ? prev.warning_events + 1
              : prev.warning_events,
          critical_events:
            data.severity === 'CRITICAL'
              ? prev.critical_events + 1
              : prev.critical_events,
        }))
      }),
    ]

    return () => {
      unsubs.forEach((unsubscribe) => unsubscribe())
      wsService.disconnect()
    }
  }, [])

  // ------------------------------------------
  // Camera
  // ------------------------------------------
  const notifyCameraReady = useCallback(
    async (ready) => {
      try {
        await api.setCameraReady(ready)

        if (ready && sessionStatus === 'idle') {
          setSessionStatus('camera_ready')
        }
      } catch (err) {
        setError(err.message)
      }
    },
    [sessionStatus],
  )

  // ------------------------------------------
  // Border
  // ------------------------------------------
  const saveBorder = useCallback(async (borderData) => {
    try {
      await api.setBorder(borderData)
      setBorder(borderData)
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const clearBorder = useCallback(async () => {
    try {
      await api.clearBorder()
      setBorder(null)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  // ------------------------------------------
  // Start surveillance
  // ------------------------------------------
  const startSurveillance = useCallback(async () => {
    try {
      setError(null)
      setDetections([])

      const session = await api.startSession({
        camera_type: 'browser_webcam',
        border,
      })

      setSessionId(session.id)

// Tell backend to start YOLO.
// We will mark surveillance active only after
// the backend confirms that AI has started.
wsService.send({
  type: 'start_ai',
  session_id: session.id,
})

      return session
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [border])

  // ------------------------------------------
  // Stop surveillance
  // ------------------------------------------
  const stopSurveillance = useCallback(async () => {
    try {
      setError(null)
  
      wsService.send({
        type: 'stop_ai',
      })
  
      // Save the final live AI statistics before clearing detections.
      const finalStats = {
        total_persons: stats.persons || 0,
        total_vehicles: stats.vehicles || 0,
      }
  
      setDetections([])
  
      const session = await api.stopSession(finalStats)
  
      setSessionStatus('surveillance_stopped')
  
      return session
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [stats])

  // ------------------------------------------
  // Reset
  // ------------------------------------------
  const resetSession = useCallback(async () => {
    try {
      setError(null)

      wsService.send({
        type: 'stop_ai',
      })

      await api.resetSession()

      setSessionStatus('idle')
      setSessionId(null)
      setEvents([])
      setAlerts([])
      setStats(INITIAL_STATS)
      setDetections([])
      setBorder(null)
      setAiStatus('ready')
    } catch (err) {
      setError(err.message)
    }
  }, [])

  return {
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
    aiStatus,
    error,

    setSessionStatus,
    notifyCameraReady,

    saveBorder,
    clearBorder,

    startSurveillance,
    stopSurveillance,
    resetSession,
  }
}