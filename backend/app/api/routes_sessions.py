"""Session management API routes."""

import json

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.camera.frame_processor import frame_processor
from app.database.database import get_db
from app.database.models import EventModel, SessionModel
from app.database.serializers import session_to_response
from app.reports.generator import report_generator
from app.schemas.events import EventSeverity, EventType
from app.schemas.sessions import SessionCreate, SessionResponse, VirtualBorder
from app.surveillance.event_engine import event_engine
from app.surveillance.session_manager import session_manager
from app.surveillance.virtual_fence import virtual_fence

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionResponse)
async def start_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    try:
        session = await session_manager.start_session(db, payload)
        if payload.border or session_manager.border:
            border = payload.border or session_manager.border
            if border:
                virtual_fence.set_border(border)

        await event_engine.emit(
            db,
            session.id,
            EventType.SESSION_STARTED,
            EventSeverity.INFO,
            f"Surveillance session {session.id} started",
            allow_duplicate=True,
        )
        return session_to_response(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stop", response_model=SessionResponse)
async def stop_session(
    stats: dict[str, Any] | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    try:
        frame_processor.stop()
        session = await session_manager.stop_session(db)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
                # Persist final V1 AI detection counts.
        # Persist unique AI detection counts collected during the session.
        ai_stats = frame_processor.get_session_stats()
        session.total_persons = ai_stats["total_persons"]
        session.total_vehicles = ai_stats["total_vehicles"]
            
        await event_engine.emit(
            db,
            session.id,
            EventType.SESSION_STOPPED,
            EventSeverity.INFO,
            f"Surveillance session {session.id} stopped",
            allow_duplicate=True,
        )

        # Update event counts
        events_result = await db.execute(
            select(EventModel).where(EventModel.session_id == session.id)
        )
        events = list(events_result.scalars().all())
        session.total_events = len(events)
        session.info_events = sum(1 for e in events if e.severity == "INFO")
        session.warning_events = sum(1 for e in events if e.severity == "WARNING")
        session.critical_events = sum(1 for e in events if e.severity == "CRITICAL")
        score, level = event_engine.calculate_risk(events)
        session.risk_score = score
        session.risk_level = level

        await db.flush()
        return session_to_response(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset")
async def reset_session() -> dict:
    frame_processor.stop()
    virtual_fence.clear()
    event_engine.reset()
    await session_manager.reset()
    return {"status": "idle", "message": "Session reset complete"}


@router.get("/active")
async def get_active_session(db: AsyncSession = Depends(get_db)) -> dict:
    if not session_manager.active_session_id:
        return {"active": False, "session": None}
    result = await db.execute(
        select(SessionModel).where(SessionModel.id == session_manager.active_session_id)
    )
    session = result.scalar_one_or_none()
    return {"active": True, "session": session_to_response(session) if session else None}


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)) -> SessionResponse:
    result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_to_response(session)


@router.post("/border")
async def set_border(border: VirtualBorder) -> dict:
    session_manager.set_border(border)
    virtual_fence.set_border(border)
    return {"status": "ok", "border": border.model_dump()}


@router.delete("/border")
async def clear_border() -> dict:
    session_manager.clear_border()
    virtual_fence.clear()
    return {"status": "ok", "border": None}


@router.get("/border/current")
async def get_border() -> dict:
    if session_manager.border:
        return {"defined": True, "border": session_manager.border.model_dump()}
    return {"defined": False, "border": None}


@router.get("", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)) -> list[SessionResponse]:
    result = await db.execute(select(SessionModel).order_by(SessionModel.start_time.desc()))
    return [session_to_response(s) for s in result.scalars().all()]
