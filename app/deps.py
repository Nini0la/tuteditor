from __future__ import annotations

from app.store import InMemoryStore
from app.tutor.fake_adapter import FakeTutorAdapter

_store = InMemoryStore()
_tutor_adapter = FakeTutorAdapter()


def get_store() -> InMemoryStore:
    return _store


def get_tutor_adapter() -> FakeTutorAdapter:
    return _tutor_adapter
