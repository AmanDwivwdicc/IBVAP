import asyncio
import json
import logging
import os
from collections.abc import AsyncGenerator

import asyncpg
import bcrypt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from sse_starlette.sse import EventSourceResponse

from app.core.database import supabase

logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

async def verify_device_auth(
    device_id: str, 
    authorization: str = Header(...), 
    x_device_id: str = Header(...)
):
    """
    Verifies the device using Authorization header and device_id.
    Ensures bcrypt runs in a threadpool so it doesn't block the async event loop.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    # Check that query param and header match (extra security)
    if device_id != x_device_id:
        raise HTTPException(status_code=400, detail="Device ID mismatch")
        
    token = authorization.split(" ")[1]
    
    response = supabase.table("devices").select("id, api_key_hash").eq("device_id", device_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Device not found")
        
    device = response.data[0]
    device_uuid = device["id"]
    
    # Run bcrypt check in a threadpool to prevent blocking the async loop
    is_valid = await run_in_threadpool(
        bcrypt.checkpw,
        token.encode('utf-8'), 
        device['api_key_hash'].encode('utf-8')
    )
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return device_uuid

async def sse_generator(device_uuid: str) -> AsyncGenerator[dict, None]:
    # 1. Update status to online
    supabase.table("devices").update({
        "is_online": True, 
        "last_seen_at": "now()"
    }).eq("id", device_uuid).execute()
    
    # 2. Get and send current config
    settings_res = supabase.table("device_settings").select("version, settings").eq("device_id", device_uuid).execute()
    if settings_res.data:
        current = settings_res.data[0]
        yield {
            "event": "settings",
            "data": json.dumps({"version": current["version"], "settings": current["settings"]})
        }
    
    # 3. Setup asyncpg LISTEN for realtime config updates
    conn = None
    queue = asyncio.Queue()
    
    async def notification_handler(connection, pid, channel, payload):
        if payload == str(device_uuid):
            await queue.put(True)
            
    db_url = os.environ.get("DATABASE_URL")
    if not db_url or "YOUR_DB_PASSWORD" in db_url or "[DB-PASSWORD]" in db_url:
        logger.warning("DATABASE_URL not correctly set, SSE updates via NOTIFY will not work.")
    else:
        try:
            conn = await asyncpg.connect(db_url, statement_cache_size=0)
            await conn.add_listener("device_settings_channel", notification_handler)
        except Exception as e:
            logger.critical(f"Failed to connect to postgres for LISTEN: {e}")

    try:
        while True:
            try:
                # Wait for either a notification or 30s timeout for heartbeat
                await asyncio.wait_for(queue.get(), timeout=30.0)
                
                # If we get here, settings changed. Fetch the new settings.
                settings_res = supabase.table("device_settings").select("version, settings").eq("device_id", device_uuid).execute()
                if settings_res.data:
                    current = settings_res.data[0]
                    yield {
                        "event": "settings",
                        "data": json.dumps({"version": current["version"], "settings": current["settings"]})
                    }
            except TimeoutError:
                # 4. Heartbeat
                yield {
                    "event": "heartbeat",
                    "data": ""
                }
    except asyncio.CancelledError:
        # Client disconnected
        pass
    finally:
        # 5. Cleanup
        if conn:
            await conn.remove_listener("device_settings_channel", notification_handler)
            await conn.close()
            
        supabase.table("devices").update({
            "is_online": False
        }).eq("id", device_uuid).execute()

@router.get("/sse")
async def control_sse(device_id: str, device_uuid: str = Depends(verify_device_auth)):
    """
    Persistent SSE connection for pushing runtime configuration changes to edge devices.
    Path matches /api/v1/control/sse?device_id=<id>
    """
    return EventSourceResponse(sse_generator(device_uuid))
