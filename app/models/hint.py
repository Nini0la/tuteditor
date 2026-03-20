from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.models.session import utcnow


class HintRequest(SQLModel, table=True):
    __tablename__ = "hint_requests"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True, nullable=False)
    task_context_id: str = Field(foreign_key="task_contexts.id", nullable=False)
    snapshot_id: str = Field(foreign_key="code_snapshots.id", nullable=False)
    thread_id: str | None = Field(default=None, foreign_key="conversation_threads.id")
    triggering_message: str | None = Field(default=None)
    request_type: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class TutorResponse(SQLModel, table=True):
    __tablename__ = "tutor_responses"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    hint_request_id: str = Field(foreign_key="hint_requests.id", unique=True, nullable=False)
    summary_of_progress: str = Field(nullable=False)
    next_step_nudge: str = Field(nullable=False)
    assumption_to_check: str | None = Field(default=None)
    confidence: float | None = Field(default=None)
    raw_payload: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
