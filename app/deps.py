from __future__ import annotations

from collections.abc import Generator

from app.config import settings
from app.db import get_db_session
from app.store import InMemoryStore
from app.tutor.adapter import TutorAdapter
from app.tutor.any_llm_adapter import AnyLLMAdapter
from app.tutor.fake_adapter import FakeTutorAdapter
from sqlmodel import Session

_store = InMemoryStore()


def _build_tutor_adapter() -> TutorAdapter:
    if settings.tutor_adapter == "fake":
        return FakeTutorAdapter()

    if settings.tutor_adapter == "any_llm":
        return AnyLLMAdapter(
            provider=settings.tutor_any_llm_provider,
            model=settings.tutor_any_llm_model,
            max_tokens=settings.tutor_any_llm_max_tokens,
            temperature=settings.tutor_any_llm_temperature,
            api_key=settings.tutor_any_llm_api_key,
            api_base=settings.tutor_any_llm_api_base,
        )

    raise RuntimeError(
        "Unsupported tutor adapter configured via TUTEDITOR_TUTOR_ADAPTER. "
        "Supported values: fake, any_llm."
    )


_tutor_adapter = _build_tutor_adapter()


def get_store() -> InMemoryStore:
    return _store


def get_tutor_adapter() -> TutorAdapter:
    return _tutor_adapter


def get_db() -> Generator[Session, None, None]:
    yield from get_db_session()
