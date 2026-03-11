from ultralytics import YOLO
import threading
import os
import torch

# ---------------- BASE PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# ---------------- MODEL PATHS ----------------
MODEL_PATHS = {
    "tomato": os.path.join(MODEL_DIR, "tomato_yolo.pt"),
    "leaf": os.path.join(MODEL_DIR, "leaf_disease_yolo.pt")
}

# ---------------- DEVICE ----------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[DETECTOR] Using device: {DEVICE}")

# ---------------- GLOBAL STATE ----------------
_current_model_name = None
_current_model = None
_confidence = 0.5

_model_lock = threading.Lock()

# ---------------- MODEL CONTROL ----------------
def set_model(name: str):
    global _current_model, _current_model_name

    if name not in MODEL_PATHS:
        raise ValueError(f"Invalid model: {name}")

    model_path = MODEL_PATHS[name]

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    with _model_lock:
        if _current_model_name == name:
            return

        model = YOLO(model_path)

        # move model to GPU
        model.to(DEVICE)

        _current_model = model
        _current_model_name = name

        print(f"[DETECTOR] Loaded model: {name} on {DEVICE}")

def set_confidence(val: float):
    global _confidence
    _confidence = max(0.01, min(1.0, val))
    print(f"[DETECTOR] Confidence set to {_confidence:.2f}")

def stop_detection():
    global _current_model, _current_model_name

    with _model_lock:
        _current_model = None
        _current_model_name = None

    print("[DETECTOR] Detection stopped")

# ---------------- DETECTION ----------------
def detect(frame):
    if _current_model is None:
        return []

    with _model_lock:
        model = _current_model
        conf = _confidence

    results = model(
        frame,
        conf=conf,
        device=DEVICE,      # GPU inference
        imgsz=320,          # faster
        half=True if DEVICE=="cuda" else False,
        verbose=False
    )[0]

    detections = []

    if results.boxes is None:
        return detections

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence_pct = float(box.conf[0]) * 100
        class_id = int(box.cls[0])
        label = model.names[class_id]

        detections.append({
            "bbox": (x1, y1, x2, y2),
            "label": label,
            "confidence": confidence_pct
        })

    return detections