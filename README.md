# Production Tools Monorepo

Three standalone tools for film/TV production workflows — Scene Reader Studio Technologies LLC.

---

## Projects

### contract-review-tool

AI-powered contract analysis using the Anthropic Claude API. Upload PDF, DOCX, or TXT files for instant structured review with password-protected access.

**Start:** Double-click `Start server.BAT` or run:

```bat
cd contract-review-tool
& "Start server.BAT"
```

**URL:** <http://localhost:5001>

**Login:** Password set via `APP_PASSWORD` in `.env`

**Setup:**

1. Copy `.env.example` → `.env`
2. Add your `ANTHROPIC_API_KEY`
3. Set `APP_PASSWORD` to your chosen login password
4. `pip install -r requirements.txt`

---

### production-budget-parser

Film/TV budget analysis with risk scoring, multi-budget comparison, Excel export, and PDF reports. SQLite-backed. **v2.1.0**

**Start:** Double-click `Start server.BAT` or from PowerShell:

```powershell
cd production-budget-parser
& "Start server.BAT"
```

**URL:** <http://localhost:8082>

**Setup:**

1. Copy `.env.example` → `.env`
2. Set `SECRET_KEY` to a random string (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
3. Set `BUDGET_API_KEY` to any string (used for the AI insights API endpoint)
4. `pip install -r requirements.txt`

**Key features (v2.1.0):**

- Interactive stat cards with modal detail views (Line Items, Departments, Budget Breakdown, Risk Assessment)
- Chart.js visualizations: department allocation, top budget items, category breakdown, risk distribution
- Multi-budget comparison with variance analysis
- Excel + PDF export
- 8-category risk scoring system (patent pending)

See [CHANGELOG.md](production-budget-parser/CHANGELOG.md) for full version history.

---

### screenflow-aura

Screenplay intelligence platform — AI-powered screenplay parsing and analysis.

**Start:** Double-click `Start server.BAT` or from PowerShell:

```powershell
cd screenflow-aura
& "Start server.BAT"
```

**URL:** <http://localhost:8083>

**Setup:**

1. Copy `.env.example` → `.env`
2. Add your `ANTHROPIC_API_KEY`
3. Set `SECRET_KEY` and `AURA_API_KEY`
4. `pip install -r requirements.txt`

**API endpoints** (all require `X-API-Key` header except health):

| Endpoint           | Method | Description            |
| ------------------ | ------ | ---------------------- |
| `/api/health`      | GET    | Status check (no auth) |
| `/api/parse`       | POST   | Parse screenplay       |
| `/api/analyze`     | POST   | AI analysis            |
| `/api/batch/parse` | POST   | Batch parsing          |
| `/api/history`     | GET    | Analysis history       |

---

## Daily Startup

**Stop all servers** (PowerShell):

```powershell
taskkill /F /IM python.exe
```

**Start each project** (PowerShell — quotes required due to space in filename):

```powershell
& "c:\Projects\production-parser\contract-review-tool\Start server.BAT"
& "c:\Projects\production-parser\production-budget-parser\Start server.BAT"
& "c:\Projects\production-parser\screenflow-aura\Start server.BAT"
```

Each script auto-checks for a local `venv/`, verifies dependencies, and prints the server URL before starting.

---

## Environment Files

Each project has a `.env.example` — copy it to `.env` and fill in values before running. `.env` files are gitignored and never committed.

| Project                  | Required Keys                                      |
| ------------------------ | -------------------------------------------------- |
| contract-review-tool     | `ANTHROPIC_API_KEY`, `APP_PASSWORD`, `SECRET_KEY`  |
| production-budget-parser | `SECRET_KEY`, `BUDGET_API_KEY`                     |
| screenflow-aura          | `ANTHROPIC_API_KEY`, `SECRET_KEY`, `AURA_API_KEY`  |

---

## Repository Structure

```text
production-parser/
├── contract-review-tool/       # Port 5001 — Contract AI analysis
├── production-budget-parser/   # Port 8082 — Budget parser v2.1.0
│   └── CHANGELOG.md            # Version history
├── screenflow-aura/            # Port 8083 — Screenplay intelligence
└── _archive/                   # Legacy scripts (reference only)
```

---

*Proprietary — Scene Reader Studio Technologies LLC. All rights reserved.*
