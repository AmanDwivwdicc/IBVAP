import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import Client, create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Import routers after supabase client is initialized
from api.control import router as control_router
from api.detections import router as detections_router
from api.devices import router as devices_router
from api.faces import router as faces_router
from api.heartbeat import router as heartbeat_router
from api.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check supabase connection on startup
    try:
        _ = supabase.table('devices').select('id').limit(1).execute()
        logger.info("✅ Supabase connection successful.")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Supabase: {e}")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="IBVAP Central Server",
    description="Command-and-control hub for distributed AI surveillance devices",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(control_router, prefix="/api/v1/control", tags=["Control"])
app.include_router(settings_router, prefix="/api/v1/control", tags=["Control"])
app.include_router(detections_router, prefix="/api/v1/detections", tags=["Detections"])
app.include_router(faces_router, prefix="/api/v1/faces", tags=["Faces"])
app.include_router(heartbeat_router, prefix="/api/v1/heartbeat", tags=["Heartbeat"])
app.include_router(devices_router, prefix="/api/v1/devices", tags=["Devices"])

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    body = await request.body()
    logger.error(f"Validation error: {exc.errors()}")
    logger.error(f"Request body: {body.decode('utf-8')[:1000]}...")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ibvap-central-server"}
