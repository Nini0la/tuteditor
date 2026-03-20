from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import get_store
from app.schemas import ThreadCreateIn
from app.services.errors import error_response
from app.services.thread_service import create_thread, list_messages, list_threads
from app.store import InMemoryStore, StoreError

router = APIRouter()


@router.post("/sessions/{session_id}/threads", status_code=201)
def post_threads(
    session_id: str,
    payload: ThreadCreateIn,
    store: InMemoryStore = Depends(get_store),
):
    try:
        return create_thread(store, session_id, payload.dict())
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)


@router.get("/sessions/{session_id}/threads", status_code=200)
def get_threads(session_id: str, store: InMemoryStore = Depends(get_store)):
    try:
        return list_threads(store, session_id)
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)


@router.get("/threads/{thread_id}/messages", status_code=200)
def get_thread_messages(thread_id: str, store: InMemoryStore = Depends(get_store)):
    try:
        return list_messages(store, thread_id)
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)
