from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, constr


class ThreadType(str, Enum):
    general = "general"
    hinting = "hinting"
    concept = "concept"
    planning = "planning"
    reflection = "reflection"


class SnapshotSource(str, Enum):
    manual_save = "manual_save"
    hint_trigger = "hint_trigger"
    thread_submit = "thread_submit"


class HintRequestType(str, Enum):
    stuck = "stuck"
    next_step = "next_step"
    review_approach = "review_approach"
    stronger_hint = "stronger_hint"


class TaskContextIn(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    description: constr(strip_whitespace=True, min_length=1)
    language: constr(strip_whitespace=True, min_length=1)
    desired_help_style: constr(strip_whitespace=True, min_length=1) = "hint_first"


class SessionCreateIn(BaseModel):
    task_context: TaskContextIn | None = None


class SnapshotIn(BaseModel):
    content: constr(min_length=1)
    cursor_line: int | None = None
    cursor_col: int | None = None
    selection_start: int | None = None
    selection_end: int | None = None
    source: SnapshotSource


class EditorSnapshotIn(BaseModel):
    content: constr(min_length=1)
    cursor_line: int | None = None
    cursor_col: int | None = None
    selection_start: int | None = None
    selection_end: int | None = None


class ThreadCreateIn(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    thread_type: ThreadType = ThreadType.general


class MessageCreateIn(BaseModel):
    content: constr(strip_whitespace=True, min_length=1)
    invoke_tutor: bool = True
    editor_snapshot: EditorSnapshotIn | None = None


class HintRequestCreateIn(BaseModel):
    request_type: HintRequestType
    triggering_message: constr(strip_whitespace=True, min_length=1) | None = None
    editor_snapshot: EditorSnapshotIn
    thread_id: str | None = None


class MessageCreateOut(BaseModel):
    message_id: str
    tutor_invoked: bool
    hint_request_id: str | None = None
    assistant_message_id: str | None = None


class HintRequestCreateOut(BaseModel):
    hint_request_id: str
    tutor_response: dict[str, Any]
