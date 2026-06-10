"""Eligibility router: POST /api/v1/eligibility.

Thin HTTP layer. All logic lives in core/eligibility/engine.py. An unknown
district/stream code surfaces as 422 (client error); the request-body
validation (z_score range, etc.) is handled by Pydantic automatically.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_db
from core.eligibility.engine import EligibilityInputError, evaluate_eligibility
from core.schemas.eligibility import EligibilityRequest, EligibilityResponse

router = APIRouter(prefix="/api/v1", tags=["eligibility"])


@router.post(
    "/eligibility",
    response_model=EligibilityResponse,
    summary="Evaluate course eligibility for a student's Z-score / district / stream",
)
async def post_eligibility(
    payload: EligibilityRequest,
    db: AsyncSession = Depends(get_db),
) -> EligibilityResponse:
    try:
        return await evaluate_eligibility(db, payload)
    except EligibilityInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
