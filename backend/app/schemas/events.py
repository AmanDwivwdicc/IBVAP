"""Pydantic schemas for security events."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class EventType(str, Enum):
    PERSON_DETECTED = "PERSON_DETECTED"
    VEHICLE_DETECTED = "VEHICLE_DETECTED"
    APPROACHING_BORDER = "APPROACHING_BORDER"
    VIRTUAL_FENCE_BREACH = "VIRTUAL_FENCE_BREACH"
    LOITERING_DETECTED = "LOITERING_DETECTED"
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_STOPPED = "SESSION_STOPPED"


class SecurityEvent(BaseModel):
    id: str
    session_id: str
    type: str
    severity: EventSeverity
    timestamp: datetime
    track_id: str | None = None
    object_type: str | None = None
    confidence: float | None = None
    message: str
    evidence_path: str | None = None
    metadata: dict[str, Any] | None = None


class EventResponse(BaseModel):
    id: str
    session_id: str
    type: str
    severity: str
    timestamp: datetime
    track_id: str | None = None
    object_type: str | None = None
    confidence: float | None = None
    message: str
    evidence_path: str | None = None

    model_config = {"from_attributes": True}


class DetectionUpdate(BaseModel):
    """WebSocket payload for detection/tracking updates (Phase 3+)."""

    frame_id: int
    tracks: list[dict[str, Any]] = Field(default_factory=list)
    inference_fps: float = 0.0
