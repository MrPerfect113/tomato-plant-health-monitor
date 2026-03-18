import cv2
import time

# ================= STREAM SOURCE =================

# Laptop camera
#STREAM_SRC = 0

# ESP32-CAM stream
STREAM_SRC = "http://esp32cam.local:81/stream"

cap = None

def get_frame():

    global cap

    # initialize camera if needed
    if cap is None or not cap.isOpened():

        cap = cv2.VideoCapture(STREAM_SRC)

        # reduce buffering latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        time.sleep(0.2)

        if not cap.isOpened():
            return None

    ret, frame = cap.read()

    if not ret:
        cap.release()
        cap = None
        return None

    return frame