"""Admin audit logging helper (Admin Slice 1, Part B).

Every admin mutation calls log_admin_action(), which appends one row to
admin_actions (masterplan §14.3: "Every mutation writes a row to admin_actions").
before/after are stored as JSON-safe dicts in the JSONB columns, so json_safe_row
converts datetime/Decimal/UUID into JSON-serializable values first (asyncpg's JSONB
encoder runs json.dumps and would otherwise choke on those types).
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.auth import AdminAction, User


def hash_ip(request: Request) -> str | None:
    if request.client is None:
        return None
    return hashlib.sha256(request.client.host.encode("utf-8")).hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    return value


def json_safe_row(mapping: Any) -> dict[str, Any]:
    """Turn a SQLAlchemy row mapping (or dict) into a JSON-serializable dict."""
    return {k: _json_safe(v) for k, v in dict(mapping).items()}


async def log_admin_action(
    db: AsyncSession,
    *,
    admin: User,
    action_type: str,
    target_table: str,
    target_id: Any,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    request: Request,
    notes: str | None = None,
) -> None:
    """Stage an admin_actions row. Caller commits (so it shares the mutation's txn)."""
    db.add(
        AdminAction(
            admin_user_id=admin.user_id,
            action_type=action_type,
            target_table=target_table,
            target_id=str(target_id) if target_id is not None else None,
            before_value=before,
            after_value=after,
            ip_hash=hash_ip(request),
            notes=notes,
        )
    )
