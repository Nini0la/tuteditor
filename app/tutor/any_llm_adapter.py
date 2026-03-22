from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.tutor.adapter import TutorAdapterError
from app.tutor.types import TutorOutput

SYSTEM_PROMPT = """You are TutEditor, a coding tutor.
Return only JSON (no markdown) with keys:
- summary_of_progress (string)
- next_step_nudge (string)
- assumption_to_check (string or null)
- confidence (number or null)
- safety: { "gave_full_solution": boolean }

Rules:
- Keep feedback short and actionable.
- Ground feedback in the provided task context and editor state.
- Do not give full final code or full end-to-end solutions.
- If uncertain, provide a cautious nudge and mark lower confidence.
"""


def _call_any_llm_completion(**kwargs: Any) -> Any:
    try:
        from any_llm import completion
    except Exception as exc:  # pragma: no cover - import errors depend on runtime environment
        raise TutorAdapterError(
            "any-llm-sdk is not available. Install it and configure provider credentials."
        ) from exc
    return completion(**kwargs)


def _extract_content(response: Any) -> str:
    try:
        message = response.choices[0].message
    except Exception as exc:
        raise TutorAdapterError("AnyLLM response is missing choices[0].message.") from exc

    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
                    continue
                nested_text = item.get("content")
                if isinstance(nested_text, str):
                    chunks.append(nested_text)
                    continue
            text_attr = getattr(item, "text", None)
            if isinstance(text_attr, str):
                chunks.append(text_attr)
                continue
            content_attr = getattr(item, "content", None)
            if isinstance(content_attr, str):
                chunks.append(content_attr)
        merged = "".join(chunks).strip()
        if merged:
            return merged

    raise TutorAdapterError("AnyLLM response did not include textual content.")


def _parse_json_object(raw_text: str) -> dict[str, Any]:
    candidate = raw_text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end <= start:
            raise TutorAdapterError("AnyLLM response was not valid JSON.") from None
        try:
            parsed = json.loads(candidate[start : end + 1])
        except json.JSONDecodeError as exc:
            raise TutorAdapterError("AnyLLM response was not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise TutorAdapterError("AnyLLM response must be a JSON object.")
    return parsed


def _as_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (float, int)):
        return float(value)
    return None


@dataclass(frozen=True)
class AnyLLMAdapter:
    provider: str
    model: str
    max_tokens: int = 300
    temperature: float = 0.2
    api_key: str | None = None
    api_base: str | None = None

    def generate_nudge(self, payload: dict[str, Any]) -> TutorOutput:
        request_content = (
            "Generate a tutoring nudge from this payload.\n"
            "Respond with JSON only.\n\n"
            f"{json.dumps(payload, ensure_ascii=True)}"
        )

        kwargs: dict[str, Any] = {
            "provider": self.provider,
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request_content},
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base

        try:
            response = _call_any_llm_completion(**kwargs)
        except Exception as exc:
            if isinstance(exc, TutorAdapterError):
                raise
            raise TutorAdapterError(
                f"AnyLLM provider request failed (provider={self.provider}, model={self.model}): {exc}"
            ) from exc

        raw_text = _extract_content(response)
        parsed = _parse_json_object(raw_text)

        summary = parsed.get("summary_of_progress")
        nudge = parsed.get("next_step_nudge")
        if not isinstance(summary, str) or not summary.strip():
            raise TutorAdapterError("AnyLLM response is missing summary_of_progress.")
        if not isinstance(nudge, str) or not nudge.strip():
            raise TutorAdapterError("AnyLLM response is missing next_step_nudge.")

        assumption = parsed.get("assumption_to_check")
        if assumption is not None and not isinstance(assumption, str):
            assumption = str(assumption)

        safety = parsed.get("safety")
        gave_full_solution = False
        if isinstance(safety, dict) and isinstance(safety.get("gave_full_solution"), bool):
            gave_full_solution = safety["gave_full_solution"]

        return {
            "summary_of_progress": summary,
            "next_step_nudge": nudge,
            "assumption_to_check": assumption,
            "confidence": _as_optional_float(parsed.get("confidence")),
            "safety": {"gave_full_solution": gave_full_solution},
            "raw_payload": {
                "provider": self.provider,
                "model": self.model,
                "request_payload": payload,
                "response_text": raw_text,
            },
        }
