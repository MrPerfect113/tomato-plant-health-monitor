import requests

ESP32_HOST = "esp32rail.local"

def move(cmd: str) -> bool:
    print("=== MOVE FUNCTION HIT ===")
    print("[MOVE] CMD:", cmd)

    try:
        url = f"http://{ESP32_HOST}/control?cmd={cmd}"

        print("[MOVE URL]:", url)

        r = requests.get(url, timeout=2)

        print("[MOVE STATUS]:", r.status_code)

        return r.status_code == 200

    except Exception as e:
        print("[MOVE ERROR]:", e)
        return False