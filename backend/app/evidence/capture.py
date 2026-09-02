"""
Evidence capture for IBVAP V1.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.core.config import settings


class EvidenceCapture:
    """Captures and stores evidence for security events."""

    def __init__(self) -> None:
        settings.evidence_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _session_dir(self, session_id: str) -> Path:
        path = settings.evidence_dir / session_id
        path.mkdir(
            parents=True,
            exist_ok=True,
        )
        return path

    def capture_snapshot(
        self,
        session_id: str,
        event_id: str,
        frame_data: bytes | None,
        metadata: dict[str, Any],
    ) -> str | None:
        """Save a full-frame JPEG snapshot and metadata."""

        event_dir = self._session_dir(session_id) / event_id

        event_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        full_metadata = {
            **metadata,
            "event_id": event_id,
            "session_id": session_id,
            "captured_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        meta_path = event_dir / "metadata.json"

        meta_path.write_text(
            json.dumps(
                full_metadata,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        if not frame_data:
            return None

        snapshot_path = event_dir / "snapshot.jpg"

        snapshot_path.write_bytes(frame_data)

        return str(snapshot_path)

    def capture_vehicle_crop(
        self,
        session_id: str,
        event_id: str,
        frame: np.ndarray,
        bbox: list[int | float],
    ) -> str | None:
        """Save a cropped vehicle image for future ANPR."""

        try:
            height, width = frame.shape[:2]

            x1, y1, x2, y2 = map(
                int,
                bbox,
            )

            padding = 10

            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(width, x2 + padding)
            y2 = min(height, y2 + padding)

            if x2 <= x1 or y2 <= y1:
                return None

            crop = frame[y1:y2, x1:x2]

            if crop.size == 0:
                return None

            event_dir = (
                self._session_dir(session_id)
                / event_id
            )

            event_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            crop_path = event_dir / "vehicle_crop.jpg"

            success = cv2.imwrite(
                str(crop_path),
                crop,
            )

            return (
                str(crop_path)
                if success
                else None
            )

        except Exception as exc:
            print(
                f"[IBVAP Evidence] Vehicle crop error: {exc}"
            )
            return None


evidence_capture = EvidenceCapture()