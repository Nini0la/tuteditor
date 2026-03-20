from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from app.models.session import utcnow


class TaskContext(SQLModel, table=True):
    __tablename__ = "task_contexts"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True, nullable=False)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    language: str = Field(nullable=False)
    desired_help_style: str = Field(default="hint_first", nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
