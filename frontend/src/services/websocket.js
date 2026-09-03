const WS_URL =
  import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws'

export class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectTimer = null
    this.shouldReconnect = true
    this.isConnecting = false
  }

  connect() {
    // Already connected or currently connecting.
    if (
      this.ws?.readyState === WebSocket.OPEN ||
      this.ws?.readyState === WebSocket.CONNECTING ||
      this.isConnecting
    ) {
      return
    }

    this.shouldReconnect = true
    this.isConnecting = true

    this.ws = new WebSocket(WS_URL)

    this.ws.onopen = () => {
      this.isConnecting = false
      this._emit('connection', { status: 'connected' })
    }

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)

        this._emit(msg.type, msg.data)
        this._emit('message', msg)
      } catch {
        // Ignore malformed messages.
      }
    }

    this.ws.onclose = () => {
      this.isConnecting = false
      this._emit('connection', {
        status: 'disconnected',
      })

      this.ws = null

      if (this.shouldReconnect) {
        clearTimeout(this.reconnectTimer)

        this.reconnectTimer = setTimeout(() => {
          this.connect()
        }, 3000)
      }
    }

    this.ws.onerror = () => {
      this.isConnecting = false

      this._emit('connection', {
        status: 'error',
      })
    }
  }

  disconnect() {
    this.shouldReconnect = false
    this.isConnecting = false

    clearTimeout(this.reconnectTimer)
    this.reconnectTimer = null

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  on(type, callback) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }

    this.listeners.get(type).add(callback)

    return () => {
      this.listeners.get(type)?.delete(callback)
    }
  }

  _emit(type, data) {
    this.listeners.get(type)?.forEach((callback) => {
      callback(data)
    })
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        typeof data === 'string'
          ? data
          : JSON.stringify(data),
      )
      return true
    }

    console.warn(
      '[IBVAP] WebSocket not connected. Message not sent:',
      data?.type,
    )

    return false
  }
}

export const wsService = new WebSocketService()