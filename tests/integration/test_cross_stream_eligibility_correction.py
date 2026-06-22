"""Pins the migration-26 stream-eligibility correction for 6 cross-stream
courses that were over-inclusive (set to all 6 streams as an MVP placeholder
per migration 12). Real sets read from the handbook §2.2.8 text."""

from __future__ import annotations

from sqlalchemy import text

EXPECTED = {
    "066U": {"COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"},
    "090U": {"COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"},
    "092K": {"COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE", "ARTS"},
    "092L": {"COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE", "ARTS"},
    "107L": {"COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"},
    "122P": {"COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE", "ENGINEERING_TECH", "BIOSYSTEMS_TECH"},
}


async def test_corrected_cross_stream_courses(db_session):
    for course_code, expected_streams in EXPECTED.items():
        rows = (
            await db_session.execute(
                text(
                    "SELECT s.code FROM course_stream_eligibility cse "
                    "JOIN streams s ON s.stream_id = cse.stream_id "
                    "WHERE cse.course_code = :cc"
                ),
                {"cc": course_code},
            )
        ).scalars().all()
        assert set(rows) == expected_streams, f"{course_code}: got {set(rows)}, expected {expected_streams}"
