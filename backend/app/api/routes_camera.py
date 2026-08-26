"""Camera status and readiness API routes."""

from fastapi import APIRouter

from app.schemas.sessions import SystemStatus
from app.surveillance.session_manager import session_manager

router = APIRouter(prefix="/api/camera", tags=["camera"])


@router.get("/status")
async def get_camera_status() -> dict:
    return {
        "camera_ready": session_manager.camera_ready,
        "session_status": session_manager.status,
        "active_session_id": session_manager.active_session_id,
    }


@router.post("/ready")
async def set_camera_ready(ready: bool = True) -> dict:
    session_manager.set_camera_ready(ready)
    status = "camera_ready" if ready else "idle"
    return {"camera_ready": ready, "status": status}


@router.get("/system")
async def get_system_status() -> SystemStatus:
    return SystemStatus(
        status="online",
        ai_pipeline="stub",
        message="AI detection pipeline not yet implemented (Phase 3)",
    )
