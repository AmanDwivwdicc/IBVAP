"""SQLAlchemy ORM models for IBVAP."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    start_time = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    camera_type = Column(String, default="browser_webcam")
    status = Column(String, default="active")  # active | stopped
    total_persons = Column(Integer, default=0)
    total_vehicles = Column(Integer, default=0)
    total_events = Column(Integer, default=0)
    warning_events = Column(Integer, default=0)
    critical_events = Column(Integer, default=0)
    info_events = Column(Integer, default=0)
    evidence_count = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String, default="LOW")
    border_config = Column(Text, nullable=True)  # JSON string


class EventModel(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    track_id = Column(String, nullable=True)
    object_type = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    message = Column(Text, nullable=False)
    evidence_path = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)


class EvidenceModel(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    snapshot_path = Column(String, nullable=True)
    metadata_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
