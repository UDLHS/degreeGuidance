"""In-process rate limiting + daily Gemini budget (W1 of the Phase-2 plan).

Why in-process: the deployed API is a single instance today; a shared-Redis
limiter is a W2+ upgrade and slots in behind the same interface. The point of
W1 is that an anonymous loop can no longer drain the Gemini quota or hammer
the public endpoints for free.

Two primitives, both clock-injectable for tests:

- SlidingWindowLimiter: per-key (client IP) hit counter over a rolling window.
- DailyBudget: one global counter per UTC day for expensive provider calls
  (chat runs, interest embeddings, admin sandbox tests). When exhausted, chat
  returns a friendly 429 and interest-ranking degrades gracefully to inert —
  eligibility itself never depends on Gemini and keeps working.
"""

from __future__ import annotations

import time
from collections import deque
from datetime import datetime, timezone
from threading import Lock


class SlidingWindowLimiter:
    def __init__(self, max_hits: int, window_seconds: float, clock=time.monotonic):
        self.max_hits = max_hits
        self.window = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str) -> tuple[bool, float]:
        """(allowed, retry_after_seconds). Records the hit when allowed."""
        now = self._clock()
        with self._lock:
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] >= self.window:
                q.popleft()
            if len(q) >= self.max_hits:
                return False, max(0.0, self.window - (now - q[0]))
            q.append(now)
            # opportunistic cleanup so idle keys don't accumulate forever
            if len(self._hits) > 10_000:
                for k in [k for k, v in self._hits.items() if not v][:5_000]:
                    self._hits.pop(k, None)
            return True, 0.0


class DailyBudget:
    def __init__(self, daily_limit: int, today=lambda: datetime.now(timezone.utc).date()):
        self.daily_limit = daily_limit
        self._today = today
        self._day = today()
        self._spent = 0
        self._lock = Lock()

    def try_spend(self, n: int = 1) -> bool:
        with self._lock:
            day = self._today()
            if day != self._day:
                self._day, self._spent = day, 0
            if self._spent + n > self.daily_limit:
                return False
            self._spent += n
            return True

    def remaining(self) -> int:
        with self._lock:
            if self._today() != self._day:
                return self.daily_limit
            return max(0, self.daily_limit - self._spent)
