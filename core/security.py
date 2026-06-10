"""Auth primitives: password hashing (bcrypt) + JWT mint/verify (PyJWT).

Pure functions — no FastAPI, no DB — so they're trivially unit-testable and
reusable by the login route, the require_admin dependency, and the
create_admin bootstrap script.

Credentials auth (masterplan §15, Admin Slice 1 A2). FastAPI is the JWT
authority: it signs HS256 access tokens with a `role` claim. When the Next.js
frontend lands, Auth.js calls the login route as its Credentials provider and
simply carries this token — no redesign needed.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from core.config import settings

# bcrypt hashes inputs up to 72 bytes; longer passwords are truncated by the
# algorithm. Admin passwords are well within that, but we encode explicitly.
_MAX_BCRYPT_BYTES = 72


def hash_password(plain: str) -> str:
    """Return a bcrypt hash (str) suitable for storing in users.password_hash."""
    pw = plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time check of a plaintext password against a stored bcrypt hash."""
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8")[:_MAX_BCRYPT_BYTES], hashed.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    """Mint a signed HS256 access token. `subject` is the user_id (str)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=expires_minutes or settings.jwt_access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Verify signature + expiry and return the claims. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
