"""Pydantic schemas for surveillance sessions."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    IDLE = "idle"
    CAMERA_READY = "camera_ready"
    SURVEILLANCE_ACTIVE = "surveillance_active"
    SURVEILLANCE_STOPPED = "surveillance_stopped"


class BorderPoint(BaseModel):
    x: float
    y: float


class VirtualBorder(BaseModel):
    point_a: BorderPoint
    point_b: BorderPoint


class SessionCreate(BaseModel):
    camera_type: str = "browser_webcam"
    border: VirtualBorder | None = None


class SessionResponse(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None
    camera_type: str
    status: str
    total_persons: int = 0
    total_vehicles: int = 0
    total_events: int = 0
    warning_events: int = 0
    critical_events: int = 0
    info_events: int = 0
    evidence_count: int = 0
    risk_score: int = 0
    risk_level: str = "LOW"
    border_config: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class SessionStats(BaseModel):
    session_id: str
    persons: int = 0
    vehicles: int = 0
    total_events: int = 0
    info_events: int = 0
    warning_events: int = 0
    critical_events: int = 0


class SystemStatus(BaseModel):
    status: str = "online"
    ai_pipeline: str = "stub"  # stub | ready | active | error
    message: str = "System operational"
