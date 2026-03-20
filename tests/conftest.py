from __future__ import annotations

import importlib
from typing import Any

import pytest

from tests.support import API_PREFIX, DEFAULT_TASK_CONTEXT, TutorSpy


@pytest.fixture
def app_instance() -> Any:
    try:
        module = importlib.import_module("app.main")
    except ModuleNotFoundError:
        pytest.skip("Backend app module 'app.main' is not available yet.")

    app = getattr(module, "app", None)
    if app is None:
        pytest.skip("'app.main' exists but does not expose 'app'.")
    return app


@pytest.fixture
def api_client(app_instance: Any) -> Any:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    with TestClient(app_instance) as client:
        yield client


@pytest.fixture
def db_session() -> Any:
    try:
        db_module = importlib.import_module("app.db")
    except ModuleNotFoundError:
        pytest.skip("DB module 'app.db' is not available yet.")

    if hasattr(db_module, "SessionLocal"):
        session = db_module.SessionLocal()
        try:
            yield session
        finally:
            session.close()
        return

    get_db = getattr(db_module, "get_db", None)
    if callable(get_db):
        generator = get_db()
        session = next(generator)
        try:
            yield session
        finally:
            session.close()
            try:
                next(generator)
            except StopIteration:
                pass
        return

    pytest.skip("Could not resolve DB session seam (expected SessionLocal or get_db).")


def _patch_tutor_dependency(monkeypatch: pytest.MonkeyPatch, app_instance: Any, spy: TutorSpy) -> bool:
    candidates = [
        ("app.deps", "get_tutor_adapter"),
        ("app.api.deps", "get_tutor_adapter"),
        ("app.tutor.adapter", "get_tutor_adapter"),
        ("app.tutor.adapter", "get_adapter"),
        ("app.services.hint_service", "get_tutor_adapter"),
        ("app.services.message_service", "get_tutor_adapter"),
        ("app.services.hint_service", "tutor_adapter"),
        ("app.services.message_service", "tutor_adapter"),
    ]

    patched_any = False
    for module_name, attr_name in candidates:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue

        if not hasattr(module, attr_name):
            continue

        original = getattr(module, attr_name)
        if callable(original):
            monkeypatch.setattr(module, attr_name, lambda: spy, raising=False)
            dependency_overrides = getattr(app_instance, "dependency_overrides", None)
            if isinstance(dependency_overrides, dict):
                dependency_overrides[original] = lambda: spy
        else:
            monkeypatch.setattr(module, attr_name, spy, raising=False)
        patched_any = True

    return patched_any


@pytest.fixture
def fake_tutor_adapter(monkeypatch: pytest.MonkeyPatch, app_instance: Any) -> TutorSpy:
    spy = TutorSpy()
    spy.patched = _patch_tutor_dependency(monkeypatch, app_instance, spy)
    return spy


@pytest.fixture
def require_tutor_spy(fake_tutor_adapter: TutorSpy) -> TutorSpy:
    if not fake_tutor_adapter.patched:
        pytest.skip(
            "Tutor adapter seam not found. Add dependency injection seam such as "
            "'get_tutor_adapter' so tutor calls can be deterministically intercepted."
        )
    return fake_tutor_adapter


@pytest.fixture
def create_session(api_client: Any) -> Any:
    def _create(*, task_context: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {}
        if task_context is not None:
            payload["task_context"] = task_context
        response = api_client.post(f"{API_PREFIX}/sessions", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _create


@pytest.fixture
def create_task_context(api_client: Any) -> Any:
    def _create(session_id: str, payload: dict[str, Any]) -> Any:
        return api_client.post(f"{API_PREFIX}/sessions/{session_id}/task-context", json=payload)

    return _create


@pytest.fixture
def update_task_context(api_client: Any) -> Any:
    def _update(session_id: str, payload: dict[str, Any]) -> Any:
        return api_client.put(f"{API_PREFIX}/sessions/{session_id}/task-context", json=payload)

    return _update


@pytest.fixture
def create_thread(api_client: Any) -> Any:
    def _create(session_id: str, *, title: str, thread_type: str = "general") -> Any:
        return api_client.post(
            f"{API_PREFIX}/sessions/{session_id}/threads",
            json={"title": title, "thread_type": thread_type},
        )

    return _create


@pytest.fixture
def create_snapshot(api_client: Any) -> Any:
    def _create(
        session_id: str,
        *,
        content: str,
        source: str,
        cursor_line: int | None = None,
        cursor_col: int | None = None,
        selection_start: int | None = None,
        selection_end: int | None = None,
    ) -> Any:
        return api_client.post(
            f"{API_PREFIX}/sessions/{session_id}/snapshots",
            json={
                "content": content,
                "source": source,
                "cursor_line": cursor_line,
                "cursor_col": cursor_col,
                "selection_start": selection_start,
                "selection_end": selection_end,
            },
        )

    return _create


@pytest.fixture
def post_message(api_client: Any) -> Any:
    def _post(thread_id: str, payload: dict[str, Any]) -> Any:
        return api_client.post(f"{API_PREFIX}/threads/{thread_id}/messages", json=payload)

    return _post


@pytest.fixture
def post_hint_request(api_client: Any) -> Any:
    def _post(session_id: str, payload: dict[str, Any]) -> Any:
        return api_client.post(f"{API_PREFIX}/sessions/{session_id}/hint-requests", json=payload)

    return _post


@pytest.fixture
def get_workspace(api_client: Any) -> Any:
    def _get(session_id: str) -> Any:
        return api_client.get(f"{API_PREFIX}/sessions/{session_id}/workspace")

    return _get


@pytest.fixture
def seeded_session(create_session: Any, create_task_context: Any) -> Any:
    def _seed(*, with_context: bool = True) -> dict[str, Any]:
        session = create_session()
        session_id = session["session_id"]
        context = None
        if with_context:
            response = create_task_context(session_id, DEFAULT_TASK_CONTEXT)
            assert response.status_code in (200, 201), response.text
            context = response.json()

        return {
            "session": session,
            "session_id": session_id,
            "task_context": context,
        }

    return _seed


@pytest.fixture
def seeded_threads(seeded_session: Any, create_thread: Any) -> Any:
    def _seed(*, with_context: bool = True) -> dict[str, Any]:
        seeded = seeded_session(with_context=with_context)
        session_id = seeded["session_id"]

        thread_a = create_thread(session_id, title="Concept Thread", thread_type="concept")
        assert thread_a.status_code == 201, thread_a.text
        thread_b = create_thread(session_id, title="Planning Thread", thread_type="planning")
        assert thread_b.status_code == 201, thread_b.text

        return {
            **seeded,
            "thread_a": thread_a.json(),
            "thread_b": thread_b.json(),
        }

    return _seed
