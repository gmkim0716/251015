const API_BASE = "/api";
const SETTINGS_KEY = "car-picker-settings";
const PLAYER_KEY = "car-picker-player";

const defaultSettings = {
  difficulty: "make_model_year",
  theme: "dark",
  font: "pretendard",
  timer: 20,
};

const textMap = {
  prompt: {
    make: "Pick the correct manufacturer for this car.",
    make_model: "Pick the correct manufacturer and model.",
    make_model_year: "Pick the correct manufacturer, model, and year.",
  },
  feedback: {
    select: "Choose one of the options before submitting.",
    loading: "Fetching a new question...",
    timeout: "Time is up. This question counts as incorrect.",
    submitError: "Unable to submit the answer right now. Please try again shortly.",
  },
};

const state = {
  settings: loadSettings(),
  question: null,
  selectedIndex: null,
  timerId: null,
  remainingSeconds: 0,
  isSubmitting: false,
  hasAnswered: false,
  stats: { correct: 0, attempts: 0, streak: 0 },
  playerName: loadPlayerName(),
};

const elements = {};

function $(selector) {
  return document.querySelector(selector);
}

function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) return { ...defaultSettings };
    const parsed = JSON.parse(raw);
    return {
      ...defaultSettings,
      ...parsed,
      timer: clampTimer(parsed.timer ?? defaultSettings.timer),
    };
  } catch {
    return { ...defaultSettings };
  }
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(state.settings));
}

function loadPlayerName() {
  return localStorage.getItem(PLAYER_KEY) || "";
}

function savePlayerName(name) {
  localStorage.setItem(PLAYER_KEY, name);
}

function clampTimer(value) {
  const num = Number(value);
  if (Number.isNaN(num)) return defaultSettings.timer;
  return Math.max(10, Math.min(60, Math.round(num)));
}

function applyTheme(theme) {
  document.body.dataset.theme = theme;
  elements.themeToggle.textContent = theme === "dark" ? "Dark Theme" : "Light Theme";
}

function applyFont(font) {
  document.body.dataset.font = font;
}

function initElements() {
  elements.image = $("#question-image");
  elements.timer = $("#timer");
  elements.prompt = $("#prompt-text");
  elements.options = $("#options");
  elements.submitButton = $("#submit-button");
  elements.nextButton = $("#next-button");
  elements.feedback = $("#feedback");
  elements.statCorrect = $("#stat-correct");
  elements.statAttempts = $("#stat-attempts");
  elements.statStreak = $("#stat-streak");
  elements.statAccuracy = $("#stat-accuracy");
  elements.serverScore = $("#server-score");
  elements.playerForm = $("#player-form");
  elements.playerNameInput = $("#player-name");
  elements.leaderboardList = $("#leaderboard-list");
  elements.refreshLeaderboard = $("#refresh-leaderboard");
  elements.themeToggle = $("#theme-toggle");
  elements.settingsToggle = $("#settings-toggle");
  elements.settingsDialog = $("#settings-dialog");
  elements.settingsForm = elements.settingsDialog.querySelector("form");
  elements.timerInput = $("#timer-input");
  elements.fontSelect = $("#font-select");
  elements.settingsCancel = $("#settings-cancel");
}

function applySettingsToUI() {
  applyTheme(state.settings.theme);
  applyFont(state.settings.font);
  elements.timer.textContent = "--";
  elements.timerInput.value = state.settings.timer;
  elements.playerNameInput.value = state.playerName;
  elements.settingsForm
    .querySelectorAll('input[name="difficulty"]')
    .forEach((input) => (input.checked = input.value === state.settings.difficulty));
  elements.settingsForm
    .querySelectorAll('input[name="theme"]')
    .forEach((input) => (input.checked = input.value === state.settings.theme));
  elements.fontSelect.value = state.settings.font;
}

async function loadQuestion() {
  stopTimer();
  elements.submitButton.disabled = true;
  elements.nextButton.disabled = true;
  state.selectedIndex = null;
  state.hasAnswered = false;
  state.question = null;
  setFeedback(textMap.feedback.loading, null);
  elements.options.innerHTML = "";

  const params = new URLSearchParams({
    difficulty: state.settings.difficulty,
    timer: String(state.settings.timer),
  });
  try {
    const response = await fetch(`${API_BASE}/question?${params.toString()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Failed to fetch question (${response.status})`);
    const question = await response.json();
    state.question = question;
    renderQuestion(question);
    renderOptions(question.options);
    state.remainingSeconds = question.timeout;
    startTimer(question.timeout);
    elements.submitButton.disabled = false;
    elements.nextButton.disabled = true;
    setFeedback("Select the best answer and press submit.", null);
  } catch (error) {
    console.error(error);
    setFeedback("Unable to load a question. Refresh and try again.", "timeout");
  }
}

function renderQuestion(question) {
  const promptText = textMap.prompt[question.difficulty] || "Identify the car shown.";
  const cacheBuster = `ts=${Date.now()}`;
  elements.image.src = `${question.imageUrl}?${cacheBuster}`;
  elements.image.alt = "Automobile quiz image";
  elements.prompt.textContent = promptText;
}

function renderOptions(options) {
  elements.options.innerHTML = "";
  options.forEach((option, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = option.label;
    button.addEventListener("click", () => selectOption(index));
    elements.options.appendChild(button);
  });
}

function selectOption(index) {
  if (!state.question || state.hasAnswered) return;
  state.selectedIndex = index;
  Array.from(elements.options.children).forEach((button, idx) => {
    button.classList.toggle("selected", idx === index);
  });
}

function startTimer(seconds) {
  const clamped = clampTimer(seconds);
  state.remainingSeconds = clamped;
  updateTimerDisplay();
  state.timerId = setInterval(() => {
    state.remainingSeconds -= 1;
    updateTimerDisplay();
    if (state.remainingSeconds <= 0) {
      stopTimer();
      handleTimeout();
    }
  }, 1000);
}

function stopTimer() {
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
}

function updateTimerDisplay() {
  elements.timer.textContent = `${Math.max(0, state.remainingSeconds)}s`;
}

function setFeedback(message, status) {
  elements.feedback.textContent = message || "";
  elements.feedback.classList.remove("correct", "wrong", "timeout");
  if (status) {
    elements.feedback.classList.add(status);
  }
}

async function handleSubmit() {
  if (!state.question || state.isSubmitting || state.hasAnswered) return;
  if (state.selectedIndex == null) {
    setFeedback(textMap.feedback.select, "timeout");
    return;
  }
  const answer = state.question.options[state.selectedIndex];
  await submitAnswer(answer, false);
}

async function handleTimeout() {
  if (!state.question || state.hasAnswered) return;
  setFeedback(textMap.feedback.timeout, "timeout");
  await submitAnswer(state.question.correct, true);
}

async function submitAnswer(answer, timedOut) {
  if (!state.question) return;
  state.isSubmitting = true;
  stopTimer();
  elements.submitButton.disabled = true;

  const payload = {
    qid: state.question.qid,
    difficulty: state.question.difficulty,
    answer,
    player: state.playerName || null,
    timeout: timedOut,
  };

  try {
    const response = await fetch(`${API_BASE}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`Answer request failed (${response.status})`);
    const result = await response.json();
    state.hasAnswered = true;
    handleAnswerResult(result, timedOut);
  } catch (error) {
    console.error(error);
    setFeedback(textMap.feedback.submitError, "timeout");
  } finally {
    state.isSubmitting = false;
    elements.nextButton.disabled = false;
  }
}

function handleAnswerResult(result, timedOut) {
  const correctLabel = result.correctAnswer.label;
  const isCorrect = result.correct && !timedOut;
  highlightOptions(correctLabel);
  updateStats(isCorrect);

  if (result.score) {
    renderServerScore(result.score);
    refreshLeaderboard();
  }

  if (timedOut) {
    setFeedback(textMap.feedback.timeout, "timeout");
  } else if (isCorrect) {
    setFeedback("Correct! Nice work.", "correct");
  } else {
    setFeedback("Incorrect. Study the details and try the next one.", "wrong");
  }
}

function highlightOptions(correctLabel) {
  Array.from(elements.options.children).forEach((button, index) => {
    const label = state.question.options[index]?.label;
    if (label === correctLabel) {
      button.classList.add("correct");
    }
    if (index === state.selectedIndex && label !== correctLabel) {
      button.classList.add("wrong");
    }
    button.disabled = true;
  });
}

function updateStats(isCorrect) {
  state.stats.attempts += 1;
  if (isCorrect) {
    state.stats.correct += 1;
    state.stats.streak += 1;
  } else {
    state.stats.streak = 0;
  }

  const accuracy =
    state.stats.attempts === 0 ? 0 : Math.round((state.stats.correct / state.stats.attempts) * 100);

  elements.statCorrect.textContent = state.stats.correct;
  elements.statAttempts.textContent = state.stats.attempts;
  elements.statStreak.textContent = state.stats.streak;
  elements.statAccuracy.textContent = `${accuracy}%`;
}

function renderServerScore(score) {
  const accuracy =
    score.total_attempts === 0
      ? 0
      : Math.round((score.total_correct / score.total_attempts) * 100);
  elements.serverScore.textContent = `${score.player}: ${score.points} pts · streak ${score.streak} · accuracy ${accuracy}%`;
}

async function refreshLeaderboard() {
  try {
    const response = await fetch(`${API_BASE}/leaderboard`, { cache: "no-store" });
    if (!response.ok) throw new Error("Leaderboard request failed");
    const data = await response.json();
    renderLeaderboard(data.entries || []);
  } catch (error) {
    console.error(error);
  }
}

function renderLeaderboard(entries) {
  elements.leaderboardList.innerHTML = "";
  if (!entries.length) {
    const empty = document.createElement("li");
    empty.textContent = "No scores recorded yet.";
    elements.leaderboardList.appendChild(empty);
    return;
  }

  entries.forEach((entry) => {
    const li = document.createElement("li");
    const nameSpan = document.createElement("span");
    nameSpan.textContent = entry.player;
    const metaSpan = document.createElement("span");
    const accuracy = Math.round((entry.accuracy || 0) * 100);
    metaSpan.textContent = `${entry.points} pts · ${accuracy}%`;
    li.appendChild(nameSpan);
    li.appendChild(metaSpan);
    elements.leaderboardList.appendChild(li);
  });
}

function bindEvents() {
  elements.submitButton.addEventListener("click", () => handleSubmit());
  elements.nextButton.addEventListener("click", () => loadQuestion());
  elements.refreshLeaderboard.addEventListener("click", () => refreshLeaderboard());
  elements.themeToggle.addEventListener("click", () => {
    state.settings.theme = state.settings.theme === "dark" ? "light" : "dark";
    applyTheme(state.settings.theme);
    saveSettings();
  });
  elements.settingsToggle.addEventListener("click", () => openSettingsDialog());
  elements.settingsCancel.addEventListener("click", () => closeSettingsDialog(false));
  elements.settingsForm.addEventListener("submit", (event) => {
    event.preventDefault();
    closeSettingsDialog(true);
  });
  elements.playerForm.addEventListener("submit", (event) => {
    event.preventDefault();
    state.playerName = elements.playerNameInput.value.trim();
    savePlayerName(state.playerName);
    setFeedback("Nickname saved.", null);
  });

  window.addEventListener("keydown", (event) => {
    if (!state.question || state.hasAnswered || document.activeElement?.tagName === "INPUT") {
      return;
    }
    const keyNumber = Number(event.key);
    if (!Number.isNaN(keyNumber) && keyNumber >= 0 && keyNumber <= 9) {
      const index = keyNumber === 0 ? 9 : keyNumber - 1;
      if (elements.options.children[index]) {
        selectOption(index);
      }
    }
    if (event.key === "Enter") {
      handleSubmit();
    }
  });
}

function openSettingsDialog() {
  applySettingsToUI();
  if (typeof elements.settingsDialog.showModal === "function") {
    elements.settingsDialog.showModal();
  } else {
    elements.settingsDialog.setAttribute("open", "");
  }
}

function closeSettingsDialog(saveChanges) {
  if (saveChanges) {
    const previousDifficulty = state.settings.difficulty;
    const previousTimer = state.settings.timer;

    const difficulty = elements.settingsForm.querySelector('input[name="difficulty"]:checked').value;
    const theme = elements.settingsForm.querySelector('input[name="theme"]:checked').value;
    const font = elements.fontSelect.value;
    const timerValue = clampTimer(elements.timerInput.value);

    state.settings = { difficulty, theme, font, timer: timerValue };
    saveSettings();
    applyTheme(theme);
    applyFont(font);

    if (previousDifficulty !== difficulty || previousTimer !== timerValue) {
      loadQuestion();
    }
  }

  if (typeof elements.settingsDialog.close === "function" && elements.settingsDialog.open) {
    elements.settingsDialog.close();
  } else {
    elements.settingsDialog.removeAttribute("open");
  }
}

async function bootstrap() {
  initElements();
  applySettingsToUI();
  bindEvents();
  refreshLeaderboard();
  await loadQuestion();
}

bootstrap();
