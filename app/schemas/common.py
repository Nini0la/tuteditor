from __future__ import annotations

from enum import Enum


class ThreadType(str, Enum):
    general = "general"
    hinting = "hinting"
    concept = "concept"
    planning = "planning"
    reflection = "reflection"


class SnapshotSource(str, Enum):
    manual_save = "manual_save"
    hint_trigger = "hint_trigger"
    thread_submit = "thread_submit"


class HintRequestType(str, Enum):
    stuck = "stuck"
    next_step = "next_step"
    review_approach = "review_approach"
    stronger_hint = "stronger_hint"
