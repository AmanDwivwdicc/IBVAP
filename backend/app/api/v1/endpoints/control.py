import asyncio
import json
import logging

import bcrypt
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.core.database import supabase

router = APIRouter()
logger = logging.getLogger(__name__)


async def authenticate_sse_device(
    authorization: str = Header(None), x_device_id: str = Header(None)
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    if not x_device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Device-ID header"
        )

    api_key = authorization.split("Bearer ")[1]

    response = (
        supabase.table("devices")
        .select("id, api_key_hash")
        .eq("device_id", x_device_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown device_id"
        )

    device = response.data[0]

    stored_hash = device.get("api_key_hash")
    if not stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device has no API key configured",
        )

    if not bcrypt.checkpw(api_key.encode("utf-8"), stored_hash.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return device


async def sse_generator(device_uuid: str, request: Request):
    """
    Generator for Server-Sent Events.
    Yields initial settings and keeps connection alive.
    In a complete implementation, this would listen to a PostgreSQL NOTIFY channel or Redis PubSub
    for updates to device_settings.
    """
    try:
        # Mark online
        supabase.table("devices").update({"is_online": True}).eq(
            "id", device_uuid
        ).execute()

        # Get current settings
        settings_res = (
            supabase.table("device_settings")
            .select("version, settings")
            .eq("device_id", device_uuid)
            .execute()
        )

        if settings_res.data:
            current_settings = settings_res.data[0]
            yield f"event: settings\ndata: {json.dumps(current_settings)}\n\n"

        # We need a pubsub mechanism to receive updates here (e.g. redis or listen/notify via a separate library,
        # since supabase-py doesn't easily expose realtime listen for asyncio generators out of the box in this context).
        # We simulate the keep-alive heartbeat loop.

        while True:
            if await request.is_disconnected():
                break

            # Send heartbeat comment
            yield ": heartbeat\n\n"

            # Sleep for heartbeat interval (e.g., 30s)
            # In a real app we'd await on a task that completes on either a pub/sub message OR a timeout
            await asyncio.sleep(30)

    except Exception as e:
        logger.error(f"SSE Error for device {device_uuid}: {e}")
    finally:
        # Mark offline when disconnected
        try:
            supabase.table("devices").update({"is_online": False}).eq(
                "id", device_uuid
            ).execute()
        except Exception:
            pass


@router.get("/sse")
async def control_sse(
    request: Request, device_id: str, device: dict = Depends(authenticate_sse_device)
):
    """
    SSE endpoint for pushing device configuration.
    Note: device_id parameter comes from the query string to match server.md.
    The headers are checked in the dependency.
    """
    device_uuid = device["id"]
    return StreamingResponse(
        sse_generator(device_uuid, request), media_type="text/event-stream"
    )
