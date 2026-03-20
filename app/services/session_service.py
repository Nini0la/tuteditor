from __future__ import annotations

from typing import Any

from app.store import InMemoryStore


def create_session(store: InMemoryStore, *, task_context_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    session = store.create_session()
    context = None
    if task_context_payload is not None:
        context = store.create_task_context(session["id"], task_context_payload)

    response = {
        "session_id": session["id"],
        "workspace_url": f"/workspace/{session['id']}",
    }
    if context is not None:
        response["task_context_id"] = context["id"]
    return response


def create_task_context(store: InMemoryStore, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return store.create_task_context(session_id, payload)


def update_task_context(store: InMemoryStore, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return store.create_task_context(session_id, payload)
