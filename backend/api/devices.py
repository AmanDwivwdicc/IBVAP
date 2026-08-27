import logging
import secrets

import bcrypt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.database import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

class CameraPayload(BaseModel):
    camera_id: str
    name: str | None = None
    source_url: str | None = None

class DeviceRegistrationPayload(BaseModel):
    device_id: str
    name: str | None = None
    location: str | None = None
    cameras: list[CameraPayload] | None = None

@router.post("")
async def register_device(payload: DeviceRegistrationPayload):
    """
    Registers a new edge device.
    Generates a secure API key, hashes it, stores the hash, 
    and returns the plaintext key ONCE.
    """
    # 1. Check if device already exists
    existing = supabase.table("devices").select("id").eq("device_id", payload.device_id).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this device_id already exists."
        )

    # 2. Generate secure API key
    # e.g. ibvap_sk_7f8a9b0c...
    raw_api_key = f"ibvap_sk_{secrets.token_urlsafe(32)}"
    
    # 3. Hash the key
    # Note: bcrypt.hashpw requires bytes
    salt = bcrypt.gensalt()
    hashed_key = bcrypt.hashpw(raw_api_key.encode('utf-8'), salt).decode('utf-8')

    # 4. Insert into database
    device_data = {
        "device_id": payload.device_id,
        "name": payload.name or f"Edge Device {payload.device_id}",
        "location": payload.location,
        "api_key_hash": hashed_key,
        "is_online": False
    }

    try:
        res = supabase.table("devices").insert(device_data).execute()
        if not res.data:
            raise Exception("No data returned from insert")
            
        device_uuid = res.data[0]["id"]
        
        # Insert cameras if provided
        if payload.cameras:
            camera_data = []
            for cam in payload.cameras:
                camera_data.append({
                    "device_id": device_uuid,
                    "camera_id": cam.camera_id,
                    "name": cam.name or f"Camera {cam.camera_id}",
                    "source_url": cam.source_url,
                    "is_active": True
                })
            supabase.table("cameras").insert(camera_data).execute()
            
    except Exception as e:
        logger.error(f"Failed to register device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during registration."
        )

    # 5. Return the plaintext key to the user
    return {
        "status": "success",
        "message": "Device registered. Copy the api_key now. It will never be shown again.",
        "device": {
            "id": res.data[0]["id"],
            "device_id": res.data[0]["device_id"],
            "name": res.data[0]["name"]
        },
        "api_key": raw_api_key
    }
