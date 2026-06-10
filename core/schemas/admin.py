"""Pydantic schemas for admin alias endpoints (Admin Slice 1, Part B1)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AliasCreate(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=15)
    alias_text: str = Field(..., min_length=1)
    source: str | None = Field(default="admin", max_length=50)
    confidence: float | None = Field(default=None, ge=0, le=1)
    is_verified: bool = Field(default=True)

    @field_validator("course_code")
    @classmethod
    def _upper_code(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("alias_text", "source")
    @classmethod
    def _strip(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v


class AliasUpdate(BaseModel):
    # all optional; only provided fields are updated (PATCH semantics)
    alias_text: str | None = Field(default=None, min_length=1)
    source: str | None = Field(default=None, max_length=50)
    confidence: float | None = Field(default=None, ge=0, le=1)
    is_verified: bool | None = None

    @field_validator("alias_text", "source")
    @classmethod
    def _strip(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v


class AliasOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    alias_id: int
    course_code: str
    alias_text: str
    source: str | None = None
    confidence: float | None = None
    is_verified: bool
    created_at: datetime


class AliasListResponse(BaseModel):
    total: int
    items: list[AliasOut]
