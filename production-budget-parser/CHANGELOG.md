# CHANGELOG — Production Budget Parser

All notable changes to this project are documented here.

---

## [2.4.0] — 2026-03-11

### Comparison Card Modals & Sample Budgets

#### Comparison Page — Interactive Cards

- All 4 comparison summary cards are now clickable with modal overlays
- **Budget A / Budget B cards**: show total budget, line items, departments, risk level, upload date + direct link to full analysis
- **Difference card**: category breakdown table sorted by largest absolute $ gap (top 10), HIGH VARIANCE badge when overall change ≥ 50%
- **% Change card**: category breakdown sorted by largest % swing (top 10), per-row ⚠ HIGH badge on any category ≥ ±50% variance
- Direction context label on Difference and % Change cards ("Budget B is higher", "Budget B vs Budget A")
- Esc key and click-outside both close modals
- `category_changes` key correctly mapped from `budget_comparison.py` result (`budget1_amount`, `budget2_amount`, `difference`, `percent_change`)

#### Sample Budgets

- 10 production budget CSV files added to `sample_budgets/` for testing and demo use
  - `01_feature_film_blockbuster.csv` — Studio blockbuster (~$13M, 59 line items)
  - `02_indie_drama_lowbudget.csv` — Indie drama (~$242K, 38 items)
  - `03_streaming_series_season1.csv` — 8-episode streaming series (~$10.5M, 44 items)
  - `04_music_video_hiphop.csv` — Music video (~$154K, 34 items)
  - `05_documentary_feature.csv` — Feature documentary (~$418K, 38 items)
  - `06_branded_content_campaign.csv` — Brand campaign 3 spots (~$496K, 42 items)
  - `07_animated_short.csv` — 2D animated short (~$385K, 30 items)
  - `08_reality_tv_pilot.csv` — Reality TV pilot (~$1.05M, 40 items)
  - `09_corporate_training_video.csv` — Corporate training video (~$50K, 28 items)
  - `10_vr_immersive_experience.csv` — VR/immersive experience (~$1.6M, 42 items)

#### Auth Config

- `APP_PASSWORD` added to `.env` (required for login — server must restart after change)
- `APP_PASSWORD` documented in `.env.example`

---

## [2.3.0] — 2026-03-10

### Authentication & HTTPS

#### Authentication

- Session-based login added to all web routes via `@login_required` decorator
- Password set via `APP_PASSWORD` environment variable (`.env`)
- Timing-safe password comparison via `hmac.compare_digest()`
- `/login` and `/logout` routes added; unauthenticated requests redirect to `/login`
- Logout link added to dashboard and analysis pages

#### HTTPS

- `Caddyfile` added for Caddy reverse proxy setup
- Supports localhost (self-signed), public domain (Let's Encrypt auto-cert), and LAN IP modes
- App remains bound to `127.0.0.1:8082`; Caddy handles TLS termination

#### Env

- `.env.example` updated with `APP_PASSWORD`, `ANTHROPIC_API_KEY`, `BUDGET_API_KEY`

---

## [2.2.0] — 2026-03-10

### Production Hardening

#### Security

- CSRF protection on all POST forms (Flask-WTF `CSRFProtect`)
- `debug=False`, `host=127.0.0.1` — no longer binds to all interfaces
- XSS: all user-supplied CSV values escaped via `html.escape()` before HTML injection
- Session cookie flags: `HTTPONLY=True`, `SAMESITE=Lax`
- API key query-string support removed — header and JSON body only
- All exception handlers log full tracebacks server-side; users receive generic messages

#### Rate Limiting

- Flask-Limiter added: 200 req/day + 60 req/hr global, 20 uploads/hr per IP

#### Input Validation

- `Amount` column coerced to numeric on upload; fully non-numeric files rejected
- Partial non-numeric rows zeroed and logged as warnings

#### Infrastructure

- Startup script auto-detects gunicorn and uses it as WSGI server; falls back to Flask dev server
- `/api/health` endpoint added (no auth required) — returns `{"status": "ok", "analyses": N}`
- `api_keys.json` cached in memory after first read (was re-read on every API request)
- All dependencies pinned to exact versions in `requirements.txt`

---

## [2.1.0] — 2026-03-10

### UI/UX Overhaul — Interactive Dashboard

#### New Features

- **Interactive Stat Cards**: All four dashboard stat cards (Total Budget, Line Items, Departments, Risk Level) are now clickable and open detailed modal overlays
  - **Total Budget modal**: Category breakdown table with amounts and percentages
  - **Line Items modal**: Full scrollable table of every budget line item with department, category, and amount
  - **Departments modal**: Per-department totals, percentages, and item counts
  - **Risk Level modal**: Overall risk score, risk category matrix, and high-risk items table (dynamic color-coded by severity)
- **Chart rendering fixed**: Department Allocation, Top 10 Budget Items, Category Breakdown, and Risk Distribution charts now render correctly on the analysis page
  - Added `charts.js` script tag (`defer`) to analysis page `<head>`
  - Changed chart initialization from `DOMContentLoaded` → `window.load` event with 200 ms fallback retry

#### Visual Changes

- **Background**: Changed from purple gradient to dark slate (`#0f172a`) for clear card contrast
- **Stat card hover effects**: Cards lift and scale on hover with blue top border and gradient highlight
- **Section title**: Color updated from `white` to `#e2e8f0` (legible on dark background)
- **Chart containers**: Minimum height set (`360px`), flex layout ensures canvas fills available space

#### Bug Fixes

- Fixed `upload_file()` calling non-existent `analyze_budget()` → corrected to `analyze_risks()`
- Fixed flash messages never displaying on index page
- Fixed `pd.read_json()` pandas 2.x compatibility — wrapped all calls in `io.StringIO()`
- Removed duplicate `<h2>📊 Visual Comparison</h2>` heading on comparison page
- Fixed chart title readability on comparison charts

#### Files Changed

- `web_app.py` — stat card modals, flash message support, chart script tag, upload route fix
- `static/css/modern-styles.css` — background, hover effects, chart container sizing
- `charts_data.py` — `window.load` event listener with fallback retry
- `comparison_charts.py` — chart title color and size fixes

---

## [2.0.0] — 2024-12-05

### Initial Release (v2.0.0)

- Flask web application with SQLite (SQLAlchemy)
- CSV budget upload and parsing
- Risk assessment via 8-category weighted system (patent pending)
- Budget comparison (2–4 files, variance calculation)
- Excel export and PDF report generation
- Chart.js interactive visualizations
- Basic authentication via `flask_auth.py`
