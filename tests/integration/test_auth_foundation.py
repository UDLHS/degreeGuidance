"""Regression tests for the auth/identity foundation (migration 19, Admin Slice 1 A1).

Verifies the schema landed correctly and the key constraints behave:
- users + admin_actions exist; eligibility_audit gained its user_id FK.
- role CHECK rejects bad roles, accepts valid ones, defaults to 'student'.
- admin_actions.admin_user_id FK is enforced (insert with a bogus user fails).
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def test_tables_exist(db_session: AsyncSession):
    row = (
        await db_session.execute(
            text(
                "SELECT to_regclass('public.users') AS u, "
                "       to_regclass('public.admin_actions') AS a"
            )
        )
    ).first()
    assert row.u == "users"
    assert row.a == "admin_actions"


async def test_eligibility_audit_user_fk_present(db_session: AsyncSession):
    row = (
        await db_session.execute(
            text(
                """
                SELECT 1
                FROM information_schema.table_constraints
                WHERE table_name = 'eligibility_audit'
                  AND constraint_type = 'FOREIGN KEY'
                  AND constraint_name = 'eligibility_audit_user_id_fkey'
                """
            )
        )
    ).first()
    assert row is not None, "deferred eligibility_audit.user_id FK was not added"


async def test_role_default_is_student(db_session: AsyncSession):
    new_id = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO users (user_id, email) VALUES (:id, :email)"),
        {"id": new_id, "email": f"default-{new_id}@example.com"},
    )
    role = (
        await db_session.execute(
            text("SELECT role FROM users WHERE user_id = :id"), {"id": new_id}
        )
    ).scalar_one()
    assert role == "student"
    await db_session.rollback()


async def test_role_check_rejects_invalid(db_session: AsyncSession):
    new_id = uuid.uuid4()
    with pytest.raises((IntegrityError, DBAPIError)):
        await db_session.execute(
            text("INSERT INTO users (user_id, email, role) VALUES (:id, :email, 'wizard')"),
            {"id": new_id, "email": f"bad-{new_id}@example.com"},
        )
        await db_session.flush()
    await db_session.rollback()


async def test_admin_actions_fk_enforced(db_session: AsyncSession):
    # admin_user_id must reference a real user; a random UUID violates the FK
    with pytest.raises((IntegrityError, DBAPIError)):
        await db_session.execute(
            text(
                "INSERT INTO admin_actions (admin_user_id, action_type) "
                "VALUES (:uid, 'edit_course')"
            ),
            {"uid": uuid.uuid4()},
        )
        await db_session.flush()
    await db_session.rollback()


async def test_admin_action_roundtrip(db_session: AsyncSession):
    uid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO users (user_id, email, role) VALUES (:id, :email, 'admin')"),
        {"id": uid, "email": f"admin-{uid}@example.com"},
    )
    await db_session.execute(
        text(
            """
            INSERT INTO admin_actions
                (admin_user_id, action_type, target_table, target_id, after_value)
            VALUES (:uid, 'edit_course', 'courses', '001A', '{"is_active": false}'::jsonb)
            """
        ),
        {"uid": uid},
    )
    n = (
        await db_session.execute(
            text("SELECT count(*) FROM admin_actions WHERE admin_user_id = :uid"),
            {"uid": uid},
        )
    ).scalar_one()
    assert n == 1
    await db_session.rollback()  # keep the test DB clean
