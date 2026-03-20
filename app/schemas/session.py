from __future__ import annotations

from pydantic import BaseModel

from app.schemas.task_context import TaskContextIn


class SessionCreateIn(BaseModel):
    task_context: TaskContextIn | None = None
