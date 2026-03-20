from __future__ import annotations

from typing import Any

EXPLICIT_EVENTS = {"hint_button", "thread_submit_invoke_true"}


def is_explicit_trigger(event: Any = None, **kwargs: Any) -> bool:
    value: Any = event
    if value is None:
        value = kwargs.get("event_type") or kwargs.get("source")

    if isinstance(value, dict):
        value = value.get("event_type") or value.get("source")

    if not isinstance(value, str):
        return False

    return value in EXPLICIT_EVENTS
