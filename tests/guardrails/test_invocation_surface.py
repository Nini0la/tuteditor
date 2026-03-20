from __future__ import annotations


def test_gr_003_tutor_invocation_surface_is_explicit_action_routes(app_instance):
    explicit_tutor_routes = {
        ("POST", "/api/v1/sessions/{session_id}/hint-requests"),
        ("POST", "/api/v1/threads/{thread_id}/messages"),
    }

    registered = set()
    for route in app_instance.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", set())
        if not path or not methods:
            continue
        for method in methods:
            registered.add((method.upper(), path))

    assert explicit_tutor_routes.issubset(registered), registered

    # Any tutor-specific HTTP path should be limited to explicit trigger endpoints.
    tutorish_routes = {
        (method, path)
        for method, path in registered
        if method == "POST"
        and (
            "hint" in path
            or "tutor" in path
            or path.endswith("/messages")
            or path.endswith("/hint-requests")
        )
    }

    assert tutorish_routes.issubset(explicit_tutor_routes), tutorish_routes
