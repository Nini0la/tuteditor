from __future__ import annotations

from collections.abc import Generator

from app.config import settings
from sqlmodel import Session, create_engine

DATABASE_URL = f"sqlite:///{settings.db_path}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_db_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
