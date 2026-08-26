"""Session lifecycle management."""

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import SessionModel
from app.schemas.sessions import SessionCreate, VirtualBorder
from app.websocket.manager import ws_manager


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_session_id() -> str:
    now = datetime.now()
    return f"SESSION-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"


def generate_event_id(index: int) -> str:
    return f"EVT-{index:03d}"


class SessionManager:
    """Manages active surveillance session state in memory + DB."""

    def __init__(self) -> None:
        self.active_session_id: str | None = None
        self.camera_ready: bool = False
        self.border: VirtualBorder | None = None
        self._event_counter: int = 0

    @property
    def status(self) -> str:
        if self.active_session_id:
            return "surveillance_active"
        if self.camera_ready:
            return "camera_ready"
        return "idle"

    def next_event_id(self) -> str:
        self._event_counter += 1
        return generate_event_id(self._event_counter)

    async def start_session(
        self,
        db: AsyncSession,
        payload: SessionCreate,
    ) -> SessionModel:
        if self.active_session_id:
            raise ValueError("A surveillance session is already active")
        if not self.camera_ready:
            raise ValueError("Camera is not ready. Enable webcam first.")
        if payload.border is None and self.border is None:
            raise ValueError("Virtual border must be defined before starting surveillance")

        border = payload.border or self.border
        session_id = generate_session_id()

        session = SessionModel(
            id=session_id,
            start_time=_utcnow(),
            camera_type=payload.camera_type,
            status="active",
            border_config=json.dumps(border.model_dump()) if border else None,
        )
        db.add(session)
        await db.flush()

        self.active_session_id = session_id
        self.border = border

        await ws_manager.broadcast(
            "session_started",
            {"session_id": session_id, "status": "surveillance_active"},
        )
        return session

    async def stop_session(self, db: AsyncSession) -> SessionModel | None:
        if not self.active_session_id:
            raise ValueError("No active surveillance session")

        result = await db.execute(
            select(SessionModel).where(SessionModel.id == self.active_session_id)
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise ValueError("Session not found in database")

        end_time = _utcnow()
        session.end_time = end_time
        session.status = "stopped"
        if session.start_time:
            start = session.start_time
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            session.duration_seconds = (end_time - start).total_seconds()

        session_id = self.active_session_id
        self.active_session_id = None

        await ws_manager.broadcast(
            "session_stopped",
            {
                "session_id": session_id,
                "status": "surveillance_stopped",
                "duration_seconds": session.duration_seconds,
            },
        )
        return session

    async def reset(self) -> None:
        self.active_session_id = None
        self.camera_ready = False
        self.border = None
        self._event_counter = 0
        await ws_manager.broadcast("session_reset", {"status": "idle"})

    def set_camera_ready(self, ready: bool) -> None:
        self.camera_ready = ready

    def set_border(self, border: VirtualBorder) -> None:
        self.border = border

    def clear_border(self) -> None:
        self.border = None


session_manager = SessionManager()
