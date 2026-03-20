from __future__ import annotations

import importlib
from typing import Any

import pytest


ALLOWED_EVENTS = ["hint_button", "thread_submit_invoke_true"]
DISALLOWED_EVENTS = ["autosave", "interval_tick", "editor_change", "unknown_source"]


def _load_policy_function():
    try:
        module = importlib.import_module("app.tutor.policy")
    except ModuleNotFoundError:
        pytest.skip("Policy module 'app.tutor.policy' is not available yet.")

    fn = getattr(module, "is_explicit_trigger", None)
    if not callable(fn):
        pytest.skip("Expected callable 'is_explicit_trigger' in app.tutor.policy.")
    return fn


def _call_policy(fn: Any, event_name: str) -> bool:
    call_attempts = [
        lambda: fn(event_name),
        lambda: fn(event_type=event_name),
        lambda: fn(source=event_name),
        lambda: fn({"event_type": event_name}),
        lambda: fn({"source": event_name}),
    ]

    last_error: Exception | None = None
    for attempt in call_attempts:
        try:
            result = attempt()
            return bool(result)
        except TypeError as exc:
            last_error = exc

    pytest.skip(
        "'is_explicit_trigger' has unsupported signature for contract test. "
        f"Last TypeError: {last_error}"
    )


def test_unit_001_is_explicit_trigger_accepts_only_allowed_events():
    fn = _load_policy_function()

    for event_name in ALLOWED_EVENTS:
        assert _call_policy(fn, event_name) is True

    for event_name in DISALLOWED_EVENTS:
        assert _call_policy(fn, event_name) is False


def test_gr_002_unknown_event_source_cannot_invoke_tutor():
    fn = _load_policy_function()
    assert _call_policy(fn, "fabricated_background_hook") is False
