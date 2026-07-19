"""Deterministic subject-rule SUGGESTIONS from the book's own wording (9.6b).

The gate (Phase 9 D6) requires a subject rule before a new course can be
approved. The admin writes it from the book's requirement prose — but for most
courses that prose is one of a handful of fixed sentence shapes the book
repeats verbatim ("At least three 'S' grades in Chemistry, Physics and
Biology…"). Those shapes are READABLE, so this module reads them.

This is NOT the deferred §2.2 grammar parser (MASTERPLAN v4 §66) and it is NOT
an LLM. It is a set of ANCHORED patterns, each of which must consume the
ENTIRE eligibility sentence to produce anything. The safety property, in one
line:

    A sentence either parses COMPLETELY into a rule, or yields NO suggestion.

There is no partial credit. Multi-route texts ("or At least…", "(i)…(ii)…",
"one of the following combinations", "Category (A)"), stream-conditional rules
("…in Art Stream or Commerce Stream"), and anything else the patterns don't
fully cover return None — the admin writes those by hand, with the book's
wording on screen. A suggestion is also only a SUGGESTION: it lands in the
gate's editable rule box marked as book-derived, the admin reviews it against
the prose shown beside it, and the server still validates every subject name
against the catalog at approve (a name that matches no catalog subject would
match no student, ever).

Every pattern below is quoted from the 2024 book; the measured shapes are in
the test file. Anything the next book phrases differently simply won't parse —
an empty box, never a wrong one.
"""

from __future__ import annotations

import re

#: how a sentence's tail can start — everything from here on is NOT the A/L
#: subject requirement (O/L conditions, aptitude notes, university listings)
_TAIL_RE = re.compile(
    r"(?:In addition\b|Candidates are required\b|Th(?:is|e) course of study\b|"
    r"The following universit|Names? of the\b|Fields of specialization\b|"
    r"The Universit|Faculty of\b).*$",
    re.I | re.S,
)

#: the boilerplate exam reference, printed after almost every clause
_EXAM_RE = re.compile(r"\s*at the G\.?C\.?E\.?\s*\(Advanced Level\)\s*Examination[.;]?", re.I)

#: any of these means the text is NOT a single unconditional route — never
#: suggest, a human decides (see module docstring)
_REJECT_RE = re.compile(
    r"\bStreams?\b|\bcombinations?\b|\bCategory\b|\(\s*(?:i{1,3}|iv|[1-4])\s*\)|"
    r"\bor\s+At least\b|\bor\s+'S'\b",
    re.I,
)

_GRADE = r"['‘’]([ABCS])['‘’]"
#: one printed subject name — letters, &, hyphens, spaces; no commas/or/slash
_NAME = r"[A-Z][A-Za-z&()\-. ]*?"

_BULLETS_RE = re.compile(r"[•●·]")
#: "(ET)"/"(SFT)"-style trailing abbreviations on subject names
_ABBREV_RE = re.compile(r"\s*\([A-Z&\s]{2,6}\)$")


def _clean(requirements_text: str) -> str | None:
    """The block's prose -> one normalized eligibility sentence, or None."""
    window = re.split(
        r"(?i)\bDegree\s+Programmes?\b|\bAvailable\s+(?:Universit|Institution)",
        requirements_text,
    )[0]
    window = re.sub(
        r"(?i)^\s*Minimum eligibility requirements for admission\s*:?", "", window
    )
    window = window.replace("‘", "'").replace("’", "'")
    window = window.replace("E xamination", "Examination")  # measured typo (136)
    window = _BULLETS_RE.sub(",", window)
    window = " ".join(window.split())
    window = _TAIL_RE.sub("", window).strip()
    window = _EXAM_RE.sub("", window).strip()
    # a trailing bullet or the eaten exam boilerplate leaves stray ",;." tails
    window = window.rstrip(".;, ").strip()
    if not window or _REJECT_RE.search(window):
        return None
    return window


def _names(segment: str, *, allow_slash: bool) -> list[str] | None:
    """A printed subject list -> clean names, or None if any item is not a
    plain subject name. '/'-joined alternatives ("Mathematics/Combined
    Mathematics") may only be split where the semantics stay identical —
    i.e. in a pick-ONE position (the caller says so)."""
    parts: list[str] = []
    for raw in re.split(r",| and ", segment):
        raw = raw.strip().strip(",;.")
        if not raw:
            continue
        if " or " in raw:
            return None
        if "/" in raw:
            if not allow_slash:
                return None
            subparts = [s.strip() for s in raw.split("/") if s.strip()]
        else:
            subparts = [raw]
        for p in subparts:
            p = _ABBREV_RE.sub("", p).strip()
            if not re.fullmatch(_NAME, p):
                return None
            parts.append(p)
    return parts if parts else None


def _cfl(subjects: list[str], count: int, grade: str) -> dict:
    # single-subject requirements read as subject_min_grade — the same shape
    # the hand-curated rules use, so suggestions look like the rest of catalog
    if count == 1 and len(subjects) == 1:
        return {"type": "subject_min_grade", "subject": subjects[0], "min_grade": grade}
    return {
        "type": "count_from_list", "subjects": subjects,
        "count": count, "min_grade": grade,
    }


def _one_of(subjects: list[str], grade: str) -> dict:
    return {"type": "one_of_min_grade", "subjects": subjects, "min_grade": grade}


def _each_of(subjects: list[str], grade: str) -> list[dict]:
    """ALL named subjects required — one subject_min_grade per name, the exact
    shape the hand-curated rules use."""
    return [
        {"type": "subject_min_grade", "subject": s, "min_grade": grade} for s in subjects
    ]


def _any_n(count: int, grade: str = "S") -> dict:
    return {"type": "any_n_subjects", "count": count, "min_grade": grade}


def _and(*conditions: dict) -> dict:
    return {"type": "and", "conditions": list(conditions)}


#: the list-introducing phrase in "…and the third subject from the following…"
_LIST_INTRO = (
    r"(?:for )?(?:the )?(?:third subject|one of the following subjects?|third subject)"
    r"(?: from (?:the following(?: list of)? subjects?|among|the following list))?"
)


def suggest_subject_rule(requirements_text: str) -> dict | None:
    """The block's prose -> a complete rule tree, or None. Never partial."""
    w = _clean(requirements_text)
    if w is None:
        return None

    # "At least 'S' grades in any three subjects"
    m = re.fullmatch(r"(?:At least )?'S' grades? (?:in|for) any three subjects", w, re.I)
    if m:
        return _any_n(3)

    # "At least 'S' grades for any three subjects from the following list of
    #  subjects; A, B, C, D"   (120) — the list phrasing is REQUIRED; a bare
    #  "any three subjects <leftover>" must fall through to None, not parse
    #  the leftover as subjects
    m = re.fullmatch(
        r"(?:At least )?'S' grades? (?:in|for) any three subjects from the "
        r"following list of subjects\s*[;:,]\s*(.+)",
        w, re.I,
    )
    if m:
        names = _names(m.group(1), allow_slash=False)
        return _cfl(names, 3, "S") if names else None

    # "At least two 'C' grades and a 'S' grade in X, Y and Z"   (001 Medicine)
    m = re.fullmatch(
        rf"At least two {_GRADE} grades and an? {_GRADE} grade in (.+)", w, re.I
    )
    if m:
        names = _names(m.group(3), allow_slash=False)
        if names and len(names) == 3:
            return _and(_cfl(names, 2, m.group(1)), _cfl(names, 3, m.group(2)))
        return None

    # "At least [three] 'S' grades in X, Y and Z"   (002, 008, 108, …)
    m = re.fullmatch(r"At least (?:three )?'S' grades? (?:in|for) (.+)", w, re.I)
    if m:
        rest = m.group(1)
        # "…X, Y and the third subject from the following subjects; LIST"
        m2 = re.fullmatch(rf"(.+?) and {_LIST_INTRO}\s*[;:,]\s*(.+)", rest, re.I)
        if m2:
            firsts = _names(m2.group(1), allow_slash=False)
            listed = _names(m2.group(2), allow_slash=True)  # pick-one position
            if firsts and len(firsts) == 2 and listed:
                return _and(
                    _cfl([firsts[0]], 1, "S"),
                    _cfl([firsts[1]], 1, "S"),
                    _one_of(listed, "S"),
                )
            return None
        # "…X and any other two subjects"   (113)
        m2 = re.fullmatch(r"(.+?) and any other two subjects", rest, re.I)
        if m2:
            names = _names(m2.group(1), allow_slash=False)
            if names and len(names) == 1:
                return _and(_cfl(names, 1, "S"), _any_n(3))
            return None
        # plain three named subjects — all required
        names = _names(rest, allow_slash=False)
        if names and len(names) == 3:
            return _and(*_each_of(names, "S"))
        return None

    # "At least a 'G' grade in N1 [or N2 [or N3]] …and… "
    m = re.fullmatch(
        rf"At least an? {_GRADE} grade in (.+?)[;,]? and (?:at least )?(.+)", w, re.I
    )
    if m:
        grade, first_seg, rest = m.group(1), m.group(2), m.group(3)
        firsts = [
            _ABBREV_RE.sub("", p).strip() for p in re.split(r" or ", first_seg)
        ]
        if not all(re.fullmatch(_NAME, p) for p in firsts):
            return None
        gate = _one_of(firsts, grade) if len(firsts) > 1 else _cfl(firsts, 1, grade)
        # "…'S' grades for any other two subjects [available]"   (038, 096)
        if re.fullmatch(
            r"'S' grades? (?:for|in) (?:any other two|two other) subjects(?: available)?",
            rest, re.I,
        ):
            return _and(gate, _any_n(3))
        # "…'S' grades for two of the following subjects; LIST"  (117, 136)
        m2 = re.fullmatch(
            r"'S' grades? (?:for|in) two (?:of the following|other) subjects"
            r"(?: listed below)?\s*[;:,]\s*(.+)",
            rest, re.I,
        )
        if m2:
            listed = _names(m2.group(1), allow_slash=False)
            return _and(gate, _cfl(listed, 2, "S")) if listed else None
        # "…'S' grades in Y and Z"   (051)
        m2 = re.fullmatch(r"'S' grades? (?:in|for) (.+)", rest, re.I)
        if m2:
            names = _names(m2.group(1), allow_slash=False)
            if names and len(names) == 2:
                return _and(gate, *_each_of(names, "S"))
        return None

    # "Three passes including at least a 'G' grade in one of the following
    #  subjects; LIST"   (026)
    m = re.fullmatch(
        rf"Three passes including at least an? {_GRADE} grade in one of the "
        r"following subjects\s*[;:,]\s*(.+)",
        w, re.I,
    )
    if m:
        listed = _names(m.group(2), allow_slash=True)  # pick-one position
        return _and(_one_of(listed, m.group(1)), _any_n(3)) if listed else None

    return None
