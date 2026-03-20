from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import get_store, get_tutor_adapter
from app.schemas import HintRequestCreateIn, HintRequestCreateOut
from app.services.errors import error_response
from app.services.hint_service import create_hint_request
from app.store import InMemoryStore, StoreError

router = APIRouter()


@router.post("/sessions/{session_id}/hint-requests", status_code=201, response_model=HintRequestCreateOut)
def post_hint_requests(
    session_id: str,
    payload: HintRequestCreateIn,
    store: InMemoryStore = Depends(get_store),
    tutor_adapter=Depends(get_tutor_adapter),
):
    try:
        return create_hint_request(
            store=store,
            tutor_adapter=tutor_adapter,
            session_id=session_id,
            request_type=payload.request_type.value,
            triggering_message=payload.triggering_message,
            editor_snapshot=payload.editor_snapshot.dict(),
            thread_id=payload.thread_id,
        )
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)
