"""22_scoring_config

Revision ID: a6acf0fb45b0
Revises: bc36f6410cca
Create Date: 2026-06-15 23:48:41.454911

Week 3 (masterplan §9): tunable recommendation-scoring weights + bucket
thresholds, versioned so they change without a redeploy. Exactly one row is
active at a time (partial unique index). The scorer reads the active row and
renormalizes weights over the dimensions that currently have data — interest /
career / industry are seeded but inert until the Week 4-5 agent/RAG layer
provides their inputs.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a6acf0fb45b0'
down_revision: Union[str, Sequence[str], None] = 'bc36f6410cca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scoring_config",
        sa.Column("config_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("weights", postgresql.JSONB, nullable=False),
        sa.Column("thresholds", postgresql.JSONB, nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    # at most one active config at a time
    op.execute(
        "CREATE UNIQUE INDEX uq_scoring_config_active ON scoring_config (is_active) WHERE is_active"
    )

    scoring_config = sa.table(
        "scoring_config",
        sa.column("version", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("weights", postgresql.JSONB),
        sa.column("thresholds", postgresql.JSONB),
        sa.column("notes", sa.Text),
    )
    op.bulk_insert(
        scoring_config,
        [
            {
                "version": "v1",
                "is_active": True,
                "weights": {
                    "interest": 0.30,
                    "career": 0.25,
                    "z_margin": 0.15,
                    "university": 0.15,
                    "industry": 0.15,
                },
                "thresholds": {
                    "safe_score": 0.6,
                    "safe_margin": 0.10,
                    "ambitious_score": 0.6,
                    "ambitious_margin": 0.05,
                    "hidden_score": 0.5,
                    "marginal_band": 0.05,
                    "z_margin_tanh_scale": 4.0,
                },
                "notes": (
                    "Masterplan §9 defaults. interest/career/industry are inert until the "
                    "Week 4-5 RAG layer; the scorer renormalizes weights over active dimensions."
                ),
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("scoring_config")
