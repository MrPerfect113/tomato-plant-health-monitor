import cv2
import time

# ================= STREAM SOURCE =================
# Laptop camera (default)
STREAM_SRC = 0

# ESP32-CAM (uncomment when needed)
#STREAM_SRC = "http://172.28.196.220:81/stream"

cap = None

def get_frame():
    global cap

    # Initialize or recover camera
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(STREAM_SRC)

        # Reduce latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Give camera time to warm up
        time.sleep(0.2)

        if not cap.isOpened():
            return None

    ret, frame = cap.read()

    if not ret:
        # Release and retry next call
        cap.release()
        cap = None
        return None

    return frame
