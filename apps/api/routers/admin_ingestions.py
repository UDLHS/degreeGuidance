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

import os
import tempfile
import uuid
from datetime import datetime, timezone

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

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from apps.api.queue import enqueue_extract_pdf
from apps.worker.jobs.ingest_zscores import ingest_zscores
from core.config import settings
from core.models.auth import User
from core.models.cutoffs import HandbookChange, IngestionRun, ParseError
from core.schemas.admin_ingestion import (
    ChangeApplyResponse,
    HandbookChangeListResponse,
    HandbookChangeOut,
    HandbookChangeUpdate,
    IngestionCreateResponse,
    IngestionRunDetail,
    IngestionRunListResponse,
    IngestionRunOut,
    ParseErrorOut,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:ingestions"],
    dependencies=[Depends(get_current_admin)],  # gate every route in this router
)

# A merged cutoff CSV is ~50 KB; a handbook PDF is ~6 MB. Caps bound abuse.
_MAX_CSV_BYTES = 5 * 1024 * 1024
_MAX_PDF_BYTES = 30 * 1024 * 1024


def _work_dir() -> Path:
    d = Path(settings.ingestion_work_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


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
    (_work_dir() / f"{run_id}.pdf").write_bytes(content)

    await log_admin_action(
        db, admin=admin, action_type="ingestion.pdf_upload",
        target_table="ingestion_runs", target_id=run_id, before=None,
        after={"run_id": run_id, "exam_year": exam_year, "file": filename},
        request=request,
    )
    await db.commit()  # commit BEFORE enqueue so the worker can see the run

    await enqueue_extract_pdf(
        run_id=run_id, pdf_path=str(_work_dir() / f"{run_id}.pdf"), exam_year=exam_year
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
    csv_path = _work_dir() / f"{run_id}.csv"
    if not csv_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extracted CSV not available for this run.",
        )
    return FileResponse(
        str(csv_path), media_type="text/csv", filename=f"ingestion_{run_id}.csv"
    )


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
    exam_year = run.year
    triggered_by = f"admin:{admin.user_id}:promote:{run_id}"

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
        csv_path = _work_dir() / f"{run_id}.csv"
        if not csv_path.exists():
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

    # link the extraction run to the produced zscore run
    run.notes = f"promoted -> zscore run {summary['run_id']}"
    await log_admin_action(
        db, admin=admin, action_type="ingestion.promote",
        target_table="ingestion_runs", target_id=summary["run_id"],
        before=None, after=summary, request=request,
        notes=f"promoted from extraction run {run_id}; reviewed_upload={reviewed_provided}",
    )
    await db.commit()
    return IngestionCreateResponse(run_type="zscore", **summary)


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

    return HandbookChangeListResponse(
        total=len(rows),
        counts={s: c for s, c in count_rows},
        items=[HandbookChangeOut.model_validate(r) for r in rows],
    )


@router.patch("/ingestions/{run_id}/changes/{change_id}", response_model=HandbookChangeOut)
async def update_change(
    run_id: uuid.UUID,
    change_id: int,
    payload: HandbookChangeUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> HandbookChangeOut:
    """Approve or reject one change. For a course_added the admin may supply the
    university_id + name_en here (merged into after_value) so apply can create
    the course stub."""
    ch = await db.get(HandbookChange, change_id)
    if ch is None or ch.run_id != run_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change not found for this run")
    if ch.status == "applied":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Change already applied")

    before_status = ch.status
    ch.status = payload.status
    ch.resolved_by = f"admin:{admin.user_id}"
    ch.resolved_at = datetime.now(timezone.utc)

    if ch.change_type == "course_added" and (payload.university_id or payload.name_en):
        merged = dict(ch.after_value or {})
        if payload.university_id is not None:
            merged["university_id"] = payload.university_id
        if payload.name_en:
            merged["name_en"] = payload.name_en
        ch.after_value = merged

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
    skipped: list[dict] = []
    now = datetime.now(timezone.utc)

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
            if not uni or not name:
                skipped.append({"course_code": ch.course_code, "reason": "needs university_id + name_en"})
                continue
            if not (await db.execute(text("SELECT 1 FROM universities WHERE university_id = :u"), {"u": uni})).first():
                skipped.append({"course_code": ch.course_code, "reason": f"unknown university_id {uni}"})
                continue
            if (await db.execute(text("SELECT 1 FROM courses WHERE course_code = :c"), {"c": ch.course_code})).first():
                ch.status, ch.resolved_by, ch.resolved_at = "applied", f"admin:{admin.user_id}", now
                skipped.append({"course_code": ch.course_code, "reason": "already exists; marked applied"})
                continue
            course_number = ch.course_code[:3] if ch.course_code[:3].isdigit() else None
            await db.execute(
                text(
                    "INSERT INTO courses (course_code, course_number, university_id, name_en, is_active) "
                    "VALUES (:code, :num, :uni, :name, false)"
                ),
                {"code": ch.course_code, "num": course_number, "uni": uni, "name": name},
            )
            ch.status, ch.resolved_by, ch.resolved_at = "applied", f"admin:{admin.user_id}", now
            await log_admin_action(
                db, admin=admin, action_type="course.create", target_table="courses",
                target_id=ch.course_code, before=None,
                after={"course_code": ch.course_code, "university_id": uni, "name_en": name, "is_active": False},
                request=request, notes=f"handbook-sync addition (run {run_id})",
            )
            applied_added += 1

    await db.commit()
    return ChangeApplyResponse(
        applied_removed=applied_removed, applied_added=applied_added, skipped=skipped
    )
