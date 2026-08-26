"""
Behavior analysis — loitering detection.

TODO (Phase 6): Implement loitering rule.
"""

from typing import Any


class BehaviorAnalyzer:
    """Analyzes tracked object behavior for security events."""

    def __init__(self, loitering_threshold_seconds: int = 30) -> None:
        self.loitering_threshold = loitering_threshold_seconds
        self._loitering_state: dict[str, dict[str, Any]] = {}

    def check_loitering(
        self,
        track_id: str,
        position: tuple[float, float],
        timestamp: float,
    ) -> bool:
        """Returns True if loitering event should be generated."""
        # TODO (Phase 6): Implement region-based loitering detection
        return False

    def reset(self) -> None:
        self._loitering_state.clear()


behavior_analyzer = BehaviorAnalyzer()
