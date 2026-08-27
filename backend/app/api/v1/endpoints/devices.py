import logging
from datetime import datetime

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import supabase
from app.models.schemas import HeartbeatSchema

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()


async def authenticate_device(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    api_key = credentials.credentials
    # For heartbeat we don't know the device ID upfront from path, we get it from payload in route
    return api_key


@router.post("/heartbeat", status_code=status.HTTP_200_OK)
async def heartbeat(
    payload: HeartbeatSchema, api_key: str = Depends(authenticate_device)
):
    try:
        response = (
            supabase.table("devices")
            .select("id, api_key_hash")
            .eq("device_id", payload.device_id)
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

        device_uuid = device["id"]

        # In a full implementation, we'd store these metrics in a time-series table or cache.
        # For now, we update the device's last_seen status

        supabase.table("devices").update(
            {"last_seen_at": datetime.utcnow().isoformat(), "is_online": True}
        ).eq("id", device_uuid).execute()

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing heartbeat: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
