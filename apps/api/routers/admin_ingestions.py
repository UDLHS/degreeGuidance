"""Admin ingestion endpoints (Admin Slice 1, Parts C1 + C2 — masterplan §14.3).

POST /api/admin/ingestions          -- upload a .csv (reviewed merged cutoffs) OR
                                       a .pdf (a handbook). CSV runs the Step 4
                                       loader synchronously and returns the
                                       summary (201). PDF persists the file,
                                       creates a 'running' extraction run, enqueues
                                       the Arq extraction job, and returns 202.
GET  /api/admin/ingestions          -- list runs (newest first, paginated).
GET  /api/admin/ingestions/{id}     -- run detail + parse_errors triage queue.
GET  /api/admin/ingestions/{id}/csv -- download the extracted CSV for review.
POST /api/admin/ingestions/{id}/promote
                                    -- commit the reviewed CSV (re-uploaded, or
                                       the stored extract) via the Step 4 loader.

Two-step PDF flow (§7.1 human-review guarantee): upload PDF -> extract (Arq) ->
review the CSV -> promote. The multi-minute pdfplumber extraction runs in the
worker, never in the request (masterplan §4.2).

Every route is gated by require_admin; every mutation writes an admin_actions row.

Upload safety (handoff §11.B): extension allow-list (.csv/.pdf) else 415; hard
size caps (CSV 5 MB, PDF 30 MB) else 413; PDF magic-byte check; bytes written to
server-named files only (never the client filename in a path); exam_year bounds
checked at the Form and the loader.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pathlib import Path

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from apps.api.queue import enqueue_extract_pdf, enqueue_generate_factsheet_draft
from apps.worker.jobs.ingest_zscores import (
    apply_stream_overrides,
    apply_unmapped_cutoffs,
    cutoff_coverage_gaps,
    ingest_zscores,
)
from core.config import settings
from core.eligibility.subject_requirements import validate_subject_rule
from core.ingestion.artifact_store import (
    artifact_exists,
    artifact_path,
    delete_artifact,
    load_artifact,
    local_artifact_path,
    put_artifact,
)
from core.ingestion.catalog_audit import audit_aptitude, audit_streams
from core.ingestion.column_mapper import normalize_label
from core.ingestion.course_details import details_from_artifact
from core.ingestion.grid_extractor import DISTRICTS_ORDER, parse_pages_spec
from core.ingestion.handbook_diff import compute_handbook_diff, record_changes
from core.ingestion.rule_suggest import suggest_subject_rule
from core.ingestion.stream_tags import resolve_group_streams, suggest_stream_codes
from core.ingestion.unicode_section import split_label
from core.models.auth import User
from core.models.cutoffs import (
    ExtractionColumn,
    HandbookChange,
    IngestionRun,
    ParseError,
)
from core.schemas.admin_ingestion import (
    AptitudeAuditItem,
    BulkConfirmResponse,
    CatalogAuditItem,
    CatalogAuditResponse,
    ChangeApplyResponse,
    ColumnListResponse,
    ColumnUpdate,
    ExtractPagesRequest,
    ExtractionColumnOut,
    HandbookChangeListResponse,
    HandbookChangeOut,
    HandbookChangeUpdate,
    IngestionCreateResponse,
    IngestionRunDetail,
    IngestionRunListResponse,
    IngestionRunOut,
    MappingConfirmResponse,
    ParseErrorOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:ingestions"],
    dependencies=[Depends(get_current_admin)],  # gate every route in this router
)

# A merged cutoff CSV is ~50 KB; a handbook PDF is ~6 MB. Caps bound abuse.
_MAX_CSV_BYTES = 5 * 1024 * 1024
_MAX_PDF_BYTES = 30 * 1024 * 1024


# ── Yearly-loop hardening (Phase 7 of docs/PHASE2_STUDENT_ADMIN_PLAN.md) ─────

def _archive_dir(year: int) -> Path:
    d = Path(settings.archive_dir) / str(year)
    d.mkdir(parents=True, exist_ok=True)
    return d


async def snapshot_year_data(
    db: AsyncSession, year: int, tag: str, run_id: str | None = None
) -> list[str]:
    """Pre-promote safety snapshot: dump the year's CURRENT rows (cutoffs +
    stream overrides + codeless) to CSVs in the archive before anything is
    overwritten, so every promote is reversible in one step. No-op for a year
    with no data yet. When run_id is given (the promote path), each dump is
    also stored as a run artifact — the archive dir is ephemeral in
    production, the DB copy is the one that makes the undo real. Returns the
    written paths (relative to archive_dir)."""
    written: list[str] = []

    async def _dump(query: str, header: list[str], name: str) -> None:
        rows = (await db.execute(text(query), {"y": year})).all()
        if not rows:
            return
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(header)
        w.writerows(rows)
        path = _archive_dir(year) / f"{name}_{tag}.csv"
        path.write_text(buf.getvalue(), encoding="utf-8-sig")
        if run_id is not None:
            # kind is tag-less: each re-promote overwrites, keeping exactly
            # the state before the LATEST promote — the one-step undo source.
            await put_artifact(db, run_id, f"{name}.csv", buf.getvalue().encode("utf-8-sig"))
        written.append(str(Path(str(year)) / path.name))

    await _dump(
        "SELECT z.course_code, d.code, z.z_score, z.notes FROM z_score_cutoffs z "
        "JOIN districts d ON d.district_id = z.district_id WHERE z.year = :y "
        "ORDER BY z.course_code, d.code",
        ["course_code", "district", "z_score", "notes"],
        "snapshot_cutoffs",
    )
    await _dump(
        "SELECT o.course_code, d.code, s.code, o.z_score, o.notes "
        "FROM course_stream_cutoff_overrides o "
        "JOIN districts d ON d.district_id = o.district_id "
        "JOIN streams s ON s.stream_id = o.stream_id WHERE o.year = :y "
        "ORDER BY o.course_code, d.code, s.code",
        ["course_code", "district", "stream", "z_score", "notes"],
        "snapshot_stream_overrides",
    )
    await _dump(
        "SELECT u.raw_label, u.course_name, u.university, d.code, u.z_score, u.notes "
        "FROM unmapped_cutoffs u JOIN districts d ON d.district_id = u.district_id "
        "WHERE u.year = :y ORDER BY u.raw_label, d.code",
        ["raw_label", "course_name", "university", "district", "z_score", "notes"],
        "snapshot_unmapped",
    )
    return written


async def archive_run_artifacts(
    db: AsyncSession, run_id: str, year: int, tag: str
) -> list[str]:
    """Copy the promoted run's artifacts (raw handbook PDF, final CSV,
    overrides/unmapped JSON) into the per-year archive dir. Sources come
    through the artifact store, so they rematerialize from the DB even when
    this instance never held the files (split API/worker in production).
    Returns the written paths (relative to archive_dir)."""
    import shutil

    written: list[str] = []
    mapping = {
        "pdf": f"handbook_{year}_{tag}.pdf",
        "csv": f"promoted_{tag}.csv",
        "overrides.json": f"overrides_{tag}.json",
        "unmapped.json": f"unmapped_{tag}.json",
    }
    for kind, dst_name in mapping.items():
        src = await artifact_path(db, run_id, kind)
        if src is not None:
            dst = _archive_dir(year) / dst_name
            shutil.copyfile(src, dst)
            written.append(str(Path(str(year)) / dst_name))
    return written


async def build_promote_checklist(
    db: AsyncSession, year: int, run_id: str | None = None
) -> dict:
    """Post-promote review card: everything the admin must eyeball, computed
    fresh from the DB (year-agnostic — future uploads change numbers, not code).
    With run_id, also reports how many of THIS book's newly-added courses are
    fully onboarded (active + streams + factsheet) — Phase 8.3."""
    gaps = await cutoff_coverage_gaps(db, year)
    overrides = (
        await db.execute(
            text("SELECT count(*) FROM course_stream_cutoff_overrides WHERE year = :y"),
            {"y": year},
        )
    ).scalar() or 0
    codeless = (
        await db.execute(
            text("SELECT count(*) FROM unmapped_cutoffs WHERE year = :y"), {"y": year}
        )
    ).scalar() or 0
    latest = (
        await db.execute(text("SELECT max(year) FROM z_score_cutoffs"))
    ).scalar()
    checklist = {
        "promoted_year": year,
        "students_now_see": latest,
        "is_default_year": latest == year,
        "coverage_gap_count": len(gaps),
        "coverage_gaps": list(gaps)[:15],
        "stream_override_rows": overrides,
        "codeless_rows": codeless,
    }

    if run_id is not None:
        added = [
            r.course_code
            for r in (
                await db.execute(
                    text(
                        "SELECT course_code FROM handbook_changes "
                        "WHERE run_id = :r AND change_type = 'course_added'"
                    ),
                    {"r": run_id},
                )
            ).all()
        ]
        pending: list[str] = []
        for code in added:
            row = (
                await db.execute(
                    text(
                        "SELECT c.is_active, "
                        "(SELECT count(*) FROM course_stream_eligibility cse "
                        " WHERE cse.course_code = c.course_code) AS stream_count, "
                        "EXISTS (SELECT 1 FROM factsheets f "
                        " WHERE f.course_number = c.course_number) AS has_factsheet "
                        "FROM courses c WHERE c.course_code = :c"
                    ),
                    {"c": code},
                )
            ).first()
            onboarded = (
                row is not None
                and bool(row.is_active)
                and int(row.stream_count) > 0
                and bool(row.has_factsheet)
            )
            if not onboarded:
                pending.append(code)
        checklist["new_courses_total"] = len(added)
        checklist["new_courses_onboarded"] = len(added) - len(pending)
        checklist["new_courses_pending"] = pending[:15]

    return checklist


async def _step4_on_bytes(content: bytes, exam_year: int, triggered_by: str) -> dict:
    """Write CSV bytes to a server-named temp file and run the Step 4 loader."""
    fd, tmp_path = tempfile.mkstemp(suffix=".csv", prefix="ingest_")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(content)
        return await ingest_zscores(tmp_path, exam_year, triggered_by=triggered_by)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@router.post("/ingestions/upload-ticket", summary="Mint a short-lived token for a direct browser upload")
async def create_upload_ticket(admin: User = Depends(get_current_admin)) -> dict:
    """The admin UI uploads handbooks straight to this API: Vercel caps
    proxied request bodies at 4.5 MB and handbooks run 6-15 MB, so the file
    cannot go through the BFF. The BFF (which alone holds the admin's
    long-lived token) calls this to mint a 10-minute token that the browser
    holds in memory just long enough to POST the file. Nothing long-lived
    ever reaches the browser."""
    from core.security import create_access_token

    minutes = 10
    return {
        "token": create_access_token(
            subject=str(admin.user_id), role=admin.role, expires_minutes=minutes
        ),
        "expires_in_minutes": minutes,
    }


@router.post(
    "/ingestions",
    response_model=IngestionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a reviewed CSV (Step 4, sync) or upload a handbook PDF (Arq, async)",
)
async def create_ingestion(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    exam_year: int = Form(..., ge=2010, le=2030),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> IngestionCreateResponse:
    filename = file.filename or ""
    lower = filename.lower()
    if lower.endswith(".csv"):
        kind, cap = "csv", _MAX_CSV_BYTES
    elif lower.endswith(".pdf"):
        kind, cap = "pdf", _MAX_PDF_BYTES
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .csv or .pdf uploads are accepted.",
        )

    content = await file.read(cap + 1)
    if len(content) > cap:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Upload exceeds the {cap // (1024 * 1024)} MB limit.",
        )

    # --- CSV: synchronous Step 4 (Part C1) ---
    if kind == "csv":
        try:
            summary = await _step4_on_bytes(
                content, exam_year, triggered_by=f"admin:{admin.user_id}"
            )
        except ValueError as exc:  # bad exam_year backstop / empty CSV
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
            ) from exc
        await log_admin_action(
            db, admin=admin, action_type="ingestion.create",
            target_table="ingestion_runs", target_id=summary["run_id"],
            before=None, after=summary, request=request,
            notes=f"exam_year={exam_year}, file={filename}",
        )
        await db.commit()
        return IngestionCreateResponse(run_type="zscore", **summary)

    # --- PDF: persist + enqueue async extraction (Part C2) ---
    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File does not look like a valid PDF (missing %PDF header).",
        )
    run = IngestionRun(
        run_type="pdf_extraction",
        source_label=f"pdf_upload:{filename}",
        year=exam_year,
        status="running",
        triggered_by=f"admin:{admin.user_id}",
    )
    db.add(run)
    await db.flush()  # populate run.run_id
    run_id = str(run.run_id)
    # DB is the durable copy (the worker is a separate machine in production);
    # the work-dir file is the local cache. Committed together with the run.
    await put_artifact(db, run_id, "pdf", content)

    await log_admin_action(
        db, admin=admin, action_type="ingestion.pdf_upload",
        target_table="ingestion_runs", target_id=run_id, before=None,
        after={"run_id": run_id, "exam_year": exam_year, "file": filename},
        request=request,
    )
    await db.commit()  # commit BEFORE enqueue so the worker can see run + PDF

    await enqueue_extract_pdf(
        run_id=run_id, pdf_path=str(local_artifact_path(run_id, "pdf")), exam_year=exam_year
    )
    response.status_code = status.HTTP_202_ACCEPTED
    return IngestionCreateResponse(run_id=run_id, status="running", run_type="pdf_extraction")


@router.get("/ingestions", response_model=IngestionRunListResponse)
async def list_ingestions(
    status_filter: str | None = Query(None, alias="status"),
    year: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> IngestionRunListResponse:
    filters = []
    if status_filter is not None:
        filters.append(IngestionRun.status == status_filter)
    if year is not None:
        filters.append(IngestionRun.year == year)

    total = (
        await db.execute(select(func.count()).select_from(IngestionRun).where(*filters))
    ).scalar_one()
    rows = (
        await db.execute(
            select(IngestionRun)
            .where(*filters)
            .order_by(IngestionRun.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()

    return IngestionRunListResponse(
        total=total, items=[IngestionRunOut.model_validate(r) for r in rows]
    )


@router.get("/ingestions/{run_id}", response_model=IngestionRunDetail)
async def get_ingestion(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> IngestionRunDetail:
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")

    errors = (
        await db.execute(
            select(ParseError)
            .where(ParseError.run_id == run_id)
            .order_by(ParseError.error_id)
        )
    ).scalars().all()

    return IngestionRunDetail(
        **IngestionRunOut.model_validate(run).model_dump(),
        parse_error_count=len(errors),
        parse_errors=[ParseErrorOut.model_validate(e) for e in errors],
    )


@router.get("/ingestions/{run_id}/csv")
async def download_ingestion_csv(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Download the extracted CSV for human review before promotion."""
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")
    csv_path = await artifact_path(db, str(run_id), "csv")
    if csv_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extracted CSV not available for this run.",
        )
    return FileResponse(
        str(csv_path), media_type="text/csv", filename=f"ingestion_{run_id}.csv"
    )


@router.get("/ingestions/{run_id}/catalog-audit", response_model=CatalogAuditResponse)
async def catalog_audit(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> CatalogAuditResponse:
    """Phase 9.3b — measure the LIVE catalog against this book.

    The gate protects new courses; this protects the ones already here. Financial
    Economics/131 was offered to all six streams for a year when the book grants
    only Arts and Commerce — nobody was wrong on purpose, nothing ever compared
    the two. Read-only: it reports, an admin decides which side is right.

    Reads the extraction's course_details.json artifact, so it costs a query
    rather than re-opening the PDF. A run from before that artifact existed
    simply reports nothing to compare.
    """
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")

    raw = await load_artifact(db, str(run_id), "course_details.json")
    details = details_from_artifact(json.loads(raw)) if raw is not None else {}
    found = await audit_streams(db, details)
    # invisible first: it costs a student a degree they could have had, whereas
    # over_granted shows them one they cannot take.
    found.sort(key=lambda d: (d.severity != "invisible", d.course_number))

    # Phase 9.6 — the aptitude flag, measured against the book's own test
    # table. None (artifact absent or table unreadable) compares nothing:
    # an unreadable table is not a claim that nobody needs a test.
    apt_raw = await load_artifact(db, str(run_id), "aptitude_codes.json")
    apt_payload = json.loads(apt_raw) if apt_raw else None
    apt_found = await audit_aptitude(
        db,
        set(apt_payload["codes"]) if apt_payload and apt_payload.get("codes") else None,
        apt_payload.get("page") if apt_payload else None,
    )
    return CatalogAuditResponse(
        exam_year=run.year,
        courses_in_book=len(details),
        aptitude_items=[
            AptitudeAuditItem(
                course_code=a.course_code,
                name=a.name,
                book_requires=a.book_requires,
                db_requires=a.db_requires,
                page_number=a.page_number,
                severity=a.severity,
            )
            for a in apt_found
        ],
        items=[
            CatalogAuditItem(
                course_number=d.course_number,
                name=d.name,
                book_streams=d.book_streams,
                db_streams=d.db_streams,
                only_in_book=d.only_in_book,
                only_in_db=d.only_in_db,
                page_number=d.page_number,
                book_may_be_incomplete=d.book_may_be_incomplete,
                severity=d.severity,
            )
            for d in found
        ],
    )


async def _unfinished_new_courses(db: AsyncSession, run_id: uuid.UUID) -> list[dict]:
    """Phase 9.3 — every new course in this run must be finished before the
    year's cutoffs may promote. There are two ways a new course silently
    disappears, and this closes both:

    - still pending, or approved but never applied → the course row does not
      exist, so its cutoff rows fail to load (`unknown_course_alias` in the
      Step-4 loader) and the course is absent from the year entirely;
    - applied but inactive or streamless → the row exists, but the engine can
      never serve it (it requires a course_stream_eligibility match).

    A rejected change IS finished — the admin decided. Returns the blockers.
    """
    rows = (
        await db.execute(
            text(
                "SELECT ch.course_code, ch.status, "
                "  (c.course_code IS NOT NULL) AS course_exists, "
                "  COALESCE(c.is_active, false)  AS is_active, "
                "  (SELECT count(*) FROM course_stream_eligibility cse "
                "     WHERE cse.course_code = ch.course_code) AS stream_count "
                "FROM handbook_changes ch "
                "LEFT JOIN courses c ON c.course_code = ch.course_code "
                "WHERE ch.run_id = :r AND ch.change_type = 'course_added' "
                "ORDER BY ch.course_code"
            ),
            {"r": run_id},
        )
    ).all()

    blockers: list[dict] = []
    for r in rows:
        if r.status == "rejected":
            continue
        if r.status != "applied" or not r.course_exists:
            blockers.append({
                "course_code": r.course_code,
                "reason": (
                    f"not created yet (status={r.status}) — its cutoffs would be "
                    "dropped and the course would be missing from this year"
                ),
            })
        elif not r.is_active:
            blockers.append({
                "course_code": r.course_code,
                "reason": "inactive — no student can see it",
            })
        elif r.stream_count == 0:
            blockers.append({
                "course_code": r.course_code,
                "reason": "no eligible streams — invisible to every student",
            })
    return blockers


@router.post("/ingestions/{run_id}/promote", response_model=IngestionCreateResponse)
async def promote_ingestion(
    run_id: uuid.UUID,
    request: Request,
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> IngestionCreateResponse:
    """Commit a reviewed extraction to z_score_cutoffs via the Step 4 loader.

    Promotes the re-uploaded reviewed CSV if one is supplied; otherwise the CSV
    the extraction job produced. Creates a separate 'zscore' run and links it to
    the extraction run (both directions).
    """
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")
    if run.run_type != "pdf_extraction":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Only pdf_extraction runs can be promoted.",
        )
    if run.status != "success":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Extraction is not in 'success' state (status={run.status}).",
        )
    # Phase 9.3 — refuse BEFORE any work (snapshot/loader) while this book's new
    # courses are unfinished. Previously the checklist only counted them after
    # the fact, so a new course could promote straight into invisibility.
    unfinished = await _unfinished_new_courses(db, run_id)
    if unfinished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": (
                    f"{len(unfinished)} new course(s) from this book are unfinished. "
                    "Finish them in the change review (or reject the ones you don't "
                    "want) before promoting — otherwise they are silently missing "
                    "for students."
                ),
                "unfinished_new_courses": unfinished,
            },
        )
    exam_year = run.year
    triggered_by = f"admin:{admin.user_id}:promote:{run_id}"
    tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Pre-promote safety snapshot (Phase 7.2): if this year already has data,
    # dump it to the archive FIRST so the promote is reversible in one step.
    snapshot_paths = await snapshot_year_data(db, exam_year, tag, run_id=str(run_id))

    reviewed_provided = file is not None and bool(file.filename)
    if reviewed_provided:
        if not (file.filename or "").lower().endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Reviewed upload must be a .csv.",
            )
        content = await file.read(_MAX_CSV_BYTES + 1)
        if len(content) > _MAX_CSV_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"Reviewed CSV exceeds the {_MAX_CSV_BYTES // (1024 * 1024)} MB limit.",
            )
        try:
            summary = await _step4_on_bytes(content, exam_year, triggered_by)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
            ) from exc
    else:
        csv_path = await artifact_path(db, str(run_id), "csv")
        if csv_path is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No extracted CSV available to promote; re-upload a reviewed CSV.",
            )
        try:
            summary = await ingest_zscores(str(csv_path), exam_year, triggered_by=triggered_by)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
            ) from exc
        # Stream-variant columns from Gate 2 (e.g. 107L's Commerce vs
        # Bio/Physical Science split) aren't in the stored CSV's plain values
        # -- apply them now that the base rows exist. Skipped when a
        # hand-reviewed CSV was uploaded instead: we can't assume the stored
        # mapping's stream intent still matches a hand-edited replacement.
        await apply_stream_overrides(db, str(run_id), exam_year)
        # Codeless columns (real z-scores, no Uni-Code) -> unmapped_cutoffs.
        await apply_unmapped_cutoffs(db, str(run_id), exam_year)

    # Permanent per-year archive (Phase 7.3): raw PDF + final CSV + artifacts.
    archived = snapshot_paths + await archive_run_artifacts(db, str(run_id), exam_year, tag)
    # Post-promote checklist (Phase 7.4): what the admin must eyeball now
    # (incl. Phase 8.3's "new courses: X of Y onboarded" for this run's book).
    checklist = await build_promote_checklist(db, exam_year, run_id=str(run_id))
    checklist["archived"] = archived

    # link the extraction run to the produced zscore run
    run.notes = (
        f"promoted -> zscore run {summary['run_id']}; "
        f"students now see {checklist['students_now_see']} by default; "
        f"{checklist['coverage_gap_count']} coverage gap(s); "
        f"{len(archived)} file(s) archived"
    )
    await log_admin_action(
        db, admin=admin, action_type="ingestion.promote",
        target_table="ingestion_runs", target_id=summary["run_id"],
        before=None, after={**summary, "checklist": checklist}, request=request,
        notes=f"promoted from extraction run {run_id}; reviewed_upload={reviewed_provided}",
    )
    await db.commit()
    return IngestionCreateResponse(run_type="zscore", checklist=checklist, **summary)


# ── Staged extraction lifecycle (Phase 1 pipeline) ───────────────────────────

@router.post(
    "/ingestions/{run_id}/extract",
    response_model=IngestionCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-extract with an admin-supplied cutoff page range",
)
async def reextract_with_pages(
    run_id: uuid.UUID,
    payload: ExtractPagesRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> IngestionCreateResponse:
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")
    if run.run_type != "pdf_extraction":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Only pdf_extraction runs can be re-extracted")
    if run.status not in ("needs_pages", "needs_mapping", "failed"):
        raise HTTPException(status.HTTP_409_CONFLICT,
                            detail=f"Run is {run.status}; re-extract only from "
                                   f"needs_pages / needs_mapping / failed")
    try:
        parse_pages_spec(payload.cutoff_pages)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc))

    if not await artifact_exists(db, str(run_id), "pdf"):
        raise HTTPException(status.HTTP_409_CONFLICT,
                            detail="Uploaded PDF no longer available; upload the handbook again")

    before_pages = run.cutoff_pages
    run.status = "running"
    run.cutoff_pages = payload.cutoff_pages
    run.error_log = None
    await log_admin_action(
        db, admin=admin, action_type="ingestion.reextract",
        target_table="ingestion_runs", target_id=str(run_id),
        before={"cutoff_pages": before_pages}, after={"cutoff_pages": payload.cutoff_pages},
        request=request,
    )
    await db.commit()
    await enqueue_extract_pdf(
        run_id=str(run_id), pdf_path=str(local_artifact_path(str(run_id), "pdf")),
        exam_year=run.year, cutoff_pages=payload.cutoff_pages,
    )
    return IngestionCreateResponse(run_id=str(run_id), status="running", run_type="pdf_extraction")


def _stream_set(col: ExtractionColumn) -> set[str]:
    return {s.strip().upper() for s in (col.override_streams or "").split(",") if s.strip()}


def _is_valid_stream_split(cols: list[ExtractionColumn]) -> bool:
    """True if a group of confirmed columns sharing one course code is a
    legitimate disjoint stream split (e.g. 107L's Commerce vs Bio/Physical
    Science columns) rather than a real duplicate that must be resolved by
    ignoring the extras.

    Allowed shapes: at most one column with no override_streams (the
    "general" column, feeding the normal cutoffs row as always), plus any
    number of override-tagged columns whose stream sets are pairwise
    disjoint. Anything else (two plain columns, or two override columns
    sharing a stream) is a real conflict.
    """
    if len(cols) <= 1:
        return True
    plain = [c for c in cols if not _stream_set(c)]
    overridden = [c for c in cols if _stream_set(c)]
    if len(plain) > 1:
        return False
    seen: set[str] = set()
    for c in overridden:
        streams = _stream_set(c)
        if not streams or (streams & seen):
            return False
        seen |= streams
    return True


def _duplicate_mappings(cols: list[ExtractionColumn]) -> dict[str, int]:
    """Effective code -> #columns targeting it, for codes where that's a real
    conflict (ignored columns excluded; legitimate stream splits excluded)."""
    by_code: dict[str, list[ExtractionColumn]] = {}
    for c in cols:
        if c.status == "ignored":
            continue
        code = c.mapped_course_code or c.suggested_course_code
        if code:
            by_code.setdefault(code, []).append(c)
    return {
        code: len(group)
        for code, group in by_code.items()
        if len(group) > 1 and not _is_valid_stream_split(group)
    }


def _is_numeric_cell(v) -> bool:
    """True if a grid cell holds an actual z-score (not NQC / blank)."""
    if v is None:
        return False
    s = str(v).strip()
    if not s or s.upper() == "NQC":
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


async def _columns_with_data(db: AsyncSession, run_id: uuid.UUID) -> set[str] | None:
    """column_keys whose grid values include >=1 real z-score, from the
    grid.json artifact. None if the artifact is missing (unknown)."""
    raw = await load_artifact(db, str(run_id), "grid.json")
    if raw is None:
        return None
    artifact = json.loads(raw)
    keys: set[str] = set()
    for gc in artifact.get("columns", []):
        if any(_is_numeric_cell(v) for v in (gc.get("values") or {}).values()):
            keys.add(gc["column_key"])
    return keys


def _group_stream_suggestions(cols: list[ExtractionColumn]) -> dict[int, list[str]]:
    """Pre-filled override_streams per column. For columns that share a course
    code (a same-course stream split), streams are assigned disjointly with the
    complement rule (open 'any subject' column -> the non-ICT universe minus the
    streams its siblings already claim); standalone columns fall back to their
    own bracket tag."""
    by_code: dict[str, list[ExtractionColumn]] = {}
    for c in cols:
        if c.status == "ignored":
            continue
        code = c.mapped_course_code or c.suggested_course_code
        if code:
            by_code.setdefault(code, []).append(c)

    result: dict[int, list[str]] = {}
    for code, grp in by_code.items():
        if len(grp) > 1:
            resolved = resolve_group_streams([g.raw_label for g in grp])
            for g, streams in zip(grp, resolved):
                result[g.column_id] = streams
    return result


@router.get("/ingestions/{run_id}/columns", response_model=ColumnListResponse)
async def list_columns(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ColumnListResponse:
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")
    cols = (
        await db.execute(
            select(ExtractionColumn)
            .where(ExtractionColumn.run_id == run_id)
            .order_by(ExtractionColumn.page_number, ExtractionColumn.column_key)
        )
    ).scalars().all()
    counts: dict[str, int] = {}
    for c in cols:
        counts[c.status] = counts.get(c.status, 0) + 1

    group_streams = _group_stream_suggestions(cols)
    with_data = await _columns_with_data(db, run_id)

    items = []
    for c in cols:
        out = ExtractionColumnOut.model_validate(c)
        out.suggested_override_streams = group_streams.get(
            c.column_id, suggest_stream_codes(c.raw_label)
        )
        out.has_data = None if with_data is None else (c.column_key in with_data)
        items.append(out)

    return ColumnListResponse(
        run_status=run.status,
        cutoff_pages=run.cutoff_pages,
        total=len(cols),
        counts=counts,
        duplicate_mappings=_duplicate_mappings(cols),
        items=items,
    )


@router.patch("/ingestions/{run_id}/columns/{column_id}", response_model=ExtractionColumnOut)
async def update_column(
    run_id: uuid.UUID,
    column_id: int,
    payload: ColumnUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> ExtractionColumnOut:
    col = await db.get(ExtractionColumn, column_id)
    if col is None or col.run_id != run_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Column not found for this run")

    before = {
        "mapped_course_code": col.mapped_course_code,
        "status": col.status,
        "override_streams": col.override_streams,
    }

    if payload.mapped_course_code is not None:
        code = payload.mapped_course_code.strip().upper()
        exists = (
            await db.execute(text("SELECT 1 FROM courses WHERE course_code = :c"), {"c": code})
        ).first()
        if not exists:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=f"Unknown course_code {code}")
        col.mapped_course_code = code
        col.status = "confirmed"

    if payload.override_streams is not None:
        streams = [s.strip().upper() for s in payload.override_streams.split(",") if s.strip()]
        if streams:
            valid = set(
                (await db.execute(
                    text("SELECT code FROM streams WHERE code = ANY(:codes)"), {"codes": streams}
                )).scalars().all()
            )
            unknown = [s for s in streams if s not in valid]
            if unknown:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT,
                                    detail=f"Unknown stream code(s): {', '.join(unknown)}")
        col.override_streams = ",".join(streams) if streams else None

    if payload.status is not None:
        if payload.status == "confirmed" and not col.mapped_course_code:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail="Cannot confirm a column with no mapped_course_code")
        if payload.status == "unmapped_kept":
            # keep-without-code is only for a column that actually HAS z-scores
            # to preserve (else it's just an empty column -> ignore). This is
            # the "z-score table has it but the Uni-Code table doesn't" case.
            with_data = await _columns_with_data(db, run_id)
            if with_data is not None and col.column_key not in with_data:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="This column has no z-score values to keep — use 'ignored' instead.",
                )
            col.mapped_course_code = None   # codeless by definition
            col.override_streams = None
        col.status = payload.status

    col.updated_at = datetime.now(timezone.utc)
    await log_admin_action(
        db, admin=admin, action_type="extraction_column.update",
        target_table="extraction_columns", target_id=str(column_id),
        before=before,
        after={
            "mapped_course_code": col.mapped_course_code,
            "status": col.status,
            "override_streams": col.override_streams,
        },
        request=request, notes=col.column_key,
    )
    await db.commit()
    await db.refresh(col)
    out = ExtractionColumnOut.model_validate(col)
    out.suggested_override_streams = suggest_stream_codes(col.raw_label)
    return out


@router.post("/ingestions/{run_id}/columns/confirm-suggested", response_model=BulkConfirmResponse)
async def confirm_suggested_columns(
    run_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> BulkConfirmResponse:
    """Bulk-confirm every pending column whose suggestion was an exact hit
    (printed code or alias, confidence 1.0). Name-similarity suggestions stay
    pending for individual review."""
    cols = (
        await db.execute(
            select(ExtractionColumn).where(
                ExtractionColumn.run_id == run_id,
                ExtractionColumn.status == "pending",
            )
        )
    ).scalars().all()
    # guard: only catalog codes may be mapped (a 'book_new' suggestion carries
    # a code the catalog doesn't have yet — the course must be created first)
    valid_codes = set(
        (await db.execute(text("SELECT course_code FROM courses"))).scalars().all()
    )
    confirmed = 0
    now = datetime.now(timezone.utc)
    for c in cols:
        if (
            c.suggested_course_code
            and c.suggested_course_code in valid_codes
            and c.suggestion_confidence is not None
            and float(c.suggestion_confidence) >= 0.999
        ):
            c.mapped_course_code = c.suggested_course_code
            c.status = "confirmed"
            c.updated_at = now
            confirmed += 1
    remaining = len(cols) - confirmed
    await log_admin_action(
        db, admin=admin, action_type="extraction_column.bulk_confirm",
        target_table="extraction_columns", target_id=str(run_id),
        before=None, after={"confirmed": confirmed, "remaining_pending": remaining},
        request=request,
    )
    await db.commit()
    return BulkConfirmResponse(confirmed=confirmed, remaining_pending=remaining)


async def _book_prefill(
    db: AsyncSession,
    artifact: dict,
    by_code: dict[str, list[ExtractionColumn]],
    course_details: dict[str, dict[str, Any]] | None = None,
    aptitude_codes: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Phase 9.2 — what the BOOK already told us about each course, for the
    new-course review gate: code -> {name_en, university_id, book_university,
    book_page, suggested_stream_codes, book_requirements_text, book_intake,
    streams_may_be_incomplete}.

    Three sources, all already extracted:
    - the book's own "Uni-Codes Assigned for each Course of Study" section
      (core.ingestion.unicode_section), carried in this run's grid artifact as
      book_code_rows — the book's authoritative name + university + page;
    - the cutoff column's bracket tag (core.ingestion.stream_tags), which
      SUGGESTS streams and returns [] when the book says nothing, so the admin
      must still choose consciously;
    - Section 2.2 (core.ingestion.course_details, artifact course_details.json,
      keyed by the 3-digit course number) — the book's own statement of which
      streams may apply, plus its requirement prose. This WINS over the bracket
      tag: the tag is a hint on a cutoff column, §2.2 is the book stating the
      rule. Where §2.2 could not be read completely, streams_may_be_incomplete
      rides along so the gate can say so instead of quietly under-granting.

    university_id resolves by exact NORMALISED name match only — never a fuzzy
    guess. An unresolved university is simply left out and the book's raw string
    is passed through for display, so the admin picks it rather than
    rubber-stamping a wrong match.
    """
    out: dict[str, dict[str, Any]] = {}

    unis = (await db.execute(text("SELECT university_id, name_en FROM universities"))).all()
    uni_by_norm = {normalize_label(u.name_en): u.university_id for u in unis}

    for r in artifact.get("book_code_rows") or []:
        code = str(r.get("code") or "").strip().upper()
        if not code:
            continue
        detail: dict[str, Any] = {}
        if r.get("course_name"):
            detail["name_en"] = str(r["course_name"]).strip()
        raw_uni = str(r.get("university") or "").strip()
        if raw_uni:
            detail["book_university"] = raw_uni
            uid = uni_by_norm.get(normalize_label(raw_uni))
            if uid is not None:
                detail["university_id"] = uid
        if r.get("page_number") is not None:
            detail["book_page"] = r["page_number"]
        out[code] = detail

    # Stream suggestion: the union of every tag across a code's columns. A split
    # code (107L: Commerce vs Bio/Physical) is eligible for BOTH — the
    # disjointness only decides which CUTOFF applies, not who may apply.
    for code, grp in by_code.items():
        suggested: list[str] = []
        for col in grp:
            for s in suggest_stream_codes(col.raw_label or ""):
                if s not in suggested:
                    suggested.append(s)
        if suggested:
            out.setdefault(code.strip().upper(), {})["suggested_stream_codes"] = sorted(suggested)

    # For the deterministic rule suggestion (9.6b) — a suggested subject name
    # that matches no catalog subject would match no STUDENT either, so an
    # unvalidatable suggestion is dropped here, never shown.
    known_subjects = {
        r.name_en for r in (await db.execute(text("SELECT name_en FROM subjects"))).all()
    }
    known_streams = {
        r.code for r in (await db.execute(text("SELECT code FROM streams"))).all()
    }

    # Section 2.2 last: it is the book STATING the rule, so it overrides the
    # bracket-tag hint above. Keyed by course number (019A -> 019), because the
    # book documents a course once and the Uni-Code adds the university.
    for code in list(out) + [c.strip().upper() for c in by_code]:
        num = code[:3]
        cd = (course_details or {}).get(num)
        if not cd:
            continue
        detail = out.setdefault(code, {})
        # 9.6b — a rule SUGGESTION read from the book's own sentence, only when
        # the whole sentence parses into one unconditional route (see
        # core/ingestion/rule_suggest.py). The admin reviews it in the editable
        # rule box against the prose shown beside it; the D6 gate re-validates
        # at approve. No parse -> no suggestion -> the box stays empty.
        if cd.get("requirements_text"):
            suggestion = suggest_subject_rule(cd["requirements_text"])
            if suggestion is not None and not validate_subject_rule(
                suggestion, known_subjects=known_subjects, known_streams=known_streams
            ):
                detail["suggested_subject_rule"] = suggestion
        if cd.get("stream_codes"):
            detail["suggested_stream_codes"] = sorted(cd["stream_codes"])
        if cd.get("streams_may_be_incomplete"):
            # the book also grants entry by subject list: what we read is a
            # floor, so the admin must widen it rather than tick and move on
            detail["streams_may_be_incomplete"] = True
        if cd.get("requirements_text"):
            detail["book_requirements_text"] = cd["requirements_text"]
        if cd.get("proposed_intake") is not None:
            detail["book_intake"] = cd["proposed_intake"]
        if cd.get("page_number") is not None:
            # §2.2 is where the details are — better provenance than the
            # Uni-Code table's page for everything except the name/university
            detail["book_details_page"] = cd["page_number"]
        if not detail.get("name_en") and cd.get("name"):
            detail["name_en"] = cd["name"]
        # Phase 9.6 — the block's remaining printed facts. Absent = the book
        # printed nothing; never defaulted.
        if cd.get("duration_years") is not None:
            detail["book_duration_years"] = cd["duration_years"]
        if cd.get("medium_text"):
            detail["book_medium_text"] = cd["medium_text"]
            detail["book_medium_codes"] = list(cd.get("medium_codes") or [])
            if cd.get("medium_needs_review"):
                # per-institution mediums (e.g. Siddha/036: Jaffna-Tamil,
                # Trincomalee-English) — a human assigns them per Uni-Code
                detail["book_medium_needs_review"] = True

    # Phase 9.6 — the practical/aptitude-test table is per Uni-Code and only a
    # STATEMENT when the table was actually read: then a code's absence means
    # "no test". aptitude_codes=None (table unreadable / older run) states
    # nothing, so the field is simply absent.
    if aptitude_codes is not None:
        for code in set(out) | {c.strip().upper() for c in by_code}:
            out.setdefault(code, {})["book_requires_aptitude"] = code in aptitude_codes

    return out


@router.post("/ingestions/{run_id}/mapping/confirm", response_model=MappingConfirmResponse)
async def confirm_mapping(
    run_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> MappingConfirmResponse:
    """Finalize Gate 2: write the Step-4 CSV from admin-confirmed columns,
    learn new aliases, run the diff (with the whole-book safeguard) and stage
    the change-set. The run becomes 'success'; cutoffs still go live only via
    the existing promote endpoint."""
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")
    if run.status != "needs_mapping":
        raise HTTPException(status.HTTP_409_CONFLICT,
                            detail=f"Run is {run.status}; mapping can only be confirmed from needs_mapping")

    cols = (
        await db.execute(
            select(ExtractionColumn).where(ExtractionColumn.run_id == run_id)
        )
    ).scalars().all()
    pending = [c for c in cols if c.status == "pending"]
    if pending:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"{len(pending)} column(s) still pending — confirm or ignore each "
                   f"(e.g. {', '.join(c.column_key for c in pending[:5])})",
        )
    used = [c for c in cols if c.status == "confirmed" and c.mapped_course_code]
    # columns preserved WITHOUT a Uni-Code (real z-scores, no code in the book)
    kept_unmapped = [c for c in cols if c.status == "unmapped_kept"]
    if not used and not kept_unmapped:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="No confirmed or kept columns to commit")

    by_code: dict[str, list[ExtractionColumn]] = {}
    for c in used:
        by_code.setdefault(c.mapped_course_code, []).append(c)

    bad_dups = {
        code: grp for code, grp in by_code.items()
        if len(grp) > 1 and not _is_valid_stream_split(grp)
    }
    if bad_dups:
        detail = "; ".join(
            f"{code}: {', '.join(c.column_key for c in grp)}" for code, grp in list(bad_dups.items())[:5]
        )
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Multiple confirmed columns map to the same course — set the extras to "
                   f"'ignored', or mark them as distinct stream variants (override_streams). {detail}",
        )

    grid_raw = await load_artifact(db, str(run_id), "grid.json")
    if grid_raw is None:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            detail="Grid artifact missing; re-extract the PDF first")
    artifact = json.loads(grid_raw)
    values_by_key: dict[str, dict[str, str | None]] = {
        c["column_key"]: c["values"] for c in artifact["columns"]
    }
    for c in used + kept_unmapped:
        if c.column_key not in values_by_key:
            raise HTTPException(status.HTTP_409_CONFLICT,
                                detail=f"Column {c.column_key} not in the grid artifact; re-extract")

    # learn aliases: printed label -> confirmed code (next year resolves exactly).
    # source carries the exam year (e.g. 'mapping_confirm:2023') so the admin
    # aliases page shows which run learned it, not just a generic label.
    alias_source = f"mapping_confirm:{run.year}"
    aliases_learned = 0
    for c in used:
        label = (c.raw_label or "").strip()
        if not label or label == c.mapped_course_code:
            continue
        res = await db.execute(text(
            "INSERT INTO course_aliases (course_code, alias_text, source, confidence, is_verified) "
            "VALUES (:code, :alias, :source, 1.0, true) "
            "ON CONFLICT ON CONSTRAINT uq_alias_per_course DO NOTHING"
        ), {"code": c.mapped_course_code, "alias": label, "source": alias_source})
        aliases_learned += res.rowcount or 0

    # One CSV column per course code (headers are course codes — self-aliases
    # from migration 17). A code whose group has a plain (non-override)
    # confirmed column uses its real values as always. A code where EVERY
    # confirmed column is a stream-variant override (e.g. 107L, Commerce vs
    # Bio/Physical Science) still gets a header so the base cutoffs row
    # exists, but with blank values -- no single number is honest for it. The
    # real per-stream numbers are written to course_stream_cutoff_overrides at
    # promote time (apply_stream_overrides) via the overrides.json artifact
    # below.
    codes_sorted = sorted(
        by_code.keys(),
        key=lambda code: min((c.page_number, c.column_key) for c in by_code[code]),
    )
    representative: dict[str, ExtractionColumn | None] = {
        code: next((c for c in grp if not _stream_set(c)), None)
        for code, grp in by_code.items()
    }
    override_columns = [c for c in used if _stream_set(c)]

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([""] + codes_sorted)
    for district in DISTRICTS_ORDER:
        row = [district]
        for code in codes_sorted:
            rep = representative[code]
            row.append(values_by_key[rep.column_key].get(district) or "" if rep else "")
        writer.writerow(row)
    await put_artifact(db, str(run_id), "csv", buf.getvalue().encode("utf-8-sig"))

    if override_columns:
        overrides_payload = {
            "columns": [
                {
                    "course_code": c.mapped_course_code,
                    "column_key": c.column_key,
                    "stream_codes": sorted(_stream_set(c)),
                    "raw_label": c.raw_label,
                    "values": values_by_key[c.column_key],
                }
                for c in override_columns
            ]
        }
        await put_artifact(
            db, str(run_id), "overrides.json",
            json.dumps(overrides_payload).encode("utf-8"),
        )
    else:
        # clear a stale artifact from a prior confirm attempt
        await delete_artifact(db, str(run_id), "overrides.json")

    # codeless columns: real z-scores, no Uni-Code -> preserved verbatim into
    # unmapped_cutoffs at promote (apply_unmapped_cutoffs), never into the CSV.
    if kept_unmapped:
        unmapped_payload = {
            "columns": [
                {
                    "column_key": c.column_key,
                    "raw_label": c.raw_label,
                    "course_name": split_label(c.raw_label)[0] or None,
                    "university": split_label(c.raw_label)[1] or None,
                    "values": values_by_key[c.column_key],
                }
                for c in kept_unmapped
            ]
        }
        await put_artifact(
            db, str(run_id), "unmapped.json",
            json.dumps(unmapped_payload).encode("utf-8"),
        )
    else:
        await delete_artifact(db, str(run_id), "unmapped.json")

    # diff with the whole-book safeguard (uses the same representative choice
    # as the CSV -- a split-only code compares blank->blank, no false delta,
    # except a one-time transition the first year a code becomes split)
    extracted: dict[str, dict[str, str]] = {}
    for code in codes_sorted:
        rep = representative[code]
        extracted[code] = (
            {d: v for d, v in values_by_key[rep.column_key].items() if v is not None}
            if rep else {}
        )
    presence_raw = await load_artifact(db, str(run_id), "presence.json")
    present = set(json.loads(presence_raw)) if presence_raw is not None else None
    await db.execute(delete(HandbookChange).where(HandbookChange.run_id == run_id))
    # Phase 9.2: hand the diff what the book already said about each course, so a
    # new course arrives at the review gate pre-filled instead of blank. The
    # Section-2.2 artifact is written by the extraction job; an older run that
    # predates it simply has no entries, and every reader treats a missing entry
    # as "the book said nothing" rather than as a claim.
    details_raw = await load_artifact(db, str(run_id), "course_details.json")
    course_details = json.loads(details_raw) if details_raw else {}
    aptitude_raw = await load_artifact(db, str(run_id), "aptitude_codes.json")
    aptitude_payload = json.loads(aptitude_raw) if aptitude_raw else None
    aptitude_codes = (
        set(aptitude_payload.get("codes") or [])
        if aptitude_payload and aptitude_payload.get("codes")
        else None
    )
    book_details = await _book_prefill(
        db, artifact, by_code, course_details, aptitude_codes=aptitude_codes
    )
    changes = await compute_handbook_diff(
        db, extracted, run.year, present_in_book=present, book_details=book_details
    )
    await record_changes(db, run_id, changes)
    change_counts: dict[str, int] = {}
    for ch in changes:
        change_counts[ch.change_type] = change_counts.get(ch.change_type, 0) + 1

    ignored = sum(1 for c in cols if c.status == "ignored")
    run.status = "success"
    run.notes = (
        f"mapping confirmed: {len(used)} columns used, {ignored} ignored, "
        f"{aliases_learned} new aliases learned"
        + (f", {len(override_columns)} stream-variant column(s)" if override_columns else "")
        + (f", {len(kept_unmapped)} kept without code" if kept_unmapped else "")
        + "; changes: "
        + (", ".join(f"{k}={v}" for k, v in sorted(change_counts.items())) or "none")
        + " — CSV ready for review & promote"
    )
    await log_admin_action(
        db, admin=admin, action_type="ingestion.mapping_confirm",
        target_table="ingestion_runs", target_id=str(run_id),
        before=None,
        after={"columns_used": len(used), "ignored": ignored,
               "aliases_learned": aliases_learned, "changes": change_counts,
               "stream_variant_columns": len(override_columns),
               "unmapped_kept_columns": len(kept_unmapped)},
        request=request,
    )
    await db.commit()
    return MappingConfirmResponse(
        columns_used=len(used),
        columns_ignored=ignored,
        csv_ready=True,
        changes=change_counts,
        aliases_learned=aliases_learned,
        stream_variant_columns=len(override_columns),
        unmapped_kept_columns=len(kept_unmapped),
    )


# ── Handbook change-set review (Phase A1 diff engine) ───────────────────────

@router.get("/ingestions/{run_id}/changes", response_model=HandbookChangeListResponse)
async def list_changes(
    run_id: uuid.UUID,
    status_filter: str | None = Query(None, alias="status"),
    change_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> HandbookChangeListResponse:
    """The diff change-set for a run, grouped for review. counts is by status
    across the whole run; items honour the optional status/type filters."""
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")

    filters = [HandbookChange.run_id == run_id]
    if status_filter:
        filters.append(HandbookChange.status == status_filter)
    if change_type:
        filters.append(HandbookChange.change_type == change_type)

    rows = (
        await db.execute(
            select(HandbookChange)
            .where(*filters)
            .order_by(HandbookChange.change_type, HandbookChange.course_code)
        )
    ).scalars().all()

    count_rows = (
        await db.execute(
            select(HandbookChange.status, func.count())
            .where(HandbookChange.run_id == run_id)
            .group_by(HandbookChange.status)
        )
    ).all()

    # D6: which new-course NUMBERS already have a baseline subject rule (e.g. a
    # course re-added under a number curated before) — the gate then shows
    # "rule exists" instead of asking for one. One query for the whole run.
    added_numbers = {
        r.course_code[:3]
        for r in rows
        if r.change_type == "course_added" and r.course_code[:3].isdigit()
    }
    with_rule: set[str] = set()
    if added_numbers:
        with_rule = {
            r.course_number
            for r in (
                await db.execute(
                    text(
                        "SELECT DISTINCT course_number FROM course_requirements "
                        "WHERE course_number = ANY(:nums) AND exam_year IS NULL"
                    ),
                    {"nums": list(added_numbers)},
                )
            ).all()
        }

    items: list[HandbookChangeOut] = []
    for r in rows:
        out = HandbookChangeOut.model_validate(r)
        if r.change_type == "course_added":
            out.subject_rule_exists = r.course_code[:3] in with_rule
        items.append(out)

    return HandbookChangeListResponse(
        total=len(rows),
        counts={s: c for s, c in count_rows},
        items=items,
    )


async def _validate_stream_codes(db: AsyncSession, codes: list[str]) -> list[str]:
    """Normalise + validate stream codes against the streams table.

    Mirrors admin_courses.replace_course_streams so the two write paths into
    course_stream_eligibility can never disagree about what a valid code is.
    """
    known = {r.code for r in (await db.execute(text("SELECT code FROM streams"))).all()}
    cleaned = sorted({c.strip().upper() for c in codes if c and c.strip()})
    unknown = [c for c in cleaned if c not in known]
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Unknown stream code(s): {', '.join(unknown)}. "
                f"Valid: {', '.join(sorted(known))}"
            ),
        )
    return cleaned


@router.patch("/ingestions/{run_id}/changes/{change_id}", response_model=HandbookChangeOut)
async def update_change(
    run_id: uuid.UUID,
    change_id: int,
    payload: HandbookChangeUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> HandbookChangeOut:
    """Approve or reject one change. For a course_added the admin supplies the
    university_id + name_en + stream_codes here (merged into after_value) so
    apply can create a complete, visible course.

    Phase 9 D1: approving a course_added requires all three. Approving without
    streams used to produce a course no student could ever see, silently."""
    ch = await db.get(HandbookChange, change_id)
    if ch is None or ch.run_id != run_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change not found for this run")
    if ch.status == "applied":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Change already applied")

    if ch.change_type == "course_added":
        merged = dict(ch.after_value or {})
        if payload.university_id is not None:
            merged["university_id"] = payload.university_id
        if payload.name_en:
            merged["name_en"] = payload.name_en
        if payload.stream_codes is not None:
            merged["stream_codes"] = await _validate_stream_codes(db, payload.stream_codes)

        # D6 — the subject rule, validated the moment it is supplied so a typo
        # dies here, not in production where it would silently hide the course
        # from every student whose subjects never string-match it.
        number = ch.course_code[:3] if ch.course_code[:3].isdigit() else None
        rule_exists = bool(
            number
            and (
                await db.execute(
                    text(
                        "SELECT 1 FROM course_requirements "
                        "WHERE course_number = :n AND exam_year IS NULL LIMIT 1"
                    ),
                    {"n": number},
                )
            ).first()
        )
        if payload.subject_rule is not None:
            if rule_exists:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=(
                        f"Course number {number} already has a curated subject rule "
                        "(see the Subject Rules page) — the gate will not overwrite "
                        "it. Approve without a rule here."
                    ),
                )
            known_subjects = {
                r.name_en for r in (await db.execute(text("SELECT name_en FROM subjects"))).all()
            }
            known_streams = {
                r.code for r in (await db.execute(text("SELECT code FROM streams"))).all()
            }
            errors = validate_subject_rule(
                payload.subject_rule,
                known_subjects=known_subjects,
                known_streams=known_streams,
            )
            if errors:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Subject rule is invalid: " + "; ".join(errors[:8]),
                )
            merged["subject_rule"] = payload.subject_rule
        ch.after_value = merged

        # D1 + D6 gate — only on approve; a reject needs no details at all.
        if payload.status == "approved":
            missing = [
                field
                for field in ("university_id", "name_en", "stream_codes")
                if not merged.get(field)
            ]
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=(
                        f"Cannot approve {ch.course_code}: missing {', '.join(missing)}. "
                        "A new course needs a university, a name and at least one "
                        "eligible stream — without a stream no student can ever see it."
                    ),
                )
            if not rule_exists and not merged.get("subject_rule"):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=(
                        f"Cannot approve {ch.course_code}: no subject rule. Streams "
                        "decide who SEES the course; the subject rule decides who "
                        "QUALIFIES — without one the engine serves it to every "
                        "student in the ticked streams regardless of their "
                        "subjects. Write the rule from the book's own wording "
                        "shown on this card (an 'any 3 passes' course is "
                        '{"type": "any_n_subjects", "count": 3}).'
                    ),
                )

    before_status = ch.status
    ch.status = payload.status
    ch.resolved_by = f"admin:{admin.user_id}"
    ch.resolved_at = datetime.now(timezone.utc)

    await log_admin_action(
        db, admin=admin, action_type="handbook_change.review",
        target_table="handbook_changes", target_id=str(change_id),
        before={"status": before_status}, after={"status": ch.status}, request=request,
        notes=payload.notes,
    )
    await db.commit()
    await db.refresh(ch)
    return HandbookChangeOut.model_validate(ch)


@router.post("/ingestions/{run_id}/changes/apply", response_model=ChangeApplyResponse)
async def apply_changes(
    run_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> ChangeApplyResponse:
    """Apply every approved course_added / course_removed change. Removed courses
    are deactivated (is_active=false, retained for chat/history); added courses
    are created as inactive stubs the admin then completes. cutoff_changed rows
    are informational — the numbers promote through the Step-4 loader."""
    run = await db.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")

    approved = (
        await db.execute(
            select(HandbookChange).where(
                HandbookChange.run_id == run_id,
                HandbookChange.status == "approved",
                HandbookChange.change_type.in_(("course_added", "course_removed")),
            )
        )
    ).scalars().all()

    applied_removed = applied_added = 0
    created_numbers: list[str | None] = []
    skipped: list[dict] = []
    now = datetime.now(timezone.utc)
    # stream code -> id, resolved once for the course_added inserts below
    stream_ids = {
        r.code: r.stream_id
        for r in (await db.execute(text("SELECT stream_id, code FROM streams"))).all()
    }

    for ch in approved:
        if ch.change_type == "course_removed":
            hit = (
                await db.execute(
                    text(
                        "UPDATE courses SET is_active = false, updated_at = now() "
                        "WHERE course_code = :c AND is_active = true RETURNING course_code"
                    ),
                    {"c": ch.course_code},
                )
            ).first()
            if hit is None:
                skipped.append({"course_code": ch.course_code, "reason": "not found or already inactive"})
                continue
            ch.status, ch.resolved_by, ch.resolved_at = "applied", f"admin:{admin.user_id}", now
            await log_admin_action(
                db, admin=admin, action_type="course.deactivate", target_table="courses",
                target_id=ch.course_code, before={"is_active": True}, after={"is_active": False},
                request=request, notes=f"handbook-sync removal (run {run_id})",
            )
            applied_removed += 1

        else:  # course_added
            av = ch.after_value or {}
            uni, name = av.get("university_id"), av.get("name_en")
            streams = list(av.get("stream_codes") or [])
            # Defensive (Phase 9 D1): the approve gate already enforces all
            # three, but a change approved by an older build can still be
            # streamless. Never create a course no student can see.
            if not uni or not name or not streams:
                skipped.append({
                    "course_code": ch.course_code,
                    "reason": "needs university_id + name_en + stream_codes",
                })
                continue
            unknown_streams = [c for c in streams if c not in stream_ids]
            if unknown_streams:
                skipped.append({
                    "course_code": ch.course_code,
                    "reason": f"unknown stream code(s): {', '.join(unknown_streams)}",
                })
                continue
            if not (await db.execute(text("SELECT 1 FROM universities WHERE university_id = :u"), {"u": uni})).first():
                skipped.append({"course_code": ch.course_code, "reason": f"unknown university_id {uni}"})
                continue
            if (await db.execute(text("SELECT 1 FROM courses WHERE course_code = :c"), {"c": ch.course_code})).first():
                ch.status, ch.resolved_by, ch.resolved_at = "applied", f"admin:{admin.user_id}", now
                skipped.append({"course_code": ch.course_code, "reason": "already exists; marked applied"})
                continue
            course_number = ch.course_code[:3] if ch.course_code[:3].isdigit() else None
            # Created ACTIVE (Phase 9 D1). Safe only because approve guarantees
            # eligible streams, written in this same transaction below: the
            # course becomes visible and complete together, or not at all.
            # Duration and the aptitude flag ride along when the book printed
            # them (Phase 9.6) — read facts, shown on the gate card the admin
            # just approved; absent = NULL/false, never a default.
            await db.execute(
                text(
                    "INSERT INTO courses (course_code, course_number, university_id, "
                    "  name_en, is_active, duration_years, requires_aptitude_test) "
                    "VALUES (:code, :num, :uni, :name, true, :dur, :apt)"
                ),
                {
                    "code": ch.course_code, "num": course_number, "uni": uni, "name": name,
                    "dur": av.get("book_duration_years"),
                    "apt": bool(av.get("book_requires_aptitude")),
                },
            )
            # Mediums (Phase 9.6): written only when the book's Medium field
            # parsed to unambiguous language names. A per-institution medium
            # (book_medium_needs_review) writes nothing — a human assigns it.
            for mcode in av.get("book_medium_codes") or []:
                await db.execute(
                    text(
                        "INSERT INTO course_mediums (course_code, medium_id) "
                        "SELECT :cc, medium_id FROM mediums WHERE code = :mc "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {"cc": ch.course_code, "mc": mcode},
                )
            for sc in streams:
                await db.execute(
                    text(
                        "INSERT INTO course_stream_eligibility (course_code, stream_id) "
                        "VALUES (:cc, :sid)"
                    ),
                    {"cc": ch.course_code, "sid": stream_ids[sc]},
                )
            # D6 — the gate-approved subject rule lands in the SAME transaction
            # as the course and its streams: who-sees-it and who-qualifies
            # arrive together, or not at all. An existing baseline rule for the
            # number wins (curated data is never clobbered from here); the gate
            # refuses a rule when one exists, so both being present means two
            # Uni-Codes of one number in the same run — the first write took it.
            rule = av.get("subject_rule")
            if rule and course_number:
                already = (
                    await db.execute(
                        text(
                            "SELECT 1 FROM course_requirements "
                            "WHERE course_number = :n AND exam_year IS NULL LIMIT 1"
                        ),
                        {"n": course_number},
                    )
                ).first()
                if not already:
                    await db.execute(
                        text(
                            "INSERT INTO course_requirements "
                            "(course_number, exam_year, subject_rule, notes) "
                            "VALUES (:n, NULL, CAST(:rule AS jsonb), :notes)"
                        ),
                        {
                            "n": course_number,
                            "rule": json.dumps(rule),
                            "notes": f"authored at the new-course gate (run {run_id})",
                        },
                    )
                    await log_admin_action(
                        db, admin=admin, action_type="course_requirement.create",
                        target_table="course_requirements", target_id=course_number,
                        before=None, after={"subject_rule": rule}, request=request,
                        notes=f"handbook-sync addition (run {run_id})",
                    )
            ch.status, ch.resolved_by, ch.resolved_at = "applied", f"admin:{admin.user_id}", now
            await log_admin_action(
                db, admin=admin, action_type="course.create", target_table="courses",
                target_id=ch.course_code, before=None,
                after={
                    "course_code": ch.course_code, "university_id": uni, "name_en": name,
                    "is_active": True, "stream_codes": streams,
                },
                request=request, notes=f"handbook-sync addition (run {run_id})",
            )
            applied_added += 1
            created_numbers.append(course_number)

    await db.commit()

    # Phase 9.4 — a course just arrived; start writing its factsheet DRAFT from
    # this book's own facts, so the slot the admin sees is pre-filled instead
    # of empty. Draft-only (D4: nothing reaches the advisor until approved),
    # and strictly best-effort: a queue outage must never fail the apply.
    for num in dict.fromkeys(created_numbers):  # de-duped, insertion order
        if num is None:
            continue
        has_factsheet = (
            await db.execute(
                text("SELECT 1 FROM factsheets WHERE course_number = :cn"), {"cn": num}
            )
        ).first()
        if has_factsheet:
            continue
        try:
            await db.execute(
                text(
                    "INSERT INTO factsheet_drafts (course_number, status) "
                    "VALUES (:cn, 'queued') "
                    "ON CONFLICT (course_number) DO UPDATE SET "
                    "  status = 'queued', content = NULL, error = NULL, "
                    "  provenance = NULL, updated_at = now()"
                ),
                {"cn": num},
            )
            await db.commit()
            await enqueue_generate_factsheet_draft(course_number=num, run_id=str(run_id))
        except Exception:  # noqa: BLE001 - best-effort; the button still exists
            await db.rollback()
            logger.warning(
                "could not enqueue factsheet draft for course number %s", num, exc_info=True
            )

    return ChangeApplyResponse(
        applied_removed=applied_removed, applied_added=applied_added, skipped=skipped
    )
