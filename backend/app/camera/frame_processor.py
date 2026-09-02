"""
IBVAP V1 frame processing pipeline.

Includes:
- YOLO detection
- Lightweight centroid tracking
- Virtual border warnings/breaches
- Vehicle evidence capture
- Event generation
"""

import time
from typing import Any

import cv2

from app.core.config import settings
from app.database.database import async_session_factory
from app.detection.detector import detector
from app.evidence.capture import evidence_capture
from app.schemas.events import EventSeverity, EventType
from app.surveillance.event_engine import event_engine
from app.surveillance.virtual_fence import virtual_fence


class FrameProcessor:
    """Processes frames through the IBVAP AI pipeline."""

    def __init__(self) -> None:
        self.is_running = False
        self.session_id: str | None = None
        self.detector_status = "unknown"

        self.frame_count = 0

        self._tracks: dict[str, dict[str, Any]] = {}
        self._next_person_id = 1
        self._next_vehicle_id = 1

        self._last_inference_times: list[float] = []

    def start(self, session_id: str) -> None:
        """Start processing for a session."""

        self.is_running = True
        self.session_id = session_id
        self.frame_count = 0

        self._tracks.clear()
        self._next_person_id = 1
        self._next_vehicle_id = 1
        self._last_inference_times.clear()

        detector.confidence = settings.detection_confidence

        self.detector_status = (
            "ready"
            if detector.load_model()
            else "error"
        )

        # Make sure the runtime-configured threshold is used.
        virtual_fence.warning_distance_px = (
            settings.border_warning_distance_px
        )

        print(
            f"[IBVAP AI] Processing started for session: "
            f"{session_id}"
        )

    def stop(self) -> None:
        print(
            f"[IBVAP AI] Processing stopped for session: "
            f"{self.session_id}"
        )

        self.is_running = False
        self.session_id = None
        self.frame_count = 0

        self._tracks.clear()
        self._last_inference_times.clear()

    @staticmethod
    def _distance(
        a: tuple[float, float],
        b: tuple[float, float],
    ) -> float:
        return (
            (a[0] - b[0]) ** 2
            + (a[1] - b[1]) ** 2
        ) ** 0.5

    def _match_detections(
        self,
        detections: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Simple nearest-centroid tracker.

        This is intentionally lightweight for V1.
        ByteTrack can replace it in Phase 4 without
        changing the rest of the event architecture.
        """

        now_frame = self.frame_count

        unmatched_tracks = set(
            self._tracks.keys()
        )

        assigned: list[dict[str, Any]] = []

        for detection in detections:
            object_type = detection["object_type"]

            cx, cy = detection["center"]

            best_id: str | None = None
            best_distance = float("inf")

            for track_id in list(unmatched_tracks):
                track = self._tracks[track_id]

                if track["object_type"] != object_type:
                    continue

                distance = self._distance(
                    (cx, cy),
                    track["center"],
                )

                if (
                    distance < best_distance
                    and distance <= 140
                ):
                    best_distance = distance
                    best_id = track_id

            if best_id is None:
                if object_type == "PERSON":
                    best_id = (
                        f"P-{self._next_person_id:02d}"
                    )
                    self._next_person_id += 1
                else:
                    best_id = (
                        f"V-{self._next_vehicle_id:02d}"
                    )
                    self._next_vehicle_id += 1

                previous_position = (
                    None
                )
                velocity = (0.0, 0.0)

            else:
                previous_position = tuple(
                    self._tracks[best_id]["center"]
                )

                old_x, old_y = previous_position

                velocity = (
                    cx - old_x,
                    cy - old_y,
                )

                unmatched_tracks.discard(
                    best_id
                )

            track = {
                "track_id": best_id,
                "object_type": object_type,
                "class_name": detection["class_name"],
                "center": (cx, cy),
                "bbox": detection["bbox"],
                "confidence": detection["confidence"],
                "last_seen_frame": now_frame,
                "previous_position": (
                    previous_position
                ),
            }

            self._tracks[best_id] = track

            enriched = {
                **detection,
                "track_id": best_id,
                "velocity": velocity,
                "previous_position": (
                    previous_position
                ),
            }

            assigned.append(enriched)

        # Remove stale tracks.
        stale = [
            track_id
            for track_id, track in self._tracks.items()
            if now_frame - track["last_seen_frame"] > 15
        ]

        for track_id in stale:
            self._tracks.pop(
                track_id,
                None,
            )

        return assigned

    @staticmethod
    def _encode_frame(
        frame: Any,
    ) -> bytes | None:
        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                85,
            ],
        )

        if not success:
            return None

        return buffer.tobytes()

    async def _create_event(
        self,
        event_type: EventType,
        severity: EventSeverity,
        message: str,
        track_id: str | None,
        object_type: str | None,
        confidence: float | None,
        frame: Any,
        metadata: dict[str, Any] | None = None,
        vehicle_bbox: list[int | float] | None = None,
    ) -> None:
        """Create event + optional evidence atomically enough for V1."""

        if not self.session_id:
            return

        session_id = self.session_id

        event_id = event_engine.generate_event_id()

        full_metadata = metadata or {}

        snapshot_bytes = self._encode_frame(
            frame
        )

        evidence_path = None
        vehicle_crop_path = None

        if snapshot_bytes is not None:
            evidence_path = evidence_capture.capture_snapshot(
                session_id=session_id,
                event_id=event_id,
                frame_data=snapshot_bytes,
                metadata=full_metadata,
            )

        if (
            vehicle_bbox is not None
            and object_type == "VEHICLE"
        ):
            vehicle_crop_path = (
                evidence_capture.capture_vehicle_crop(
                    session_id=session_id,
                    event_id=event_id,
                    frame=frame,
                    bbox=vehicle_bbox,
                )
            )

            if vehicle_crop_path:
                full_metadata[
                    "vehicle_crop_path"
                ] = vehicle_crop_path

        async with async_session_factory() as db:
            await event_engine.emit(
                db=db,
                session_id=session_id,
                event_type=event_type,
                severity=severity,
                message=message,
                track_id=track_id,
                object_type=object_type,
                confidence=confidence,
                evidence_path=evidence_path,
                metadata=full_metadata,
                allow_duplicate=False,
                event_id_override=event_id,
            )

            await db.commit()

    async def process_frame(
        self,
        frame: Any,
        frame_id: int,
    ) -> dict[str, Any]:
        """Run the V1 surveillance pipeline on one frame."""

        if (
            not self.is_running
            or self.session_id is None
        ):
            return {
                "frame_id": frame_id,
                "detections": [],
                "tracks": [],
                "inference_fps": 0.0,
                "status": "inactive",
            }

        start_time = time.perf_counter()

        detections = detector.detect(frame)

        tracks = self._match_detections(
            detections
        )

        self.frame_count += 1

        elapsed = (
            time.perf_counter() - start_time
        )

        current_fps = (
            1.0 / elapsed
            if elapsed > 0
            else 0.0
        )

        self._last_inference_times.append(
            current_fps
        )

        if len(self._last_inference_times) > 20:
            self._last_inference_times.pop(0)

        average_fps = (
            sum(self._last_inference_times)
            / len(self._last_inference_times)
        )

        # ------------------------------------------------
        # Security event rules
        # ------------------------------------------------

        for track in tracks:

            track_id = track["track_id"]
            object_type = track["object_type"]
            confidence = track["confidence"]
            current_position = tuple(
                track["center"]
            )

            previous_position = (
                track["previous_position"]
            )

            velocity = tuple(
                track["velocity"]
            )

            # --------------------------------------------
            # PERSON + VIRTUAL BORDER
            # --------------------------------------------
            if (
                object_type == "PERSON"
                and virtual_fence.is_defined()
                and previous_position is not None
            ):

                print(
    "[FENCE DEBUG]",
    {
        "track_id": track_id,
        "current": current_position,
        "previous": previous_position,
        "velocity": velocity,
        "border_defined": virtual_fence.is_defined(),
        "frame": (
            frame.shape[1],
            frame.shape[0],
        ),
    }
)
                approaching = virtual_fence.check_approaching(
    track_id=track_id,
    current_pos=current_position,
    velocity=velocity,
    frame_width=frame.shape[1],
    frame_height=frame.shape[0],
)

                if approaching:
                    await self._create_event(
                        event_type=(
                            EventType.APPROACHING_BORDER
                        ),
                        severity=(
                            EventSeverity.WARNING
                        ),
                        message=(
                            f"Person {track_id} is "
                            "approaching/touching the "
                            "virtual border."
                        ),
                        track_id=track_id,
                        object_type="PERSON",
                        confidence=confidence,
                        frame=frame,
                        metadata={
                            "position": list(
                                current_position
                            ),
                            "velocity": list(
                                velocity
                            ),
                        },
                    )

                crossing = virtual_fence.check_crossing(
    track_id=track_id,
    current_pos=current_position,
    previous_pos=previous_position,
    frame_width=frame.shape[1],
    frame_height=frame.shape[0],
)

                if crossing:
                    await self._create_event(
                        event_type=(
                            EventType.VIRTUAL_FENCE_BREACH
                        ),
                        severity=(
                            EventSeverity.CRITICAL
                        ),
                        message=(
                            f"Person {track_id} "
                            "crossed the virtual border."
                        ),
                        track_id=track_id,
                        object_type="PERSON",
                        confidence=confidence,
                        frame=frame,
                        metadata={
                            "direction": crossing[
                                "direction"
                            ],
                            "position": list(
                                current_position
                            ),
                        },
                    )

            # --------------------------------------------
            # VEHICLE EVIDENCE
            # --------------------------------------------
            if object_type == "VEHICLE":

                await self._create_event(
                    event_type=(
                        EventType.VEHICLE_DETECTED
                    ),
                    severity=EventSeverity.INFO,
                    message=(
                        f"{track['class_name']} "
                        f"{track_id} detected."
                    ),
                    track_id=track_id,
                    object_type="VEHICLE",
                    confidence=confidence,
                    frame=frame,
                    vehicle_bbox=track["bbox"],
                    metadata={
                        "vehicle_class": (
                            track["class_name"]
                        ),
                        "bbox": track["bbox"],
                    },
                )

        # Prepare frontend track payload.
        frontend_tracks = []

        for track in tracks:
            frontend_tracks.append(
                {
                    "track_id": track["track_id"],
                    "object_type": track["object_type"],
                    "class_name": track["class_name"],
                    "confidence": track["confidence"],
                    "bbox": track["bbox"],
                    "center": track["center"],
                    "frame_width": frame.shape[1],
                    "frame_height": frame.shape[0],
                }
            )

        return {
            "frame_id": frame_id,
            "session_id": self.session_id,
            "detections": tracks,
            "tracks": frontend_tracks,
            "inference_fps": round(
                average_fps,
                2,
            ),
            "status": "active",
            "frame_count": self.frame_count,
        }


frame_processor = FrameProcessor()