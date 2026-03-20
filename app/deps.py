from __future__ import annotations

from collections.abc import Generator

from app.db import get_db_session
from app.store import InMemoryStore
from app.tutor.fake_adapter import FakeTutorAdapter
from sqlmodel import Session

_store = InMemoryStore()
_tutor_adapter = FakeTutorAdapter()


def get_store() -> InMemoryStore:
    return _store


def get_tutor_adapter() -> FakeTutorAdapter:
    return _tutor_adapter


def get_db() -> Generator[Session, None, None]:
    yield from get_db_session()
