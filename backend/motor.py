import requests

ESP32_IP = "10.88.0.213"

MOTOR_URL = f"http://{ESP32_IP}/control"
SERVO_URL = f"http://{ESP32_IP}/servo"

VALID_COMMANDS = {"forward", "backward", "stop"}

def move(cmd: str) -> bool:

    print("[MOTOR] CMD RECEIVED:", cmd)

    if cmd not in VALID_COMMANDS:
        print("[MOTOR] Invalid command:", cmd)
        return False

    try:

        r = requests.post(
            MOTOR_URL,
            data=cmd,
            headers={"Content-Type": "text/plain"},
            timeout=2
        )

        print("[MOTOR] ESP32 STATUS:", r.status_code)

        return r.status_code == 200

    except Exception as e:

        print("[MOTOR] ERROR:", e)

        return False