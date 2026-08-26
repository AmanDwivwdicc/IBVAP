import { useCallback, useEffect, useRef, useState } from 'react'

export function useWebcam() {
  const videoRef = useRef(null)
  const streamRef = useRef(null)

  const [status, setStatus] = useState('camera_offline')
  const [error, setError] = useState(null)

  const start = useCallback(async () => {
    try {
      setError(null)

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
        audio: false,
      })

      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }

      setStatus('camera_ready')
      return true
    } catch (err) {
      const msg =
        err.name === 'NotAllowedError'
          ? 'Camera permission denied. Please allow webcam access.'
          : err.name === 'NotFoundError'
            ? 'No camera found on this device.'
            : `Camera error: ${err.message}`

      setError(msg)
      setStatus('camera_offline')
      return false
    }
  }, [])

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null

    if (videoRef.current) {
      videoRef.current.srcObject = null
    }

    setStatus('camera_offline')
  }, [])

  // Capture the current webcam frame as JPEG data URL.
  const captureFrame = useCallback((quality = 0.65) => {
    const video = videoRef.current

    if (!video || video.readyState < 2 || !video.videoWidth) {
      return null
    }

    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const context = canvas.getContext('2d')

    if (!context) {
      return null
    }

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height,
    )

    return canvas.toDataURL('image/jpeg', quality)
  }, [])

  useEffect(() => {
    return () => stop()
  }, [stop])

  return {
    videoRef,
    status,
    error,
    start,
    stop,
    captureFrame,
    stream: streamRef,
  }
}