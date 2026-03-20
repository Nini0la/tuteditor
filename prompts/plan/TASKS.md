# TutEditor MVP Tasks (Codex-Executable)

Ordered for dependency safety. Each ticket should be completed and committed before the next.

## T001 - Project Skeleton (Python Web App)
- Goal: Create backend-first MVP app structure.
- Files:
  - `app/__init__.py`
  - `app/main.py`
  - `app/config.py`
  - `app/api/__init__.py`
  - `app/api/router.py`
  - `app/templates/workspace.html`
  - `app/static/js/workspace.js`
  - `app/static/css/workspace.css`
- Changes:
  - add FastAPI app bootstrap and root workspace route placeholder.
  - wire static and template serving.
- Done when:
  - `uv run uvicorn app.main:app --reload` starts and `/workspace/demo` renders.

## T002 - Dependencies + Tooling
- Goal: Add runtime and dev dependencies.
- Files:
  - `pyproject.toml`
- Changes:
  - add `fastapi`, `uvicorn`, `sqlmodel` (or `sqlalchemy` + `pydantic`), `alembic`, `jinja2`.
  - add `pytest`, `httpx` for tests.
- Done when:
  - environment installs cleanly and app boots.

## T003 - Database Setup
- Goal: Provide DB engine/session lifecycle.
- Files:
  - `app/db.py`
  - `app/deps.py`
- Changes:
  - SQLite engine config.
  - request-scoped DB session dependency.
- Done when:
  - health endpoint can access DB without errors.

## T004 - Domain Models
- Goal: Implement persistence models from `SPEC.md`.
- Files:
  - `app/models/session.py`
  - `app/models/task_context.py`
  - `app/models/code_snapshot.py`
  - `app/models/conversation.py`
  - `app/models/hint.py`
  - `app/models/__init__.py`
- Changes:
  - define all MVP entities and enums.
  - include created/updated timestamps.
- Done when:
  - metadata imports resolve and tables can be generated.

## T005 - Migrations
- Goal: Add migration pipeline and initial schema migration.
- Files:
  - `alembic.ini`
  - `alembic/env.py`
  - `alembic/versions/<timestamp>_init_schema.py`
- Changes:
  - configure alembic for model metadata.
  - create initial schema.
- Done when:
  - `alembic upgrade head` succeeds on clean DB.

## T006 - Pydantic Schemas
- Goal: Define API request/response contracts.
- Files:
  - `app/schemas/session.py`
  - `app/schemas/task_context.py`
  - `app/schemas/snapshot.py`
  - `app/schemas/thread.py`
  - `app/schemas/hint.py`
  - `app/schemas/common.py`
- Changes:
  - mirror `SPEC.md` contracts and error format.
- Done when:
  - schema import tests pass.

## T007 - Session + Context APIs
- Goal: Implement session creation first, with editable task context managed separately.
- Files:
  - `app/api/session_routes.py`
  - `app/services/session_service.py`
- Endpoints:
  - `POST /api/v1/sessions`
  - `POST /api/v1/sessions/{session_id}/task-context`
  - `PUT /api/v1/sessions/{session_id}/task-context`
- Done when:
  - create session returns ids and workspace URL; task context can be added later and updated repeatedly.

## T008 - Workspace Aggregate API
- Goal: Load all state for single-page boot.
- Files:
  - `app/api/workspace_routes.py`
  - `app/services/workspace_service.py`
- Endpoint:
  - `GET /api/v1/sessions/{session_id}/workspace`
- Done when:
  - response includes session, latest active task context, task context history metadata, latest snapshot, and threads.

## T009 - Snapshot API
- Goal: Persist editor snapshots.
- Files:
  - `app/api/snapshot_routes.py`
  - `app/services/snapshot_service.py`
- Endpoint:
  - `POST /api/v1/sessions/{session_id}/snapshots`
- Done when:
  - snapshot creates with proper `source`.

## T010 - Thread CRUD APIs
- Goal: Support parallel side conversation containers.
- Files:
  - `app/api/thread_routes.py`
  - `app/services/thread_service.py`
- Endpoints:
  - `POST /api/v1/sessions/{session_id}/threads`
  - `GET /api/v1/sessions/{session_id}/threads`
  - `GET /api/v1/threads/{thread_id}/messages`
- Done when:
  - multiple threads can be created and listed.

## T011 - Tutor Adapter Interface
- Goal: Isolate LLM provider details behind service abstraction.
- Files:
  - `app/tutor/adapter.py`
  - `app/tutor/types.py`
  - `app/tutor/fake_adapter.py`
- Changes:
  - define `generate_nudge(payload) -> TutorOutput`.
  - include fake adapter for local tests.
- Done when:
  - app can run without external LLM credentials.

## T012 - Prompt Payload Composer
- Goal: Build prompt payload from current session state.
- Files:
  - `app/tutor/payload_builder.py`
- Changes:
  - implement input schema assembly from:
    - task context,
    - latest snapshot + recent edits,
    - selected thread context.
- Done when:
  - unit tests validate schema shape.

## T013 - Hint Request API (Button Trigger)
- Goal: Implement explicit hint-trigger flow.
- Files:
  - `app/api/hint_routes.py`
  - `app/services/hint_service.py`
- Endpoint:
  - `POST /api/v1/sessions/{session_id}/hint-requests`
- Behavior:
  - require an active task context version,
  - use latest task context if multiple versions exist,
  - persist snapshot,
  - create hint request,
  - call tutor adapter,
  - persist tutor response.
- Done when:
  - returns `tutor_response` payload as in spec.

## T014 - Thread Message Submit + Optional Tutor Invoke
- Goal: Implement side-thread explicit tutor path.
- Files:
  - `app/api/message_routes.py`
  - `app/services/message_service.py`
- Endpoint:
  - `POST /api/v1/threads/{thread_id}/messages`
- Behavior:
  - always save user message.
  - only invoke tutor when `invoke_tutor=true`.
- Done when:
  - response returns `tutor_invoked` and ids.

## T015 - Invocation Guardrails
- Goal: Prevent accidental continuous monitoring behavior.
- Files:
  - `app/services/hint_service.py`
  - `app/services/message_service.py`
  - `app/tutor/policy.py`
- Changes:
  - central `is_explicit_trigger(event)` guard.
  - fail closed on unknown trigger sources.
- Done when:
  - test proves no periodic/background path invokes tutor.

## T016 - Workspace UI Shell
- Goal: Build single-page layout with required panels.
- Files:
  - `app/templates/workspace.html`
  - `app/static/css/workspace.css`
- UI blocks:
  - task context panel,
  - code editor panel,
  - side-thread list + active thread,
  - hint button.
- Done when:
  - page is usable desktop/mobile and all blocks render.

## T017 - Frontend State Store + API Client
- Goal: Implement client-side state model from `SPEC.md`.
- Files:
  - `app/static/js/state.js`
  - `app/static/js/api.js`
  - `app/static/js/workspace.js`
- Changes:
  - workspace boot from aggregate endpoint.
  - state transitions for context-required, ready, requesting.
- Done when:
  - user actions update UI consistently.

## T018 - Task Context Form Flow
- Goal: Enforce context-required tutor use while allowing context edits during session.
- Files:
  - `app/static/js/workspace.js`
  - `app/templates/workspace.html`
- Changes:
  - block tutor triggers until context exists.
  - allow creating first context after session creation.
  - allow editing current context via API without losing prior versions.
- Done when:
  - hint and tutor-invoking submit are disabled without context, but context can be edited anytime after creation.

## T019 - Parallel Threads UI Flow
- Goal: Fully support multiple side threads.
- Files:
  - `app/static/js/workspace.js`
- Changes:
  - create/select threads.
  - fetch/render per-thread message history.
- Done when:
  - at least two threads can be used independently in one session.

## T020 - Hint Button End-to-End
- Goal: Wire explicit hint button to backend trigger.
- Files:
  - `app/static/js/workspace.js`
- Changes:
  - capture editor snapshot only.
  - call hint endpoint and render response card.
- Done when:
  - click produces persisted tutor message.

## T021 - Side-Thread Submit End-to-End
- Goal: Wire thread submit to explicit tutor path.
- Files:
  - `app/static/js/workspace.js`
- Changes:
  - submit message with optional `invoke_tutor` toggle.
  - render assistant response when invoked.
- Done when:
  - submit can either chat-only or chat+hint depending on toggle.

## T022 - Error Handling + UX Feedback
- Goal: Make failures understandable and recoverable.
- Files:
  - `app/static/js/workspace.js`
  - `app/api/*_routes.py` (as needed)
- Changes:
  - render API errors using standard error contract.
  - include retry affordance.
- Done when:
  - `TASK_CONTEXT_REQUIRED` and validation errors are clearly shown.

## T023 - Tests: API + Service
- Goal: Add automated confidence for core loop and guardrails.
- Files:
  - `tests/test_sessions.py`
  - `tests/test_threads.py`
  - `tests/test_hints.py`
  - `tests/test_trigger_policy.py`
- Coverage:
  - context required,
  - context version update preserves history,
  - latest context is used by tutor payload,
  - explicit triggers only,
  - parallel threads,
  - hint persistence.
- Done when:
  - tests pass locally with fake adapter.

## T024 - Smoke Script + Readme
- Goal: Make MVP runnable by any contributor.
- Files:
  - `README.md`
  - `scripts/smoke_mvp.sh`
- Changes:
  - startup steps, migration command, and smoke path.
- Done when:
  - fresh clone can run MVP and validate core loop in under 10 minutes.

## Suggested Commit Grouping
- Commit A: T001-T005
- Commit B: T006-T010
- Commit C: T011-T015
- Commit D: T016-T021
- Commit E: T022-T024
