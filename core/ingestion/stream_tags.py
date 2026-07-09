"""Deterministic bracket-tag -> A/L stream code parser.

Cutoff-table column labels occasionally carry a bracketed stream/subject
qualifier distinguishing a per-stream cutoff variant of the SAME official
Uni-Code (measured case: Food Business Management/107L prints
"[Commerce Stream]" and "[Biological / Physical Science Stream]" as two
separate cutoff-table columns, both legitimately 107L). This maps that
bracket text to canonical streams.code values for the admin's review --
it only ever SUGGESTS (never silently applies): unrecognised text returns
an empty list so a human must type the stream codes manually, the same
human-gate philosophy as the rest of the mapping ladder.
"""

from __future__ import annotations

import re

_BRACKET_RE = re.compile(r"\[([^\]]*)\]")

# Order matters only for readability; each pattern is independent and
# case-insensitive. "BIO" also catches "Biological".
_STREAM_KEYWORDS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bCOMMERCE\b", re.I), "COMMERCE"),
    (re.compile(r"\bARTS\b", re.I), "ARTS"),
    (re.compile(r"\bBIO", re.I), "BIO_SCIENCE"),
    (re.compile(r"\bPHYSICAL\b", re.I), "PHYSICAL_SCIENCE"),
    (re.compile(r"\bENGINEERING\b", re.I), "ENGINEERING_TECH"),
    (re.compile(r"\bBIOSYSTEMS\b", re.I), "BIOSYSTEMS_TECH"),
    (
        re.compile(r"\bICT\b|INFORMATION\s*(?:AND|&)?\s*COMMUNICATION\s*TECHNOLOGY", re.I),
        "ICT",
    ),
]

# "[Any subject combination]" is the OPEN/general-quota track: everyone
# eligible for the course who isn't already covered by a sibling's specific
# stream. On its own (no sibling context) it falls back to all non-ICT
# streams, matching the cross-stream admission convention.
_ANY_SUBJECT_RE = re.compile(r"\bANY\s+SUBJECT\s+COMBINATION\b", re.I)
_ALL_NON_ICT = ["ARTS", "COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE", "ENGINEERING_TECH", "BIOSYSTEMS_TECH"]


def _explicit_from_tag(tag: str) -> list[str]:
    codes: list[str] = []
    for pattern, code in _STREAM_KEYWORDS:
        if pattern.search(tag) and code not in codes:
            codes.append(code)
    return codes


def parse_streams(raw_label: str) -> tuple[list[str], bool]:
    """Bracket tag(s) -> (explicit_stream_codes, is_open).

    is_open is True when a tag says "Any subject combination" (the open quota,
    resolved to the complement of its siblings by resolve_group_streams).
    explicit_stream_codes is [] for an open tag or when nothing is recognised
    (a human decides, never a guess)."""
    tags = _BRACKET_RE.findall(raw_label)
    if not tags:
        return [], False
    codes: list[str] = []
    is_open = False
    for tag in tags:
        if _ANY_SUBJECT_RE.search(tag):
            is_open = True
            continue
        for c in _explicit_from_tag(tag):
            if c not in codes:
                codes.append(c)
    return codes, is_open


def suggest_stream_codes(raw_label: str) -> list[str]:
    """Bracket tag(s) in raw_label -> the stream codes they refer to, for a
    STANDALONE column (no sibling context). Returns [] when there's no bracket
    tag, or none of its words are recognised. An open ("any subject") tag
    expands to all non-ICT streams here; in a shared-code group use
    resolve_group_streams instead so it becomes the disjoint complement."""
    explicit, is_open = parse_streams(raw_label)
    if is_open:
        merged = list(explicit)
        for c in _ALL_NON_ICT:
            if c not in merged:
                merged.append(c)
        return merged
    return explicit


def resolve_group_streams(labels: list[str], universe: list[str] | None = None) -> list[list[str]]:
    """Assign DISJOINT streams across a group of columns that share one course
    code (e.g. Management Studies (TV) - A [Commerce] + - B [Any subject]).

    - explicit-tag columns keep their own streams (Commerce, Bio/Physical …);
    - an open ("any subject combination") column gets `universe` minus every
      stream already claimed by a sibling — the reserved-quota logic, so a
      Commerce student never matches two cutoffs.

    `universe` is the "any subject" pool. It defaults to the six non-ICT
    streams — the handbook's established cross-stream convention (migration 16,
    handbook §2.2.7/§2.2.8). It is deliberately NOT course_stream_eligibility,
    which for these courses lists only the home stream (e.g. 022R -> COMMERCE)
    and would make the complement empty. Returned list is parallel to `labels`.
    """
    pool = list(universe) if universe else list(_ALL_NON_ICT)
    parsed = [parse_streams(l) for l in labels]
    claimed: list[str] = []
    for explicit, is_open in parsed:
        if not is_open:
            for c in explicit:
                if c not in claimed:
                    claimed.append(c)
    out: list[list[str]] = []
    for explicit, is_open in parsed:
        if is_open:
            out.append([c for c in pool if c not in claimed])
        else:
            out.append(explicit)
    return out
