# TutEditor MVP Specification

## 1. Scope
MVP delivers one web workspace page where users:
- create a session,
- provide task context before requesting tutoring,
- edit code,
- use parallel side conversations,
- explicitly trigger tutoring via:
  - `Hint / I'm getting stuck`, or
  - side-thread message submit.

Tutor inference is event-driven only. No continuous monitoring.

## 2. System Overview
- Client: Single workspace page (`/workspace/{session_id}`), JS-driven UI state.
- API: FastAPI JSON endpoints.
- DB: SQLite (MVP) with migration support.
- Tutor service: Python orchestration layer + model adapter.
- Trigger policy: Tutor calls only from explicit API actions.

## 3. Data Model

## 3.1 Entity Relationship Summary
- `Session` 1:N `TaskContext` (MVP: one active context, editable over time)
- `Session` 1:N `CodeSnapshot`
- `Session` 1:N `ConversationThread`
- `ConversationThread` 1:N `ConversationMessage`
- `Session` 1:N `HintRequest`
- `HintRequest` 1:1 `TutorResponse` (MVP)

## 3.2 Tables

### `sessions`
- `id` (uuid, pk)
- `created_at` (datetime, not null)
- `updated_at` (datetime, not null)
- `status` (text: `active|archived`, default `active`)

### `task_contexts`
- `id` (uuid, pk)
- `session_id` (uuid, fk `sessions.id`, indexed)
- `title` (text, not null)
- `description` (text, not null)
- `language` (text, not null)
- `desired_help_style` (text, not null, default `hint_first`)
- `is_active` (bool, not null, default true)
- `created_at` (datetime, not null)
- `updated_at` (datetime, not null)

### `code_snapshots`
- `id` (uuid, pk)
- `session_id` (uuid, fk `sessions.id`, indexed)
- `content` (text, not null)
- `cursor_line` (int, nullable)
- `cursor_col` (int, nullable)
- `selection_start` (int, nullable)
- `selection_end` (int, nullable)
- `source` (text: `manual_save|hint_trigger|thread_submit`, not null)
- `created_at` (datetime, not null)

### `conversation_threads`
- `id` (uuid, pk)
- `session_id` (uuid, fk `sessions.id`, indexed)
- `title` (text, not null)
- `thread_type` (text, not null, default `general`)
- `linked_task_context_id` (uuid, fk `task_contexts.id`, nullable, usually latest active context)
- `created_at` (datetime, not null)

Allowed `thread_type` (MVP enum):
- `general`
- `hinting`
- `concept`
- `planning`
- `reflection`

### `conversation_messages`
- `id` (uuid, pk)
- `thread_id` (uuid, fk `conversation_threads.id`, indexed)
- `role` (text: `user|assistant|system`, not null)
- `content` (text, not null)
- `created_at` (datetime, not null)
- `triggered_tutor` (bool, default `false`)
- `hint_request_id` (uuid, fk `hint_requests.id`, nullable)

### `hint_requests`
- `id` (uuid, pk)
- `session_id` (uuid, fk `sessions.id`, indexed)
- `task_context_id` (uuid, fk `task_contexts.id`, not null)
- `snapshot_id` (uuid, fk `code_snapshots.id`, not null)
- `thread_id` (uuid, fk `conversation_threads.id`, nullable)
- `triggering_message` (text, nullable)
- `request_type` (text, not null)
- `created_at` (datetime, not null)

Allowed `request_type` (MVP enum):
- `stuck`
- `next_step`
- `review_approach`
- `stronger_hint`

### `tutor_responses`
- `id` (uuid, pk)
- `hint_request_id` (uuid, unique, fk `hint_requests.id`)
- `summary_of_progress` (text, not null)
- `next_step_nudge` (text, not null)
- `assumption_to_check` (text, nullable)
- `confidence` (float, nullable)
- `raw_payload` (json, nullable)
- `created_at` (datetime, not null)

## 4. API Contracts
Base path: `/api/v1`

## 4.1 Session + Task Context

### `POST /sessions`
Create session only.

Request:
```json
{}
```

Response `201`:
```json
{
  "session_id": "uuid",
  "workspace_url": "/workspace/uuid"
}
```

### `POST /sessions/{session_id}/task-context`
Create the first active task context for an existing session.

Request:
```json
{
  "title": "Binary search exercise",
  "description": "Implement iterative binary search over sorted ints",
  "language": "python",
  "desired_help_style": "hint_first"
}
```

Response `201`:
```json
{
  "task_context_id": "uuid"
}
```

Validation:
- session must exist.
- request must include valid task context fields.

### `PUT /sessions/{session_id}/task-context`
Update active context by creating a new task context version and marking prior active context inactive.

Request:
```json
{
  "title": "Add preprocessing to the ML pipeline",
  "description": "Continue from previous pipeline and now add scaling + split",
  "language": "python",
  "desired_help_style": "hint_first"
}
```

Behavior:
- prior active task context becomes `is_active=false`
- new task context becomes `is_active=true`
- tutor uses latest active context only

Response `200`: new active task context object.

## 4.2 Workspace State

### `GET /sessions/{session_id}/workspace`
Fetch aggregate workspace model for initial page load.

Response `200`:
```json
{
  "session": {"id": "uuid", "status": "active"},
  "task_context": {...},
  "task_context_history": [...],
  "latest_snapshot": {...},
  "threads": [...],
  "active_thread_id": "uuid|null"
}
```

## 4.3 Editor Snapshot

### `POST /sessions/{session_id}/snapshots`
Persist current editor state.

Request:
```json
{
  "content": "def binary_search(...):\n    ...",
  "cursor_line": 12,
  "cursor_col": 8,
  "selection_start": null,
  "selection_end": null,
  "source": "manual_save"
}
```

Response `201`:
```json
{
  "snapshot_id": "uuid",
  "created_at": "2026-03-19T18:30:00Z"
}
```

## 4.4 Conversation Threads

### `POST /sessions/{session_id}/threads`
Create side thread.

Request:
```json
{
  "title": "Loop reasoning",
  "thread_type": "concept"
}
```

Response `201`: thread object.

### `GET /sessions/{session_id}/threads`
List threads with latest message preview.

### `GET /threads/{thread_id}/messages`
List thread messages in chronological order.

## 4.5 Side-Thread Submit (Explicit Tutor Trigger Path)

### `POST /threads/{thread_id}/messages`
Submit user message; optionally invoke tutor.

Request:
```json
{
  "content": "What logical step am I missing?",
  "invoke_tutor": true,
  "editor_snapshot": {
    "content": "def train(...):\n    ...",
    "cursor_line": 42,
    "cursor_col": 5
  }
}
```

Behavior:
- Always stores user message.
- If `invoke_tutor=true`, creates `HintRequest` with `request_type=next_step` and calls tutor.
- If `invoke_tutor=false`, no tutor call.

Response `201`:
```json
{
  "message_id": "uuid",
  "tutor_invoked": true,
  "hint_request_id": "uuid|null",
  "assistant_message_id": "uuid|null"
}
```

## 4.6 Hint Button Trigger (Explicit Tutor Trigger Path)

### `POST /sessions/{session_id}/hint-requests`
Explicit hint trigger from main workspace button.

Request:
```json
{
  "request_type": "stuck",
  "triggering_message": "I can't get base case right",
  "editor_snapshot": {
    "content": "def merge_sort(...):\n    ...",
    "cursor_line": 18,
    "cursor_col": 3
  },
  "thread_id": "uuid|null"
}
```

Response `201`:
```json
{
  "hint_request_id": "uuid",
  "tutor_response": {
    "summary_of_progress": "...",
    "next_step_nudge": "...",
    "assumption_to_check": "..."
  }
}
```

Validation:
- Reject with `409` if session has no active task context.

## 4.7 Error Contract
All non-2xx responses:
```json
{
  "error": {
    "code": "TASK_CONTEXT_REQUIRED",
    "message": "Declare task context before requesting tutoring."
  }
}
```

## 5. UI State Model (Single Workspace Page)

## 5.1 Top-Level State Shape
```ts
type WorkspaceState = {
  session: { id: string; status: "active" | "archived" };
  taskContext: {
    loaded: boolean;
    value: null | {
      id: string;
      title: string;
      description: string;
      language: string;
      desiredHelpStyle: string;
      isActive: boolean;
    };
  };
  editor: {
    content: string;
    cursorLine: number | null;
    cursorCol: number | null;
    dirty: boolean;
    latestSnapshotId: string | null;
  };
  threads: {
    byId: Record<string, Thread>;
    order: string[];
    activeThreadId: string | null;
  };
  tutor: {
    busy: boolean;
    lastHintRequestId: string | null;
    lastError: string | null;
  };
  ui: {
    mode: "context_required" | "ready" | "requesting_tutor";
    panels: { contextOpen: boolean; sidebarOpen: boolean };
  };
};
```

## 5.2 Interaction Rules
- On first load without context:
  - show context form modal/panel,
  - disable hint button and tutor-invoking thread submit.
- Task context can be edited during a session; latest saved version becomes active.
- `Hint / I'm getting stuck`:
  - snapshot editor,
  - call hint-request endpoint,
  - append response card to active thread or default hinting thread.
- Thread message submit:
  - if user selected "Ask tutor" (default true), call message endpoint with `invoke_tutor=true`.
- No polling-based tutor calls.

## 6. Prompt Payload Schema
Used by backend tutor orchestrator for explicit events only.

## 6.1 Input Schema (JSON)
```json
{
  "event": {
    "event_type": "hint_button" ,
    "request_type": "stuck",
    "timestamp": "2026-03-19T18:30:00Z"
  },
  "session": {
    "session_id": "uuid",
    "thread_id": "uuid|null"
  },
  "task_context": {
    "title": "string",
    "description": "string",
    "language": "python",
    "desired_help_style": "hint_first"
  },
  "editor_state": {
    "snapshot_id": "uuid",
    "content": "string",
    "cursor_line": 12,
    "cursor_col": 8,
    "recent_edits": [
      {"kind": "insert", "line": 10, "text": "while low <= high:"}
    ]
  },
  "thread_context": {
    "thread_type": "concept",
    "recent_messages": [
      {"role": "user", "content": "string"},
      {"role": "assistant", "content": "string"}
    ]
  },
  "policy": {
    "pedagogy": "nudge_not_solution",
    "max_response_tokens": 300
  }
}
```

## 6.2 Output Schema (JSON)
```json
{
  "summary_of_progress": "What the user has already done",
  "next_step_nudge": "Small actionable next step, no full solution",
  "assumption_to_check": "Potential misconception or invariant to verify",
  "optional_checks": [
    "Check whether your stopping condition matches your intent",
    "Consider the missing edge case before the next line"
  ],
  "safety": {
    "gave_full_solution": false
  }
}
```

Output guardrails:
- Must not provide full final code.
- Must reference user context/code state.
- Must remain concise and actionable.

## 7. Acceptance Criteria
- User cannot trigger tutor until task context exists.
- Updating task context makes the new version active for subsequent tutor calls.
- Multiple threads can be created and used independently.
- Tutor calls occur only on:
  - hint button request,
  - thread message submit with `invoke_tutor=true`.
- Tutor response is persisted and visible in workspace thread UI.
- No background/interval inference path exists in code.
