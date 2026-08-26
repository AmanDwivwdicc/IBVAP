"""
Frame processing pipeline for IBVAP V1.

Phase 3:
- YOLO detection
- No tracking yet
- No behavior/event analysis yet
"""

from time import monotonic
from typing import Any

from app.core.config import settings
from app.detection.detector import detector


class FrameProcessor:
    """Processes webcam frames through the AI detection pipeline."""

    def __init__(self) -> None:
        self.is_running = False
        self.session_id: str | None = None
        self.detector_status = "unknown"
        self.frame_count = 0

        self._last_inference_time: float | None = None
        self._inference_times: list[float] = []

    def start(self, session_id: str) -> None:
        """Start AI processing for a surveillance session."""

        self.is_running = True
        self.session_id = session_id
        self.frame_count = 0
        self._last_inference_time = None
        self._inference_times.clear()

        # Ensure YOLO is ready.
        detector.confidence = settings.detection_confidence
        detector.load_model()

        print(f"[IBVAP AI] Processing started for session: {session_id}")

    def stop(self) -> None:
        """Stop AI processing."""

        print(
            f"[IBVAP AI] Processing stopped for session: {self.session_id}"
        )

        self.is_running = False
        self.session_id = None
        self.frame_count = 0
        self._last_inference_time = None
        self._inference_times.clear()

    def process_frame(
        self,
        frame: Any,
        frame_id: int,
    ) -> dict[str, Any]:
        """
        Run detection on one frame.

        Tracking and security-event logic are intentionally excluded
        from Phase 3.
        """

        if not self.is_running or self.session_id is None:
            return {
                "frame_id": frame_id,
                "detections": [],
                "tracks": [],
                "inference_fps": 0.0,
                "status": "inactive",
            }

        start_time = monotonic()

        detections = detector.detect(frame)

        elapsed = monotonic() - start_time

        if elapsed > 0:
            inference_fps = 1.0 / elapsed
        else:
            inference_fps = 0.0

        self._inference_times.append(inference_fps)

        if len(self._inference_times) > 20:
            self._inference_times.pop(0)

        average_fps = (
            sum(self._inference_times) / len(self._inference_times)
            if self._inference_times
            else 0.0
        )

        self.frame_count += 1

        return {
            "frame_id": frame_id,
            "session_id": self.session_id,
            "detections": detections,
            "tracks": [],
            "inference_fps": round(average_fps, 2),
            "status": "active",
            "frame_count": self.frame_count,
        }


frame_processor = FrameProcessor()