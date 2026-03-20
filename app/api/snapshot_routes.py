from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import get_store
from app.schemas import SnapshotIn
from app.services.errors import error_response
from app.services.snapshot_service import create_snapshot
from app.store import InMemoryStore, StoreError

router = APIRouter()


@router.post("/sessions/{session_id}/snapshots", status_code=201)
def post_snapshots(
    session_id: str,
    payload: SnapshotIn,
    store: InMemoryStore = Depends(get_store),
):
    try:
        snapshot = create_snapshot(store, session_id, payload.dict())
        return {
            "snapshot_id": snapshot["id"],
            "created_at": snapshot["created_at"],
        }
    except StoreError as exc:
        return error_response(exc.status_code, code=exc.code, message=exc.message)
