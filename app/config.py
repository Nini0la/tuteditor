from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "TutEditor MVP"
    db_path: Path = Path("/tmp/tuteditor_mvp.sqlite3")


settings = Settings()
