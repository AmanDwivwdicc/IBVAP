"""
Surveillance Intelligence Report generator.

TODO (Phase 9): Full report with evidence thumbnails and PDF export.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.models import EventModel, SessionModel
from app.surveillance.event_engine import EventEngine


class ReportGenerator:
    """Generates structured surveillance intelligence reports."""

    def __init__(self) -> None:
        settings.reports_dir.mkdir(parents=True, exist_ok=True)

    async def generate(self, db: AsyncSession, session_id: str) -> dict[str, Any]:
        result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        events_result = await db.execute(
            select(EventModel)
            .where(EventModel.session_id == session_id)
            .order_by(EventModel.timestamp)
        )
        events = list(events_result.scalars().all())

        info_count = sum(1 for e in events if e.severity == "INFO")
        warning_count = sum(1 for e in events if e.severity == "WARNING")
        critical_count = sum(1 for e in events if e.severity == "CRITICAL")
        risk_score, risk_level = EventEngine.calculate_risk(events)

        incident_timeline = [
            {
                "time": e.timestamp.isoformat() if e.timestamp else None,
                "event_type": e.type,
                "severity": e.severity,
                "track_id": e.track_id,
                "description": e.message,
                "confidence": e.confidence,
                "evidence_path": e.evidence_path,
            }
            for e in events
            if e.severity in ("WARNING", "CRITICAL")
        ]

        report = {
            "header": {
                "title": "IBVAP",
                "subtitle": "INTELLIGENT BORDER VIDEO ANALYTICS PLATFORM",
                "report_type": "SURVEILLANCE INTELLIGENCE REPORT",
            },
            "session": {
                "session_id": session.id,
                "date": session.start_time.strftime("%Y-%m-%d") if session.start_time else None,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "duration_seconds": session.duration_seconds,
                "camera_source": session.camera_type,
            },
            "detection_summary": {
                "unique_persons": session.total_persons,
                "unique_vehicles": session.total_vehicles,
                "total_tracked_objects": session.total_persons + session.total_vehicles,
            },
            "event_summary": {
                "total_events": len(events),
                "info_events": info_count,
                "warning_events": warning_count,
                "critical_events": critical_count,
            },
            "incident_timeline": incident_timeline,
            "risk_summary": {
                "score": risk_score,
                "level": risk_level,
                "disclaimer": "Prototype rule-based risk score — not a military threat assessment model.",
            },
            "evidence_gallery": [
                {"event_id": e.id, "path": e.evidence_path, "type": e.type}
                for e in events
                if e.evidence_path
            ],
            "final_summary": self._build_final_summary(critical_count, warning_count, events),
        }

        report_path = settings.reports_dir / f"{session_id}.json"
        report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        report["report_path"] = str(report_path)
        return report

    def _build_final_summary(
        self,
        critical: int,
        warning: int,
        events: list[EventModel],
    ) -> str:
        if critical == 0 and warning == 0:
            return "No warning or critical security events were detected during the surveillance session."

        breach = sum(1 for e in events if e.type == "VIRTUAL_FENCE_BREACH")
        loitering = sum(1 for e in events if e.type == "LOITERING_DETECTED")
        parts = []
        if critical:
            parts.append(f"{critical} critical security event(s)")
        if warning:
            parts.append(f"{warning} warning event(s)")
        detail = []
        if breach:
            detail.append(f"{breach} virtual fence breach(es)")
        if loitering:
            detail.append(f"{loitering} loitering event(s)")
        summary = f"{' and '.join(parts)} were detected during the surveillance session"
        if detail:
            summary += f", including {' and '.join(detail)}"
        return summary + "."


report_generator = ReportGenerator()
