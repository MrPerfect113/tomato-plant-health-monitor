import cv2
from ultralytics import YOLO

# LOAD TOMATO DETECTION MODEL (CHANGE NAME IF NEEDED)
model = YOLO("models/tomato_yolo.pt")

# LOAD TEST IMAGE (TOMATO / PLANT IMAGE)
img = cv2.imread("test.jpg")

if img is None:
    raise FileNotFoundError("test.jpg not found")

# RUN INFERENCE
results = model(img, conf=0.25, verbose=False)[0]

print("Classes:", model.names)
print("Number of boxes:", len(results.boxes))

# PRINT DETECTIONS
for box in results.boxes:
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    x1, y1, x2, y2 = map(int, box.xyxy[0])

    print({
        "label": model.names[cls],
        "confidence": round(conf * 100, 2),
        "bbox": [x1, y1, x2, y2]
    })

# VISUALIZE
for box in results.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

cv2.imshow("TOMATO MODEL CHECK", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
