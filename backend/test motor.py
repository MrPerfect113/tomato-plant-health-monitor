import requests

r = requests.post(
    "http://127.0.0.1:5000/api/speed",
    json={"speed": 120}
)

print(r.status_code)
print(r.text)