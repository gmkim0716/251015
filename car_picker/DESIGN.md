# Car Picker Quiz – Design Summary

## Goals and Requirements
- Serve a 10-choice quiz that shows a random car image and asks for the make/model/year depending on difficulty.
- Difficulty modes: `make` (manufacturer only), `make_model`, `make_model_year`.
- Enforce a per-question timer; expired questions count as incorrect.
- Provide local session stats and a server-backed leaderboard.
- Allow users to switch light/dark themes and choose among bundled Korean-friendly fonts.
- Defer thumbnail generation and duplicate filtering to a future phase.

## Architecture Overview

### Backend (FastAPI)
- **Settings** (`settings.py`): central configuration (`data_dir`, static mount paths, default timeout, leaderboard size). Environment-driven via `CAR_PICKER_*`.
- **Indexer** (`indexer.py`): scans `car_picker/data`, parses filenames into `CarEntry` objects, and builds lookup maps by make/model.
- **Sampler** (`sampler.py`): generates question payloads with 10 unique options following difficulty-specific heuristics.
- **Question store** (`store.py`): keeps recent questions in memory for answer verification and expiration.
- **Scoreboard** (`score.py`): in-memory leaderboard with difficulty and streak bonuses.
- **API routes** (`routes.py`):
  - `GET /api/question`: serve question metadata and options, honoring `difficulty` and optional `timer` query params.
  - `POST /api/answer`: validate submissions (including timeout cases) and update the leaderboard.
  - `GET /api/leaderboard`: return top N scores.
  - `POST /api/leaderboard/reset`: utility endpoint for clearing scores.
- **App entry** (`main.py`): wires everything together, mounts static assets (`/static/assets`) and car images (`/static/cars`), and exposes `index.html`.

### Frontend (Vanilla JS)
- **Template** (`templates/index.html`): single-page layout with header, image display, options grid, controls, stats sidebar, leaderboard, and settings dialog.
- **Script** (`static/app.js`):
  - Manages state (current question, selections, timer, stats, settings, player name).
  - Fetches questions/answers via the API, handles timeout logic, triggers leaderboard refreshes.
  - Applies theme/font preferences and keyboard shortcuts (1–0 for selections, Enter to submit).
- **Styles** (`static/styles.css`): responsive layout, theme variables, and component styling for light/dark modes.

### Data Handling
- Filenames follow the scraper convention `Make_Model_Year_..._<RandomID>.jpg`. Parsing logic validates make/model/year tokens and ignores other metadata for now.
- `CarDataset` exposes helpers to fetch entries by make/model and to iterate randomly, supporting distractor generation.

## Scoring Rules
- Correct answer: 10 base points.
- Bonus: +0 (`make`), +5 (`make_model`), +10 (`make_model_year`).
- Streak bonus: +5 when a player reaches a streak of 3 or more.
- Incorrect or timeout: streak reset; no points awarded.

## Testing Strategy
- `test_indexer.py`: validates filename parsing and dataset loading.
- `test_sampler.py`: ensures quizzes contain the correct answer and 10 unique options.
- `test_api.py`: exercises the full API flow (question → answer → leaderboard) with `TestClient`.

## Future Enhancements
- Add thumbnail generation and caching for faster loads.
- Persist leaderboard data to SQLite or another datastore.
- Introduce authentication or session management for long-lived player profiles.
- Improve distractor quality (e.g., trim levels, regional variants) as needed.
