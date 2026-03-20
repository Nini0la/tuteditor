from __future__ import annotations

from tests.support import DEFAULT_EDITOR_SNAPSHOT, assert_error_envelope


def test_unit_002_hint_service_invokes_only_with_explicit_trigger_and_context(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
):
    with_context = seeded_session(with_context=True)
    session_with_context = with_context["session_id"]

    ok_response = post_hint_request(
        session_with_context,
        {
            "request_type": "stuck",
            "triggering_message": "I am stuck",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert ok_response.status_code == 201, ok_response.text
    assert require_tutor_spy.call_count == 1

    without_context = seeded_session(with_context=False)
    session_without_context = without_context["session_id"]

    missing_context_response = post_hint_request(
        session_without_context,
        {
            "request_type": "stuck",
            "triggering_message": "I am still stuck",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )
    assert missing_context_response.status_code == 409, missing_context_response.text
    assert_error_envelope(missing_context_response.json(), code="TASK_CONTEXT_REQUIRED")

    assert require_tutor_spy.call_count == 1


def test_gr_004_hint_service_blocks_or_sanitizes_full_solution_output(
    seeded_session,
    post_hint_request,
    require_tutor_spy,
):
    seeded = seeded_session(with_context=True)
    session_id = seeded["session_id"]

    unsafe_next_step = "def binary_search(nums, target):\n    # full solution\n    return solved\n"
    require_tutor_spy.output = {
        "summary_of_progress": "You started the function.",
        "next_step_nudge": unsafe_next_step,
        "assumption_to_check": "None",
        "safety": {"gave_full_solution": True},
    }

    response = post_hint_request(
        session_id,
        {
            "request_type": "stuck",
            "triggering_message": "Give me a hint",
            "editor_snapshot": dict(DEFAULT_EDITOR_SNAPSHOT),
        },
    )

    if response.status_code >= 400:
        assert_error_envelope(response.json())
        return

    assert response.status_code == 201, response.text
    body = response.json()
    tutor_response = body["tutor_response"]

    assert tutor_response["summary_of_progress"]
    assert tutor_response["next_step_nudge"]
    assert tutor_response["next_step_nudge"] != unsafe_next_step
