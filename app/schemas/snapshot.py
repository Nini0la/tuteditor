from __future__ import annotations

from pydantic import BaseModel, constr

from app.schemas.common import SnapshotSource


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
