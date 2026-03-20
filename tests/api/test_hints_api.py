from __future__ import annotations

from tests.support import DEFAULT_EDITOR_SNAPSHOT, assert_error_envelope


def test_api_012_hint_request_persists_snapshot_hint_and_tutor_response(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
    get_workspace,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    response = post_hint_request(
        session_id,
        {
            "request_type": "stuck",
            "triggering_message": "I cannot get the loop invariant right.",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
            "thread_id": None,
        },
    )
    assert response.status_code == 201, response.text

    body = response.json()
    assert body["hint_request_id"]
    assert body["tutor_response"]["summary_of_progress"]
    assert body["tutor_response"]["next_step_nudge"]

    assert require_tutor_spy.call_count == 1

    workspace = get_workspace(session_id)
    assert workspace.status_code == 200, workspace.text
    latest_snapshot = workspace.json()["latest_snapshot"]
    assert latest_snapshot is not None
    assert latest_snapshot["source"] == "hint_trigger"


def test_api_013_hint_request_returns_context_required_without_active_context(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
    get_workspace,
):
    seeded = seeded_session(with_context=False)
    session_id = seeded["session_id"]

    response = post_hint_request(
        session_id,
        {
            "request_type": "stuck",
            "triggering_message": "Help",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert response.status_code == 409, response.text

    body = response.json()
    assert_error_envelope(body, code="TASK_CONTEXT_REQUIRED")
    assert require_tutor_spy.call_count == 0

    workspace = get_workspace(session_id)
    assert workspace.status_code == 200, workspace.text
    assert workspace.json()["latest_snapshot"] is None


def test_api_014_hint_request_type_enum_is_enforced(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    response = post_hint_request(
        session_id,
        {
            "request_type": "explain_everything",
            "triggering_message": "Do all the work",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert response.status_code in (400, 422), response.text
    assert require_tutor_spy.call_count == 0


def test_neg_003_hint_request_malformed_editor_snapshot_rejected(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    response = post_hint_request(
        session_id,
        {
            "request_type": "stuck",
            "triggering_message": "Missing snapshot content",
            "editor_snapshot": {"cursor_line": 1, "cursor_col": 1},
        },
    )
    assert response.status_code in (400, 422), response.text
    assert require_tutor_spy.call_count == 0


def test_neg_005_adapter_exception_returns_safe_error_and_no_partial_persistence(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
    get_workspace,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    require_tutor_spy.raise_error = RuntimeError("adapter failure")

    response = post_hint_request(
        session_id,
        {
            "request_type": "stuck",
            "triggering_message": "Will fail",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )

    assert response.status_code >= 400
    assert_error_envelope(response.json())

    workspace = get_workspace(session_id)
    assert workspace.status_code == 200, workspace.text
    assert workspace.json()["latest_snapshot"] is None
