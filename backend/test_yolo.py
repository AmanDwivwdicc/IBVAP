from ultralytics import YOLO

print("Loading YOLO...")
model = YOLO("yolov8n.pt")

print("Running test inference...")
results = model("https://ultralytics.com/images/bus.jpg", conf=0.4)

for result in results:
    print("\nDetections:")
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = result.names[class_id]

        if class_name in {"person", "car", "motorcycle", "bus", "truck"}:
            print(f"{class_name}: {confidence:.2f}")

print("\nYOLO TEST SUCCESSFUL")