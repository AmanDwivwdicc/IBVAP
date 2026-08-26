/** @typedef {'idle' | 'camera_ready' | 'surveillance_active' | 'surveillance_stopped' | 'camera_offline'} SessionStatus */

/**
 * @typedef {Object} BorderPoint
 * @property {number} x
 * @property {number} y
 */

/**
 * @typedef {Object} VirtualBorder
 * @property {BorderPoint} point_a
 * @property {BorderPoint} point_b
 */

/**
 * @typedef {Object} SecurityEvent
 * @property {string} event_id
 * @property {string} session_id
 * @property {string} event_type
 * @property {'INFO' | 'WARNING' | 'CRITICAL'} severity
 * @property {string} timestamp
 * @property {string|null} track_id
 * @property {string} message
 * @property {number|null} confidence
 * @property {string|null} evidence_path
 */

/**
 * @typedef {Object} SessionStats
 * @property {number} persons
 * @property {number} vehicles
 * @property {number} total_events
 * @property {number} info_events
 * @property {number} warning_events
 * @property {number} critical_events
 */

export {}
