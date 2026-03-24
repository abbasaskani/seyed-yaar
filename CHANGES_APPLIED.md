# Changes applied

## GitHub Pages reachability
- `docs/index.html` now redirects immediately to `./app.html`.
- Added `docs/404.html` to redirect broken GitHub Pages routes back to `./app.html`.
- `docs/manifest.json` start URL changed to `./app.html` and `scope` set to `./`.
- `docs/sw.js` cache bumped and navigation fallback added so the app is still reachable offline / after bad routes.

## Latitude UI offset fix
- Added a UI-only latitude correction in `docs/app.js`.
- Display/export latitude now uses `lat - 0.27`.
- Raw analytical coordinates and internal computation remain unchanged.

## Notes
- This package contains the deployable GitHub Pages/front-end portion plus a few top-level repo files.
- The current fix request only required the Pages/front-end files.
