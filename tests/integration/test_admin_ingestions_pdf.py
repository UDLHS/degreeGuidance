"""Admin PDF-ingestion + promote tests (Admin Slice 1, Part C2 — masterplan §16.4).

Covers the async PDF path and the two-step promote flow:
- POST /ingestions with a .pdf -> 202, 'running' pdf_extraction run, Arq job
  enqueued (mocked — no live Redis needed), audited.
- the extraction job itself, run once against the real 2024 handbook, flips the
  run to success and writes a reviewable CSV.
- GET /ingestions/{id}/csv download.
- POST /ingestions/{id}/promote: stored CSV and re-uploaded CSV, plus the
  status/type/404 guards.

Isolation:
- enqueue is monkeypatched, so the suite never touches Redis.
- the ingestion work dir is redirected to a per-test tmp_path, so uploaded PDFs
  and extracted CSVs never pollute data/ingestion_work.
- the loader/job commit on the shared core.db engine, so (as in the C1 tests) we
  use sentinel exam_year=2030 + FK-safe teardown, and dispose that engine per test.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import create_access_token, hash_password

SENTINEL_YEAR = 2030
KNOWN_ALIAS = "MEDICINE (University of Colombo)"  # -> 001A
KNOWN_DISTRICT = "Colombo"
HANDBOOK = Path(__file__).resolve().parents[2] / "data" / "raw_handbooks" / "handbook_2024.pdf"

_FAKE_PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    """Redirect the ingestion work dir AND the permanent archive to throwaway
    tmp dirs for each test (promote snapshots/archives since Phase 7)."""
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path))
    monkeypatch.setattr(settings, "archive_dir", str(tmp_path / "archive"))
    return tmp_path


@pytest_asyncio.fixture(autouse=True)
async def _dispose_loader_engine():
    """The Step 4 loader and the extraction job commit on the shared (pooled)
    core.db.engine. Dispose it after each test so a pooled connection isn't
    reused on the next test's event loop."""
    yield
    from core.db import engine as loader_engine

    await loader_engine.dispose()


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"authtest-admin-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="admin")
    await db_session.execute(text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR})
    await db_session.execute(text("DELETE FROM ingestion_runs WHERE year = :y"), {"y": SENTINEL_YEAR})
    await db_session.execute(text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid})
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


@pytest_asyncio.fixture
async def student_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'student', true)"
        ),
        {"id": uid, "em": f"authtest-student-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="student")
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


@pytest.fixture
def enqueue_spy(monkeypatch):
    """Replace the real Arq enqueue with a recorder — no Redis needed."""
    calls: list[dict] = []

    async def _fake(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr("apps.api.routers.admin_ingestions.enqueue_extract_pdf", _fake)
    return calls


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _pdf_upload(content: bytes = _FAKE_PDF, *, year: int = SENTINEL_YEAR,
                filename: str = "handbook.pdf") -> dict:
    return {
        "files": {"file": (filename, content, "application/pdf")},
        "data": {"exam_year": str(year)},
    }


async def _insert_extraction_run(db: AsyncSession, *, status: str = "success") -> uuid.UUID:
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


# ---- auth gates ----

async def test_pdf_upload_requires_token(client: AsyncClient):
    r = await client.post("/api/admin/ingestions", **_pdf_upload())
    assert r.status_code == 401


async def test_promote_requires_token(client: AsyncClient):
    r = await client.post(f"/api/admin/ingestions/{uuid.uuid4()}/promote")
    assert r.status_code == 401


async def test_promote_rejects_student(client: AsyncClient, student_token: str):
    r = await client.post(
        f"/api/admin/ingestions/{uuid.uuid4()}/promote", headers=_auth(student_token)
    )
    assert r.status_code == 403


async def test_csv_download_requires_token(client: AsyncClient):
    r = await client.get(f"/api/admin/ingestions/{uuid.uuid4()}/csv")
    assert r.status_code == 401


# ---- PDF upload (enqueue mocked) ----

async def test_pdf_upload_enqueues_job(
    client: AsyncClient, admin_token: str, db_session: AsyncSession,
    enqueue_spy: list, work_dir: Path,
):
    r = await client.post("/api/admin/ingestions", headers=_auth(admin_token), **_pdf_upload())
    assert r.status_code == 202, r.text
    body = r.json()
    assert body["run_type"] == "pdf_extraction"
    assert body["status"] == "running"
    run_id = body["run_id"]

    # run row created in running/pdf_extraction state
    row = (
        await db_session.execute(
            text("SELECT run_type, status FROM ingestion_runs WHERE run_id = :r"),
            {"r": run_id},
        )
    ).first()
    assert row is not None
    assert row.run_type == "pdf_extraction"
    assert row.status == "running"

    # job enqueued with the right args, and the PDF persisted in the work dir
    assert len(enqueue_spy) == 1
    assert enqueue_spy[0]["run_id"] == run_id
    assert enqueue_spy[0]["exam_year"] == SENTINEL_YEAR
    assert (work_dir / f"{run_id}.pdf").exists()

    # audited
    audited = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM admin_actions WHERE action_type = 'ingestion.pdf_upload' "
                "AND target_id = :t"
            ),
            {"t": run_id},
        )
    ).scalar_one()
    assert audited == 1


async def test_pdf_upload_rejects_bad_magic(client: AsyncClient, admin_token: str, enqueue_spy: list):
    r = await client.post(
        "/api/admin/ingestions",
        headers=_auth(admin_token),
        **_pdf_upload(content=b"this is not a pdf"),
    )
    assert r.status_code == 415
    assert len(enqueue_spy) == 0  # nothing enqueued on rejection


async def test_unknown_extension_rejected(client: AsyncClient, admin_token: str):
    r = await client.post(
        "/api/admin/ingestions",
        headers=_auth(admin_token),
        files={"file": ("data.txt", b"x", "text/plain")},
        data={"exam_year": str(SENTINEL_YEAR)},
    )
    assert r.status_code == 415


# ---- extraction job (real handbook PDF) ----

@pytest.mark.skipif(not HANDBOOK.exists(), reason="2024 handbook PDF not present")
async def test_extract_job_real_pdf(db_session: AsyncSession, admin_token: str, work_dir: Path):
    """Staged lifecycle: extraction parks the run at needs_mapping with
    extraction_columns rows, a grid artifact and the whole-book presence set.
    The CSV is only written later by mapping/confirm; the PDF is retained."""
    from apps.worker.jobs.extract_pdf import extract_pdf_job

    rid = await _insert_extraction_run(db_session, status="running")
    pdf_copy = work_dir / f"{rid}.pdf"
    shutil.copy(HANDBOOK, pdf_copy)

    result = await extract_pdf_job(None, run_id=str(rid), pdf_path=str(pdf_copy), exam_year=SENTINEL_YEAR)
    assert result["status"] == "needs_mapping", result

    row = (
        await db_session.execute(
            text("SELECT status, records_processed, cutoff_pages FROM ingestion_runs WHERE run_id = :r"),
            {"r": rid},
        )
    ).first()
    assert row.status == "needs_mapping"
    assert row.records_processed > 6000  # ~6,525 grid cells in the 2024 handbook
    assert row.cutoff_pages == "179-188"  # auto-detected range recorded

    n_cols = (
        await db_session.execute(
            text("SELECT count(*) FROM extraction_columns WHERE run_id = :r"), {"r": rid}
        )
    ).scalar_one()
    assert n_cols > 250  # 262 logical columns

    prefilled = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM extraction_columns "
                "WHERE run_id = :r AND mapped_course_code IS NOT NULL"
            ),
            {"r": rid},
        )
    ).scalar_one()
    assert prefilled > 250  # exact code/alias hits are pre-filled for review

    assert (work_dir / f"{rid}.grid.json").exists()
    assert (work_dir / f"{rid}.presence.json").exists()
    assert not (work_dir / f"{rid}.csv").exists()  # CSV comes from mapping/confirm
    assert pdf_copy.exists()  # PDF retained for re-extract + confirm

    # both artifacts must also be in the DB store — in production the confirm
    # stage runs on a different machine than this worker
    kinds = {
        row[0]
        for row in (
            await db_session.execute(
                text("SELECT kind FROM ingestion_artifacts WHERE run_id = :r"), {"r": rid}
            )
        ).all()
    }
    assert {"grid.json", "presence.json"} <= kinds


# ---- CSV download ----

async def test_csv_download_ok(client: AsyncClient, admin_token: str, db_session: AsyncSession, work_dir: Path):
    rid = await _insert_extraction_run(db_session, status="success")
    (work_dir / f"{rid}.csv").write_text("district,001A\nColombo,2.5\n", encoding="utf-8")

    r = await client.get(f"/api/admin/ingestions/{rid}/csv", headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "001A" in r.text


async def test_csv_download_missing_file_is_404(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    rid = await _insert_extraction_run(db_session, status="success")  # no CSV on disk
    r = await client.get(f"/api/admin/ingestions/{rid}/csv", headers=_auth(admin_token))
    assert r.status_code == 404


async def test_csv_download_unknown_run_is_404(client: AsyncClient, admin_token: str):
    r = await client.get(f"/api/admin/ingestions/{uuid.uuid4()}/csv", headers=_auth(admin_token))
    assert r.status_code == 404


# ---- promote ----

async def test_promote_stored_csv(client: AsyncClient, admin_token: str, db_session: AsyncSession, work_dir: Path):
    rid = await _insert_extraction_run(db_session, status="success")
    (work_dir / f"{rid}.csv").write_text(
        f"district,{KNOWN_ALIAS}\n{KNOWN_DISTRICT},2.5000\n", encoding="utf-8"
    )

    r = await client.post(f"/api/admin/ingestions/{rid}/promote", headers=_auth(admin_token))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["run_type"] == "zscore"
    assert body["status"] == "success"
    assert body["processed"] == 1

    # cutoff landed under the sentinel year
    cutoff = (
        await db_session.execute(
            text("SELECT z_score FROM z_score_cutoffs WHERE year = :y AND course_code = '001A'"),
            {"y": SENTINEL_YEAR},
        )
    ).first()
    assert cutoff is not None and float(cutoff.z_score) == 2.5

    # extraction run linked to the produced zscore run + promotion audited
    note = (
        await db_session.execute(
            text("SELECT notes FROM ingestion_runs WHERE run_id = :r"), {"r": rid}
        )
    ).scalar_one()
    assert note is not None and body["run_id"] in note
    audited = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM admin_actions WHERE action_type = 'ingestion.promote' "
                "AND target_id = :t"
            ),
            {"t": body["run_id"]},
        )
    ).scalar_one()
    assert audited == 1


async def test_promote_reuploaded_csv(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    rid = await _insert_extraction_run(db_session, status="success")  # no stored CSV
    csv = f"district,{KNOWN_ALIAS}\n{KNOWN_DISTRICT},2.6000\n"
    r = await client.post(
        f"/api/admin/ingestions/{rid}/promote",
        headers=_auth(admin_token),
        files={"file": ("reviewed.csv", csv.encode("utf-8"), "text/csv")},
    )
    assert r.status_code == 200, r.text
    assert r.json()["processed"] == 1


async def test_promote_requires_success_status(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    rid = await _insert_extraction_run(db_session, status="running")
    r = await client.post(f"/api/admin/ingestions/{rid}/promote", headers=_auth(admin_token))
    assert r.status_code == 409


async def test_promote_rejects_non_extraction_run(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    rid = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO ingestion_runs (run_id, run_type, year, status) VALUES (:r, 'zscore', :y, 'success')"),
        {"r": rid, "y": SENTINEL_YEAR},
    )
    await db_session.commit()
    r = await client.post(f"/api/admin/ingestions/{rid}/promote", headers=_auth(admin_token))
    assert r.status_code == 422


async def test_promote_unknown_run_is_404(client: AsyncClient, admin_token: str):
    r = await client.post(f"/api/admin/ingestions/{uuid.uuid4()}/promote", headers=_auth(admin_token))
    assert r.status_code == 404
