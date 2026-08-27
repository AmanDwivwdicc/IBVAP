from fastapi import APIRouter

from app.api.v1.endpoints import control, detections, devices

api_router = APIRouter()

api_router.include_router(detections.router, prefix="/detections", tags=["detections"])
api_router.include_router(control.router, prefix="/control", tags=["control"])
api_router.include_router(devices.router, tags=["devices"])
