from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.services.errors import TASK_CONTEXT_REQUIRED_MESSAGE
from app.store import InMemoryStore, StoreError
from app.tutor.payload_builder import build_payload
from app.tutor.policy import is_explicit_trigger


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_tutor_output(output: dict[str, Any]) -> dict[str, Any]:
    summary = output.get("summary_of_progress")
    nudge = output.get("next_step_nudge")

    if not isinstance(summary, str) or not summary.strip():
        raise StoreError("INVALID_TUTOR_OUTPUT", "Tutor output is missing summary_of_progress.", 422)
    if not isinstance(nudge, str) or not nudge.strip():
        raise StoreError("INVALID_TUTOR_OUTPUT", "Tutor output is missing next_step_nudge.", 422)

    safety = output.get("safety")
    if isinstance(safety, dict) and safety.get("gave_full_solution") is True:
        raise StoreError("UNSAFE_TUTOR_OUTPUT", "Tutor output violated nudge-only policy.", 422)

    return {
        "summary_of_progress": summary,
        "next_step_nudge": nudge,
        "assumption_to_check": output.get("assumption_to_check"),
        "confidence": output.get("confidence"),
        "raw_payload": output.get("raw_payload"),
    }


def submit_message(
    *,
    store: InMemoryStore,
    tutor_adapter: Any,
    thread_id: str,
    content: str,
    invoke_tutor: bool,
    editor_snapshot: dict[str, Any] | None,
) -> dict[str, Any]:
    thread = store.get_thread(thread_id)
    session_id = thread["session_id"]

    user_message = store.create_message(thread_id, role="user", content=content)

    if not invoke_tutor:
        return {
            "message_id": user_message["id"],
            "tutor_invoked": False,
            "hint_request_id": None,
            "assistant_message_id": None,
        }

    if not is_explicit_trigger("thread_submit_invoke_true"):
        raise StoreError("INVALID_TRIGGER_SOURCE", "Unknown tutor trigger source.", 400)

    task_context = store.get_active_task_context(session_id)
    if task_context is None:
        raise StoreError("TASK_CONTEXT_REQUIRED", TASK_CONTEXT_REQUIRED_MESSAGE, 409)

    if editor_snapshot is None:
        raise StoreError("EDITOR_SNAPSHOT_REQUIRED", "editor_snapshot is required when invoke_tutor=true.", 422)

    snapshot = store.create_snapshot(
        session_id,
        {
            "content": editor_snapshot["content"],
            "cursor_line": editor_snapshot.get("cursor_line"),
            "cursor_col": editor_snapshot.get("cursor_col"),
            "selection_start": editor_snapshot.get("selection_start"),
            "selection_end": editor_snapshot.get("selection_end"),
            "source": "thread_submit",
        },
    )

    recent_messages = store.list_messages(thread_id)

    payload = build_payload(
        event_type="thread_submit_invoke_true",
        request_type="next_step",
        session_id=session_id,
        thread_id=thread_id,
        task_context=task_context,
        snapshot=snapshot,
        thread=thread,
        recent_messages=recent_messages,
        timestamp=_now(),
    )

    try:
        tutor_raw = tutor_adapter.generate_nudge(payload)
    except Exception as exc:  # pragma: no cover
        raise StoreError("TUTOR_ADAPTER_ERROR", str(exc), 502) from exc

    validated = _validate_tutor_output(tutor_raw)

    hint_request = store.create_hint_request(
        session_id=session_id,
        task_context_id=task_context["id"],
        snapshot_id=snapshot["id"],
        thread_id=thread_id,
        request_type="next_step",
        triggering_message=content,
    )
    store.create_tutor_response(hint_request_id=hint_request["id"], payload=validated)

    assistant_content = f"{validated['summary_of_progress']}\n{validated['next_step_nudge']}"
    assistant_message = store.create_message(
        thread_id,
        role="assistant",
        content=assistant_content,
        triggered_tutor=True,
        hint_request_id=hint_request["id"],
    )

    return {
        "message_id": user_message["id"],
        "tutor_invoked": True,
        "hint_request_id": hint_request["id"],
        "assistant_message_id": assistant_message["id"],
    }
