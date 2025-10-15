const hoursEl = document.getElementById("hours");
const minutesEl = document.getElementById("minutes");
const secondsEl = document.getElementById("seconds");
const millisecondsEl = document.getElementById("milliseconds");
const ampmTag = document.getElementById("ampmTag");
const millisecondsLabel = document.getElementById("millisecondsLabel");
const selectedCityEl = document.getElementById("selectedCity");
const timezoneOffsetEl = document.getElementById("timezoneOffset");
const titleTextEl = document.getElementById("titleText");
const mapInstructionEl = document.getElementById("mapInstruction");
const languageToggle = document.getElementById("languageToggle");
const toggleButton = document.getElementById("toggleButton");

const translations = {
  en: {
    title: "Impact World Timer",
    pause: "Pause",
    resume: "Resume",
    languageButton: "\uD55C\uAD6D\uC5B4",
    instruction: "Select a city to shift the timer timezone.",
    milliseconds: "MS",
    am: "AM",
    pm: "PM",
    day: "Daytime in",
    night: "Nighttime in",
  },
  ko: {
    title: "\uC784\uD329\uD2B8 \uC6D4\uB4DC \uD0C0\uC774\uBA38",
    pause: "\uC77C\uC2DC\uC815\uC9C0",
    resume: "\uC7AC\uAC1C",
    languageButton: "English",
    instruction: "\uB3C4\uC2DC\uB97C \uB20C\uB7EC \uD0C0\uC784\uC874\uC744 \uBCC0\uACBD\uD558\uC138\uC694.",
    milliseconds: "\uBC00\uB9AC\uCD08",
    am: "\uC624\uC804",
    pm: "\uC624\uD6C4",
    day: "\uB0AE \uC0C1\uD0DC",
    night: "\uBC24 \uC0C1\uD0DC",
  },
};

const cityDefinitions = [
  {
    id: "losAngeles",
    timeZone: "America/Los_Angeles",
    names: { en: "Los Angeles", ko: "\uB85C\uC2A4\uC568\uC820\uB808\uC2A4" },
  },
  {
    id: "newYork",
    timeZone: "America/New_York",
    names: { en: "New York", ko: "\uB274\uC695" },
  },
  {
    id: "saoPaulo",
    timeZone: "America/Sao_Paulo",
    names: { en: "S\u00E3o Paulo", ko: "\uC0C1\uD30C\uC6B8\uB8E8" },
  },
  {
    id: "london",
    timeZone: "Europe/London",
    names: { en: "London", ko: "\uB7F0\uB358" },
  },
  {
    id: "dubai",
    timeZone: "Asia/Dubai",
    names: { en: "Dubai", ko: "\uB450\uBC14\uC774" },
  },
  {
    id: "seoul",
    timeZone: "Asia/Seoul",
    names: { en: "Seoul", ko: "\uC11C\uC6B8" },
  },
  {
    id: "tokyo",
    timeZone: "Asia/Tokyo",
    names: { en: "Tokyo", ko: "\uB3C4\uCFC4" },
  },
  {
    id: "sydney",
    timeZone: "Australia/Sydney",
    names: { en: "Sydney", ko: "\uC2DC\uB4DC\uB2C8" },
  },
];

const cityMarkers = new Map();
document.querySelectorAll(".city-marker").forEach((marker) => {
  const cityId = marker.dataset.city;
  cityMarkers.set(cityId, marker);
});

let currentLanguage = "en";
let selectedCityId = "seoul";
let selectedTimeZone = "Asia/Seoul";
let animationFrameId = null;
let isRunning = true;
let lastSecond = null;
let lastMinute = null;

function getZonedDate(date, timeZone) {
  const invDate = new Date(
    date.toLocaleString("en-US", { timeZone, hour12: false })
  );
  const diff = date.getTime() - invDate.getTime();
  return new Date(date.getTime() + diff);
}

function updateOffsetLabel(now) {
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: selectedTimeZone,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZoneName: "shortOffset",
  });
  const parts = formatter.formatToParts(now);
  const offsetPart = parts.find((part) => part.type === "timeZoneName");
  timezoneOffsetEl.textContent = offsetPart
    ? offsetPart.value.replace("GMT", "UTC")
    : "";
}

function triggerAnimation(element, className) {
  element.classList.remove(className);
  element.offsetHeight;
  element.classList.add(className);
}

function updateTime() {
  const now = new Date();
  const zonedDate = getZonedDate(now, selectedTimeZone);
  const ms = zonedDate.getMilliseconds();
  const seconds = zonedDate.getSeconds();
  const minutes = zonedDate.getMinutes();
  const hours24 = zonedDate.getHours();

  const periodKey = hours24 >= 12 ? "pm" : "am";
  const hours12 = hours24 % 12 || 12;

  hoursEl.textContent = String(hours12).padStart(2, "0");
  minutesEl.textContent = String(minutes).padStart(2, "0");
  secondsEl.textContent = String(seconds).padStart(2, "0");
  millisecondsEl.textContent = String(ms).padStart(3, "0");
  ampmTag.textContent = translations[currentLanguage][periodKey];

  if (seconds !== lastSecond) {
    triggerAnimation(secondsEl, "time-part--impact");
  }

  if (minutes !== lastMinute) {
    triggerAnimation(minutesEl, "time-part--slam");
    triggerAnimation(hoursEl, "time-part--impact");
  }

  lastSecond = seconds;
  lastMinute = minutes;

  updateOffsetLabel(now);
  refreshCityDaylight(now);
}

function refreshCityDaylight(baseDate) {
  cityDefinitions.forEach((city) => {
    const marker = cityMarkers.get(city.id);
    if (!marker) {
      return;
    }
    const displayName = city.names[currentLanguage];
    const zoned = getZonedDate(baseDate, city.timeZone);
    const hour = zoned.getHours();
    const isDay = hour >= 6 && hour < 18;
    const stateText = marker.querySelector(".city-state");
    marker.classList.toggle("is-day", isDay);
    marker.classList.toggle("is-night", !isDay);
    stateText.textContent = isDay ? "☀" : "☾";
    marker.setAttribute(
      "aria-label",
      `${displayName} · ${
        isDay ? translations[currentLanguage].day : translations[currentLanguage].night
      }`
    );
  });
}

function updateSelectedCityDisplay() {
  const city = cityDefinitions.find((entry) => entry.id === selectedCityId);
  if (!city) {
    return;
  }
  selectedCityEl.textContent = city.names[currentLanguage];
  document.title = translations[currentLanguage].title;
}

function applyLanguage() {
  const copy = translations[currentLanguage];
  titleTextEl.textContent = copy.title;
  languageToggle.textContent = copy.languageButton;
  languageToggle.setAttribute(
    "aria-label",
    currentLanguage === "en"
      ? "Switch to Korean"
      : "\uD55C\uAD6D\uC5B4\uC5D0\uC11C \uC601\uC5B4\uB85C \uC804\uD658"
  );
  toggleButton.textContent = isRunning ? copy.pause : copy.resume;
  mapInstructionEl.textContent = copy.instruction;
  millisecondsLabel.textContent = copy.milliseconds;
  ampmTag.textContent = copy.am;
  document.documentElement.lang = currentLanguage;

  cityDefinitions.forEach((city) => {
    const marker = cityMarkers.get(city.id);
    if (!marker) {
      return;
    }
    marker.querySelector(".city-name").textContent = city.names[currentLanguage];
  });

  updateSelectedCityDisplay();
  updateTime();
}

function setSelectedCity(cityId) {
  const city = cityDefinitions.find((entry) => entry.id === cityId);
  if (!city) {
    return;
  }
  selectedCityId = city.id;
  selectedTimeZone = city.timeZone;
  cityMarkers.forEach((marker, id) => {
    marker.classList.toggle("is-selected", id === selectedCityId);
  });
  updateSelectedCityDisplay();
  updateTime();
}

function startTimer() {
  if (animationFrameId !== null) {
    return;
  }
  const tick = () => {
    updateTime();
    animationFrameId = window.requestAnimationFrame(tick);
  };
  updateTime();
  animationFrameId = window.requestAnimationFrame(tick);
}

function stopTimer() {
  if (animationFrameId === null) {
    return;
  }
  window.cancelAnimationFrame(animationFrameId);
  animationFrameId = null;
}

toggleButton.addEventListener("click", () => {
  const copy = translations[currentLanguage];
  if (isRunning) {
    stopTimer();
    toggleButton.textContent = copy.resume;
  } else {
    startTimer();
    toggleButton.textContent = copy.pause;
  }
  isRunning = !isRunning;
});

languageToggle.addEventListener("click", () => {
  currentLanguage = currentLanguage === "en" ? "ko" : "en";
  applyLanguage();
});

cityDefinitions.forEach((city) => {
  const marker = cityMarkers.get(city.id);
  if (!marker) {
    return;
  }
  marker.addEventListener("click", () => {
    setSelectedCity(city.id);
  });
});

["hours", "minutes", "seconds"].forEach((key) => {
  const element = document.getElementById(key);
  element.addEventListener("animationend", () => {
    element.classList.remove("time-part--impact", "time-part--slam");
  });
});

setSelectedCity(selectedCityId);
applyLanguage();
startTimer();
