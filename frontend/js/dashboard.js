/* ================= GLOBAL STATE ================= */

let streamActive = false;
let detectionActive = false;

let forwardActive = false;
let backwardActive = false;
let fullDetectActive = false;

/* ================= STREAM ================= */

function startStream() {

  if (streamActive) return;

  fetch("/api/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "start" })
  });

  const v = document.getElementById("video");
  const placeholder = document.getElementById("placeholder");

  if (v) {
    v.src = "";

    if (placeholder) {
      placeholder.style.display = "none";
      placeholder.innerText = "No video stream";
    }

    setTimeout(() => {
      v.src = "/video";
      v.classList.remove("hidden");
    }, 100);
  }

  streamActive = true;
  updateRailAvailability();

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

  const v = document.getElementById("video");
  const placeholder = document.getElementById("placeholder");

  if (v) {
    v.src = "";
    v.classList.add("hidden");
  }

  if (placeholder) {
    placeholder.style.display = "flex";
  }

  if (detectionActive) stopDetection(true);
  if (forwardActive || backwardActive) stopRail(true);

  streamActive = false;
  detectionActive = false;

  updateRailAvailability();

  if (window.distanceTimer) {
    clearInterval(window.distanceTimer);
    window.distanceTimer = null;
  }
}

/* ================= DETECTION ================= */

function showDetectionPanel() {

  if (!streamActive) return;

  fetch("/api/detection/start", { method: "POST" })
    .then(() => {
      detectionActive = true;
      document.getElementById("detectionPanel")?.classList.remove("hidden");
      updateRailAvailability();
    });
}

function stopDetection(internal = false) {

  if (!internal && !detectionActive) return;

  fetch("/api/detection/stop", { method: "POST" });

  detectionActive = false;

  document.getElementById("detectionPanel")?.classList.add("hidden");

  stopRail(true);
  updateRailAvailability();
}

/* ================= MODEL ================= */

async function selectModel(name) {

  if (!streamActive) {
    console.error("Start stream first");
    return;
  }

  console.log("Switching model:", name);

  // force stop detection
  await fetch("/api/detection/stop", { method: "POST" });
  detectionActive = false;

  // set model
  const res = await fetch("/api/model", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: name })
  });

  const data = await res.json();

  if (data.error) {
    console.error("MODEL ERROR:", data.error);
    return;
  }

  // UI update
  document.getElementById("activeModel").innerText = name.toUpperCase();

  // restart detection
  await fetch("/api/detection/start", { method: "POST" });
  detectionActive = true;

  updateRailAvailability();

  console.log("Model switched");
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
  });

  clearRailStates();

  if (dir === "forward") {
    forwardActive = true;
    document.getElementById("forwardBtn")?.classList.add("btn-active");
    setRailStatus("Moving Forward");
  } else {
    backwardActive = true;
    document.getElementById("backwardBtn")?.classList.add("btn-active");
    setRailStatus("Moving Backward");
  }
}

function stopRail() {

  fetch("/api/rail", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cmd: "stop" })
  });

  clearRailStates();
  setRailStatus("Idle");
}

/* ================= AUTO ================= */

function startFullDetect() {

  if (!railAllowed() || fullDetectActive) return;

  fullDetectActive = true;

  setRailStatus("Auto Running");

  fetch("/api/fulldetect", { method: "POST" });

  monitorAuto();
}

function monitorAuto() {

  const interval = setInterval(() => {

    fetch("/api/status")
      .then(r => r.json())
      .then(data => {

        if (data.auto === "IDLE" && fullDetectActive) {
          finishFullDetect();
          clearInterval(interval);
        }

      });

  }, 400);
}

function finishFullDetect() {
  fullDetectActive = false;
  setRailStatus("Idle");
}

/* ================= HELPERS ================= */

function railAllowed() {
  return streamActive && detectionActive;
}

function updateRailAvailability() {
  const allowed = streamActive && detectionActive;

  ["forwardBtn", "backwardBtn", "fullDetectBtn"].forEach(id => {
    document.getElementById(id)?.classList.toggle("btn-disabled", !allowed);
  });
}

function clearRailStates() {
  forwardActive = false;
  backwardActive = false;

  document.getElementById("forwardBtn")?.classList.remove("btn-active");
  document.getElementById("backwardBtn")?.classList.remove("btn-active");
}

function setRailStatus(text) {
  const el = document.getElementById("railStatus");
  if (el) el.innerText = "Rail Status: " + text;
}

/* ================= SERVO ================= */

let servoBusy = false;

function moveServo(angle) {

  if (servoBusy) return;

  servoBusy = true;

  fetch("/api/servo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ angle: angle })
  }).finally(() => {
    setTimeout(() => servoBusy = false, 300);
  });
}

/* ================= DISTANCE ================= */

function pollDistance() {

  fetch("/api/status")
    .then(res => res.json())
    .then(data => {

      console.log("DIST:", data);

      const el = document.getElementById("distanceValue");

      if (el && data.distance_cm !== undefined) {
        el.innerText = Number(data.distance_cm).toFixed(2);
      }

    })
    .catch(err => console.error("DIST ERROR:", err));
}

/* ================= SPEED ================= */

document.addEventListener("DOMContentLoaded", () => {

  const slider = document.getElementById("speedSlider");
  const value = document.getElementById("speedValue");

  if (!slider || !value) return;

  value.innerText = slider.value;

  let timeout = null;

  slider.addEventListener("input", () => {

    value.innerText = slider.value;

    clearTimeout(timeout);

    timeout = setTimeout(() => {

      console.log("SPEED:", slider.value);

      fetch("/api/speed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          speed: parseInt(slider.value)
        })
      });

    }, 100);

  });

});