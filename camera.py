import cv2
import time

STREAM_SRC = "http://10.174.101.50:81/stream"

cap = None
last_connect = 0

def get_frame():
    global cap, last_connect

    # reconnect logic
    if cap is None or not cap.isOpened():

        if time.time() - last_connect < 1:
            return None

        last_connect = time.time()

        cap = cv2.VideoCapture(STREAM_SRC)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        time.sleep(0.2)

        if not cap.isOpened():
            cap = None
            return None

    ret, frame = cap.read()

    if not ret or frame is None:
        cap.release()
        cap = None
        return None

    return frame