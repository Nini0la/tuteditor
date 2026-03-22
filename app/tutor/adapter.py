from __future__ import annotations

from typing import Any, Protocol

from app.tutor.types import TutorOutput


class TutorAdapterError(RuntimeError):
    pass


class TutorAdapter(Protocol):
    def generate_nudge(self, payload: dict[str, Any]) -> TutorOutput:
        ...
