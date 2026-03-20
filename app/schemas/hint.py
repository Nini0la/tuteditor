from __future__ import annotations

from typing import Any

from pydantic import BaseModel, constr

from app.schemas.common import HintRequestType
from app.schemas.snapshot import EditorSnapshotIn


class HintRequestCreateIn(BaseModel):
    request_type: HintRequestType
    triggering_message: constr(strip_whitespace=True, min_length=1) | None = None
    editor_snapshot: EditorSnapshotIn
    thread_id: str | None = None


class HintRequestCreateOut(BaseModel):
    hint_request_id: str
    tutor_response: dict[str, Any]
