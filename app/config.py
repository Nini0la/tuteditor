from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "TutEditor MVP"
    db_path: Path = Path("/tmp/tuteditor_mvp.sqlite3")
    tutor_adapter: str = "fake"
    tutor_any_llm_provider: str = "openai"
    tutor_any_llm_model: str = "gpt-4.1-mini"
    tutor_any_llm_max_tokens: int = 300
    tutor_any_llm_temperature: float = 0.2
    tutor_any_llm_api_key: str | None = None
    tutor_any_llm_api_base: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            db_path=Path(os.getenv("TUTEDITOR_DB_PATH", "/tmp/tuteditor_mvp.sqlite3")),
            tutor_adapter=os.getenv("TUTEDITOR_TUTOR_ADAPTER", "fake").strip().lower(),
            tutor_any_llm_provider=os.getenv("TUTEDITOR_ANY_LLM_PROVIDER", "openai").strip(),
            tutor_any_llm_model=os.getenv("TUTEDITOR_ANY_LLM_MODEL", "gpt-4.1-mini").strip(),
            tutor_any_llm_max_tokens=int(os.getenv("TUTEDITOR_ANY_LLM_MAX_TOKENS", "300")),
            tutor_any_llm_temperature=float(os.getenv("TUTEDITOR_ANY_LLM_TEMPERATURE", "0.2")),
            tutor_any_llm_api_key=os.getenv("TUTEDITOR_ANY_LLM_API_KEY"),
            tutor_any_llm_api_base=os.getenv("TUTEDITOR_ANY_LLM_API_BASE"),
        )


settings = Settings.from_env()
