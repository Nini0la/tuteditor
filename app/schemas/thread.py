from __future__ import annotations

from pydantic import BaseModel, constr

from app.schemas.common import ThreadType
from app.schemas.snapshot import EditorSnapshotIn


class ThreadCreateIn(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    thread_type: ThreadType = ThreadType.general


class MessageCreateIn(BaseModel):
    content: constr(strip_whitespace=True, min_length=1)
    invoke_tutor: bool = True
    editor_snapshot: EditorSnapshotIn | None = None


class MessageCreateOut(BaseModel):
    message_id: str
    tutor_invoked: bool
    hint_request_id: str | None = None
    assistant_message_id: str | None = None
