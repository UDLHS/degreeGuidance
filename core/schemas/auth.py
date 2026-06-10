"""Pydantic request/response models for authentication (Admin Slice 1 A2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    # email kept as a plain str (no email-validator dependency); normalized lower.
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiry
    role: str


class CurrentUser(BaseModel):
    """Public-safe view of the authenticated user (no password_hash)."""

    user_id: str
    email: str
    display_name: str | None = None
    role: str
