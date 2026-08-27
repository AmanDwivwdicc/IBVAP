import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.database import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/known")
async def upload_known_face(
    name: str = Form(...),
    description: str | None = Form(None),
    threat_level: str | None = Form("medium"),
    file: UploadFile = File(...)
):
    """
    Upload a face image to the watchlist.
    This requires extracting the 512d face embedding via ONNX.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Must be an image file")

    image_bytes = await file.read()
    
    # 1. Run ONNX Model to extract embedding (Mocked for MVP)
    # In a real system, you'd pass image_bytes to insightface or similar
    logger.info(f"Extracting embedding for {name} (Mocked)...")
    
    # Generate a dummy 512d vector formatted as pgvector string
    import random
    mock_vector = "[" + ",".join([str(random.uniform(-1, 1)) for _ in range(512)]) + "]"
    
    # 2. Upload reference image to Storage
    import uuid
    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    storage_path = f"watchlist/{file_id}.{ext}"
    
    try:
        supabase.storage.from_("evidence").upload(
            path=storage_path,
            file=image_bytes,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        logger.error(f"Failed to upload face image: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image to storage")
        
    # 3. Save to database
    res = supabase.table("known_faces").insert({
        "name": name,
        "description": description,
        "threat_level": threat_level,
        "face_embedding": mock_vector,
        "reference_image_path": storage_path
    }).execute()
    
    if not res.data:
        # Rollback storage
        supabase.storage.from_("evidence").remove([storage_path])
        raise HTTPException(status_code=500, detail="Failed to save profile to database")
        
    return {"status": "success", "profile": res.data[0]}
