from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import get_store
from app.services.errors import error_response
from app.services.workspace_service import get_workspace
from app.store import InMemoryStore, StoreError

router = APIRouter()


@router.get("/sessions/{session_id}/workspace", status_code=200)
def get_workspace_route(session_id: str, store: InMemoryStore = Depends(get_store)):
    try:
        return get_workspace(store, session_id)
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)
