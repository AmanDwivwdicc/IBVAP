"""Report generation API routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.database import get_db
from app.reports.generator import report_generator

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{session_id}")
async def get_report(session_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        return await report_generator.generate(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}/download")
async def download_report(session_id: str, db: AsyncSession = Depends(get_db)):
    report = await report_generator.generate(db, session_id)
    report_path = settings.reports_dir / f"{session_id}.json"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        path=str(report_path),
        filename=f"IBVAP-Report-{session_id}.json",
        media_type="application/json",
    )
