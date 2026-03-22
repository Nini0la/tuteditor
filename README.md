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

## Tutor Adapter Configuration

Default adapter is fake (deterministic; used by tests).

Enable Mozilla.ai any-llm:

```bash
export TUTEDITOR_TUTOR_ADAPTER=any_llm
export TUTEDITOR_ANY_LLM_PROVIDER=openai
export TUTEDITOR_ANY_LLM_MODEL=gpt-4.1-mini
```

Optional overrides:
- `TUTEDITOR_ANY_LLM_MAX_TOKENS` (default `300`)
- `TUTEDITOR_ANY_LLM_TEMPERATURE` (default `0.2`)
- `TUTEDITOR_ANY_LLM_API_KEY` (optional direct key override)
- `TUTEDITOR_ANY_LLM_API_BASE` (optional direct base URL override)

Provider credentials are still read using any-llm/provider env vars (for example `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`).

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
