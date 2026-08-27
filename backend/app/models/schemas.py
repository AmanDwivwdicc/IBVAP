from datetime import datetime

from pydantic import BaseModel, Field


class EvidenceSchema(BaseModel):
    content_type: str = Field(..., description="MIME type, usually image/jpeg")
    jpeg_base64: str = Field(..., description="Base64 encoded image string")


class DetectionSchema(BaseModel):
    feature: str | None = None
    class_id: int | None = None
    class_name: str | None = None
    confidence: float | None = None
    bbox_xyxy: list[float] | None = None
    tracker_id: int | None = None
    evidence: dict | None = None


class AlertPayloadSchema(BaseModel):
    device_id: str
    camera_id: str
    timestamp: str | datetime
    detections: list[DetectionSchema] = []


class AlertResponseSchema(BaseModel):
    alert_id: str


class HeartbeatSchema(BaseModel):
    device_id: str
    cpu_percent: float
    memory_percent: float
    temperature_celsius: float
    uptime_seconds: int
    queue_depth: int
    cameras_active: int
