from __future__ import annotations

from typing import Any


class FakeTutorAdapter:
    def generate_nudge(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_type = payload.get("event", {}).get("request_type", "stuck")
        summary = "You have started structuring your solution."
        next_step = "Focus on one small invariant and verify it with a quick test case."
        if request_type == "next_step":
            next_step = "Identify the immediate next operation and validate it on a tiny input."

        return {
            "summary_of_progress": summary,
            "next_step_nudge": next_step,
            "assumption_to_check": "Confirm your stopping condition matches the intended behavior.",
            "safety": {"gave_full_solution": False},
            "raw_payload": payload,
        }
