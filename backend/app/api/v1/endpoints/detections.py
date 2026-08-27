import base64
import logging
import uuid
from datetime import datetime

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.database import supabase
from app.models.schemas import AlertPayloadSchema, AlertResponseSchema

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()


async def authenticate_device(
    payload: AlertPayloadSchema,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Authenticates the device by looking up its device_id and verifying the API key hash.
    Returns the device database record.
    """
    api_key = credentials.credentials

    # 1. Look up device
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

    # 2. Verify API key
    stored_hash = device.get("api_key_hash")
    if not stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device has no API key configured",
        )

    # Check hash (encoded to bytes for bcrypt)
    if not bcrypt.checkpw(api_key.encode("utf-8"), stored_hash.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return device


@router.post(
    "/", response_model=AlertResponseSchema, status_code=status.HTTP_201_CREATED
)
async def ingest_alert(
    payload: AlertPayloadSchema,
    request: Request,
    device: dict = Depends(authenticate_device),
):
    """
    Ingests an alert from an edge device.
    1. Authenticates
    2. Resolves/creates camera
    3. Uploads evidence to storage
    4. Saves to database
    5. Returns 201 Created immediately
    """
    device_uuid = device["id"]

    try:
        # 1. Resolve or create camera
        camera_res = (
            supabase.table("cameras")
            .select("id")
            .eq("device_id", device_uuid)
            .eq("camera_id", payload.camera_id)
            .execute()
        )

        if camera_res.data:
            camera_uuid = camera_res.data[0]["id"]
        else:
            # Auto-register camera
            new_cam = (
                supabase.table("cameras")
                .insert(
                    {
                        "device_id": device_uuid,
                        "camera_id": payload.camera_id,
                        "name": f"Auto-registered {payload.camera_id}",
                    }
                )
                .execute()
            )
            camera_uuid = new_cam.data[0]["id"]

        alert_uuid = str(uuid.uuid4())
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        evidence_path = None
        has_evidence = False

        # 2. Extract and upload evidence
        # Find the first detection with evidence (usually only one per alert in this architecture)
        for det in payload.detections:
            if det.evidence and det.evidence.jpeg_base64:
                try:
                    image_bytes = base64.b64decode(det.evidence.jpeg_base64)
                    storage_path = f"{payload.device_id}/{payload.camera_id}/{date_str}/{alert_uuid}.jpg"

                    supabase.storage.from_(settings.STORAGE_BUCKET_EVIDENCE).upload(
                        file=image_bytes,
                        path=storage_path,
                        file_options={"content-type": "image/jpeg"},
                    )
                    evidence_path = storage_path
                    has_evidence = True
                    break  # Only upload once per alert
                except Exception as e:
                    logger.error(
                        f"Failed to upload evidence for alert {alert_uuid}: {e}"
                    )
                    # Decide whether to fail the whole request or continue without evidence.
                    # Continuing without evidence might be safer for edge device resilience.

        # 3. Strip evidence from raw payload before saving
        raw_payload_dict = payload.model_dump()
        for det in raw_payload_dict["detections"]:
            if "evidence" in det:
                del det["evidence"]

        # 4. Insert Alert
        alert_data = {
            "id": alert_uuid,
            "device_id": device_uuid,
            "camera_id": camera_uuid,
            "timestamp": payload.timestamp.isoformat(),
            "detection_count": len(payload.detections),
            "has_evidence": has_evidence,
            "evidence_path": evidence_path,
            "raw_payload": raw_payload_dict,
            "processed": False,
        }

        supabase.table("alerts").insert(alert_data).execute()

        # 5. Insert Detections
        if payload.detections:
            detections_data = []
            for det in payload.detections:
                detections_data.append(
                    {
                        "alert_id": alert_uuid,
                        "feature": det.feature,
                        "class_id": det.class_id,
                        "class_name": det.class_name,
                        "confidence": det.confidence,
                        "bbox_xyxy": det.bbox_xyxy,
                        "tracker_id": det.tracker_id,
                    }
                )
            supabase.table("detections").insert(detections_data).execute()

        # 6. Update device last seen
        supabase.table("devices").update(
            {"last_seen_at": datetime.utcnow().isoformat()}
        ).eq("id", device_uuid).execute()

        # (PostgreSQL LISTEN/NOTIFY or background task for AI processing will pick it up from here)

        return {"alert_id": alert_uuid}

    except Exception as e:
        logger.error(f"Error processing alert: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
