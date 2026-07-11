"""Unit tests for the W1 guards (core/ratelimit.py) with injected clocks."""

from __future__ import annotations

from datetime import date

from core.ratelimit import DailyBudget, SlidingWindowLimiter


def test_sliding_window_allows_then_blocks_then_recovers():
    t = [0.0]
    lim = SlidingWindowLimiter(max_hits=3, window_seconds=60.0, clock=lambda: t[0])

    assert all(lim.allow("ip1")[0] for _ in range(3))
    allowed, retry = lim.allow("ip1")
    assert not allowed and 0 < retry <= 60

    # other keys are independent
    assert lim.allow("ip2")[0]

    # window slides: first hit expires at t=60
    t[0] = 60.1
    assert lim.allow("ip1")[0]


def test_sliding_window_partial_expiry():
    t = [0.0]
    lim = SlidingWindowLimiter(max_hits=2, window_seconds=10.0, clock=lambda: t[0])
    assert lim.allow("k")[0]
    t[0] = 5.0
    assert lim.allow("k")[0]
    assert not lim.allow("k")[0]
    t[0] = 10.5  # first expired, second still inside
    assert lim.allow("k")[0]
    assert not lim.allow("k")[0]


def test_daily_budget_spend_and_rollover():
    day = [date(2026, 7, 11)]
    b = DailyBudget(daily_limit=2, today=lambda: day[0])
    assert b.try_spend() and b.try_spend()
    assert not b.try_spend()
    assert b.remaining() == 0
    day[0] = date(2026, 7, 12)  # midnight rollover resets
    assert b.remaining() == 2
    assert b.try_spend()


def test_daily_budget_bulk_spend_never_overshoots():
    b = DailyBudget(daily_limit=5, today=lambda: date(2026, 7, 11))
    assert b.try_spend(4)
    assert not b.try_spend(2)  # would exceed
    assert b.try_spend(1)
    assert b.remaining() == 0