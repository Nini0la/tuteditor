from __future__ import annotations

from app.store import InMemoryStore


def create_thread(store: InMemoryStore, session_id: str, payload: dict) -> dict:
    return store.create_thread(session_id, payload)


def list_threads(store: InMemoryStore, session_id: str) -> list[dict]:
    return store.list_threads(session_id)


def list_messages(store: InMemoryStore, thread_id: str) -> list[dict]:
    return store.list_messages(thread_id)
