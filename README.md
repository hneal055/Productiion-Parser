# Production Tools Monorepo

Three standalone tools for film/TV production workflows — Scene Reader Studio Technologies LLC.

| Project | Version | Port | Description |
| --- | --- | --- | --- |
| contract-review-tool | v1.3.0 | 5001 | AI contract analysis (PDF/DOCX/TXT) |
| production-budget-parser | v2.5.0 | 8082 | Film/TV budget parsing and risk scoring |
| screenflow-aura | v3.1.0 | 8083 | Screenplay intelligence API |

---

## Quick Start (Docker — recommended)

```bash
# 1. Copy and fill .env for each project
cp contract-review-tool/.env.example      contract-review-tool/.env
cp production-budget-parser/.env.example  production-budget-parser/.env
cp screenflow-aura/.env.example           screenflow-aura/.env

# 2. Edit each .env — set SECRET_KEY, ADMIN_PASSWORD/AURA_API_KEY, ANTHROPIC_API_KEY

# 3. Start all three services
docker compose up -d --build
```

Services start on ports 5001, 8082, 8083. Database migrations run automatically on first boot.

---

## Quick Start (Local / Windows)

```powershell
# Start all three servers (each in its own terminal)
& "c:\Projects\production-parser\contract-review-tool\Start server.BAT"
& "c:\Projects\production-parser\production-budget-parser\Start server.BAT"
& "c:\Projects\production-parser\screenflow-aura\Start server.BAT"

# Stop all servers
taskkill /F /IM python.exe
```

Each `.BAT` script auto-activates the local `venv/`, installs dependencies, and prints the server URL.

---

## Projects

### contract-review-tool — v1.3.0

AI-powered contract analysis. Upload PDF, DOCX, or TXT for a structured review with risk flags, fairness assessment, and negotiation points — streamed in real-time via SSE.

**URL:** <http://localhost:5001> · **Login:** username + password (set via `ADMIN_USERNAME` / `ADMIN_PASSWORD`)

**Setup:**
```bash
cd contract-review-tool
cp .env.example .env          # fill in SECRET_KEY, ADMIN_PASSWORD, ANTHROPIC_API_KEY
pip install -r requirements.txt
flask db upgrade              # run migrations (or just start — app auto-migrates)
python app.py
```

---

### production-budget-parser — v2.5.0

Film/TV budget parser with risk scoring, multi-budget comparison, Excel/PDF export, and AI-powered line-item analysis. SQLite-backed with Alembic migrations.

**URL:** <http://localhost:8082> · **Login:** username + password (set via `ADMIN_USERNAME` / `ADMIN_PASSWORD`)

**Setup:**
```bash
cd production-budget-parser
cp .env.example .env          # fill in SECRET_KEY, ADMIN_PASSWORD, ANTHROPIC_API_KEY, BUDGET_API_KEY
pip install -r requirements.txt
python web_app.py
```

**Key features:**
- Interactive dashboard — stat cards, Chart.js visualizations, modal detail views
- 8-category risk scoring system (patent pending)
- Multi-budget comparison with variance analysis
- Excel + PDF export

See [CHANGELOG.md](production-budget-parser/CHANGELOG.md) for full version history.

---

### screenflow-aura — v3.1.0

Screenplay intelligence REST API. All endpoints protected by API key auth. Keys managed via admin endpoints — no manual DB edits required.

**URL:** <http://localhost:8083>

**Setup:**
```bash
cd screenflow-aura
cp .env.example .env          # fill in SECRET_KEY, ANTHROPIC_API_KEY, AURA_API_KEY, AURA_ADMIN_TOKEN
pip install -r requirements.txt
python app.py
```

**Analysis endpoints** (require `X-API-Key` header):

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/health` | GET | Status check — no auth required |
| `/api/parse` | POST | Full screenplay parse (20/hr) |
| `/api/analyze` | POST | Deep narrative analysis (20/hr) |
| `/api/validate` | POST | Format compliance check (20/hr) |
| `/api/batch/parse` | POST | Batch parse multiple scripts (5/hr) |
| `/api/history` | GET | Paginated analysis history |
| `/api/metrics` | GET | Usage metrics by type |

**Key management endpoints** (require `X-Admin-Token` header):

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/admin/keys` | GET | List all API keys |
| `/api/admin/keys` | POST | Create new key — raw key returned once |
| `/api/admin/keys/<id>` | DELETE | Revoke key (soft disable) |
| `/api/admin/keys/<id>?permanent=1` | DELETE | Hard-delete key |

---

## Environment Variables

Each project has a `.env.example`. Copy to `.env` and fill in before running. Never commit `.env` files.

**Generate secure values:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

| Project | Required | Optional |
| --- | --- | --- |
| contract-review-tool | `SECRET_KEY`, `ADMIN_PASSWORD`, `ANTHROPIC_API_KEY` | `ADMIN_USERNAME` (default: `admin`), `HTTPS` |
| production-budget-parser | `SECRET_KEY`, `ADMIN_PASSWORD`, `ANTHROPIC_API_KEY` | `BUDGET_API_KEY`, `HTTPS` |
| screenflow-aura | `SECRET_KEY`, `ANTHROPIC_API_KEY`, `AURA_API_KEY` | `AURA_ADMIN_TOKEN`, `HTTPS`, `PORT` |

Set `HTTPS=true` in each `.env` when running behind a TLS reverse proxy (Caddy) to enable `SESSION_COOKIE_SECURE`.

---

## Tests

```bash
cd contract-review-tool     && python -m pytest tests/ -v   # 19 tests
cd production-budget-parser && python -m pytest tests/ -v   # 20 tests
cd screenflow-aura          && python -m pytest tests/ -v   # 23 tests
```

---

## Repository Structure

```text
production-parser/
├── contract-review-tool/       # Port 5001 — v1.3.0
│   ├── migrations/             # Alembic schema migrations
│   ├── templates/
│   ├── tests/
│   └── Dockerfile
├── production-budget-parser/   # Port 8082 — v2.5.0
│   ├── migrations/
│   ├── _archive/               # Retired modules (reference only)
│   ├── templates/
│   ├── tests/
│   └── Dockerfile
├── screenflow-aura/            # Port 8083 — v3.1.0
│   ├── migrations/
│   ├── tests/
│   └── Dockerfile
└── docker-compose.yml          # Orchestrates all three services
```

---

*Proprietary — Scene Reader Studio Technologies LLC. All rights reserved.*
