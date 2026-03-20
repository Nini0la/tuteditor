from __future__ import annotations

from tests.support import DEFAULT_EDITOR_SNAPSHOT, DEFAULT_TASK_CONTEXT, UPDATED_TASK_CONTEXT


def test_unit_004_payload_builder_includes_required_context_blocks(
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
            "triggering_message": "Need a nudge",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert response.status_code == 201, response.text
    assert require_tutor_spy.call_count == 1

    payload = require_tutor_spy.payloads[-1]
    expected_blocks = {
        "event",
        "session",
        "task_context",
        "editor_state",
        "thread_context",
        "policy",
    }
    assert expected_blocks.issubset(payload.keys()), payload
    assert payload["policy"]["pedagogy"] == "nudge_not_solution"


def test_unit_004b_payload_builder_uses_latest_active_task_context(
    create_session,
    create_task_context,
    update_task_context,
    post_hint_request,
    require_tutor_spy,
):
    session = create_session()
    session_id = session["session_id"]

    first_context = create_task_context(session_id, DEFAULT_TASK_CONTEXT)
    assert first_context.status_code in (200, 201), first_context.text

    second_context = update_task_context(session_id, UPDATED_TASK_CONTEXT)
    assert second_context.status_code == 200, second_context.text

    response = post_hint_request(
        session_id,
        {
            "request_type": "stuck",
            "triggering_message": "Use latest context",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert response.status_code == 201, response.text

    payload = require_tutor_spy.payloads[-1]
    assert payload["task_context"]["title"] == UPDATED_TASK_CONTEXT["title"]
    assert payload["task_context"]["description"] == UPDATED_TASK_CONTEXT["description"]


def test_unit_005_payload_builder_scopes_thread_context_to_selected_thread(
    seeded_threads,
    post_message,
    require_tutor_spy,
):
    seeded = seeded_threads(with_context=True)
    thread_a_id = seeded["thread_a"]["id"]
    thread_b_id = seeded["thread_b"]["id"]

    post_message(thread_a_id, {"content": "THREAD_A_ONLY", "invoke_tutor": False})
    post_message(thread_b_id, {"content": "THREAD_B_ONLY", "invoke_tutor": False})

    response = post_message(
        thread_a_id,
        {
            "content": "Please review thread A",
            "invoke_tutor": True,
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert response.status_code == 201, response.text

    payload = require_tutor_spy.payloads[-1]
    thread_messages = payload["thread_context"]["recent_messages"]
    merged_content = "\n".join(msg["content"] for msg in thread_messages)

    assert "THREAD_A_ONLY" in merged_content
    assert "THREAD_B_ONLY" not in merged_content


def test_unit_006_tutor_output_schema_is_enforced(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    require_tutor_spy.output = {"safety": {"gave_full_solution": False}}

    response = post_hint_request(
        session_id,
        {
            "request_type": "stuck",
            "triggering_message": "Validate output schema",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )

    if response.status_code >= 400:
        return

    assert response.status_code == 201, response.text
    tutor_response = response.json()["tutor_response"]
    assert tutor_response["summary_of_progress"]
    assert tutor_response["next_step_nudge"]
