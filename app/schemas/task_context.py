from __future__ import annotations

from pydantic import BaseModel, constr


class TaskContextIn(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    description: constr(strip_whitespace=True, min_length=1)
    language: constr(strip_whitespace=True, min_length=1)
    desired_help_style: constr(strip_whitespace=True, min_length=1) = "hint_first"
