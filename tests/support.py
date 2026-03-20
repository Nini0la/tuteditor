from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

API_PREFIX = "/api/v1"

DEFAULT_TASK_CONTEXT = {
    "title": "Binary search exercise",
    "description": "Implement iterative binary search over sorted integers.",
    "language": "python",
    "desired_help_style": "hint_first",
}

UPDATED_TASK_CONTEXT = {
    "title": "Binary search with edge cases",
    "description": "Handle empty arrays and duplicate values correctly.",
    "language": "python",
    "desired_help_style": "hint_first",
}

DEFAULT_EDITOR_SNAPSHOT = {
    "content": "def binary_search(nums, target):\n    return -1\n",
    "cursor_line": 2,
    "cursor_col": 11,
}


@dataclass
class TutorSpy:
    call_count: int = 0
    payloads: list[dict[str, Any]] = field(default_factory=list)
    patched: bool = False
    raise_error: Exception | None = None
    output: dict[str, Any] = field(
        default_factory=lambda: {
            "summary_of_progress": "You defined the function signature.",
            "next_step_nudge": "Track low/high pointers and update them each loop.",
            "assumption_to_check": "Check off-by-one handling at loop boundaries.",
            "safety": {"gave_full_solution": False},
        }
    )

    def generate_nudge(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.call_count += 1
        self.payloads.append(payload)
        if self.raise_error is not None:
            raise self.raise_error
        return dict(self.output)

    async def agenerate_nudge(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.generate_nudge(payload)


def extract_task_context_id(payload: dict[str, Any]) -> str | None:
    return payload.get("task_context_id") or payload.get("id")


def extract_thread_id(payload: dict[str, Any]) -> str | None:
    return payload.get("thread_id") or payload.get("id")


def normalize_messages_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        messages = payload.get("messages")
        if isinstance(messages, list):
            return messages
    raise AssertionError(f"Unexpected messages payload shape: {payload!r}")


def assert_error_envelope(payload: dict[str, Any], *, code: str | None = None) -> None:
    assert "error" in payload, payload
    assert isinstance(payload["error"], dict), payload
    assert "code" in payload["error"], payload
    assert "message" in payload["error"], payload
    if code is not None:
        assert payload["error"]["code"] == code, payload
