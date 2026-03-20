from __future__ import annotations

from tests.support import DEFAULT_EDITOR_SNAPSHOT


def test_api_005_post_snapshots_persists_snapshot_with_valid_source(
    seeded_session,
    create_snapshot,
    get_workspace,
):
    seeded = seeded_session(with_context=False)
    session_id = seeded["session_id"]

    response = create_snapshot(
        session_id,
        content=DEFAULT_EDITOR_SNAPSHOT["content"],
        source="manual_save",
        cursor_line=DEFAULT_EDITOR_SNAPSHOT["cursor_line"],
        cursor_col=DEFAULT_EDITOR_SNAPSHOT["cursor_col"],
    )
    assert response.status_code == 201, response.text

    snapshot_id = response.json()["snapshot_id"]

    workspace = get_workspace(session_id)
    assert workspace.status_code == 200, workspace.text
    latest_snapshot = workspace.json()["latest_snapshot"]

    assert latest_snapshot is not None
    assert latest_snapshot["id"] == snapshot_id
    assert latest_snapshot["content"] == DEFAULT_EDITOR_SNAPSHOT["content"]
    assert latest_snapshot["source"] == "manual_save"


def test_api_006_post_snapshots_rejects_unknown_source(
    seeded_session,
    create_snapshot,
    get_workspace,
):
    seeded = seeded_session(with_context=False)
    session_id = seeded["session_id"]

    response = create_snapshot(
        session_id,
        content="print('tick')\n",
        source="auto_tick",
    )
    assert response.status_code in (400, 422), response.text

    workspace = get_workspace(session_id)
    assert workspace.status_code == 200, workspace.text
    assert workspace.json()["latest_snapshot"] is None
