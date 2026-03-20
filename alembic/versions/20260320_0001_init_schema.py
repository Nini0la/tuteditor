"""init schema

Revision ID: 20260320_0001
Revises:
Create Date: 2026-03-20 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260320_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "task_contexts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("language", sa.String(), nullable=False),
        sa.Column("desired_help_style", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_contexts_session_id"), "task_contexts", ["session_id"], unique=False)

    op.create_table(
        "code_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("cursor_line", sa.Integer(), nullable=True),
        sa.Column("cursor_col", sa.Integer(), nullable=True),
        sa.Column("selection_start", sa.Integer(), nullable=True),
        sa.Column("selection_end", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_code_snapshots_session_id"), "code_snapshots", ["session_id"], unique=False)

    op.create_table(
        "conversation_threads",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("thread_type", sa.String(), nullable=False),
        sa.Column("linked_task_context_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["linked_task_context_id"], ["task_contexts.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversation_threads_session_id"), "conversation_threads", ["session_id"], unique=False)

    op.create_table(
        "hint_requests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("task_context_id", sa.String(), nullable=False),
        sa.Column("snapshot_id", sa.String(), nullable=False),
        sa.Column("thread_id", sa.String(), nullable=True),
        sa.Column("triggering_message", sa.String(), nullable=True),
        sa.Column("request_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.ForeignKeyConstraint(["snapshot_id"], ["code_snapshots.id"]),
        sa.ForeignKeyConstraint(["task_context_id"], ["task_contexts.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["conversation_threads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hint_requests_session_id"), "hint_requests", ["session_id"], unique=False)

    op.create_table(
        "tutor_responses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("hint_request_id", sa.String(), nullable=False),
        sa.Column("summary_of_progress", sa.String(), nullable=False),
        sa.Column("next_step_nudge", sa.String(), nullable=False),
        sa.Column("assumption_to_check", sa.String(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["hint_request_id"], ["hint_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hint_request_id"),
    )

    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("triggered_tutor", sa.Boolean(), nullable=False),
        sa.Column("hint_request_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["hint_request_id"], ["hint_requests.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["conversation_threads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_conversation_messages_thread_id"),
        "conversation_messages",
        ["thread_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_conversation_messages_thread_id"), table_name="conversation_messages")
    op.drop_table("conversation_messages")
    op.drop_table("tutor_responses")
    op.drop_index(op.f("ix_hint_requests_session_id"), table_name="hint_requests")
    op.drop_table("hint_requests")
    op.drop_index(op.f("ix_conversation_threads_session_id"), table_name="conversation_threads")
    op.drop_table("conversation_threads")
    op.drop_index(op.f("ix_code_snapshots_session_id"), table_name="code_snapshots")
    op.drop_table("code_snapshots")
    op.drop_index(op.f("ix_task_contexts_session_id"), table_name="task_contexts")
    op.drop_table("task_contexts")
    op.drop_table("sessions")
