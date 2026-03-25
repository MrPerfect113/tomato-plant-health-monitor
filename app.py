from flask import (Flask, Response, jsonify, request, send_from_directory, redirect, session)
from flask_cors import CORS
import cv2
import os
import time
import requests
import threading

from camera import get_frame
from detector import detect, set_model, stop_detection
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
ESP32_RAIL = "10.174.101.60"
ESP32_CAM = "10.174.101.50"
ESP32_SERVO = "10.174.101.70"

ESP32_STATUS_URL = f"http://{ESP32_RAIL}/status"

# ================= GLOBAL STATES =================
stream_enabled = False
detection_enabled = False
CURRENT_MODEL = "tomato"

auto_running = False
auto_state = "IDLE"
TARGET_DISTANCE = 110

latest_distance = 0

auto_start_time = 0
MAX_AUTO_TIME = 30

http = requests.Session()

# ================= DEVICE MONITOR =================
def check_devices():
    global latest_distance

    prev_rail = None
    prev_cam = None

    while True:

        # ===== RAIL + DISTANCE =====
        rail_status = False
        try:
            r = http.get(ESP32_STATUS_URL, timeout=1)
            latest_distance = r.json().get("distance_cm", 0)
            rail_status = True
        except:
            rail_status = False

        if rail_status != prev_rail:
            print(f"[{time.strftime('%H:%M:%S')}] RAIL {'CONNECTED' if rail_status else 'DISCONNECTED'}")
            prev_rail = rail_status

        # ===== CAMERA =====
        cam_status = False
        try:
            cap = cv2.VideoCapture(f"http://{ESP32_CAM}:81/stream")
            ok, _ = cap.read()
            cap.release()
            cam_status = ok
        except:
            pass

        if cam_status != prev_cam:
            print(f"[{time.strftime('%H:%M:%S')}] CAM {'CONNECTED' if cam_status else 'DISCONNECTED'}")
            prev_cam = cam_status

        time.sleep(2)

# ================= AUTO LOOP =================
def auto_loop():
    global auto_running, auto_state, auto_start_time

    while True:

        if not auto_running:
            time.sleep(0.1)
            continue

        # ===== GET LIVE DISTANCE =====
        try:
            r = http.get(ESP32_STATUS_URL, timeout=1)
            data = r.json()
            distance = data.get("distance_cm", 0)
        except:
            time.sleep(2)
            continue

        print("DIST:", distance, "TARGET:", TARGET_DISTANCE)

        # ===== TIMEOUT =====
        if time.time() - auto_start_time > MAX_AUTO_TIME:
            print("[AUTO] TIMEOUT")
            move("stop")
            auto_running = False
            auto_state = "IDLE"
            continue

        # ===== INIT =====
        if auto_state == "INIT":

            print("[AUTO] INIT")

            try:
                # RESET (VERIFY)
                r = http.get(f"http://{ESP32_RAIL}/reset", timeout=2)
                if r.status_code != 200:
                    print("[AUTO] RESET FAIL")
                    auto_running = False
                    auto_state = "IDLE"
                    continue

                time.sleep(0.2)

                # SERVO → 0 (BLOCKING)
                r = http.get(f"http://{ESP32_SERVO}/servo?angle=0", timeout=5)
                if r.text != "DONE":
                    print("[AUTO] Servo INIT FAIL")
                    auto_running = False
                    auto_state = "IDLE"
                    continue

                time.sleep(0.2)

                move("forward")

                auto_state = "FORWARD"
                auto_start_time = time.time()

            except:
                print("[AUTO] INIT ERROR")
                auto_running = False
                auto_state = "IDLE"

        # ===== FORWARD =====
        elif auto_state == "FORWARD":

            if distance >= TARGET_DISTANCE - 1:

                print("[AUTO] TARGET REACHED")

                move("stop")
                time.sleep(0.3)

                r = http.get(f"http://{ESP32_SERVO}/servo?angle=180", timeout=5)
                if r.text != "DONE":
                    print("[AUTO] Servo ROTATE FAIL")
                    auto_running = False
                    auto_state = "IDLE"
                    continue

                time.sleep(0.2)

                auto_state = "RETURN"

        # ===== RETURN =====
        elif auto_state == "RETURN":
            time.sleep(2) 
            move("backward")
            auto_state = "BACK"

        # ===== BACK =====
        elif auto_state == "BACK":

            if distance <= 3:

                print("[AUTO] HOME")

                move("stop")
                time.sleep(0.3)

                http.get(f"http://{ESP32_SERVO}/servo?angle=0", timeout=5)

                auto_running = False
                auto_state = "IDLE"

        time.sleep(0.2)

# ================= DASHBOARD =================
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "dashboard.html")

# ================= VIDEO =================
def video_stream():
    global stream_enabled, detection_enabled

    while True:

        if not stream_enabled:
            break

        frame = get_frame()

        if frame is None:
            time.sleep(0.01)
            continue

        if detection_enabled:
            detections = detect(frame)

            for d in detections:
                x1, y1, x2, y2 = d["bbox"]
                label = f'{d["label"]} {d["confidence"]:.1f}%'

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, label, (x1, max(y1 - 8, 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)

        ret, jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])

        if not ret:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               jpeg.tobytes() +
               b"\r\n")

@app.route("/video")
def video():
    return Response(video_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

# ================= STREAM =================
@app.route("/api/stream", methods=["POST"])
def api_stream():
    global stream_enabled, detection_enabled

    data = request.get_json(force=True)

    if data.get("action") == "start":
        stream_enabled = True
    else:
        stream_enabled = False
        detection_enabled = False
        stop_detection()

    return jsonify({"stream": stream_enabled})

# ================= DETECTION =================
@app.route("/api/detection/start", methods=["POST"])
def api_detection_start():
    global detection_enabled
    detection_enabled = True
    return jsonify({"enabled": True})

@app.route("/api/detection/stop", methods=["POST"])
def api_detection_stop():
    global detection_enabled
    detection_enabled = False
    stop_detection()
    return jsonify({"enabled": False})

# ================= MODEL =================
@app.route("/api/model", methods=["POST"])
def api_model():
    global CURRENT_MODEL

    model = request.json.get("model")
    set_model(model)
    CURRENT_MODEL = model

    return jsonify({"model": model})

@app.route("/api/model", methods=["GET"])
def get_model():
    return jsonify({"model": CURRENT_MODEL})

# ================= RAIL =================
@app.route("/api/rail", methods=["POST"])
def api_rail():
    cmd = request.json.get("cmd")

    if cmd not in ("forward", "backward", "stop"):
        return jsonify({"error": "invalid"}), 400

    return jsonify({"success": move(cmd)})

# ================= SPEED =================
@app.route("/api/speed", methods=["POST"])
def api_speed():

    val = int(request.json.get("speed", 0))
    val = max(0, min(255, val))

    try:
        r = http.get(f"http://{ESP32_RAIL}/speed?val={val}", timeout=2)
        return jsonify({"success": r.status_code == 200})
    except:
        return jsonify({"success": False})

# ================= SERVO =================
@app.route("/api/servo", methods=["POST"])
def api_servo():

    angle = int(request.json.get("angle", 90))

    try:
        r = http.get(f"http://{ESP32_SERVO}/servo?angle={angle}", timeout=3)
        return jsonify({"success": r.status_code == 200})
    except:
        return jsonify({"success": False})

# ================= STATUS =================
@app.route("/api/status")
def api_status():
    try:
        r = http.get(ESP32_STATUS_URL, timeout=1)
        data = r.json()

        return jsonify({
            "distance_cm": data.get("distance_cm", 0),
            "auto": auto_state
        })

    except Exception as e:
        print("STATUS ERROR:", e)
        return jsonify({"distance_cm": 0}), 503
# ================= FULL DETECT =================
@app.route("/api/fulldetect", methods=["POST"])
def api_fulldetect():
    global auto_running, auto_state, auto_start_time

    auto_running = True
    auto_state = "INIT"
    auto_start_time = time.time()

    return jsonify({"success": True})

# ================= RUN =================
if __name__ == "__main__":

    threading.Thread(target=check_devices, daemon=True).start()
    threading.Thread(target=auto_loop, daemon=True).start()

    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)