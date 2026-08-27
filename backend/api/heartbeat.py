import logging

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import bcrypt

from app.core.database import supabase

logger = logging.getLogger(__name__)

router = APIRouter()

class HeartbeatPayload(BaseModel):
    device_id: str
    cpu_percent: float | None = None
    memory_percent: float | None = None
    temperature_celsius: float | None = None
    uptime_seconds: int | None = None
    queue_depth: int | None = None
    cameras_active: int | None = None

# Using the same cache from detections to avoid hitting DB
from .detections import _device_auth_cache

async def verify_heartbeat_device(payload: HeartbeatPayload, authorization: str = Header(None)):
    """Verifies edge device API key from Authorization: Bearer <key> for heartbeat"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header format"
        )
    
    token = authorization.split(" ")[1]
    
    if payload.device_id in _device_auth_cache:
        return _device_auth_cache[payload.device_id]
    
    response = await run_in_threadpool(
        lambda: supabase.table("devices").select("id, api_key_hash").eq("device_id", payload.device_id).execute()
    )
    
    if not response.data:
        logger.error(f"Device {payload.device_id} not found in database for heartbeat")
        raise HTTPException(status_code=401, detail="Invalid API key (device not found)")
        
    device = response.data[0]
    if device.get("api_key_hash"):
        try:
            is_valid = await run_in_threadpool(
                bcrypt.checkpw,
                token.encode('utf-8'), 
                device['api_key_hash'].encode('utf-8')
            )
            if is_valid:
                _device_auth_cache[payload.device_id] = device["id"]
                return device["id"]
        except Exception:
            pass
                
    raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("")
async def receive_heartbeat(payload: HeartbeatPayload, device_uuid: str = Depends(verify_heartbeat_device)):
    """
    Receives periodic health pings from edge devices.
    Updates the device's is_online status and last_seen_at timestamp.
    """
    # 2. Update device status
    update_res = await run_in_threadpool(
        lambda: supabase.table("devices").update({
            "is_online": True,
            "last_seen_at": "now()"
        }).eq("id", device_uuid).execute()
    )

    if not update_res.data:
        logger.error(f"Failed to update heartbeat for {device_uuid}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device heartbeat"
        )
        
    return {"status": "ok"}
