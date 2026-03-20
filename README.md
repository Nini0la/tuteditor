## TutEditor MVP

Single-page tutoring workspace with:
- task context declaration,
- code editor snapshot capture,
- parallel side threads,
- explicit tutoring triggers only (`hint button` or `invoke_tutor=true` message submit).

## Prerequisites

- Python `3.12+`
- `uv`
- Node.js + npm (for Playwright UI tests)

## Setup

```bash
uv sync --dev
npm install
npx playwright install chromium
```

## Run App

```bash
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Open:
- `http://127.0.0.1:8000/workspace/<session_id>`

## Run Tests

API/unit:

```bash
uv run python -m pytest -q
```

UI:

```bash
npm run test:ui
```

## Smoke Path (Under 10 Minutes)

```bash
./scripts/smoke_mvp.sh
```

The smoke script validates:
- health endpoint,
- session creation without context,
- task context creation,
- thread creation,
- chat-only thread message (`invoke_tutor=false`),
- explicit hint request (`request_type=stuck`).
