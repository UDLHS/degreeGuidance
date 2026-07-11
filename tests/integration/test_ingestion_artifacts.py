"""Cross-instance artifact store (W2 follow-through).

In production the API and the Arq worker are separate Render services with
separate ephemeral disks; every stage handoff of the staged PDF pipeline
(pdf → grid/presence → csv/overrides/unmapped → promote) crosses machines.
These tests simulate that split by WIPING the local work dir between stages:
whatever survives did so through the ingestion_artifacts table, which is
exactly what production relies on.

Isolation follows the established pdf-suite pattern: per-test tmp work dir,
sentinel exam_year=2029 (loader bound is <=2030; 2030-2034 are taken by the
other suites), purge-first fixtures, FK-safe teardown, shared loader engine
disposed per test.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.ingestion.artifact_store import (
    artifact_exists,
    artifact_path,
    delete_artifact,
    load_artifact,
    local_artifact_path,
    put_artifact,
)
from core.security import create_access_token, hash_password

SENTINEL_YEAR = 2029
KNOWN_ALIAS = "MEDICINE (University of Colombo)"  # -> 001A via seeded aliases
COURSE = "001A"

_FAKE_PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path))
    monkeypatch.setattr(settings, "archive_dir", str(tmp_path / "archive"))
    return tmp_path


@pytest_asyncio.fixture(autouse=True)
async def _dispose_loader_engine():
    yield
    from core.db import engine as loader_engine

    await loader_engine.dispose()


def _wipe_local(work_dir: Path) -> None:
    """Simulate the next stage running on a different machine (or after a
    deploy): every work-dir file this 'instance' wrote is gone."""
    for p in work_dir.iterdir():
        if p.is_file():
            p.unlink()


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    # purge-first: a crashed prior run must not poison this one
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM ingestion_runs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"artifacts-admin-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="admin")
    # runs cascade to artifacts / extraction_columns / handbook_changes
    await db_session.execute(text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR})
    await db_session.execute(text("DELETE FROM ingestion_runs WHERE year = :y"), {"y": SENTINEL_YEAR})
    await db_session.execute(text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid})
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


@pytest.fixture
def enqueue_spy(monkeypatch):
    calls: list[dict] = []

    async def _fake(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr("apps.api.routers.admin_ingestions.enqueue_extract_pdf", _fake)
    return calls


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _insert_run(db: AsyncSession, *, status: str) -> uuid.UUID:
    rid = uuid.uuid4()
    await db.execute(
        text(
            "INSERT INTO ingestion_runs (run_id, run_type, year, status) "
            "VALUES (:r, 'pdf_extraction', :y, :s)"
        ),
        {"r": rid, "y": SENTINEL_YEAR, "s": status},
    )
    await db.commit()
    return rid


# ---- the store itself ----

async def test_store_roundtrip_rematerialize_and_delete(
    db_session: AsyncSession, work_dir: Path
):
    rid = await _insert_run(db_session, status="running")
    payload = b'{"hello": "artifact"}'

    path = await put_artifact(db_session, rid, "grid.json", payload)
    await db_session.commit()
    assert path == work_dir / f"{rid}.grid.json"
    assert path.read_bytes() == payload

    # different machine: local cache gone, DB copy serves and rematerializes
    _wipe_local(work_dir)
    assert not path.exists()
    assert await load_artifact(db_session, rid, "grid.json") == payload
    assert path.exists(), "load_artifact must rematerialize the cache file"

    # artifact_path yields a usable file even after another wipe
    _wipe_local(work_dir)
    resolved = await artifact_path(db_session, rid, "grid.json")
    assert resolved is not None and resolved.read_bytes() == payload

    # upsert overwrites
    await put_artifact(db_session, rid, "grid.json", b"v2")
    await db_session.commit()
    _wipe_local(work_dir)
    assert await load_artifact(db_session, rid, "grid.json") == b"v2"

    assert await artifact_exists(db_session, rid, "grid.json") is True
    assert await artifact_exists(db_session, rid, "nope.json") is False

    await delete_artifact(db_session, rid, "grid.json")
    await db_session.commit()
    assert await load_artifact(db_session, rid, "grid.json") is None
    assert await artifact_path(db_session, rid, "grid.json") is None

    await db_session.execute(
        text("DELETE FROM ingestion_runs WHERE run_id = :r"), {"r": rid}
    )
    await db_session.commit()


# ---- upload persists the PDF durably ----

async def test_upload_stores_pdf_artifact(
    client: AsyncClient, admin_token: str, db_session: AsyncSession,
    enqueue_spy: list, work_dir: Path,
):
    r = await client.post(
        "/api/admin/ingestions",
        headers=_auth(admin_token),
        files={"file": ("handbook.pdf", _FAKE_PDF, "application/pdf")},
        data={"exam_year": str(SENTINEL_YEAR)},
    )
    assert r.status_code == 202, r.text
    run_id = r.json()["run_id"]

    stored = (
        await db_session.execute(
            text("SELECT content FROM ingestion_artifacts WHERE run_id = :r AND kind = 'pdf'"),
            {"r": run_id},
        )
    ).scalar_one()
    assert bytes(stored) == _FAKE_PDF

    # the worker instance never saw this disk — the PDF is still reachable
    _wipe_local(work_dir)
    assert await artifact_exists(db_session, run_id, "pdf") is True
    resolved = await artifact_path(db_session, run_id, "pdf")
    assert resolved is not None and resolved.read_bytes() == _FAKE_PDF


# ---- download + promote read through the store ----

async def test_csv_download_rematerializes_from_db(
    client: AsyncClient, admin_token: str, db_session: AsyncSession, work_dir: Path
):
    rid = await _insert_run(db_session, status="success")
    await put_artifact(
        db_session, rid, "csv", "district,001A\nColombo,2.5\n".encode("utf-8")
    )
    await db_session.commit()

    _wipe_local(work_dir)  # the confirm ran on another instance
    r = await client.get(f"/api/admin/ingestions/{rid}/csv", headers=_auth(admin_token))
    assert r.status_code == 200
    assert "001A" in r.text


async def test_promote_stored_csv_after_disk_wipe(
    client: AsyncClient, admin_token: str, db_session: AsyncSession, work_dir: Path
):
    rid = await _insert_run(db_session, status="success")
    csv_bytes = f"district,{KNOWN_ALIAS}\nColombo,2.5000\n".encode("utf-8")
    await put_artifact(db_session, rid, "csv", csv_bytes)
    await db_session.commit()

    _wipe_local(work_dir)  # promote runs on a fresh instance after a deploy
    r = await client.post(f"/api/admin/ingestions/{rid}/promote", headers=_auth(admin_token))
    assert r.status_code == 200, r.text
    assert r.json()["processed"] == 1

    z = (
        await db_session.execute(
            text("SELECT z_score FROM z_score_cutoffs WHERE year = :y AND course_code = :c"),
            {"y": SENTINEL_YEAR, "c": COURSE},
        )
    ).scalar_one()
    assert float(z) == 2.5


# ---- worker job resolves the PDF via the store ----

async def test_extract_job_fails_cleanly_when_pdf_nowhere(
    db_session: AsyncSession, work_dir: Path
):
    from apps.worker.jobs.extract_pdf import extract_pdf_job

    rid = await _insert_run(db_session, status="running")
    result = await extract_pdf_job(
        None, run_id=str(rid), pdf_path=str(work_dir / f"{rid}.pdf"),
        exam_year=SENTINEL_YEAR,
    )
    assert result["status"] == "failed"

    err = (
        await db_session.execute(
            text("SELECT error_log FROM ingestion_runs WHERE run_id = :r"), {"r": rid}
        )
    ).scalar_one()
    assert "artifact store" in err

    await db_session.execute(text("DELETE FROM ingestion_runs WHERE run_id = :r"), {"r": rid})
    await db_session.commit()


# ---- the full split-instance chain: confirm + promote from DB only ----

async def test_confirm_and_promote_survive_disk_wipes(
    client: AsyncClient, admin_token: str, db_session: AsyncSession, work_dir: Path
):
    """Upload machine ≠ extract machine ≠ confirm machine ≠ promote machine.
    Between every stage the disk is wiped; only ingestion_artifacts carries
    the pipeline forward — the production topology."""
    rid = await _insert_run(db_session, status="needs_mapping")
    await db_session.execute(
        text(
            "INSERT INTO extraction_columns "
            "(run_id, column_key, page_number, raw_label, mapped_course_code, status) "
            "VALUES (:r, 'p1c1', 1, :label, :code, 'confirmed')"
        ),
        {"r": rid, "label": COURSE, "code": COURSE},  # label == code: no alias learning
    )
    # the grid artifact was written by the worker on ITS machine
    grid = '{"columns": [{"column_key": "p1c1", "values": {"COLOMBO": "1.8000"}}]}'
    await put_artifact(db_session, rid, "grid.json", grid.encode("utf-8"))
    await db_session.commit()

    _wipe_local(work_dir)  # confirm runs on the API instance
    r = await client.post(
        f"/api/admin/ingestions/{rid}/mapping/confirm", headers=_auth(admin_token)
    )
    assert r.status_code == 200, r.text
    assert r.json()["csv_ready"] is True

    kinds = {
        row[0]
        for row in (
            await db_session.execute(
                text("SELECT kind FROM ingestion_artifacts WHERE run_id = :r"), {"r": rid}
            )
        ).all()
    }
    assert "csv" in kinds, "confirm must persist the CSV durably, not just on disk"

    _wipe_local(work_dir)  # promote happens days later, after a redeploy
    r = await client.post(f"/api/admin/ingestions/{rid}/promote", headers=_auth(admin_token))
    assert r.status_code == 200, r.text

    # confirm's CSV carries every district row (blanks included), so filter
    z = (
        await db_session.execute(
            text(
                "SELECT z.z_score FROM z_score_cutoffs z "
                "JOIN districts d ON d.district_id = z.district_id "
                "WHERE z.year = :y AND z.course_code = :c AND d.code = 'COLOMBO'"
            ),
            {"y": SENTINEL_YEAR, "c": COURSE},
        )
    ).scalar_one()
    assert float(z) == 1.8
