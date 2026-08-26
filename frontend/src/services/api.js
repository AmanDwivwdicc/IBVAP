const API_BASE = import.meta.env.VITE_API_URL || ''

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => request('/api/health'),
  config: () => request('/api/config'),
  systemStatus: () => request('/api/camera/system'),

  setCameraReady: (ready = true) =>
    request(`/api/camera/ready?ready=${ready}`, { method: 'POST' }),

  getCameraStatus: () => request('/api/camera/status'),

  startSession: (payload) =>
    request('/api/sessions/start', { method: 'POST', body: JSON.stringify(payload) }),

  stopSession: (stats = {}) =>
    request('/api/sessions/stop', {
      method: 'POST',
      body: JSON.stringify(stats),
    }),

  resetSession: () => request('/api/sessions/reset', { method: 'POST' }),

  getActiveSession: () => request('/api/sessions/active'),

  getSession: (id) => request(`/api/sessions/${id}`),

  listSessions: () => request('/api/sessions'),

  setBorder: (border) =>
    request('/api/sessions/border', { method: 'POST', body: JSON.stringify(border) }),

  clearBorder: () => request('/api/sessions/border', { method: 'DELETE' }),

  getBorder: () => request('/api/sessions/border/current'),

  getSessionEvents: (sessionId) => request(`/api/events/session/${sessionId}`),

  getReport: (sessionId) => request(`/api/reports/${sessionId}`),

  downloadReport: (sessionId) =>
    `${API_BASE}/api/reports/${sessionId}/download`,
}
