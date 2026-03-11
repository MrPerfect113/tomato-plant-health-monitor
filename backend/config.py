USE_ESP32_CAM = False
LAPTOP_CAM_INDEX = 0

MODEL_PATH = "models/tomato_yolo.pt"
CONF_THRESHOLD = 0.25

ESP32_IP = "192.168.1.55"

SERVO_URL = f"http://{ESP32_IP}/servo"
MOTOR_URL = f"http://{ESP32_IP}/control"
STATUS_URL = f"http://{ESP32_IP}/status"