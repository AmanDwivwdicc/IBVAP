"""
YOLO-based object detector for IBVAP V1.
"""

from typing import Any

from ultralytics import YOLO


RELEVANT_CLASSES = {
    0: "person",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck"}


class ObjectDetector:
    """Detect persons and vehicles using YOLO."""

    def __init__(
        self,
        confidence: float = 0.40,
        model_path: str = "yolov8n.pt",
    ) -> None:
        self.confidence = confidence
        self.model_path = model_path
        self.model: YOLO | None = None
        self.is_loaded = False
        self.load_error: str | None = None

    def load_model(self) -> bool:
        """Load the YOLO model."""
        if self.is_loaded and self.model is not None:
            return True

        try:
            self.model = YOLO(self.model_path)
            self.is_loaded = True
            self.load_error = None

            print(
                f"[IBVAP AI] YOLO loaded: "
                f"{self.model_path} | confidence={self.confidence}"
            )

            return True

        except Exception as exc:
            self.model = None
            self.is_loaded = False
            self.load_error = str(exc)

            print(f"[IBVAP AI] YOLO load failed: {exc}")
            return False

    def detect(self, frame: Any) -> list[dict[str, Any]]:
        """Run YOLO inference on an OpenCV frame."""

        if frame is None:
            return []

        if not self.is_loaded or self.model is None:
            if not self.load_model():
                return []

        frame_height, frame_width = frame.shape[:2]

        try:
            results = self.model.predict(
                source=frame,
                conf=self.confidence,
                classes=list(RELEVANT_CLASSES.keys()),
                device="cpu",
                verbose=False,
            )

            detections: list[dict[str, Any]] = []

            for result in results:
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    class_id = int(box.cls[0].item())

                    if class_id not in RELEVANT_CLASSES:
                        continue

                    confidence = float(box.conf[0].item())

                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    x1 = max(0, min(int(x1), frame_width - 1))
                    y1 = max(0, min(int(y1), frame_height - 1))
                    x2 = max(0, min(int(x2), frame_width - 1))
                    y2 = max(0, min(int(y2), frame_height - 1))

                    class_name = RELEVANT_CLASSES[class_id]

                    object_type = (
                        "VEHICLE"
                        if class_name in VEHICLE_CLASSES
                        else "PERSON"
                    )

                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    detections.append(
                        {
                            "class_name": class_name,
                            "object_type": object_type,
                            "confidence": round(confidence, 4),
                            "bbox": [x1, y1, x2, y2],
                            "center": [center_x, center_y],
                            "frame_width": frame_width,
                            "frame_height": frame_height,
                            "track_id": None,
                        }
                    )

            return detections

        except Exception as exc:
            print(f"[IBVAP AI] Detection error: {exc}")
            return []


detector = ObjectDetector()