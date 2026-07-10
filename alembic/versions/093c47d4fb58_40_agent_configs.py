"""40 agent configs (versioned, one active)

Phase 4 of docs/PHASE2_STUDENT_ADMIN_PLAN.md — the AI advisor's behavior
(system prompt, model, tool-loop bounds, web-search default) becomes admin-
editable data instead of code. Versioned rows, at most one active (same
pattern as scoring_config); the orchestrator falls back to its built-in
prompt when the table is empty, so rollout/rollback is zero-risk.

The prompt is a TEMPLATE: live facts ({available_years}, {latest_year},
{course_count}, {today}) are injected at render time from the DB — the fix for
the hardcoded-prompt drift ("2019-2023", "261 courses") that a yearly handbook
upload would otherwise reintroduce every year.

Revision ID: 093c47d4fb58
Revises: 985e13967bd9
Create Date: 2026-07-10 20:49:26.222576
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '093c47d4fb58'
down_revision: Union[str, Sequence[str], None] = '985e13967bd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_configs",
        sa.Column("config_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("system_prompt_template", sa.Text, nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("web_search_default", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("max_tool_turns", sa.Integer, nullable=False, server_default=sa.text("6")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("max_tool_turns BETWEEN 1 AND 12", name="ck_agent_configs_turns"),
    )
    # at most one active config at a time
    op.create_index(
        "uq_agent_configs_one_active",
        "agent_configs",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )


def downgrade() -> None:
    op.drop_index("uq_agent_configs_one_active", table_name="agent_configs")
    op.drop_table("agent_configs")
