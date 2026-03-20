from __future__ import annotations

from tests.support import API_PREFIX, normalize_messages_payload


def test_unit_003_message_service_with_invoke_false_remains_chat_only(
    seeded_threads,
    post_message,
    require_tutor_spy,
    api_client,
):
    seeded = seeded_threads(with_context=True)
    thread_id = seeded["thread_a"]["id"]

    response = post_message(
        thread_id,
        {
            "content": "Just store this note.",
            "invoke_tutor": False,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()

    assert body["tutor_invoked"] is False
    assert body["hint_request_id"] is None
    assert body["assistant_message_id"] is None
    assert require_tutor_spy.call_count == 0

    messages_response = api_client.get(f"{API_PREFIX}/threads/{thread_id}/messages")
    assert messages_response.status_code == 200, messages_response.text

    messages = normalize_messages_payload(messages_response.json())
    assert [m["role"] for m in messages] == ["user"]
    assert [m["content"] for m in messages] == ["Just store this note."]
