from __future__ import annotations

from types import SimpleNamespace

import pytest

import app.tutor.any_llm_adapter as any_llm_adapter_module
from app.tutor.adapter import TutorAdapterError
from app.tutor.any_llm_adapter import AnyLLMAdapter


def _response(content: str):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_any_llm_adapter_parses_json_response(monkeypatch):
    adapter = AnyLLMAdapter(provider="openai", model="gpt-4.1-mini")

    def fake_completion(**kwargs):
        assert kwargs["provider"] == "openai"
        assert kwargs["model"] == "gpt-4.1-mini"
        return _response(
            '{"summary_of_progress":"You set up the loop.","next_step_nudge":"Check the exit condition before updating pointers.","assumption_to_check":"Verify low/high bounds.","confidence":0.62,"safety":{"gave_full_solution":false}}'
        )

    monkeypatch.setattr(any_llm_adapter_module, "_call_any_llm_completion", fake_completion)

    output = adapter.generate_nudge({"event": {"request_type": "stuck"}})

    assert output["summary_of_progress"] == "You set up the loop."
    assert output["next_step_nudge"] == "Check the exit condition before updating pointers."
    assert output["assumption_to_check"] == "Verify low/high bounds."
    assert output["confidence"] == 0.62
    assert output["safety"]["gave_full_solution"] is False


def test_any_llm_adapter_wraps_provider_failure(monkeypatch):
    adapter = AnyLLMAdapter(provider="openai", model="gpt-4.1-mini")

    def fake_completion(**kwargs):
        raise RuntimeError("simulated upstream outage")

    monkeypatch.setattr(any_llm_adapter_module, "_call_any_llm_completion", fake_completion)

    with pytest.raises(TutorAdapterError, match="provider=openai"):
        adapter.generate_nudge({"event": {"request_type": "stuck"}})


def test_any_llm_adapter_rejects_non_json_output(monkeypatch):
    adapter = AnyLLMAdapter(provider="openai", model="gpt-4.1-mini")

    monkeypatch.setattr(
        any_llm_adapter_module,
        "_call_any_llm_completion",
        lambda **kwargs: _response("This is not JSON"),
    )

    with pytest.raises(TutorAdapterError, match="valid JSON"):
        adapter.generate_nudge({"event": {"request_type": "stuck"}})
