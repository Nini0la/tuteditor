from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlmodel import Session

from app.api.router import api_router
from app.config import settings
from app.deps import get_db, get_store
from app.store import StoreError

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name)
app.include_router(api_router)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.exec(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/workspace/{session_id}", response_class=HTMLResponse)
def workspace_page(request: Request, session_id: str):
    store = get_store()
    try:
        store.get_session(session_id)
    except StoreError:
        return HTMLResponse(status_code=404, content="Workspace not found")

    return templates.TemplateResponse(
        "workspace.html",
        {
            "request": request,
            "session_id": session_id,
        },
    )
