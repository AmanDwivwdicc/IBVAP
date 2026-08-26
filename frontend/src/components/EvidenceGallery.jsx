import { ImageOff } from 'lucide-react'

export default function EvidenceGallery({ items = [] }) {
  return (
    <div className="panel p-6">
      <h2 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-4">
        Evidence Gallery
      </h2>

      {items.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <ImageOff className="w-10 h-10 mx-auto mb-2 opacity-40" />
          <p className="text-sm">No evidence captured during this session</p>
          <p className="text-xs mt-1 text-gray-600">Evidence capture activates with WARNING/CRITICAL events (Phase 7)</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {items.map((item) => (
            <div key={item.event_id} className="bg-gray-800 rounded border border-gray-700 overflow-hidden">
              {item.path?.endsWith('.jpg') ? (
                <img src={item.path} alt={`Evidence ${item.event_id}`} className="w-full h-32 object-cover" />
              ) : (
                <div className="w-full h-32 flex items-center justify-center bg-gray-900 text-gray-500 text-xs">
                  Evidence pending
                </div>
              )}
              <div className="p-2 text-xs font-mono">
                <div className="text-gray-400">{item.event_id}</div>
                <div className="text-cyan-400">{item.type}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
