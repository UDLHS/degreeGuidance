"""Reader for the handbook's practical/aptitude-test table (Phase 9.6).

The book states, in one definitive table, exactly which Uni-Codes require a
practical/aptitude test:

    REQUIREMENT TO PASS THE PRACTICAL/ APTITUDE TEST
    Course of Study            University / Campus / Institute        Uni-Code
    ARTS (SP) - MASS MEDIA     SRIPALEE CAMPUS, UNIVERSITY OF COLOMBO 020S
    ARCHITECTURE               UNIVERSITY OF MORATUWA                 023G
    ...

(2024 book p.159, 2025 book p.158 — found by its PRINTED HEADING, never by a
page number, so a renumbered book still reads correctly.) This is a per-CODE
fact — Music at Jaffna (068E) and Music at VPA (068Z) are separate rows — and
it drives the student-facing conditional-eligibility badge, so it is read
deterministically from this table, never inferred from prose.

The heading match is deliberately CASE-SENSITIVE: the table of contents prints
the same words in title case ("Requirement to pass the practical/ aptitude
test  152", 2024 p.5) and matching it would start the scan 150 pages early.

Where the table cannot be found, the result is empty plus a warning — the
catalog's hand-seeded flags then simply stay as they are; nothing is guessed.
"""

from __future__ import annotations

import re

#: the section heading as PRINTED — all caps, tolerant of spacing and the
#: slash's whereabouts ("PRACTICAL/ APTITUDE", "PRACTICAL / APTITUDE")
_HEADING_RE = re.compile(r"REQUIREMENT\s+TO\s+PASS\s+THE\s+PRACTICAL\s*/\s*APTITUDE\s+TEST")

#: a Uni-Code token — 3 digits + 1 letter, the table's row terminator
_CODE_RE = re.compile(r"\b(\d{3}[A-Z])\b")


def parse_aptitude_codes(
    pages: list[tuple[int, str]],
) -> tuple[list[str], int | None, list[str]]:
    """All pages -> (sorted uni-codes requiring the test, heading page, warnings).

    Collection starts at the printed heading and continues over consecutive
    pages while they still yield code tokens (the table may spill past a page
    break); the first code-less page after the table ends it. Empty result +
    warning when the heading is absent — a future book that drops or renames
    the section reads as "nothing found", never as "nobody needs a test".
    """
    codes: set[str] = set()
    heading_page: int | None = None
    warnings: list[str] = []
    collecting = False

    for pno, text in pages:
        if not collecting:
            if _HEADING_RE.search(text):
                collecting = True
                heading_page = pno
            else:
                continue
        page_codes = _CODE_RE.findall(text)
        if page_codes:
            codes.update(page_codes)
        elif pno != heading_page:
            break  # the table ended on the previous page

    if heading_page is None:
        warnings.append(
            "aptitude-test table not found — no page prints 'REQUIREMENT TO "
            "PASS THE PRACTICAL/ APTITUDE TEST'; existing aptitude flags were "
            "left untouched"
        )
    elif not codes:
        warnings.append(
            f"aptitude-test heading found on page {heading_page} but no "
            "Uni-Codes could be read from the table — existing aptitude flags "
            "were left untouched"
        )
    return sorted(codes), heading_page, warnings
