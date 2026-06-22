"""24_course_requirements

Revision ID: df0357f343ce
Revises: a6acf0fb45b0
Create Date: 2026-06-22 16:45:29.145471

Week 3 follow-up: subject-combination prerequisites (handbook §2.2), keyed by
COURSE_NUMBER (the 3-digit course-of-study code, e.g. "008" for Engineering) --
NOT course_code -- because the subject rule is defined per course-of-study
TYPE and applies identically across every university offering it (verified by
reading the full §2.2: e.g. Engineering's rule is the same at Moratuwa,
Peradeniya, Ruhuna, etc.).

subject_rule is a small JSONB boolean-condition tree, evaluated deterministically
in Python (core/eligibility/subject_requirements.py) -- no LLM ever touches this.
A course with NO row here is treated as ungated (stream-level check only),
so curation can be incremental without ever breaking existing behaviour.

ol_requirements is free text only -- NOT evaluated by the engine (O-Level data
is out of scope for the deterministic checker per the decision in this session);
it exists so the future RAG/chat layer can mention it.

exam_year is nullable: NULL = baseline rule; a specific year overrides it for
courses whose requirements change (e.g. Law's stated 2025/2026 rule change).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'df0357f343ce'
down_revision: Union[str, Sequence[str], None] = 'a6acf0fb45b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_requirements",
        sa.Column("requirement_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("course_number", sa.String(5), nullable=False),
        sa.Column("exam_year", sa.Integer, nullable=True),
        sa.Column("subject_rule", postgresql.JSONB, nullable=False),
        sa.Column("ol_requirements", sa.Text, nullable=True),
        sa.Column("source_section", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    # one baseline (exam_year IS NULL) row per course_number, plus optional
    # one row per (course_number, exam_year) override
    op.execute(
        "CREATE UNIQUE INDEX uq_course_requirements_baseline "
        "ON course_requirements (course_number) WHERE exam_year IS NULL"
    )
    op.create_index(
        "ix_course_requirements_number_year",
        "course_requirements",
        ["course_number", "exam_year"],
    )


def downgrade() -> None:
    op.drop_table("course_requirements")
