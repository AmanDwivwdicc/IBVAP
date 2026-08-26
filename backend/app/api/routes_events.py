"""Events API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.database.models import EventModel
from app.schemas.events import EventResponse

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/session/{session_id}", response_model=list[EventResponse])
async def get_session_events(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[EventModel]:
    result = await db.execute(
        select(EventModel)
        .where(EventModel.session_id == session_id)
        .order_by(EventModel.timestamp.desc())
    )
    return list(result.scalars().all())


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)) -> EventModel:
    result = await db.execute(select(EventModel).where(EventModel.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
