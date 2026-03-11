# CHANGELOG — Contract Review Tool

All notable changes to this project are documented here.

---

## [1.1.0] — 2026-03-11

### Performance — Streaming Analysis

#### Speed

- Analysis time reduced from 45–60 seconds to **15–30 seconds**
- `max_tokens` reduced from 4,000 → 1,500 (primary time lever)
- Prompt rewritten to target 800–1,200 output tokens with concise 1-2 line-per-item structure
- Contract input capped at 12,000 characters (~3,000 tokens) to bound request time on large documents

#### Streaming

- `/upload` route now returns `text/event-stream` (Server-Sent Events) instead of buffered JSON
- Claude response streamed token-by-token via `client.messages.stream()` (Anthropic Python SDK)
- Frontend consumes SSE with `fetch` + `response.body.getReader()` — no polling, no page reload
- Live text preview scrolls as analysis generates
- `done` event carries full parsed analysis JSON; triggers `sessionStorage` save + redirect to `/results`
- `error` event surfaces Claude or server errors cleanly to the UI

#### UX

- Loading stage label advances automatically: *Reading → Key Terms → Risks → Negotiation → Finalizing*
- Live elapsed-time counter (`0s`, `1s`, `2s`…) replaces static "15–30 seconds" copy
- Stream preview box (`.stream-preview`) appears as first tokens arrive
- Styles moved to `style.css` (`.stream-preview`, `.stream-preview.visible`)

#### Files Changed

- `app.py` — new `_build_analysis_prompt()`, `stream_contract_analysis()`, rewritten `/upload` route
- `templates/contract.html` — streaming fetch reader, stage timer, preview box
- `static/style.css` — `.stream-preview` and `.stream-preview.visible` classes

---

## [1.0.0] — 2024-12-05

### Initial Release

- Flask web application with SQLite history (`AnalysisHistory` model)
- PDF, DOCX, DOC, TXT contract upload and text extraction
- AI analysis via Claude (`claude-sonnet-4-6`): key terms, risk assessment, fairness verdict, negotiation points
- Session-based login with `APP_PASSWORD` env var
- Results page with structured display of analysis sections
- Analysis history page with past reviews
- Batch analysis endpoint (`/api/batch`)
