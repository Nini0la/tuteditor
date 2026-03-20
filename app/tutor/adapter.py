from __future__ import annotations

from typing import Any, Protocol


class TutorAdapter(Protocol):
    def generate_nudge(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...
