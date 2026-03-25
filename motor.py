import requests

# ================= ESP CONFIG =================
ESP32_RAIL = "10.174.101.60"
ESP32_SERVO = "10.174.101.70"

http = requests.Session()

VALID_COMMANDS = {"forward", "backward", "stop"}


# ================= GENERIC =================
def call(url, timeout=2):
    try:
        r = http.get(url, timeout=timeout)
        return r.status_code == 200, r.text
    except Exception as e:
        print("[ESP ERROR]", e)
        return False, None


# ================= RAIL =================
def move(cmd: str) -> bool:

    if cmd not in VALID_COMMANDS:
        return False

    success, _ = call(f"http://{ESP32_RAIL}/{cmd}")

    print(f"[RAIL] {cmd} -> {success}")
    return success


def stop() -> bool:
    return move("stop")


# ================= SERVO =================
def move_servo(angle: int) -> bool:

    angle = max(0, min(180, angle))

    success, res = call(f"http://{ESP32_SERVO}/servo?angle={angle}", timeout=3)

    print(f"[SERVO] {angle} -> {success}")

    if success and res == "DONE":
        return True

    return False