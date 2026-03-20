from __future__ import annotations

from app.store import InMemoryStore


def get_workspace(store: InMemoryStore, session_id: str) -> dict:
    return store.get_workspace_model(session_id)
