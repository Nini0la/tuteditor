from __future__ import annotations

from fastapi import APIRouter

from app.api.hint_routes import router as hint_router
from app.api.message_routes import router as message_router
from app.api.session_routes import router as session_router
from app.api.snapshot_routes import router as snapshot_router
from app.api.thread_routes import router as thread_router
from app.api.workspace_routes import router as workspace_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(session_router)
api_router.include_router(workspace_router)
api_router.include_router(snapshot_router)
api_router.include_router(thread_router)
api_router.include_router(message_router)
api_router.include_router(hint_router)
