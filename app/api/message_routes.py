from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import get_store, get_tutor_adapter
from app.schemas import MessageCreateIn, MessageCreateOut
from app.services.errors import error_response
from app.services.message_service import submit_message
from app.store import InMemoryStore, StoreError

router = APIRouter()


@router.post("/threads/{thread_id}/messages", status_code=201, response_model=MessageCreateOut)
def post_thread_messages(
    thread_id: str,
    payload: MessageCreateIn,
    store: InMemoryStore = Depends(get_store),
    tutor_adapter=Depends(get_tutor_adapter),
):
    try:
        return submit_message(
            store=store,
            tutor_adapter=tutor_adapter,
            thread_id=thread_id,
            content=payload.content,
            invoke_tutor=payload.invoke_tutor,
            editor_snapshot=payload.editor_snapshot.dict() if payload.editor_snapshot else None,
        )
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)
