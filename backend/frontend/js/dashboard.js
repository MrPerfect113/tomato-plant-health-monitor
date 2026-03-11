/* ================= GLOBAL STATE ================= */

let streamActive = false;
let detectionActive = false;

let forwardActive = false;
let backwardActive = false;
let fullDetectActive = false;

/* ================= STREAM ================= */

function startStream() {
  fetch("/api/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "start" })
  });

  const v = document.getElementById("video");
  v.src = "/video?" + Date.now();
  v.classList.remove("hidden");

  document.getElementById("placeholder").style.display = "none";

  streamActive = true;
  updateRailAvailability();

  // ⬇️ ADD THIS
  if (!window.distanceTimer) {
    window.distanceTimer = setInterval(pollDistance, 300);
  }
}

function stopStream() {
  fetch("/api/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "stop" })
  });

  document.getElementById("video").classList.add("hidden");
  document.getElementById("placeholder").style.display = "flex";

  streamActive = false;
  detectionActive = false;

  stopRail(true);
  stopDetection(true);
  updateRailAvailability();

  // ⬇️ ADD THIS
  clearInterval(window.distanceTimer);
  window.distanceTimer = null;
}

/* ================= DETECTION ================= */

function showDetectionPanel() {
  if (!streamActive) {
    showError("No video stream found");
    return;
  }

  fetch("/api/detection/start", { method: "POST" })
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        showError(data.error);
        return;
      }

      detectionActive = true;
      document.getElementById("detectionPanel").classList.remove("hidden");
      updateRailAvailability();
    });
}

function stopDetection(internal = false) {
  if (!internal && !detectionActive) return;

  fetch("/api/detection/stop", { method: "POST" });

  detectionActive = false;
  document.getElementById("detectionPanel").classList.add("hidden");

  stopRail(true);
  updateRailAvailability();
}

/* ================= MODEL ================= */

function selectModel(model) {
  if (!streamActive || !detectionActive) {
    showError("Start detection first");
    return;
  }

  fetch("/api/model", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model })
  });

  document.getElementById("activeModel").innerText =
    model === "tomato" ? "Tomato Condition" : "Leaf Disease";

  document.getElementById("tomatoBtn").classList.remove("btn-active");
  document.getElementById("leafBtn").classList.remove("btn-active");

  document.getElementById(
    model === "tomato" ? "tomatoBtn" : "leafBtn"
  ).classList.add("btn-active");
}

/* ================= CONFIDENCE ================= */

function setConfidence(v) {
  document.getElementById("confValue").innerText = v + "%";

  fetch("/api/confidence", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value: v })
  });
}

/* ================= RAIL ================= */

function toggleForward() {
  if (!railAllowed()) return;
  forwardActive ? stopRail() : startRail("forward");
}

function toggleBackward() {
  if (!railAllowed()) return;
  backwardActive ? stopRail() : startRail("backward");
}

function startRail(dir) {
  fetch("/api/rail", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cmd: dir })
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        showError(data.error);
        return;
      }

      clearRailStates();

      if (dir === "forward") {
        forwardActive = true;
        document.getElementById("forwardBtn").classList.add("btn-active");
        setRailStatus("Moving Forward");
      } else {
        backwardActive = true;
        document.getElementById("backwardBtn").classList.add("btn-active");
        setRailStatus("Moving Backward");
      }
    });
}

function stopRail(internal = false) {
  if (!internal && !railAllowed()) return;

  fetch("/api/rail", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cmd: "stop" })
  });

  clearRailStates();
  setRailStatus("Idle");
}

/* ================= FULL DETECT ================= */

function startFullDetect() {
  if (!railAllowed() || fullDetectActive) return;

  fullDetectActive = true;
  disableManualRail();
  setRailStatus("Full Detect Running");

  document.getElementById("fullDetectBtn").classList.add("btn-active");
  document.getElementById("fullDetectProgress").classList.remove("hidden");

  simulateProgress();
}

function simulateProgress() {
  let p = 0;
  const bar = document.getElementById("progressBar");

  const timer = setInterval(() => {
    p += 5;
    bar.style.width = p + "%";

    if (p >= 100) {
      clearInterval(timer);
      finishFullDetect();
    }
  }, 400);
}

function finishFullDetect() {
  fullDetectActive = false;

  document.getElementById("progressBar").style.width = "0%";
  document.getElementById("fullDetectProgress").classList.add("hidden");
  document.getElementById("fullDetectBtn").classList.remove("btn-active");

  enableManualRail();
  setRailStatus("Full Detect Complete");
}

/* ================= GATING ================= */

function railAllowed() {
  if (!streamActive) {
    showError("No video stream");
    return false;
  }
  if (!detectionActive) {
    showError("Start detection first");
    return false;
  }
  return true;
}

function updateRailAvailability() {
  const allowed = streamActive && detectionActive;

  ["forwardBtn", "backwardBtn", "fullDetectBtn"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle("btn-disabled", !allowed);
  });
}

/* ================= HELPERS ================= */

function clearRailStates() {
  forwardActive = false;
  backwardActive = false;
  document.getElementById("forwardBtn").classList.remove("btn-active");
  document.getElementById("backwardBtn").classList.remove("btn-active");
}

function setRailStatus(text) {
  document.getElementById("railStatus").innerText =
    "Rail Status: " + text;
}

function disableManualRail() {
  ["forwardBtn", "backwardBtn"].forEach(id =>
    document.getElementById(id).classList.add("btn-disabled")
  );
}

function enableManualRail() {
  ["forwardBtn", "backwardBtn"].forEach(id =>
    document.getElementById(id).classList.remove("btn-disabled")
  );
}

function showError(msg) {
  const p = document.getElementById("placeholder");
  p.style.display = "flex";
  p.style.color = "#ff6b6b";
  p.innerText = msg;
}

/* ================= AUTH ================= */

function logout() {
  fetch("/logout", { method: "POST" })
    .then(() => window.location.href = "/login");
}

window.addEventListener("beforeunload", () => {
  navigator.sendBeacon("/logout");
});

function pollDistance() {
  fetch("/api/status")
    .then(res => res.json())
    .then(data => {
      if (data.distance_cm !== undefined) {
        document.getElementById("distanceValue").innerText =
          data.distance_cm.toFixed(2);
      }
    })
    .catch(() => {});
}
let servoTimer = null;

function moveServo(angle){

  document.getElementById("servoValue").innerText = angle

  fetch(`/servo/${angle}`)
  .then(res => res.json())
  .then(data => console.log("SERVO:", data))
  .catch(err => console.error(err))

}
