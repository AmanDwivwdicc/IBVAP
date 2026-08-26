"""
Camera module — browser webcam is handled client-side in V1.

This module provides interfaces for server-side camera processing (Phase 3+).
"""

from typing import Any


class WebcamCapture:
    """TODO (Phase 3+): Server-side webcam capture if needed."""

    def __init__(self) -> None:
        self.is_active = False

    def start(self, device_id: int = 0) -> bool:
        """Start capturing from webcam. Returns False if unavailable."""
        # TODO: Implement with OpenCV VideoCapture when server-side capture is needed
        return False

    def read_frame(self) -> Any:
        """Read a single frame. Returns None if unavailable."""
        # TODO: Implement frame capture
        return None

    def stop(self) -> None:
        self.is_active = False


webcam = WebcamCapture()
