const feed = document.getElementById("feed");
const countEl = document.getElementById("count");
const thresholdEl = document.getElementById("threshold");
const alertEl = document.getElementById("alert");
const calmEl = document.getElementById("calm");
const logEl = document.getElementById("log");
const emptyEl = document.getElementById("empty");
const errorEl = document.getElementById("error");
const captionEl = document.getElementById("caption");
const liveEl = document.getElementById("live");
const liveLabel = document.getElementById("live-label");

const seen = new Set();
let lastSignature = null;

function fmt(seconds) {
  const whole = Math.max(0, Math.floor(Number(seconds) || 0));
  const minutes = Math.floor(whole / 60);
  const remain = whole % 60;
  return String(minutes).padStart(2, "0") + ":" + String(remain).padStart(2, "0");
}

function setLive(on) {
  liveEl.classList.toggle("on", on);
  liveLabel.textContent = on ? "Live" : "Reconnecting";
}

function addEvent(event) {
  if (seen.has(event.id)) return;
  seen.add(event.id);
  const item = document.createElement("li");
  const time = document.createElement("span");
  time.className = "time";
  time.textContent = fmt(event.time_sec);
  const message = document.createElement("span");
  const verb = event.type === "left" ? "left" : "entered";
  message.textContent = "Person " + event.track_id + " " + verb;
  item.append(time, message);
  logEl.prepend(item);
  emptyEl.hidden = true;
  while (logEl.children.length > 50) {
    logEl.removeChild(logEl.lastElementChild);
  }
}

function onMessage(raw) {
  const msg = JSON.parse(raw.data);
  if (msg.error && !msg.frame_jpeg) {
    errorEl.hidden = false;
    errorEl.textContent = msg.error;
    return;
  }
  errorEl.hidden = true;
  if (msg.frame_jpeg) {
    feed.src = "data:image/jpeg;base64," + msg.frame_jpeg;
  }
  countEl.textContent = String(msg.count);
  thresholdEl.textContent = "Alert when more than " + msg.threshold + " people are in frame.";
  captionEl.textContent =
    fmt(msg.time_sec) + " · " + msg.boxes.length + " boxes · " + msg.detector;
  const signature = (msg.alert ? "1" : "0") + ":" + msg.count;
  if (signature !== lastSignature) {
    lastSignature = signature;
    alertEl.hidden = !msg.alert;
    calmEl.hidden = !!msg.alert;
    if (msg.alert) {
      alertEl.textContent =
        "Occupancy is " + msg.count + ", above the threshold of " + msg.threshold + ".";
    }
  }
  for (const event of msg.events) addEvent(event);
}

function connect() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(protocol + "://" + location.host + "/ws");
  socket.onopen = function () { setLive(true); };
  socket.onclose = function () {
    setLive(false);
    setTimeout(connect, 1000);
  };
  socket.onmessage = onMessage;
}

connect();
