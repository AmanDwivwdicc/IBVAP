import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.database import supabase

logger = logging.getLogger(__name__)

router = APIRouter()

class SettingsUpdatePayload(BaseModel):
    settings: dict[str, Any]

@router.put("/devices/{device_uuid}/settings")
async def update_device_settings(device_uuid: str, payload: SettingsUpdatePayload):
    """
    Updates the device settings in the database.
    Because Supabase Realtime is enabled on the table (or we use PG NOTIFY),
    the active SSE connection will pick this up and push it to the device.
    """
    import uuid
    new_version = str(uuid.uuid4())
    
    # Check if config exists
    existing = supabase.table("device_settings").select("id").eq("device_id", device_uuid).execute()
    
    if existing.data:
        res = supabase.table("device_settings").update({
            "settings": payload.settings,
            "version": new_version
        }).eq("device_id", device_uuid).execute()
    else:
        res = supabase.table("device_settings").insert({
            "device_id": device_uuid,
            "settings": payload.settings,
            "version": new_version
        }).execute()
        
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to update settings")
        
    # Postgres NOTIFY to wake up the SSE generator immediately
    try:
        # We need asyncpg to send the NOTIFY
        import asyncpg
        db_url = os.environ.get("DATABASE_URL")
        if db_url and not "YOUR_DB_PASSWORD" in db_url and not "[DB-PASSWORD]" in db_url:
            conn = await asyncpg.connect(db_url)
            # The payload must match what the SSE generator listens for (device_uuid)
            await conn.execute(f"NOTIFY device_settings_channel, '{device_uuid}'")
            await conn.close()
    except Exception as e:
        logger.error(f"Failed to trigger Postgres NOTIFY for SSE update: {e}")
        # We don't fail the request, the 30s heartbeat fallback will catch it eventually

    return {"status": "success", "version": new_version}
