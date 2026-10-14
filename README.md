# Transit Games
See `CLAUDE.md` for how the project fits together.

Local preview: `npm run build` then open `public/index.html` (or `npm start`). Needs `src/firebase-config.js` filled in.
Deploy: push to GitHub; Vercel runs `node build.mjs` and serves `public/`.
Firebase: Firestore database + Authentication (Anonymous, Email/Password, Google), rules in `firestore.rules`.
