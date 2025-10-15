# Impact World Timer

## Features
- Punchy 12-hour clock with AM/PM tag, millisecond precision, and kinetic transitions on every second and minute change.
- Dual-language interface (English / 한국어) with a single-click toggle.
- Interactive world map background with major city hotspots that instantly shift the timer's timezone.
- Automatic day and night indicators per city so you can see where the sun is shining right now.
- Pause and resume control that freezes the display while keeping your timezone and language selections intact.

## Getting Started
1. Open `timer/index.html` in a modern browser.
2. Click the glowing city markers to jump between timezones.
3. Use the language toggle in the header to switch between English and Korean copy.
4. Hit `Pause` to freeze the moment, or `Resume` to bring the action back.

## Customisation
- To add another city, duplicate one of the existing `.city-marker` buttons in `timer/index.html`, set its `data-timezone`, and update `cityDefinitions` in `timer/script.js` with translations and the same `id`.
- Colours, animations, and layout are controlled via CSS tokens in `timer/styles.css`.
