from ultralytics import YOLO
import threading
import os
import torch
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATHS = {
    "tomato": os.path.join(MODEL_DIR, "tomato_yolo.pt"),
    "leaf": os.path.join(MODEL_DIR, "leaf_disease_yolo.pt")
}

def choose_device():
    return "cuda" if torch.cuda.is_available() else "cpu"

DEVICE = choose_device()
print(f"[DETECTOR] Using {DEVICE}")

_current_model_name = None
_current_model = None
_model_lock = threading.Lock()

def set_model(name: str):
    global _current_model, _current_model_name

    if name not in MODEL_PATHS:
        raise ValueError("Invalid model")

    model_path = MODEL_PATHS[name]

    with _model_lock:
        if _current_model_name == name:
            return

        model = YOLO(model_path)
        model.to(DEVICE)

        # warmup
        dummy = np.zeros((320, 320, 3), dtype=np.uint8)
        model(dummy, device=DEVICE, imgsz=320, verbose=False)

        _current_model = model
        _current_model_name = name

        print(f"[DETECTOR] Loaded {name}")

def stop_detection():
    print("[DETECTOR] Detection paused")

def detect(frame):

    if _current_model is None:
        return []

    with _model_lock:
        model = _current_model

    results = model(
        frame,
        conf=0.5,
        device=DEVICE,
        imgsz=320,
        half=True if DEVICE == "cuda" else False,
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

set_model("tomato")