# TutEditor MVP Plan

## Objective
Build a web-only, Python-first TutEditor MVP centered on one workspace page where:
- the user declares task context first,
- writes code in an editor,
- runs parallel side conversations,
- and explicitly triggers tutoring (hint button or side-thread submit).

## Hard Constraints
- Web app only.
- Task context is required before tutoring.
- Parallel side conversations are first-class.
- No continuous monitoring or auto-intervention.
- Single workspace page for MVP.
- Python-first implementation.

## Architecture Direction (MVP)
- Backend: FastAPI + SQLite + SQLModel (or SQLAlchemy + Pydantic).
- Frontend: Single HTML workspace with JS modules and CSS (no heavy SPA framework required for MVP).
- LLM layer: Python service adapter called only on explicit events.
- Storage:
  - session + task context,
  - editor snapshots/recent edits,
  - conversation threads/messages,
  - hint requests and tutor responses.

## Delivery Phases

### Phase 0: Foundation
- Scaffold backend app structure, config, and DB session management.
- Add health endpoint and local run workflow.
- Define shared schemas and error format.

Exit criteria:
- App boots locally.
- DB connection works.
- Basic API docs render.

### Phase 1: Core Domain + Persistence
- Implement models:
  - `Session`
  - `TaskContext`
  - `CodeSnapshot`
  - `ConversationThread`
  - `ConversationMessage`
  - `HintRequest`
  - `TutorResponse`
- Add migrations.

Exit criteria:
- DB tables created via migration.
- CRUD works through repository/service layer.

### Phase 2: API Contracts
- Implement REST endpoints for:
  - session + task context bootstrap,
  - editor snapshot updates,
  - thread creation/listing,
  - side-thread message submit (explicit tutor trigger path),
  - hint request trigger (explicit tutor trigger path),
  - workspace aggregate fetch.
- Enforce context-first validation.

Exit criteria:
- Endpoints match `SPEC.md`.
- Integration tests pass for happy path and guardrails.

### Phase 3: Tutor Orchestration
- Build prompt payload composer from:
  - task context,
  - latest code + recent edits,
  - relevant thread context,
  - optional runtime/test error info.
- Build tutor response parser and persistence.
- Add strict invocation policy: explicit trigger only.

Exit criteria:
- Tutor is called only from explicit events.
- Payload and output conform to schema.

### Phase 4: Single Workspace UI
- Build one page with:
  - task context panel,
  - code editor area,
  - parallel conversation sidebar,
  - explicit hint button,
  - tutor response cards.
- Block tutoring actions until task context exists.

Exit criteria:
- User can run end-to-end loop on one page.
- Multiple threads usable in parallel.

### Phase 5: Hardening + Demo Readiness
- Add request logging and basic telemetry.
- Add input validation and UX error states.
- Add seed/demo data + docs.

Exit criteria:
- Reliable local demo.
- Clear known limitations documented.

## Non-Goals (MVP)
- Continuous code monitoring.
- Autonomous agent behavior.
- Multi-page product surface.
- Full project-wide reasoning across large repos.
- Background tutoring without explicit user actions.

## Definition of Done
- A user can:
  1. Open workspace.
  2. Provide task context.
  3. Write/update code.
  4. Create/use multiple side threads.
  5. Click `Hint / I'm getting stuck` or submit a thread message.
  6. Receive grounded nudge-style tutor output.
- No tutor call happens without explicit trigger.

