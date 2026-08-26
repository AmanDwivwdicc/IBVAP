"""
Virtual fence / border logic.

TODO (Phase 5): Implement line crossing detection.
"""

from typing import Any

from app.schemas.sessions import VirtualBorder


class VirtualFence:
    """Manages virtual border and crossing detection."""

    def __init__(self) -> None:
        self.border: VirtualBorder | None = None
        self.warning_distance_px: int = 80

    def set_border(self, border: VirtualBorder) -> None:
        self.border = border

    def clear(self) -> None:
        self.border = None

    def is_defined(self) -> bool:
        return self.border is not None

    def check_crossing(
        self,
        track_id: str,
        current_pos: tuple[float, float],
        previous_pos: tuple[float, float],
    ) -> dict[str, Any] | None:
        """
        Check if a track crossed the virtual border.

        Returns crossing info or None.
        """
        # TODO (Phase 5): Implement line crossing algorithm
        return None

    def check_approaching(
        self,
        track_id: str,
        current_pos: tuple[float, float],
        velocity: tuple[float, float],
    ) -> bool:
        """Check if track is approaching the border within warning distance."""
        # TODO (Phase 5): Implement approaching border detection
        return False


virtual_fence = VirtualFence()
