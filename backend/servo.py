import requests

ESP32_IP = "10.88.0.213"

def move_servo(angle):

    try:
        url = f"http://{ESP32_IP}/servo"

        r = requests.get(
            url,
            params={"angle": angle},
            timeout=2
        )

        print("[SERVO] angle:", angle, "status:", r.status_code)

        return r.status_code == 200

    except Exception as e:
        print("[SERVO ERROR]", e)
        return False