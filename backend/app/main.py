"""IBVAP — Intelligent Border Video Analytics Platform — FastAPI Backend."""

import base64
import binascii
import json
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_camera import router as camera_router
from app.api.routes_events import router as events_router
from app.api.routes_reports import router as reports_router
from app.api.routes_sessions import router as sessions_router
from app.camera.frame_processor import frame_processor
from app.core.config import settings
from app.database.database import init_db
from app.detection.detector import detector
from app.websocket.manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.evidence_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)

    await init_db()

    detector.confidence = settings.detection_confidence

    if detector.load_model():
        frame_processor.detector_status = "ready"
        print("[IBVAP] AI engine: READY")
    else:
        frame_processor.detector_status = "error"
        print("[IBVAP] AI engine: FAILED TO LOAD")

    yield

    frame_processor.stop()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligent Border Video Analytics Platform — SIH Prototype V1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(camera_router)
app.include_router(sessions_router)
app.include_router(events_router)
app.include_router(reports_router)

app.mount(
    "/evidence",
    StaticFiles(directory=str(settings.evidence_dir)),
    name="evidence",
)


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": settings.app_name,
        "version": settings.app_version,
        "ai_pipeline": "yolo_detection",
        "ai_status": getattr(
            frame_processor,
            "detector_status",
            "unknown",
        ),
    }


@app.get("/api/config")
async def get_config():
    return {
        "detection_confidence": settings.detection_confidence,
        "inference_fps": settings.inference_fps,
        "loitering_threshold_seconds": settings.loitering_threshold_seconds,
        "border_warning_distance_px": settings.border_warning_distance_px,
    }


def decode_frame(image_data: str) -> np.ndarray | None:
    """Decode a base64 JPEG/data URL into an OpenCV frame."""

    try:
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        raw_bytes = base64.b64decode(
            image_data,
            validate=True,
        )

        array = np.frombuffer(
            raw_bytes,
            dtype=np.uint8,
        )

        frame = cv2.imdecode(
            array,
            cv2.IMREAD_COLOR,
        )

        return frame

    except (ValueError, binascii.Error):
        return None

    except Exception as exc:
        print(f"[IBVAP] Frame decode error: {exc}")
        return None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)

    try:
        await ws_manager.send_personal(
            websocket,
            "connected",
            {
                "message": "Connected to IBVAP real-time channel",
                "ai_pipeline": "yolo_detection",
                "ai_status": getattr(
                    frame_processor,
                    "detector_status",
                    "unknown",
                ),
            },
        )

        while True:
            raw_message = await websocket.receive_text()

            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                await ws_manager.send_personal(
                    websocket,
                    "error",
                    {
                        "message": "Invalid WebSocket JSON message",
                    },
                )
                continue

            message_type = message.get("type")

            # -----------------------------------------
            # START AI
            # -----------------------------------------
            if message_type == "start_ai":
                session_id = message.get("session_id")

                if not session_id:
                    await ws_manager.send_personal(
                        websocket,
                        "error",
                        {
                            "message": "session_id is required to start AI",
                        },
                    )
                    continue

                frame_processor.start(session_id)

                await ws_manager.send_personal(
                    websocket,
                    "ai_started",
                    {
                        "session_id": session_id,
                        "status": "active",
                    },
                )

            # -----------------------------------------
            # FRAME
            # -----------------------------------------
            elif message_type == "frame":
                if not frame_processor.is_running:
                    print("[IBVAP] Frame received but AI is not running")
                    continue

                session_id = message.get("session_id")
                image_data = message.get("image")
                frame_id = int(message.get("frame_id", 0))

                if session_id != frame_processor.session_id:
                    print(
                        f"[IBVAP] Frame session mismatch: "
                        f"{session_id} != {frame_processor.session_id}"
                    )
                    continue

                if not image_data:
                    print("[IBVAP] Empty frame received")
                    continue

                frame = decode_frame(image_data)

                if frame is None:
                    print(
                        f"[IBVAP] Could not decode frame {frame_id}"
                    )
                    continue

                if frame_id % 5 == 0:
                    print(
                        f"[IBVAP] Frame {frame_id} received: "
                        f"{frame.shape[1]}x{frame.shape[0]}"
                    )

                result = frame_processor.process_frame(
                    frame,
                    frame_id,
                )

                if frame_id % 5 == 0:
                    print(
                        f"[IBVAP] Frame {frame_id}: "
                        f"{len(result['detections'])} detections"
                    )

                await ws_manager.send_personal(
                    websocket,
                    "detections",
                    result,
                )

            # -----------------------------------------
            # STOP AI
            # -----------------------------------------
            elif message_type == "stop_ai":
                frame_processor.stop()

                await ws_manager.send_personal(
                    websocket,
                    "ai_stopped",
                    {
                        "status": "inactive",
                    },
                )

            # -----------------------------------------
            # PING
            # -----------------------------------------
            elif message_type == "ping":
                await ws_manager.send_personal(
                    websocket,
                    "pong",
                    {
                        "status": "online",
                    },
                )

            else:
                await ws_manager.send_personal(
                    websocket,
                    "error",
                    {
                        "message": f"Unknown message type: {message_type}",
                    },
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        frame_processor.stop()

    except Exception as exc:
        print(f"[IBVAP] WebSocket error: {exc}")
        ws_manager.disconnect(websocket)
        frame_processor.stop()