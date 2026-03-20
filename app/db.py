from __future__ import annotations

import sqlite3

from app.config import settings


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(str(settings.db_path), check_same_thread=False)


SessionLocal = _connect


def get_db():
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()
