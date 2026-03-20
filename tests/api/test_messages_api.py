from __future__ import annotations

from tests.support import DEFAULT_EDITOR_SNAPSHOT, assert_error_envelope


def test_api_009_message_submit_chat_only_when_invoke_tutor_false(
    seeded_threads,
    post_message,
    require_tutor_spy,
):
    seeded = seeded_threads(with_context=True)
    thread_id = seeded["thread_a"]["id"]

    response = post_message(
        thread_id,
        {
            "content": "Can you explain what this loop does?",
            "invoke_tutor": False,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()

    assert body["tutor_invoked"] is False
    assert body["hint_request_id"] is None
    assert body["assistant_message_id"] is None
    assert body["message_id"]
    assert require_tutor_spy.call_count == 0


def test_api_010_message_submit_invokes_tutor_when_invoke_tutor_true(
    seeded_threads,
    post_message,
    require_tutor_spy,
):
    seeded = seeded_threads(with_context=True)
    thread_id = seeded["thread_a"]["id"]

    response = post_message(
        thread_id,
        {
            "content": "What logical step am I missing?",
            "invoke_tutor": True,
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()

    assert body["tutor_invoked"] is True
    assert body["hint_request_id"]
    assert body["assistant_message_id"]
    assert require_tutor_spy.call_count == 1


def test_api_011_message_submit_with_tutor_fails_without_context(
    seeded_threads,
    post_message,
    require_tutor_spy,
):
    seeded = seeded_threads(with_context=False)
    thread_id = seeded["thread_a"]["id"]

    response = post_message(
        thread_id,
        {
            "content": "Please help",
            "invoke_tutor": True,
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert response.status_code == 409, response.text
    assert_error_envelope(response.json(), code="TASK_CONTEXT_REQUIRED")
    assert require_tutor_spy.call_count == 0


def test_neg_002_message_submit_missing_content_rejected(
    seeded_threads,
    post_message,
    require_tutor_spy,
):
    seeded = seeded_threads(with_context=True)
    thread_id = seeded["thread_a"]["id"]

    response = post_message(thread_id, {"invoke_tutor": True})
    assert response.status_code in (400, 422), response.text
    assert require_tutor_spy.call_count == 0
