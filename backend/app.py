from flask import (Flask, Response, jsonify, request, send_from_directory, redirect, session)
from flask_cors import CORS
import cv2
import os
import time
import socket
import requests

from camera import get_frame
from detector import detect, set_confidence, set_model, stop_detection
from motor import move
from auth import auth

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# ================= APP INIT =================
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.secret_key = "industrial-secret-key"
CORS(app)
app.register_blueprint(auth)

# ================= ESP CONFIG =================
ESP32_HOST = "esp32rail.local"

ESP32_STATUS_URL = f"http://{ESP32_HOST}/status"
ESP32_CONTROL_URL = f"http://{ESP32_HOST}/control"
# ================= GLOBAL STATES =================
stream_enabled = False
detection_enabled = False

http = requests.Session()

# ================= DISABLE CACHE =================
@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ================= DASHBOARD =================
@app.route("/")
def index():
    print("SESSION:", session)

    if "user" not in session:
        print("NOT LOGGED IN → REDIRECT")
        return redirect("/login")

    print("LOGGED IN → DASHBOARD")
    return send_from_directory(FRONTEND_DIR, "dashboard.html")

# ================= VIDEO STREAM =================
def video_stream():
    global stream_enabled, detection_enabled

    while True:

        if not stream_enabled:
            time.sleep(0.05)
            continue

        frame = get_frame()

        if frame is None:
            time.sleep(0.02)
            continue

        detections = detect(frame) if detection_enabled else []

        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            label = f'{d["label"]} {d["confidence"]:.1f}%'

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 8, 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )

        ret, jpeg = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpeg.tobytes() +
            b"\r\n"
        )

@app.route("/video")
def video():
    if "user" not in session:
        return redirect("/login")

    return Response(
        video_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# ================= STREAM CONTROL =================
@app.route("/api/stream", methods=["POST"])
def api_stream():
    global stream_enabled, detection_enabled

    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(force=True)
    action = data.get("action")

    if action == "start":
        stream_enabled = True

    elif action == "stop":
        stream_enabled = False
        detection_enabled = False
        stop_detection()

    return jsonify({
        "stream": stream_enabled,
        "detection": detection_enabled
    })

# ================= DETECTION =================
@app.route("/api/detection/start", methods=["POST"])
def api_detection_start():

    global detection_enabled

    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    if not stream_enabled:
        return jsonify({"error": "No video stream found"}), 400

    detection_enabled = True
    return jsonify({"enabled": True})

@app.route("/api/detection/stop", methods=["POST"])
def api_detection_stop():

    global detection_enabled

    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    detection_enabled = False
    stop_detection()

    return jsonify({"enabled": False})

# ================= MODEL =================
@app.route("/api/model", methods=["POST"])
def api_model():

    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(force=True)
    model = data.get("model")

    if model not in ("tomato", "leaf"):
        return jsonify({"error": "invalid model"}), 400

    set_model(model)

    return jsonify({"model": model})

# ================= CONFIDENCE =================
@app.route("/api/confidence", methods=["POST"])
def api_confidence():

    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(force=True)
    value = float(data.get("value", 30))

    set_confidence(value / 100.0)

    return jsonify({"confidence": value})

# ================= RAIL CONTROL =================
@app.route("/api/rail", methods=["POST"])
def api_rail():

    print("=== API_RAIL HIT ===")

    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(force=True)   # <-- THIS LINE IS MANDATORY

    print("[RAW DATA]:", data)

    cmd = data.get("cmd")

    print("[CMD]:", cmd)

    if not cmd:
        return jsonify({"error": "cmd missing"}), 400

    if cmd not in ("forward", "backward", "stop"):
        return jsonify({"error": "invalid command"}), 400

    success = move(cmd)

    print("[RESULT]:", success)

    return jsonify({"success": success})

# ================= ESP STATUS =================
@app.route("/api/status", methods=["GET"])
def api_status():

    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401

    try:
        r = http.get(ESP32_STATUS_URL, timeout=1)
        return jsonify(r.json())

    except Exception as e:
        print("[STATUS ERROR]:", e)

        return jsonify({
            "rotations": 0,
            "distance_cm": 0,
            "error": "ESP32 offline"
        }), 503

# ================= FULL DETECT =================
@app.route("/api/fulldetect", methods=["POST"])
def api_fulldetect():

    # TEMP: disable auth for testing
    # if "user" not in session:
    #     return jsonify({"error": "unauthorized"}), 401

    try:
        url = f"http://{ESP32_HOST}:80/fulldetect"
        print("[FULL DETECT] URL:", url)

        r = http.get(url, timeout=3)

        print("[FULL DETECT] STATUS:", r.status_code)

        return jsonify({"success": r.status_code == 200})

    except Exception as e:
        print("[FULL DETECT] ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)