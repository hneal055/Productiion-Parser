# CHANGELOG — ScreenFlow AURA

All notable changes to this project are documented here.

---

## [3.1.1] — 2026-03-21

### Action Card Toolbar — Index Page

- Added action card toolbar to `templates/index.html` below the stats section
- **Back to Dashboard** — reloads `/`
- **Save to** dropdown — Save as PDF (print dialog), Save as TXT (client-side download of page text)
- **Print Report** — `window.print()`; `@media print` hides the toolbar
- **Copy to Clipboard** — copies full page text via `navigator.clipboard`
- Cards styled to match the dark theme (`rgba` borders, `#a78bfa` accent colour)
- Dropdown closes on outside click

---

## [3.1.0] — 2026-03-11

### Initial Flask + SQLite Rewrite

- Rewritten from `http.server` to Flask with real Claude AI, SQLite persistence, and API key auth
- All endpoints protected by `X-API-Key` header auth; keys stored as SHA-256 hashes
- Admin endpoints (`/api/admin/keys`) protected by separate `X-Admin-Token`
- `/api/parse`, `/api/analyze`, `/api/validate` — 20/hr rate limit per key
- `/api/batch/parse` — batch up to 10 scripts, 5/hr rate limit
- `/api/history` — paginated analysis history
- `/api/metrics` — usage breakdown by analysis type
- Flask-Migrate (Alembic) for schema management; `db.create_all()` fallback when no migrations dir
- `templates/index.html` — Jinja2 API reference page with live stats
- `AURA_API_KEY` env var seeds default key on first boot
