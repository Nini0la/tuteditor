from __future__ import annotations

from tests.support import (
    API_PREFIX,
    DEFAULT_TASK_CONTEXT,
    UPDATED_TASK_CONTEXT,
    extract_task_context_id,
)


def test_api_001_post_sessions_creates_session_without_task_context(api_client):
    response = api_client.post(f"{API_PREFIX}/sessions", json={})
    assert response.status_code == 201, response.text

    body = response.json()
    assert body["session_id"]
    assert body["workspace_url"].endswith(body["session_id"])

    workspace = api_client.get(f"{API_PREFIX}/sessions/{body['session_id']}/workspace")
    assert workspace.status_code == 200, workspace.text
    workspace_body = workspace.json()

    assert workspace_body["task_context"] is None
    assert isinstance(workspace_body["task_context_history"], list)


def test_api_002_post_task_context_creates_initial_active_context(
    create_session,
    create_task_context,
    get_workspace,
):
    session = create_session()
    session_id = session["session_id"]

    response = create_task_context(session_id, DEFAULT_TASK_CONTEXT)
    assert response.status_code in (200, 201), response.text

    context_body = response.json()
    context_id = extract_task_context_id(context_body)
    assert context_id

    workspace = get_workspace(session_id)
    assert workspace.status_code == 200, workspace.text
    workspace_body = workspace.json()

    assert workspace_body["task_context"] is not None
    assert workspace_body["task_context"]["id"] == context_id
    assert workspace_body["task_context"].get("is_active", True) is True


def test_api_002b_put_task_context_creates_new_active_version(
    create_session,
    create_task_context,
    update_task_context,
    get_workspace,
):
    session = create_session()
    session_id = session["session_id"]

    first_response = create_task_context(session_id, DEFAULT_TASK_CONTEXT)
    assert first_response.status_code in (200, 201), first_response.text
    first_context_id = extract_task_context_id(first_response.json())
    assert first_context_id

    second_response = update_task_context(session_id, UPDATED_TASK_CONTEXT)
    assert second_response.status_code == 200, second_response.text
    second_context_id = extract_task_context_id(second_response.json())
    assert second_context_id
    assert second_context_id != first_context_id

    workspace = get_workspace(session_id)
    assert workspace.status_code == 200, workspace.text
    workspace_body = workspace.json()

    assert workspace_body["task_context"]["id"] == second_context_id

    history = workspace_body["task_context_history"]
    assert isinstance(history, list)
    assert len(history) >= 2

    by_id = {item["id"]: item for item in history if "id" in item}
    assert by_id[first_context_id].get("is_active", False) is False
    assert by_id[second_context_id].get("is_active", True) is True
