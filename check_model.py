import cv2
from ultralytics import YOLO

# Load model
model = YOLO("models/tomato_yolo.pt")

# Load a TEST IMAGE (must be a LEAF image from dataset or similar)
img = cv2.imread("test.jpg")

if img is None:
    raise FileNotFoundError("test.jpg not found")

# Run inference
results = model(img, conf=0.25, verbose=False)[0]

# Print raw results
print("Classes:", model.names)
print("Number of boxes:", len(results.boxes))

# Print detections
for box in results.boxes:
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    x1, y1, x2, y2 = map(int, box.xyxy[0])

    print({
        "label": model.names[cls],
        "confidence": round(conf * 100, 2),
        "bbox": [x1, y1, x2, y2]
    })

# Optional: visualize
for box in results.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

cv2.imshow("YOLO Check", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
