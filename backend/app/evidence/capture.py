"""
Evidence capture — snapshots and metadata for WARNING/CRITICAL events.

TODO (Phase 7): Implement snapshot saving from frame data.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings


class EvidenceCapture:
    """Captures and stores evidence for security events."""

    def __init__(self) -> None:
        settings.evidence_dir.mkdir(parents=True, exist_ok=True)

    def _session_dir(self, session_id: str) -> Path:
        path = settings.evidence_dir / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def capture_snapshot(
        self,
        session_id: str,
        event_id: str,
        frame_data: bytes | None,
        metadata: dict[str, Any],
    ) -> str | None:
        """
        Save evidence snapshot and metadata.

        TODO (Phase 7): Accept actual frame bytes from frontend or processor.
        Returns path to snapshot or None.
        """
        event_dir = self._session_dir(session_id) / event_id
        event_dir.mkdir(parents=True, exist_ok=True)

        meta_path = event_dir / "metadata.json"
        full_metadata = {
            **metadata,
            "event_id": event_id,
            "session_id": session_id,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
        meta_path.write_text(json.dumps(full_metadata, indent=2), encoding="utf-8")

        snapshot_path = event_dir / "snapshot.jpg"
        if frame_data:
            snapshot_path.write_bytes(frame_data)
            return str(snapshot_path)

        # Placeholder marker when no frame available yet
        placeholder = event_dir / "snapshot.pending"
        placeholder.write_text("Evidence capture pending — AI pipeline not active", encoding="utf-8")
        return str(meta_path)


evidence_capture = EvidenceCapture()
