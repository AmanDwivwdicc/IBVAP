import base64
import logging
from datetime import datetime

import bcrypt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from app.core.database import supabase

logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

# --- Pydantic Models for the Incoming Payload ---

class EvidencePayload(BaseModel):
    content_type: str
    jpeg_base64: str

class DetectionPayload(BaseModel):
    feature: str | None = None
    class_id: int | None = None
    class_name: str | None = None
    confidence: float | None = None
    bbox_xyxy: list[float] | None = None
    tracker_id: int | None = None
    evidence: dict | None = None

class AlertPayload(BaseModel):
    device_id: str
    camera_id: str
    timestamp: str | datetime
    detections: list[DetectionPayload] = []

# --- Dependencies ---

# --- Global Caches to reduce Supabase latency under heavy load ---
_device_auth_cache: dict[str, str] = {}  # device_id -> device_uuid
_camera_id_cache: dict[tuple[str, str], str] = {} # (device_uuid, camera_id) -> db_camera_uuid

async def verify_edge_device(payload: AlertPayload, authorization: str = Header(None)):
    """Verifies edge device API key from Authorization: Bearer <key> for a specific device"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header format"
        )
    
    token = authorization.split(" ")[1]
    
    # Check memory cache first to save 50ms+ database hit
    if payload.device_id in _device_auth_cache:
        # Note: In production you might want to expire cache or cache the token hash specifically
        # to ensure revoked keys take effect immediately. For this demo, this is fine.
        return _device_auth_cache[payload.device_id]
    
    # Fetch only the specific device based on the device_id in the payload
    logger.debug(f"Verifying device ID: {payload.device_id}")
    # run in threadpool as python supabase is synchronous
    response = await run_in_threadpool(
        lambda: supabase.table("devices").select("id, api_key_hash").eq("device_id", payload.device_id).execute()
    )
    
    if not response.data:
        logger.error(f"Device {payload.device_id} not found in database")
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
                logger.debug(f"Device {payload.device_id} authenticated successfully")
                _device_auth_cache[payload.device_id] = device["id"]
                return device["id"]
            else:
                logger.error(f"Invalid password hash for device {payload.device_id}")
        except Exception as e:
            logger.error(f"Bcrypt error for {payload.device_id}: {e}")
            pass
                
    raise HTTPException(status_code=401, detail="Invalid API key")

# --- Routes ---

@router.post("")
async def ingest_alert(payload: AlertPayload, device_uuid: str = Depends(verify_edge_device)):
    """
    Ingests alerts from edge devices.
    Processes evidence images, saves to Storage, and writes to database.
    """
    
    # 2. Resolve Camera ID using Cache to save DB roundtrips
    cache_key = (device_uuid, payload.camera_id)
    if cache_key in _camera_id_cache:
        db_camera_uuid = _camera_id_cache[cache_key]
    else:
        camera_res = await run_in_threadpool(
            lambda: supabase.table("cameras").select("id").eq("device_id", device_uuid).eq("camera_id", payload.camera_id).execute()
        )
        
        if camera_res.data:
            db_camera_uuid = camera_res.data[0]["id"]
        else:
            # Auto-register camera
            new_cam_res = await run_in_threadpool(
                lambda: supabase.table("cameras").insert({
                    "device_id": device_uuid,
                    "camera_id": payload.camera_id,
                    "name": f"Camera {payload.camera_id}",
                    "is_active": True
                }).execute()
            )
            if new_cam_res.data:
                db_camera_uuid = new_cam_res.data[0]["id"]
                
        # save to cache
        _camera_id_cache[cache_key] = db_camera_uuid
    
    # 3. Process Evidence and Insert Alert
    timestamp_str = payload.timestamp if isinstance(payload.timestamp, str) else payload.timestamp.isoformat()
    alert_insert_data = {
        "device_id": device_uuid,
        "camera_id": db_camera_uuid,
        "timestamp": timestamp_str,
        "detection_count": len(payload.detections),
        "has_evidence": False,
        "evidence_path": None,
        "raw_payload": None, # Will set this after stripping base64
        "processed": False
    }

    # Extract base64 evidence if any detection has it
    # Note: server.md says: "If ANY detection has evidence.jpeg_base64... upload to Storage"
    # Assuming one evidence image per alert for the entire frame.
    evidence_b64 = None
    for d in payload.detections:
        if d.evidence and d.evidence.get("jpeg_base64"):
            evidence_b64 = d.evidence.get("jpeg_base64")
            break
            
    # We must strip the evidence from the raw payload before saving to DB
    stripped_payload = payload.model_dump(mode="json")
    for d in stripped_payload["detections"]:
        if "evidence" in d and d["evidence"] is not None:
            # We keep the evidence object but strip the massive base64 string
            d["evidence"]["jpeg_base64"] = "[STRIPPED]"
            
    alert_insert_data["raw_payload"] = stripped_payload

    # Upload evidence to Supabase Storage if it exists
    if evidence_b64:
        try:
            # Decode base64
            image_bytes = base64.b64decode(evidence_b64)
            
            # Format: {device_id}/{camera_id}/{date}/{alert_id}.jpg
            if isinstance(payload.timestamp, str):
                try:
                    ts = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
                    date_str = ts.strftime("%Y-%m-%d")
                except ValueError:
                    date_str = datetime.now().strftime("%Y-%m-%d")
            else:
                date_str = payload.timestamp.strftime("%Y-%m-%d")
            
            # We don't have the alert_uuid yet, so we'll generate one in python
            import uuid
            alert_uuid = str(uuid.uuid4())
            alert_insert_data["id"] = alert_uuid
            
            storage_path = f"{payload.device_id}/{payload.camera_id}/{date_str}/{alert_uuid}.jpg"
            
            # Upload to Supabase Storage in a threadpool so it doesn't block FastAPI
            await run_in_threadpool(
                lambda: supabase.storage.from_("evidence").upload(
                    path=storage_path,
                    file=image_bytes,
                    file_options={"content-type": "image/jpeg"}
                )
            )
            
            alert_insert_data["has_evidence"] = True
            alert_insert_data["evidence_path"] = storage_path
            
        except Exception as e:
            logger.error(f"Failed to process/upload evidence: {e}")
            # Specs say return 500 if server error so edge will retry
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process evidence image"
            )

    # Insert the Alert
    alert_res = await run_in_threadpool(
        lambda: supabase.table("alerts").insert(alert_insert_data).execute()
    )
    if not alert_res.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert alert"
        )
        
    db_alert_uuid = alert_res.data[0]["id"]
    
    # 4. Insert Detections
    if payload.detections:
        detections_insert_data = []
        needs_ai_processing = False
        
        for d in payload.detections:
            detections_insert_data.append({
                "alert_id": db_alert_uuid,
                "feature": d.feature or "object_detection",
                "class_id": d.class_id,
                "class_name": d.class_name,
                "confidence": d.confidence,
                "bbox_xyxy": d.bbox_xyxy,
                "tracker_id": d.tracker_id
            })
            
            # Check if this alert needs secondary AI processing
            # class_id=0 (person), class_id=2,3,5,7 (vehicles)
            if d.class_id in [0, 2, 3, 5, 7]:
                needs_ai_processing = True
                
        await run_in_threadpool(
            lambda: supabase.table("detections").insert(detections_insert_data).execute()
        )
        
        # 5. Queue AI Task
        if needs_ai_processing and alert_insert_data["has_evidence"]:
            # Trigger PostgreSQL NOTIFY or just leave processed=False 
            # for a polling worker (specs suggest polling or NOTIFY).
            # For simplicity, we just leave processed=False and the background worker
            # can use: SELECT * FROM alerts WHERE processed=false AND has_evidence=true
            pass

    # 6. Respond immediately
    return {"alert_id": db_alert_uuid}
