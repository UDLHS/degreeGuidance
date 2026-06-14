"""Admin ingestion endpoints (Admin Slice 1, Part C1 — masterplan §14.3, handoff §7).

POST /api/admin/ingestions          -- upload a REVIEWED merged CSV + exam_year,
                                       run the existing Step 4 loader synchronously,
                                       return the run summary (run_id/status/counts).
GET  /api/admin/ingestions          -- list ingestion_runs (newest first, paginated).
GET  /api/admin/ingestions/{run_id} -- one run + its parse_errors (triage queue).

C1 is the CSV-direct path only — no new infrastructure. Step 4 is a single bulk
upsert (sub-second on ~6,500 cells), so it runs in-request. The multi-minute
PDF -> OCR extraction is C2, which adds the PDF-upload variant + an Arq job +
the /promote two-step from §14.3.

Every route is gated by require_admin; the upload writes an admin_actions row.

Upload safety (handoff §11.B "For Part C"):
- only a .csv filename is accepted (415 otherwise);
- the body is read with a hard size cap (413 if exceeded);
- the bytes are written to a server-named temp file (never the client filename),
  which is always unlinked in a finally;
- exam_year is bounds-checked by the Form (2010-2030) AND by the loader.
"""

from __future__ import annotations

import os
import tempfile
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from apps.worker.jobs.ingest_zscores import ingest_zscores
from core.models.auth import User
from core.models.cutoffs import IngestionRun, ParseError
from core.schemas.admin_ingestion import (
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

# A merged cutoff CSV is ~50 KB (25 districts x ~261 courses). 5 MB is generous
# headroom while still bounding an abusive upload.
_MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post(
    "/ingestions",
    response_model=IngestionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a reviewed merged Z-score CSV via the Step 4 loader",
)
async def create_ingestion(
    request: Request,
    file: UploadFile = File(...),
    exam_year: int = Form(..., ge=2010, le=2030),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> IngestionCreateResponse:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .csv uploads are accepted for ingestion.",
        )

    # Read with a hard cap: read one byte past the limit to detect overflow
    # without loading an unbounded body into memory.
    content = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"CSV exceeds the {_MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
        )

    # Server-named temp file — never trust the client filename in a path.
    fd, tmp_path = tempfile.mkstemp(suffix=".csv", prefix="ingest_")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(content)

        try:
            summary = await ingest_zscores(
                tmp_path, exam_year, triggered_by=f"admin:{admin.user_id}"
            )
        except ValueError as exc:  # bad exam_year (backstop) or empty CSV
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
            ) from exc
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    await log_admin_action(
        db,
        admin=admin,
        action_type="ingestion.create",
        target_table="ingestion_runs",
        target_id=summary["run_id"],
        before=None,
        after=summary,
        request=request,
        notes=f"exam_year={exam_year}, file={filename}",
    )
    await db.commit()

    return IngestionCreateResponse(**summary)


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
