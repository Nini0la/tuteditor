from __future__ import annotations

from typing import Any, TypedDict


class TutorSafety(TypedDict, total=False):
    gave_full_solution: bool


class TutorOutput(TypedDict, total=False):
    summary_of_progress: str
    next_step_nudge: str
    assumption_to_check: str | None
    confidence: float | None
    safety: TutorSafety
    raw_payload: dict[str, Any]
