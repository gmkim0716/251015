const timeDisplay = document.getElementById("timeDisplay");
const toggleButton = document.getElementById("toggleButton");

let timerId = null;
let isRunning = true;

function formatTime(date) {
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function updateTime() {
  const now = new Date();
  timeDisplay.textContent = formatTime(now);
}

function startTimer() {
  if (timerId !== null) {
    return;
  }
  updateTime();
  timerId = window.setInterval(updateTime, 1000);
}

function stopTimer() {
  if (timerId === null) {
    return;
  }
  window.clearInterval(timerId);
  timerId = null;
}

toggleButton.addEventListener("click", () => {
  if (isRunning) {
    stopTimer();
    toggleButton.textContent = "Resume";
  } else {
    startTimer();
    toggleButton.textContent = "Pause";
  }
  isRunning = !isRunning;
});

startTimer();
