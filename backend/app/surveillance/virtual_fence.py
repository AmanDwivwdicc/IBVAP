"""
Virtual fence / border logic for IBVAP V1.

The frontend stores the border as normalized coordinates
(0.0 -> 1.0). YOLO detections are pixel coordinates.

This module converts the normalized border into the same
pixel coordinate system as the current frame.
"""

from typing import Any

from app.schemas.sessions import VirtualBorder


class VirtualFence:
    """Manages a virtual border and detects proximity/crossing."""

    def __init__(self) -> None:
        self.border: VirtualBorder | None = None
        self.warning_distance_px: int = 80

    def set_border(self, border: VirtualBorder) -> None:
        self.border = border

    def clear(self) -> None:
        self.border = None

    def is_defined(self) -> bool:
        return self.border is not None

    def _pixel_points(
        self,
        frame_width: int,
        frame_height: int,
    ) -> tuple[
        tuple[float, float],
        tuple[float, float],
    ] | None:
        """Convert normalized border coordinates to pixels."""

        if self.border is None:
            return None

        a = self.border.point_a
        b = self.border.point_b

        return (
            (
                a.x * frame_width,
                a.y * frame_height,
            ),
            (
                b.x * frame_width,
                b.y * frame_height,
            ),
        )

    @staticmethod
    def _signed_side(
        point: tuple[float, float],
        a: tuple[float, float],
        b: tuple[float, float],
    ) -> float:
        """Return the signed side of a directed line."""

        px, py = point
        ax, ay = a
        bx, by = b

        return (
            (bx - ax) * (py - ay)
            - (by - ay) * (px - ax)
        )

    @staticmethod
    def _distance_to_segment(
        point: tuple[float, float],
        a: tuple[float, float],
        b: tuple[float, float],
    ) -> float:
        """Calculate distance from point to line segment."""

        px, py = point
        ax, ay = a
        bx, by = b

        dx = bx - ax
        dy = by - ay

        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            return (
                (px - ax) ** 2
                + (py - ay) ** 2
            ) ** 0.5

        t = (
            (px - ax) * dx
            + (py - ay) * dy
        ) / length_sq

        t = max(0.0, min(1.0, t))

        closest_x = ax + t * dx
        closest_y = ay + t * dy

        return (
            (px - closest_x) ** 2
            + (py - closest_y) ** 2
        ) ** 0.5

    def check_crossing(
        self,
        track_id: str,
        current_pos: tuple[float, float],
        previous_pos: tuple[float, float],
        frame_width: int,
        frame_height: int,
    ) -> dict[str, Any] | None:
        """Detect a track crossing the virtual border."""

        del track_id

        points = self._pixel_points(
            frame_width,
            frame_height,
        )

        if points is None:
            return None

        a, b = points

        previous_side = self._signed_side(
            previous_pos,
            a,
            b,
        )

        current_side = self._signed_side(
            current_pos,
            a,
            b,
        )

        # The object must move from one side to the other.
        crossed = (
            (
                previous_side < 0
                and current_side > 0
            )
            or
            (
                previous_side > 0
                and current_side < 0
            )
        )

        if not crossed:
            return None

        direction = (
            "SIDE_A_TO_B"
            if previous_side < 0
            else "SIDE_B_TO_A"
        )

        return {
            "crossed": True,
            "direction": direction,
            "previous_side": previous_side,
            "current_side": current_side,
        }

    def check_approaching(
        self,
        track_id: str,
        current_pos: tuple[float, float],
        velocity: tuple[float, float],
        frame_width: int,
        frame_height: int,
    ) -> bool:
        """
        Detect a person approaching/touching the virtual border.
        """

        print(
    "[FENCE CHECK]",
    {
        "current": current_pos,
        "velocity": velocity,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "border": (
            self.border.model_dump()
            if self.border
            else None
        ),
    }
)

        del track_id

        points = self._pixel_points(
            frame_width,
            frame_height,
        )

        if points is None:
            return False

        a, b = points

        distance = self._distance_to_segment(
            current_pos,
            a,
            b,
        )

        if distance > self.warning_distance_px:
            return False

        vx, vy = velocity

        speed = (
            vx * vx + vy * vy
        ) ** 0.5

        # Being extremely close to the line counts as
        # a border-touch warning even when stationary.
        if distance <= 15:
            return True

        if speed < 1.0:
            return False

        px, py = current_pos

        dx = b[0] - a[0]
        dy = b[1] - a[1]

        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            return True

        t = (
            (px - a[0]) * dx
            + (py - a[1]) * dy
        ) / length_sq

        t = max(0.0, min(1.0, t))

        closest_x = a[0] + t * dx
        closest_y = a[1] + t * dy

        toward_x = closest_x - px
        toward_y = closest_y - py

        dot = (
            vx * toward_x
            + vy * toward_y
        )

        return dot > 0


virtual_fence = VirtualFence()