# Production Tools Monorepo

Three standalone tools for film/TV production workflows.

---

## Projects

### contract-review-tool

AI-powered contract analysis using the Anthropic Claude API. Upload PDF, DOCX, or TXT files for instant structured review.

**Start:** Double-click `Start server.BAT` or run:

```bat
cd contract-review-tool
venv\Scripts\python.exe app.py
```

**URL:** <http://localhost:5001>

**Setup:**

1. Copy `.env.example` → `.env`
2. Add your `ANTHROPIC_API_KEY`
3. `pip install -r requirements.txt`

---

### production-budget-parser

Film/TV budget analysis with risk scoring, multi-budget comparison, Excel export, and PDF reports. SQLite-backed.

**Start:**

```bat
cd production-budget-parser
python web_app.py
```

**Setup:**

1. Copy `.env.example` → `.env`
2. Set `SECRET_KEY` to a random string
3. `pip install -r requirements.txt`

---

### screenflow-aura

Screenplay intelligence platform. Entry point: `enterprise_aura_api.py`.

---

## Environment Files

Each project has a `.env.example` — copy it to `.env` and fill in values before running. `.env` files are gitignored and never committed.
