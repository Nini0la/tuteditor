from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from app.models.session import utcnow


class CodeSnapshot(SQLModel, table=True):
    __tablename__ = "code_snapshots"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True, nullable=False)
    content: str = Field(nullable=False)
    cursor_line: int | None = Field(default=None)
    cursor_col: int | None = Field(default=None)
    selection_start: int | None = Field(default=None)
    selection_end: int | None = Field(default=None)
    source: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
