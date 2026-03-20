from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class StoreError(Exception):
    code: str
    message: str
    status_code: int


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self.sessions: dict[str, dict[str, Any]] = {}
        self.task_contexts: dict[str, dict[str, Any]] = {}
        self.snapshots: dict[str, dict[str, Any]] = {}
        self.threads: dict[str, dict[str, Any]] = {}
        self.messages: dict[str, dict[str, Any]] = {}
        self.hint_requests: dict[str, dict[str, Any]] = {}
        self.tutor_responses: dict[str, dict[str, Any]] = {}

        self.session_task_context_ids: dict[str, list[str]] = {}
        self.session_snapshot_ids: dict[str, list[str]] = {}
        self.session_thread_ids: dict[str, list[str]] = {}
        self.thread_message_ids: dict[str, list[str]] = {}
        self.session_hint_request_ids: dict[str, list[str]] = {}

    def _ensure_session(self, session_id: str) -> dict[str, Any]:
        session = self.sessions.get(session_id)
        if session is None:
            raise StoreError("SESSION_NOT_FOUND", "Session was not found.", 404)
        return session

    def create_session(self) -> dict[str, Any]:
        with self._lock:
            session_id = str(uuid4())
            now = utc_now()
            session = {
                "id": session_id,
                "status": "active",
                "created_at": now,
                "updated_at": now,
            }
            self.sessions[session_id] = session
            self.session_task_context_ids[session_id] = []
            self.session_snapshot_ids[session_id] = []
            self.session_thread_ids[session_id] = []
            self.session_hint_request_ids[session_id] = []
            return dict(session)

    def get_session(self, session_id: str) -> dict[str, Any]:
        with self._lock:
            return dict(self._ensure_session(session_id))

    def get_task_context_history(self, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            self._ensure_session(session_id)
            context_ids = self.session_task_context_ids[session_id]
            return [dict(self.task_contexts[context_id]) for context_id in context_ids]

    def get_active_task_context(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            self._ensure_session(session_id)
            for context_id in reversed(self.session_task_context_ids[session_id]):
                context = self.task_contexts[context_id]
                if context["is_active"]:
                    return dict(context)
            return None

    def create_task_context(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            session = self._ensure_session(session_id)
            now = utc_now()

            for context_id in self.session_task_context_ids[session_id]:
                self.task_contexts[context_id]["is_active"] = False
                self.task_contexts[context_id]["updated_at"] = now

            context_id = str(uuid4())
            context = {
                "id": context_id,
                "session_id": session_id,
                "title": payload["title"],
                "description": payload["description"],
                "language": payload["language"],
                "desired_help_style": payload["desired_help_style"],
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }

            self.task_contexts[context_id] = context
            self.session_task_context_ids[session_id].append(context_id)
            session["updated_at"] = now
            return dict(context)

    def create_snapshot(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            session = self._ensure_session(session_id)
            now = utc_now()
            snapshot_id = str(uuid4())
            snapshot = {
                "id": snapshot_id,
                "session_id": session_id,
                "content": payload["content"],
                "cursor_line": payload.get("cursor_line"),
                "cursor_col": payload.get("cursor_col"),
                "selection_start": payload.get("selection_start"),
                "selection_end": payload.get("selection_end"),
                "source": payload["source"],
                "created_at": now,
            }
            self.snapshots[snapshot_id] = snapshot
            self.session_snapshot_ids[session_id].append(snapshot_id)
            session["updated_at"] = now
            return dict(snapshot)

    def get_latest_snapshot(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            self._ensure_session(session_id)
            snapshot_ids = self.session_snapshot_ids[session_id]
            if not snapshot_ids:
                return None
            return dict(self.snapshots[snapshot_ids[-1]])

    def create_thread(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            session = self._ensure_session(session_id)
            now = utc_now()
            thread_id = str(uuid4())
            active_context = self.get_active_task_context(session_id)
            thread = {
                "id": thread_id,
                "session_id": session_id,
                "title": payload["title"],
                "thread_type": payload["thread_type"],
                "linked_task_context_id": active_context["id"] if active_context else None,
                "created_at": now,
            }
            self.threads[thread_id] = thread
            self.thread_message_ids[thread_id] = []
            self.session_thread_ids[session_id].append(thread_id)
            session["updated_at"] = now
            return dict(thread)

    def list_threads(self, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            self._ensure_session(session_id)
            return [dict(self.threads[thread_id]) for thread_id in self.session_thread_ids[session_id]]

    def get_thread(self, thread_id: str) -> dict[str, Any]:
        with self._lock:
            thread = self.threads.get(thread_id)
            if thread is None:
                raise StoreError("THREAD_NOT_FOUND", "Thread was not found.", 404)
            return dict(thread)

    def create_message(
        self,
        thread_id: str,
        *,
        role: str,
        content: str,
        triggered_tutor: bool = False,
        hint_request_id: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            thread = self.threads.get(thread_id)
            if thread is None:
                raise StoreError("THREAD_NOT_FOUND", "Thread was not found.", 404)

            message_id = str(uuid4())
            message = {
                "id": message_id,
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "created_at": utc_now(),
                "triggered_tutor": triggered_tutor,
                "hint_request_id": hint_request_id,
            }
            self.messages[message_id] = message
            self.thread_message_ids[thread_id].append(message_id)
            return dict(message)

    def list_messages(self, thread_id: str) -> list[dict[str, Any]]:
        with self._lock:
            if thread_id not in self.threads:
                raise StoreError("THREAD_NOT_FOUND", "Thread was not found.", 404)
            message_ids = self.thread_message_ids[thread_id]
            messages = [dict(self.messages[message_id]) for message_id in message_ids]
            messages.sort(key=lambda message: message["created_at"])
            return messages

    def create_hint_request(
        self,
        *,
        session_id: str,
        task_context_id: str,
        snapshot_id: str,
        thread_id: str | None,
        request_type: str,
        triggering_message: str | None,
    ) -> dict[str, Any]:
        with self._lock:
            session = self._ensure_session(session_id)
            if thread_id is not None and thread_id not in self.threads:
                raise StoreError("THREAD_NOT_FOUND", "Thread was not found.", 404)

            hint_request_id = str(uuid4())
            hint_request = {
                "id": hint_request_id,
                "session_id": session_id,
                "task_context_id": task_context_id,
                "snapshot_id": snapshot_id,
                "thread_id": thread_id,
                "triggering_message": triggering_message,
                "request_type": request_type,
                "created_at": utc_now(),
            }
            self.hint_requests[hint_request_id] = hint_request
            self.session_hint_request_ids[session_id].append(hint_request_id)
            session["updated_at"] = hint_request["created_at"]
            return dict(hint_request)

    def create_tutor_response(self, *, hint_request_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            if hint_request_id not in self.hint_requests:
                raise StoreError("HINT_REQUEST_NOT_FOUND", "Hint request was not found.", 404)

            tutor_response_id = str(uuid4())
            response = {
                "id": tutor_response_id,
                "hint_request_id": hint_request_id,
                "summary_of_progress": payload["summary_of_progress"],
                "next_step_nudge": payload["next_step_nudge"],
                "assumption_to_check": payload.get("assumption_to_check"),
                "confidence": payload.get("confidence"),
                "raw_payload": payload.get("raw_payload"),
                "created_at": utc_now(),
            }
            self.tutor_responses[hint_request_id] = response
            return dict(response)

    def get_workspace_model(self, session_id: str) -> dict[str, Any]:
        with self._lock:
            session = dict(self._ensure_session(session_id))
            task_context = self.get_active_task_context(session_id)
            task_context_history = self.get_task_context_history(session_id)
            latest_snapshot = self.get_latest_snapshot(session_id)
            threads = self.list_threads(session_id)
            active_thread_id = threads[0]["id"] if threads else None

            return {
                "session": {"id": session["id"], "status": session["status"]},
                "task_context": task_context,
                "task_context_history": task_context_history,
                "latest_snapshot": latest_snapshot,
                "threads": threads,
                "active_thread_id": active_thread_id,
            }
