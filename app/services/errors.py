from __future__ import annotations

from fastapi.responses import JSONResponse


TASK_CONTEXT_REQUIRED_MESSAGE = "Declare task context before requesting tutoring."


def error_response(status_code: int, *, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )
