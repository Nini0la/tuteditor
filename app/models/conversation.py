from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from app.models.session import utcnow


class ConversationThread(SQLModel, table=True):
    __tablename__ = "conversation_threads"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True, nullable=False)
    title: str = Field(nullable=False)
    thread_type: str = Field(default="general", nullable=False)
    linked_task_context_id: str | None = Field(default=None, foreign_key="task_contexts.id")
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class ConversationMessage(SQLModel, table=True):
    __tablename__ = "conversation_messages"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    thread_id: str = Field(foreign_key="conversation_threads.id", index=True, nullable=False)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    triggered_tutor: bool = Field(default=False, nullable=False)
    hint_request_id: str | None = Field(default=None, foreign_key="hint_requests.id")
