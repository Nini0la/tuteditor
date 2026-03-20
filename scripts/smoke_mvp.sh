#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "[smoke] syncing dependencies"
uv sync --dev >/dev/null

echo "[smoke] applying migrations"
uv run alembic upgrade head >/dev/null

echo "[smoke] starting app"
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 >/tmp/tuteditor_smoke.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" >/dev/null 2>&1 || true' EXIT

echo "[smoke] waiting for health endpoint"
for _ in {1..40}; do
  if curl -fsS "$BASE_URL/health" >/dev/null; then
    break
  fi
  sleep 0.25
done
curl -fsS "$BASE_URL/health" >/dev/null

SESSION_JSON="$(curl -fsS -X POST "$BASE_URL/api/v1/sessions" -H "content-type: application/json" -d '{}')"
SESSION_ID="$(uv run python -c 'import json,sys; print(json.load(sys.stdin)["session_id"])' <<<"$SESSION_JSON")"
echo "[smoke] session created: $SESSION_ID"

curl -fsS -X POST "$BASE_URL/api/v1/sessions/$SESSION_ID/task-context" \
  -H "content-type: application/json" \
  -d '{"title":"Smoke Task","description":"Validate explicit trigger loop","language":"python","desired_help_style":"hint_first"}' >/dev/null
echo "[smoke] task context created"

THREAD_JSON="$(curl -fsS -X POST "$BASE_URL/api/v1/sessions/$SESSION_ID/threads" \
  -H "content-type: application/json" \
  -d '{"title":"Smoke Thread","thread_type":"general"}')"
THREAD_ID="$(uv run python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$THREAD_JSON")"
echo "[smoke] thread created: $THREAD_ID"

curl -fsS -X POST "$BASE_URL/api/v1/threads/$THREAD_ID/messages" \
  -H "content-type: application/json" \
  -d '{"content":"chat only smoke message","invoke_tutor":false}' >/dev/null
echo "[smoke] chat-only message submitted"

curl -fsS -X POST "$BASE_URL/api/v1/sessions/$SESSION_ID/hint-requests" \
  -H "content-type: application/json" \
  -d '{"request_type":"stuck","triggering_message":"smoke","editor_snapshot":{"content":"def f():\n    return 1\n","cursor_line":1,"cursor_col":1},"thread_id":null}' >/dev/null
echo "[smoke] explicit hint request submitted"

echo "[smoke] success"
