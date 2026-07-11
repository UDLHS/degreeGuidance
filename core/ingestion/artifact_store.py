"""Cross-instance artifact store for the staged ingestion pipeline.

Production runs the API and the Arq worker as separate services with separate
ephemeral disks (Render), so a file one process writes is invisible to the
other — and even a single instance loses its disk on every deploy. The
work-dir file convention ({run_id}.<kind>) therefore can't be the source of
truth in production.

This module makes the ingestion_artifacts table the durable copy and demotes
the local work dir to a cache:

- put_artifact  — upsert the DB row (commits with the caller's transaction)
                  and refresh the local cache file.
- load_artifact — local file first; else the DB row, rematerializing the
                  cache file for subsequent path-based reads.
- artifact_path — like load_artifact but returns a real local Path, for
                  consumers that need a filename (pdfplumber, FileResponse,
                  the Step-4 loader).

One code path everywhere: on a laptop the cache always hits (same disk), on
split services the DB fills the gap. Nothing here is year- or format-aware —
artifacts are keyed by run, so future handbook uploads need no changes.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import IngestionArtifact


def _work_dir() -> Path:
    d = Path(settings.ingestion_work_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def local_artifact_path(run_id: str | uuid.UUID, kind: str) -> Path:
    """The artifact's work-dir cache location ({run_id}.<kind>)."""
    return _work_dir() / f"{run_id}.{kind}"


async def put_artifact(
    db: AsyncSession, run_id: str | uuid.UUID, kind: str, content: bytes
) -> Path:
    """Write-through: upsert the DB row and refresh the local cache file.
    The DB write commits (or rolls back) with the caller's transaction; the
    cache file is best-effort and safe to lose. Returns the local path."""
    stmt = pg_insert(IngestionArtifact.__table__).values(
        run_id=uuid.UUID(str(run_id)), kind=kind, content=content
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_artifact_run_kind",
        set_={"content": stmt.excluded.content, "updated_at": func.now()},
    )
    await db.execute(stmt)
    path = local_artifact_path(run_id, kind)
    path.write_bytes(content)
    return path


async def load_artifact(
    db: AsyncSession, run_id: str | uuid.UUID, kind: str
) -> bytes | None:
    """The artifact's bytes: local cache first, else the DB row (which also
    rematerializes the cache). None if it exists nowhere."""
    path = local_artifact_path(run_id, kind)
    if path.exists():
        return path.read_bytes()
    content = (
        await db.execute(
            select(IngestionArtifact.content).where(
                IngestionArtifact.run_id == uuid.UUID(str(run_id)),
                IngestionArtifact.kind == kind,
            )
        )
    ).scalar_one_or_none()
    if content is not None:
        path.write_bytes(content)
    return content


async def artifact_path(
    db: AsyncSession, run_id: str | uuid.UUID, kind: str
) -> Path | None:
    """A real local file for path-based consumers, rematerialized from the DB
    if this instance doesn't have it. None if the artifact exists nowhere."""
    content = await load_artifact(db, run_id, kind)
    return local_artifact_path(run_id, kind) if content is not None else None


async def artifact_exists(
    db: AsyncSession, run_id: str | uuid.UUID, kind: str
) -> bool:
    if local_artifact_path(run_id, kind).exists():
        return True
    n = (
        await db.execute(
            select(func.count())
            .select_from(IngestionArtifact)
            .where(
                IngestionArtifact.run_id == uuid.UUID(str(run_id)),
                IngestionArtifact.kind == kind,
            )
        )
    ).scalar_one()
    return bool(n)


async def delete_artifact(
    db: AsyncSession, run_id: str | uuid.UUID, kind: str
) -> None:
    """Remove the artifact everywhere (DB row + local cache). Used to clear a
    stale optional artifact from a prior confirm attempt."""
    await db.execute(
        delete(IngestionArtifact).where(
            IngestionArtifact.run_id == uuid.UUID(str(run_id)),
            IngestionArtifact.kind == kind,
        )
    )
    local_artifact_path(run_id, kind).unlink(missing_ok=True)
