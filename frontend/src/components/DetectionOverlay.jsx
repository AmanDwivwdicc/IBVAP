export default function DetectionOverlay({ tracks = [] }) {
  if (!tracks.length) return null

  return (
    <div className="absolute inset-0 w-full h-full pointer-events-none">
      {tracks.map((track, index) => {
        const [x1, y1, x2, y2] = track.bbox || [0, 0, 0, 0]

        const frameWidth = Number(track.frame_width) || 1280
        const frameHeight = Number(track.frame_height) || 720

        const left = (Number(x1) / frameWidth) * 100
        const top = (Number(y1) / frameHeight) * 100

        const width =
          ((Number(x2) - Number(x1)) / frameWidth) * 100

        const height =
          ((Number(y2) - Number(y1)) / frameHeight) * 100

        const isPerson = track.object_type === 'PERSON'

        const color = isPerson
          ? '#00ff88'
          : '#ff00ff'

        return (
          <div
            key={`${track.class_name}-${index}`}
            className="absolute"
            style={{
              left: `${left}%`,
              top: `${top}%`,
              width: `${width}%`,
              height: `${height}%`,
              border: `4px solid ${color}`,
              boxSizing: 'border-box',
              backgroundColor: 'transparent',
              zIndex: 100,
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: '0',
                top: '-30px',
                backgroundColor: color,
                color: '#000',
                padding: '4px 8px',
                fontSize: '13px',
                fontWeight: 'bold',
                fontFamily: 'monospace',
                whiteSpace: 'nowrap',
                borderRadius: '3px',
              }}
            >
              {track.object_type}
              {' '}
              {Math.round((track.confidence || 0) * 100)}%
            </div>
          </div>
        )
      })}
    </div>
  )
}