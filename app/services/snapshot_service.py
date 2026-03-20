from __future__ import annotations

from app.store import InMemoryStore


def create_snapshot(store: InMemoryStore, session_id: str, payload: dict) -> dict:
    return store.create_snapshot(session_id, payload)
