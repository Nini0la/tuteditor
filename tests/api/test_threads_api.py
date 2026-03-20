from __future__ import annotations

from tests.support import API_PREFIX, normalize_messages_payload


def test_api_007_thread_create_and_list_support_parallel_threads(
    seeded_session,
    create_thread,
    api_client,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    first = create_thread(session_id, title="Loop reasoning", thread_type="concept")
    assert first.status_code == 201, first.text
    first_body = first.json()

    second = create_thread(session_id, title="Plan next step", thread_type="planning")
    assert second.status_code == 201, second.text
    second_body = second.json()

    listed = api_client.get(f"{API_PREFIX}/sessions/{session_id}/threads")
    assert listed.status_code == 200, listed.text
    threads = listed.json()
    if isinstance(threads, dict):
        threads = threads.get("threads", [])

    by_id = {thread["id"]: thread for thread in threads}
    assert first_body["id"] in by_id
    assert second_body["id"] in by_id
    assert by_id[first_body["id"]]["thread_type"] == "concept"
    assert by_id[second_body["id"]]["thread_type"] == "planning"


def test_api_008_message_list_is_thread_scoped_and_ordered(
    seeded_threads,
    post_message,
    api_client,
):
    seeded = seeded_threads(with_context=True)
    thread_a_id = seeded["thread_a"]["id"]
    thread_b_id = seeded["thread_b"]["id"]

    assert post_message(thread_a_id, {"content": "A1", "invoke_tutor": False}).status_code == 201
    assert post_message(thread_b_id, {"content": "B1", "invoke_tutor": False}).status_code == 201
    assert post_message(thread_a_id, {"content": "A2", "invoke_tutor": False}).status_code == 201

    response = api_client.get(f"{API_PREFIX}/threads/{thread_a_id}/messages")
    assert response.status_code == 200, response.text

    messages = normalize_messages_payload(response.json())
    contents = [msg["content"] for msg in messages]
    assert contents == ["A1", "A2"]

    created_at = [msg.get("created_at") for msg in messages]
    assert created_at == sorted(created_at)


def test_neg_001_invalid_thread_type_rejected(seeded_session, create_thread, api_client):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    response = create_thread(session_id, title="Invalid thread", thread_type="offtopic")
    assert response.status_code in (400, 422), response.text

    listed = api_client.get(f"{API_PREFIX}/sessions/{session_id}/threads")
    assert listed.status_code == 200, listed.text
    threads = listed.json()
    if isinstance(threads, dict):
        threads = threads.get("threads", [])

    assert threads == []
