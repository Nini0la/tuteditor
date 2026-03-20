from __future__ import annotations

from tests.support import API_PREFIX, assert_error_envelope


def test_api_003_workspace_returns_complete_initial_model(seeded_session, get_workspace):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    response = get_workspace(session_id)
    assert response.status_code == 200, response.text
    body = response.json()

    expected_keys = {
        "session",
        "task_context",
        "task_context_history",
        "latest_snapshot",
        "threads",
        "active_thread_id",
    }
    assert expected_keys.issubset(set(body.keys())), body
    assert body["latest_snapshot"] is None
    assert body["threads"] == []


def test_api_004_workspace_returns_latest_snapshot_only(
    seeded_session,
    create_snapshot,
    get_workspace,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    first = create_snapshot(
        session_id,
        content="print('first')\n",
        source="manual_save",
        cursor_line=1,
        cursor_col=5,
    )
    assert first.status_code == 201, first.text
    first_id = first.json()["snapshot_id"]

    second = create_snapshot(
        session_id,
        content="print('second')\n",
        source="manual_save",
        cursor_line=1,
        cursor_col=6,
    )
    assert second.status_code == 201, second.text
    second_id = second.json()["snapshot_id"]

    response = get_workspace(session_id)
    assert response.status_code == 200, response.text
    latest = response.json()["latest_snapshot"]

    assert latest is not None
    assert latest["id"] == second_id
    assert latest["id"] != first_id


def test_neg_004_workspace_unknown_session_returns_404(api_client):
    missing_id = "00000000-0000-0000-0000-000000000000"
    response = api_client.get(f"{API_PREFIX}/sessions/{missing_id}/workspace")

    assert response.status_code == 404
    assert_error_envelope(response.json())
