# TutEditor MVP Test Plan (Codex-Executable)

This test plan is the implementation contract for automated test coverage of TutEditor MVP.
It is traced to:
- `prompts/research/RESEARCH.md`
- `prompts/implementation/SPEC.md`
- `prompts/plan/TASKS.md`

## 1. Test Strategy

- Test layers:
  - API tests (FastAPI + DB + fake tutor adapter)
  - Service/unit tests (pure services + policy + payload builder)
  - UI interaction tests (workspace state + user flows)
  - Guardrail tests (explicit-trigger-only enforcement)
  - Negative tests (validation/errors/fail-closed behavior)
- Use fake tutor adapter and explicit call counters/spies in all non-e2e tests.
- Fail closed principle: unknown or missing trigger information must produce no tutor call.

## 2. Traceability Map (Core Behaviors)

1. Task context required before tutor invocation
- Source:
  - `RESEARCH.md` section `1. User-declared task context comes first`
  - `SPEC.md` sections `4.1`, `4.6 Validation`, `5.2`
  - `TASKS.md` `T007`, `T013`, `T018`, `T023`

2. Tutor runs only on explicit triggers
- Source:
  - `RESEARCH.md` section `3. Tutoring should be user-triggered, not constantly running`
  - `SPEC.md` sections `1`, `4.5`, `4.6`, `5.2`, `7`
  - `TASKS.md` `T014`, `T015`, `T021`, `T023`

3. Hint button persists snapshot + hint request + tutor response
- Source:
  - `RESEARCH.md` section `3` and `Refined Core Product Loop`
  - `SPEC.md` sections `4.6`, `6.1`, `6.2`, `7`
  - `TASKS.md` `T013`, `T020`, `T023`

4. Side-thread submit invokes tutor only when explicitly requested
- Source:
  - `RESEARCH.md` section `3`
  - `SPEC.md` section `4.5`
  - `TASKS.md` `T014`, `T021`, `T023`

5. Multiple side threads remain isolated
- Source:
  - `RESEARCH.md` section `2. Parallel side conversations are a core feature`
  - `SPEC.md` sections `3`, `4.4`, `5.1`, `7`
  - `TASKS.md` `T010`, `T019`, `T023`

6. No background or periodic tutor invocation exists
- Source:
  - `RESEARCH.md` section `3`
  - `SPEC.md` sections `1`, `5.2`, `7`
  - `TASKS.md` `T015`, `T023`

7. Tutor responses remain nudges, not full solutions
- Source:
  - `RESEARCH.md` sections `Refined Core Product Loop`, `Updated MVP Requirements`
  - `SPEC.md` section `6.2 Output guardrails`
  - `TASKS.md` `T011`, `T012`, `T013`, `T015`

8. Workspace aggregate endpoint returns correct initial state
- Source:
  - `SPEC.md` sections `4.2`, `5.1`, `5.2`
  - `TASKS.md` `T008`, `T017`, `T023`

## 3. Test Environment and Instrumentation

## 3.1 Required Fixtures

- `db_session` fixture: clean SQLite DB per test (transaction rollback or temp file).
- `api_client` fixture: FastAPI test client.
- `fake_tutor_adapter` fixture: deterministic output and `call_count` + captured payloads.
- `seeded_session` fixture: session, optionally with one active task context.
- `seeded_threads` fixture: two or more threads in same session.

## 3.2 Common Assertions

- Tutor invocation assertion:
  - `fake_tutor_adapter.call_count == expected`
- Persistence assertions:
  - snapshot record exists with expected `source`
  - hint request record exists and links expected `snapshot_id`/`thread_id`
  - tutor response exists and links expected `hint_request_id`
- Error assertion format:
  - response body matches `SPEC.md` section `4.7 Error Contract`

## 4. API Tests

## 4.1 Sessions and Context

### API-001 `POST /api/v1/sessions` creates session without requiring task context
- Type: API
- Trace:
  - `SPEC.md` `4.1`, `5.2`
  - `TASKS.md` `T007`, `T018`
- Steps:
  1. POST session without `task_context`.
- Expected pass condition:
  - `201` with `session_id` and `workspace_url`.
  - session row created.
  - no active task context yet.

### API-002 `POST /sessions/{session_id}/task-context` creates initial active context
- Type: API
- Trace:
  - `SPEC.md` `4.1`, `5.2`
  - `TASKS.md` `T007`, `T018`
- Steps:
  1. Create a session.
  2. POST valid task context payload to `/sessions/{session_id}/task-context`.
- Expected pass condition:
  - `201` with `task_context_id`.
  - DB contains one active task context linked to session.

### API-002B `PUT /sessions/{session_id}/task-context` creates new active version
- Type: API
- Trace:
  - `SPEC.md` `4.1`, `4.2`, `5.2`, `7`
  - `TASKS.md` `T007`, `T008`, `T018`, `T023`
- Steps:
  1. Create session.
  2. Create initial task context.
  3. PUT updated task context.
- Expected pass condition:
  - `200` with new active `task_context_id`.
  - prior context is inactive.
  - new context is active.
  - workspace history includes both versions.

## 4.2 Workspace Aggregate

### API-003 `GET /api/v1/sessions/{id}/workspace` returns complete initial model
- Type: API
- Trace:
  - `SPEC.md` `4.2`, `5.1`
  - `TASKS.md` `T008`
- Steps:
  1. Seed session + context with no snapshots and no threads.
  2. GET workspace endpoint.
- Expected pass condition:
  - `200` with keys: `session`, `task_context`, `task_context_history`, `latest_snapshot`, `threads`, `active_thread_id`.
  - `latest_snapshot` is `null` and `threads` is empty list.

### API-004 Workspace aggregate returns latest snapshot only
- Type: API
- Trace:
  - `SPEC.md` `4.2`
  - `TASKS.md` `T008`, `T009`
- Steps:
  1. Create two snapshots in same session with increasing timestamps.
  2. GET workspace endpoint.
- Expected pass condition:
  - `latest_snapshot.id` equals most recent snapshot id.

## 4.3 Snapshot Endpoint

### API-005 `POST /snapshots` persists snapshot with valid `source`
- Type: API
- Trace:
  - `SPEC.md` `4.3`
  - `TASKS.md` `T009`
- Steps:
  1. POST snapshot with `source=manual_save`.
- Expected pass condition:
  - `201` and snapshot row persisted with same content/cursor/source.

### API-006 `POST /snapshots` rejects unknown `source`
- Type: Negative/API
- Trace:
  - `SPEC.md` `3.2 code_snapshots.source enum`
  - `TASKS.md` `T006`, `T009`
- Steps:
  1. POST snapshot with `source=auto_tick`.
- Expected pass condition:
  - validation error, no DB insert.

## 4.4 Thread APIs

### API-007 Thread create/list supports parallel threads
- Type: API
- Trace:
  - `RESEARCH.md` section `2`
  - `SPEC.md` `4.4`, `7`
  - `TASKS.md` `T010`, `T019`
- Steps:
  1. Create two threads (`concept`, `planning`) for same session.
  2. List session threads.
- Expected pass condition:
  - both thread IDs present, correct thread types/titles.

### API-008 Message list is thread-scoped and ordered
- Type: API
- Trace:
  - `SPEC.md` `4.4 GET /threads/{thread_id}/messages`
  - `TASKS.md` `T010`, `T019`
- Steps:
  1. Create thread A and B.
  2. Insert messages interleaved by time across A/B.
  3. GET messages for A.
- Expected pass condition:
  - response includes only A messages in chronological order.

## 4.5 Side-Thread Submit

### API-009 `POST /threads/{thread_id}/messages` stores message without tutor when `invoke_tutor=false`
- Type: API/Guardrail
- Trace:
  - `SPEC.md` `4.5 Behavior`
  - `TASKS.md` `T014`, `T015`
- Steps:
  1. POST message with `invoke_tutor=false`.
- Expected pass condition:
  - `201`, `tutor_invoked=false`, `hint_request_id=null`, `assistant_message_id=null`.
  - user message persisted.
  - `fake_tutor_adapter.call_count` unchanged.

### API-010 `POST /threads/{thread_id}/messages` invokes tutor when `invoke_tutor=true`
- Type: API
- Trace:
  - `SPEC.md` `4.5`
  - `TASKS.md` `T014`, `T021`
- Steps:
  1. POST message with `invoke_tutor=true` and editor snapshot.
- Expected pass condition:
  - `201`, `tutor_invoked=true`, non-null hint and assistant IDs.
  - user message + hint request + tutor response persisted.
  - hint request `request_type=next_step`.

### API-011 Side-thread submit with `invoke_tutor=true` fails when context missing
- Type: Negative/API
- Trace:
  - `RESEARCH.md` section `1`
  - `SPEC.md` `4.6 Validation`, `4.7`
- Steps:
  1. Seed session without any active task context.
  2. Submit thread message with `invoke_tutor=true`.
- Expected pass condition:
  - `409` with `TASK_CONTEXT_REQUIRED` error payload.
  - user message persistence behavior follows chosen contract and is explicitly asserted.
  - no tutor call.

## 4.6 Hint Button Endpoint

### API-012 `POST /hint-requests` persists snapshot, hint request, tutor response
- Type: API
- Trace:
  - `RESEARCH.MD` section `3` and `Refined Core Product Loop`
  - `SPEC.md` `4.6`, `7`
  - `TASKS.md` `T013`, `T020`
- Steps:
  1. POST hint request with inline `editor_snapshot` and `request_type=stuck`.
- Expected pass condition:
  - `201` with `hint_request_id` and `tutor_response` object.
  - snapshot persisted with `source=hint_trigger`.
  - hint request links to snapshot/task context.
  - tutor response persisted with non-empty `summary_of_progress` and `next_step_nudge`.

### API-013 `POST /hint-requests` returns `409 TASK_CONTEXT_REQUIRED` without context
- Type: Negative/API
- Trace:
  - `SPEC.md` `4.6 Validation`, `4.7`
  - `TASKS.md` `T013`, `T018`
- Steps:
  1. POST hint request on session lacking any active task context.
- Expected pass condition:
  - `409` with exact `TASK_CONTEXT_REQUIRED` code/message semantics.
  - no snapshot/hint/tutor rows created.

### API-014 `request_type` enum enforcement
- Type: Negative/API
- Trace:
  - `SPEC.md` `3.2 hint_requests.request_type enum`
  - `TASKS.md` `T006`, `T013`
- Steps:
  1. POST hint request with unsupported `request_type=explain_everything`.
- Expected pass condition:
  - validation error; no tutor call.

## 5. Service and Unit Tests

## 5.1 Trigger Policy

### UNIT-001 `is_explicit_trigger` accepts only allowed events
- Type: Unit/Guardrail
- Trace:
  - `SPEC.md` `1`, `7`
  - `TASKS.md` `T015`
- Steps:
  1. Evaluate policy with known events (`hint_button`, `thread_submit_invoke_true`).
  2. Evaluate with unknown events (`autosave`, `interval_tick`, `editor_change`).
- Expected pass condition:
  - policy returns true only for explicit allowed events.
  - unknown events rejected (fail closed).

### UNIT-002 Hint service invokes tutor only after explicit trigger and context check
- Type: Unit/Guardrail
- Trace:
  - `RESEARCH.MD` sections `1`, `3`
  - `TASKS.md` `T013`, `T015`
- Steps:
  1. Call hint service with valid context and explicit event.
  2. Call with missing context.
- Expected pass condition:
  - first call invokes tutor once.
  - second call raises/returns context-required error and no tutor call.

### UNIT-003 Message service with `invoke_tutor=false` remains chat-only
- Type: Unit/Guardrail
- Trace:
  - `SPEC.md` `4.5 Behavior`
  - `TASKS.md` `T014`, `T015`
- Steps:
  1. Call message service with `invoke_tutor=false`.
- Expected pass condition:
  - user message persisted.
  - no hint request/tutor response created.

## 5.2 Payload and Response Semantics

### UNIT-004 Payload builder includes required context blocks
- Type: Unit
- Trace:
  - `RESEARCH.md` section `1` system implication
  - `SPEC.md` `6.1`
  - `TASKS.md` `T012`
- Steps:
  1. Build payload from seeded context/snapshot/thread.
- Expected pass condition:
  - payload contains `event`, `session`, `task_context`, `editor_state`, `thread_context`, `policy`.
  - `policy.pedagogy == nudge_not_solution`.

### UNIT-004B Payload builder uses latest active task context
- Type: Unit
- Trace:
  - `SPEC.md` `4.1`, `6.1`, `7`
  - `TASKS.md` `T012`, `T023`
- Steps:
  1. Seed two task context versions for one session, only latest active.
  2. Build tutor payload.
- Expected pass condition:
  - payload includes latest active task context only.
  - inactive prior context is not used as active context.

### UNIT-005 Payload builder scopes thread context to active/selected thread
- Type: Unit
- Trace:
  - `RESEARCH.MD` section `2` system implication
  - `SPEC.md` `6.1 thread_context`
  - `TASKS.md` `T012`, `T019`
- Steps:
  1. Seed two threads with distinct histories.
  2. Build payload for thread A.
- Expected pass condition:
  - payload includes recent messages from A only, none from B.

### UNIT-006 Tutor output schema and nudge guardrails
- Type: Unit/Guardrail
- Trace:
  - `RESEARCH.MD` `Updated MVP Requirements`
  - `SPEC.md` `6.2` output schema and guardrails
  - `TASKS.md` `T011`, `T013`, `T015`
- Steps:
  1. Validate adapter/service output object.
- Expected pass condition:
  - contains `summary_of_progress`, `next_step_nudge`.
  - if `safety.gave_full_solution=true`, response is rejected/sanitized per policy.

## 6. UI Interaction Tests

Use browser E2E (Playwright preferred) and run against fake tutor adapter.

### UI-001 First load without context enters `context_required` mode
- Type: UI
- Trace:
  - `SPEC.md` `5.1`, `5.2`
  - `TASKS.md` `T017`, `T018`
- Steps:
  1. Open workspace for session with no context.
- Expected pass condition:
  - context panel visible.
  - hint button disabled.
  - tutor-invoking submit control disabled.

### UI-002 Saving first context transitions UI to `ready`
- Type: UI
- Trace:
  - `SPEC.md` `5.1 ui.mode`
  - `TASKS.md` `T018`
- Steps:
  1. Fill and submit context form.
- Expected pass condition:
  - mode changes to `ready`.
  - tutor trigger controls enabled.

### UI-002B Updating context keeps UI ready and switches active context
- Type: UI
- Trace:
  - `SPEC.md` `5.1`, `5.2`, `7`
  - `TASKS.md` `T018`, `T023`
- Steps:
  1. Load workspace with existing active context.
  2. Edit and save updated context.
  3. Trigger tutor action afterward.
- Expected pass condition:
  - UI remains in `ready` mode.
  - latest context is shown as active.
  - subsequent tutor call uses updated context.

### UI-003 Hint button flow persists and renders tutor response card
- Type: UI/E2E
- Trace:
  - `RESEARCH.MD` `Refined Core Product Loop`
  - `SPEC.md` `5.2` hint interaction rule
  - `TASKS.md` `T020`
- Steps:
  1. Enter code in editor.
  2. Click `Hint / I'm getting stuck`.
- Expected pass condition:
  - UI enters `requesting_tutor` then returns `ready`.
  - response card appears in active/default hinting thread.
  - backend records snapshot + hint request + tutor response.

### UI-004 Side-thread submit without tutor stays chat-only
- Type: UI/E2E
- Trace:
  - `SPEC.md` `4.5`, `5.2`
  - `TASKS.md` `T021`
- Steps:
  1. In active thread, disable `Ask tutor` toggle.
  2. Submit message.
- Expected pass condition:
  - user message appears.
  - no assistant tutor response appears.
  - backend `tutor_invoked=false`.

### UI-005 Side-thread submit with tutor renders assistant response
- Type: UI/E2E
- Trace:
  - `SPEC.md` `4.5`, `5.2`
  - `TASKS.md` `T021`
- Steps:
  1. Enable `Ask tutor` toggle.
  2. Submit message.
- Expected pass condition:
  - user message and assistant response both render.
  - backend `tutor_invoked=true` with non-null IDs.

### UI-006 Multiple threads remain isolated in UI state and rendering
- Type: UI/E2E
- Trace:
  - `RESEARCH.MD` section `2`
  - `SPEC.md` `5.1 threads.byId/order/activeThreadId`
  - `TASKS.md` `T019`
- Steps:
  1. Create thread A and B.
  2. Send messages in A, switch to B, send different messages.
  3. Return to A.
- Expected pass condition:
  - each thread shows only its own history.
  - active thread switching does not leak content.

## 7. Guardrail Tests

### GR-001 No polling/interval tutor invocation path in frontend
- Type: Guardrail (static + runtime)
- Trace:
  - `RESEARCH.MD` section `3`
  - `SPEC.md` `5.2 No polling-based tutor calls`
  - `TASKS.md` `T015`
- Steps:
  1. Static grep for `setInterval`, polling loops, or auto tutor call hooks in `workspace.js`.
  2. Run UI idle for fixed window (for example 30s) without actions.
- Expected pass condition:
  - no periodic tutor API calls observed.

### GR-002 Unknown event source cannot invoke tutor
- Type: Guardrail/Unit
- Trace:
  - `TASKS.md` `T015 fail closed`
  - `SPEC.md` `1`, `7`
- Steps:
  1. Call policy/service with fabricated trigger source.
- Expected pass condition:
  - request rejected or treated as non-invoking; tutor call count unchanged.

### GR-003 Tutor-only endpoints are explicit action endpoints
- Type: Guardrail/API
- Trace:
  - `SPEC.md` `4.5`, `4.6`
  - `TASKS.md` `T013`, `T014`, `T015`
- Steps:
  1. Inspect registered routes.
- Expected pass condition:
  - tutor invocation is reachable only through `POST /hint-requests` and `POST /threads/{thread_id}/messages` with `invoke_tutor=true` behavior.

### GR-004 Pedagogy guardrail blocks full-solution output
- Type: Guardrail/Unit
- Trace:
  - `RESEARCH.MD` `response style focused on nudging, not solving`
  - `SPEC.md` `6.2 Output guardrails`
- Steps:
  1. Feed service a fake adapter response flagged as full solution.
- Expected pass condition:
  - service rejects/sanitizes and does not persist unsafe tutor response unchanged.

## 8. Negative Cases

### NEG-001 Invalid `thread_type` rejected
- Type: Negative/API
- Trace:
  - `SPEC.md` `3.2 conversation_threads.thread_type enum`
  - `TASKS.md` `T006`, `T010`
- Steps:
  1. Create thread with `thread_type=offtopic`.
- Expected pass condition:
  - validation error; no thread created.

### NEG-002 Missing message content rejected
- Type: Negative/API
- Trace:
  - `SPEC.md` `4.5 request requires content`
  - `TASKS.md` `T006`, `T014`
- Steps:
  1. Submit thread message with empty or absent `content`.
- Expected pass condition:
  - validation error and no tutor call.

### NEG-003 Hint request with malformed editor snapshot rejected
- Type: Negative/API
- Trace:
  - `SPEC.md` `4.6 request schema`
  - `TASKS.md` `T006`, `T013`
- Steps:
  1. Send `editor_snapshot` missing required `content`.
- Expected pass condition:
  - validation error; no snapshot/hint/tutor persistence.

### NEG-004 Workspace endpoint with unknown session id returns not found
- Type: Negative/API
- Trace:
  - `SPEC.md` `4.2`
  - `TASKS.md` `T008`
- Steps:
  1. GET workspace for non-existent session.
- Expected pass condition:
  - `404` with standard error envelope.

### NEG-005 DB or tutor adapter exception returns safe error and preserves consistency
- Type: Negative/Service/API
- Trace:
  - `TASKS.md` `T022 Error Handling + UX Feedback`
- Steps:
  1. Force adapter exception during hint request.
- Expected pass condition:
  - non-2xx standardized error.
  - no partial persistence (or explicit transactional contract verified).

## 9. Suggested Test File Layout

- `tests/api/test_sessions_api.py`
  - `API-001`, `API-002`, `API-002B`
- `tests/api/test_workspace_api.py`
  - `API-003`, `API-004`, `NEG-004`
- `tests/api/test_snapshots_api.py`
  - `API-005`, `API-006`
- `tests/api/test_threads_api.py`
  - `API-007`, `API-008`, `NEG-001`
- `tests/api/test_messages_api.py`
  - `API-009`, `API-010`, `API-011`, `NEG-002`
- `tests/api/test_hints_api.py`
  - `API-012`, `API-013`, `API-014`, `NEG-003`, `NEG-005`
- `tests/unit/test_trigger_policy.py`
  - `UNIT-001`, `GR-002`
- `tests/unit/test_hint_service.py`
  - `UNIT-002`, `GR-004`
- `tests/unit/test_message_service.py`
  - `UNIT-003`
- `tests/unit/test_payload_builder.py`
  - `UNIT-004`, `UNIT-004B`, `UNIT-005`, `UNIT-006`
- `tests/ui/test_workspace_interactions.spec.ts`
  - `UI-001` through `UI-006`, `UI-002B`, `GR-001`
- `tests/guardrails/test_invocation_surface.py`
  - `GR-003`

## 10. Exit Criteria

MVP test plan is satisfied when:
1. All tests in sections 4-8 are implemented and passing.
2. Every core behavior in section 2 is covered by at least one API test, one service/unit or guardrail test, and one UI test where applicable.
3. No test indicates any tutor invocation from non-explicit events.
