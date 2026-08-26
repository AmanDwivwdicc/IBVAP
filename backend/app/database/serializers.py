"""Helpers for serializing database models to API responses."""

import json
from typing import Any

from app.database.models import SessionModel
from app.schemas.sessions import SessionResponse


def session_to_response(session: SessionModel) -> SessionResponse:
    border_config: dict[str, Any] | None = None
    if session.border_config:
        try:
            border_config = json.loads(session.border_config)
        except json.JSONDecodeError:
            border_config = None

    return SessionResponse(
        id=session.id,
        start_time=session.start_time,
        end_time=session.end_time,
        duration_seconds=session.duration_seconds,
        camera_type=session.camera_type,
        status=session.status,
        total_persons=session.total_persons,
        total_vehicles=session.total_vehicles,
        total_events=session.total_events,
        warning_events=session.warning_events,
        critical_events=session.critical_events,
        info_events=session.info_events,
        evidence_count=session.evidence_count,
        risk_score=session.risk_score,
        risk_level=session.risk_level,
        border_config=border_config,
    )
