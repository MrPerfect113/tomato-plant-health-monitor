GET /video
- Live MJPEG stream from ESP32-CAM

GET /api/detections
- Returns YOLO detections as JSON

POST /api/rail
Body: { "cmd": "forward | reverse | stop" }
- Sends command to rail ESP32
