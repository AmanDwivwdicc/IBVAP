import { useCallback, useEffect, useRef, useState } from 'react'

export default function VirtualFenceCanvas({
  videoRef,
  border,
  isDrawing,
  onBorderComplete,
  disabled,
}) {
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const [points, setPoints] = useState([])
  const [previewPoint, setPreviewPoint] = useState(null)

  const getRelativeCoords = useCallback((e) => {
    const canvas = canvasRef.current
    if (!canvas) return null
    const rect = canvas.getBoundingClientRect()
    return {
      x: (e.clientX - rect.left) / rect.width,
      y: (e.clientY - rect.top) / rect.height,
    }
  }, [])

  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return
    canvas.width = container.clientWidth
    canvas.height = container.clientHeight
  }, [])

  useEffect(() => {
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    return () => window.removeEventListener('resize', resizeCanvas)
  }, [resizeCanvas])

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const w = canvas.width
    const h = canvas.height

    ctx.clearRect(0, 0, w, h)

    const drawLine = (a, b, color, width, dash = []) => {
      ctx.save()
      ctx.strokeStyle = color
      ctx.lineWidth = width
      ctx.setLineDash(dash)
      ctx.beginPath()
      ctx.moveTo(a.x * w, a.y * h)
      ctx.lineTo(b.x * w, b.y * h)
      ctx.stroke()
      ctx.restore()
    }

    // Draw saved border
    if (border?.point_a && border?.point_b) {
      drawLine(border.point_a, border.point_b, '#ef4444', 3)
      // Endpoint markers
      ;[border.point_a, border.point_b].forEach((p) => {
        ctx.beginPath()
        ctx.arc(p.x * w, p.y * h, 6, 0, Math.PI * 2)
        ctx.fillStyle = '#ef4444'
        ctx.fill()
      })
    }

    // Draw in-progress points
    if (isDrawing && points.length === 1 && previewPoint) {
      drawLine(points[0], previewPoint, '#f59e0b', 2, [8, 4])
      ctx.beginPath()
      ctx.arc(points[0].x * w, points[0].y * h, 6, 0, Math.PI * 2)
      ctx.fillStyle = '#f59e0b'
      ctx.fill()
    }

    if (isDrawing && points.length === 2) {
      drawLine(points[0], points[1], '#f59e0b', 2)
    }
  }, [border, isDrawing, points, previewPoint])

  useEffect(() => {
    draw()
  }, [draw])

  const handleClick = (e) => {
    if (!isDrawing || disabled) return
    const coords = getRelativeCoords(e)
    if (!coords) return

    if (points.length === 0) {
      setPoints([coords])
    } else if (points.length === 1) {
      const newBorder = { point_a: points[0], point_b: coords }
      setPoints([points[0], coords])
      onBorderComplete(newBorder)
      setPoints([])
      setPreviewPoint(null)
    }
  }

  const handleMouseMove = (e) => {
    if (!isDrawing || points.length !== 1) return
    setPreviewPoint(getRelativeCoords(e))
  }

  return (
    <div ref={containerRef} className="absolute inset-0">
      <canvas
        ref={canvasRef}
        className={`absolute inset-0 w-full h-full ${isDrawing ? 'cursor-crosshair' : 'pointer-events-none'}`}
        style={{ zIndex: 10, pointerEvents: isDrawing ? 'auto' : 'none' }}
        onClick={handleClick}
        onMouseMove={handleMouseMove}
      />
    </div>
  )
}
