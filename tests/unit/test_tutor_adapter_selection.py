from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.config import Settings
from app.deps import _build_tutor_adapter
from app.tutor.any_llm_adapter import AnyLLMAdapter
from app.tutor.fake_adapter import FakeTutorAdapter


def test_settings_from_env_defaults_to_fake_adapter(monkeypatch):
    monkeypatch.delenv("TUTEDITOR_TUTOR_ADAPTER", raising=False)

    settings = Settings.from_env()

    assert settings.tutor_adapter == "fake"


def test_build_tutor_adapter_selects_fake_adapter(monkeypatch):
    monkeypatch.setattr(
        "app.deps.settings",
        SimpleNamespace(
            tutor_adapter="fake",
            tutor_any_llm_provider="openai",
            tutor_any_llm_model="gpt-4.1-mini",
            tutor_any_llm_max_tokens=300,
            tutor_any_llm_temperature=0.2,
            tutor_any_llm_api_key=None,
            tutor_any_llm_api_base=None,
        ),
    )

    adapter = _build_tutor_adapter()
    assert isinstance(adapter, FakeTutorAdapter)


def test_build_tutor_adapter_selects_any_llm_adapter(monkeypatch):
    monkeypatch.setattr(
        "app.deps.settings",
        SimpleNamespace(
            tutor_adapter="any_llm",
            tutor_any_llm_provider="openai",
            tutor_any_llm_model="gpt-4.1-mini",
            tutor_any_llm_max_tokens=300,
            tutor_any_llm_temperature=0.2,
            tutor_any_llm_api_key=None,
            tutor_any_llm_api_base=None,
        ),
    )

    adapter = _build_tutor_adapter()
    assert isinstance(adapter, AnyLLMAdapter)
    assert adapter.provider == "openai"
    assert adapter.model == "gpt-4.1-mini"


def test_build_tutor_adapter_rejects_unknown_adapter(monkeypatch):
    monkeypatch.setattr(
        "app.deps.settings",
        SimpleNamespace(
            tutor_adapter="unsupported",
            tutor_any_llm_provider="openai",
            tutor_any_llm_model="gpt-4.1-mini",
            tutor_any_llm_max_tokens=300,
            tutor_any_llm_temperature=0.2,
            tutor_any_llm_api_key=None,
            tutor_any_llm_api_base=None,
        ),
    )

    with pytest.raises(RuntimeError, match="Unsupported tutor adapter"):
        _build_tutor_adapter()
