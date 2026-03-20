from __future__ import annotations

from typing import Any


def build_payload(
    *,
    event_type: str,
    request_type: str,
    session_id: str,
    thread_id: str | None,
    task_context: dict[str, Any],
    snapshot: dict[str, Any],
    thread: dict[str, Any] | None,
    recent_messages: list[dict[str, Any]],
    timestamp: str,
) -> dict[str, Any]:
    return {
        "event": {
            "event_type": event_type,
            "request_type": request_type,
            "timestamp": timestamp,
        },
        "session": {
            "session_id": session_id,
            "thread_id": thread_id,
        },
        "task_context": {
            "title": task_context["title"],
            "description": task_context["description"],
            "language": task_context["language"],
            "desired_help_style": task_context["desired_help_style"],
        },
        "editor_state": {
            "snapshot_id": snapshot["id"],
            "content": snapshot["content"],
            "cursor_line": snapshot.get("cursor_line"),
            "cursor_col": snapshot.get("cursor_col"),
            "recent_edits": [],
        },
        "thread_context": {
            "thread_type": (thread or {}).get("thread_type", "general"),
            "recent_messages": [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in recent_messages
            ],
        },
        "policy": {
            "pedagogy": "nudge_not_solution",
            "max_response_tokens": 300,
        },
    }
