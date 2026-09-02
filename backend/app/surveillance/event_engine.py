"""
Security event engine — produces structured events.

Phase 3/6:
- Central event creation
- Persistent globally-unique event IDs
- Session-level duplicate prevention
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import EventModel
from app.schemas.events import EventSeverity, EventType, SecurityEvent
from app.websocket.manager import ws_manager


class EventEngine:
    """Central event management."""

    SEVERITY_POINTS = {
        EventSeverity.INFO: 0,
        EventSeverity.WARNING: 10,
        EventSeverity.CRITICAL: 30,
    }

    def __init__(self) -> None:
        self._emitted_keys: set[str] = set()

    def _dedup_key(
        self,
        event_type: str,
        track_id: str | None,
        session_id: str,
    ) -> str:
        return f"{session_id}:{event_type}:{track_id or 'global'}"

    @staticmethod
    def generate_event_id() -> str:
        """
        Generate a globally unique, human-readable event ID.

        Example:
        EVT-7A4C91F2
        """
        return f"EVT-{uuid.uuid4().hex[:8].upper()}"

    async def emit(
        self,
        db: AsyncSession,
        session_id: str,
        event_type: EventType | str,
        severity: EventSeverity,
        message: str,
        track_id: str | None = None,
        object_type: str | None = None,
        confidence: float | None = None,
        evidence_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        allow_duplicate: bool = False,
        event_id_override: str | None = None,
    ) -> SecurityEvent | None:
        """Create and broadcast a security event."""

        type_str = (
            event_type.value
            if isinstance(event_type, EventType)
            else event_type
        )

        # Prevent duplicate logical events within the same session.
        if not allow_duplicate:
            key = self._dedup_key(
                type_str,
                track_id,
                session_id,
            )

            if key in self._emitted_keys:
                return None

            self._emitted_keys.add(key)

        # IMPORTANT:
        # Do not use the session manager's counter.
        # Event IDs must remain unique across sessions and restarts.
        event_id = event_id_override or self.generate_event_id()

        now = datetime.now(timezone.utc)

        event = SecurityEvent(
            id=event_id,
            session_id=session_id,
            type=type_str,
            severity=severity,
            timestamp=now,
            track_id=track_id,
            object_type=object_type,
            confidence=confidence,
            message=message,
            evidence_path=evidence_path,
            metadata=metadata,
        )

        db_event = EventModel(
            id=event.id,
            session_id=event.session_id,
            type=event.type,
            severity=event.severity.value,
            timestamp=event.timestamp,
            track_id=event.track_id,
            object_type=event.object_type,
            confidence=event.confidence,
            message=event.message,
            evidence_path=event.evidence_path,
            metadata_json=(
                json.dumps(metadata)
                if metadata
                else None
            ),
        )

        db.add(db_event)

        await db.flush()

        await ws_manager.broadcast(
            "event",
            {
                "event_id": event.id,
                "session_id": event.session_id,
                "event_type": event.type,
                "severity": event.severity.value,
                "timestamp": event.timestamp.isoformat(),
                "track_id": event.track_id,
                "message": event.message,
                "confidence": event.confidence,
                "evidence_path": event.evidence_path,
            },
        )

        return event

    def reset(self) -> None:
        """Reset in-memory duplicate tracking."""
        self._emitted_keys.clear()

    @staticmethod
    def calculate_risk(
        events: list[EventModel],
    ) -> tuple[int, str]:
        """Calculate deterministic prototype risk score."""

        score = sum(
            EventEngine.SEVERITY_POINTS.get(
                EventSeverity(event.severity),
                0,
            )
            for event in events
        )

        if score >= 60:
            level = "CRITICAL"
        elif score >= 30:
            level = "HIGH"
        elif score >= 10:
            level = "MEDIUM"
        else:
            level = "LOW"

        return score, level


event_engine = EventEngine()
