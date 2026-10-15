# Transit Games: project notes for Claude

Companion site for city-scale transit games (Rail Rush, Area Claiming, Ticket to Ride). Static site on Vercel; data and sign-in on Firebase (Firestore + Auth). No server code.

## Layout
- `src/shell.html`: home, start/ongoing/past lists, create-game dialog, account dialog, light/dark toggle. Each game runs in an iframe (`srcdoc`) inside it.
- `src/rail-rush.html`, `src/area-claiming.html`, `src/ticket-to-ride.html`: one self-contained file per game (HTML + CSS + JS).
- `src/platform.js`: the ONLY file that talks to Firebase. Provides `claude.use('db')` (a Firestore instance) and `claude.use('user')` (`id()`), plus `window.TGAuth` for accounts. Games use `db.doc/collection/onSnapshot/get/set/update/delete/add/where`.
- `src/firebase-config.js`: Firebase web config (not secret).
- `firestore.rules`: security rules; paste changes into Firebase console > Firestore > Rules.
- `build.mjs`: `npm run build` embeds the games, config and platform into `public/index.html`. `public/` is generated: never edit it.
- `test/`: Python + Playwright tests with a mock shared database (`harness.py`). Run `python3 test/t_full.py` (also `t_3team.py`, `t_area.py`, `t_boston.py`, `t_theme.py`) after `npm run build`. Needs `pip install playwright && playwright install chromium`.
- `tools/`: Boston map data (`boston.json`) already embedded in Rail Rush; kept for reference.

## Working rules
- Edit files in `src/`, run `npm run build`, run the relevant tests, then deploy.
- Data lives under `games/{gid}/...` (events, players, teams, challenges, members) and `hides/`. Rail Rush state is derived from an append-only `events` log by the pure function `fold()`; change rules there, not by mutating stored state.
- Keep games free of Firebase imports; add any new backend capability in `platform.js`.
- Once a Rail Rush game has started, teams are locked (`teamsLocked()`): no joining or switching, except for players whose team the host removed. The game doc gets `startedAt`, and the shell refuses late non-member joiners unless spectators are allowed. Tests: `test/t_lock.py`.
- Do not use `alert/confirm/prompt`; use in-page dialogs.
- Deploy: commit and push to GitHub; Vercel builds automatically (`vercel.json`).
