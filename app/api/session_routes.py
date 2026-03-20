from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import get_store
from app.schemas import SessionCreateIn, TaskContextIn
from app.services.errors import error_response
from app.services.session_service import (
    create_session,
    create_task_context,
    update_task_context,
)
from app.store import InMemoryStore, StoreError

router = APIRouter()


@router.post("/sessions", status_code=201)
def post_sessions(payload: SessionCreateIn, store: InMemoryStore = Depends(get_store)):
    try:
        context_payload = payload.task_context.dict() if payload.task_context else None
        return create_session(store, task_context_payload=context_payload)
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)


@router.post("/sessions/{session_id}/task-context", status_code=201)
def post_task_context(
    session_id: str,
    payload: TaskContextIn,
    store: InMemoryStore = Depends(get_store),
):
    try:
        return create_task_context(store, session_id, payload.dict())
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)


@router.put("/sessions/{session_id}/task-context", status_code=200)
def put_task_context(
    session_id: str,
    payload: TaskContextIn,
    store: InMemoryStore = Depends(get_store),
):
    try:
        return update_task_context(store, session_id, payload.dict())
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)
