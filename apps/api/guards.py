"""Shared W1 guard instances + the public rate-limit middleware.

Keying: the student traffic reaches FastAPI through the Next.js proxies, so
the direct peer is the proxy — the real client IP arrives in X-Forwarded-For
(first hop), which the public BFF now forwards. Requests with no client at
all (in-process ASGI test transport) are exempt; real sockets always have one.

Scope: only the anonymous public tier (/api/v1/*) is limited. Admin routes are
already auth-gated, and the auth endpoints keep their own audit trail.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from core.config import settings
from core.ratelimit import DailyBudget, SlidingWindowLimiter

chat_limiter = SlidingWindowLimiter(settings.rate_limit_chat_per_minute, 60.0)
public_limiter = SlidingWindowLimiter(settings.rate_limit_public_per_minute, 60.0)
gemini_budget = DailyBudget(settings.gemini_daily_call_budget)

_CHAT_PATH = "/api/v1/chat"
_PUBLIC_PREFIX = "/api/v1/"


def client_key(request: Request) -> str | None:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else None


async def public_rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith(_PUBLIC_PREFIX):
        key = client_key(request)
        if key is not None:  # None = in-process test transport, exempt
            limiter = chat_limiter if path == _CHAT_PATH else public_limiter
            allowed, retry_after = limiter.allow(f"{'chat' if limiter is chat_limiter else 'pub'}:{key}")
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests — please wait a moment and try again."
                    },
                    headers={"Retry-After": str(max(1, int(retry_after) + 1))},
                )
    return await call_next(request)
