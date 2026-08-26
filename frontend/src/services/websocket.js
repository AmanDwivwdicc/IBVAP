const WS_URL =
  import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws'
export class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectTimer = null
    this.shouldReconnect = true
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return

    this.ws = new WebSocket(WS_URL)

    this.ws.onopen = () => {
      this._emit('connection', { status: 'connected' })
    }

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        this._emit(msg.type, msg.data)
        this._emit('message', msg)
      } catch {
        // ignore malformed messages
      }
    }

    this.ws.onclose = () => {
      this._emit('connection', { status: 'disconnected' })
      if (this.shouldReconnect) {
        this.reconnectTimer = setTimeout(() => this.connect(), 3000)
      }
    }

    this.ws.onerror = () => {
      this._emit('connection', { status: 'error' })
    }
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
  }

  on(type, callback) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set())
    this.listeners.get(type).add(callback)
    return () => this.listeners.get(type)?.delete(callback)
  }

  _emit(type, data) {
    this.listeners.get(type)?.forEach((cb) => cb(data))
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }
}

export const wsService = new WebSocketService()
