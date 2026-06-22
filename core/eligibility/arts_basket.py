"""Arts Stream (course_number 019) eligibility -- the 4-basket subject system.

Handbook §2.2.1.1, transcribed in full this session. This is Sri Lanka's
single largest-intake course of study (6,983 seats) and uses a selection
system unlike anything else in the handbook -- deliberately NOT forced into
the generic subject_rule tree (core/eligibility/subject_requirements.py); a
forced-fit risks getting it subtly wrong.

Rule, in full:
  - Exactly 3 subjects, each at >= S grade.
  - At least 1 subject from Basket 01, UNLESS one of 3 exceptions applies:
      (a) all 3 subjects are the National Languages (Sinhala, Tamil, English)
      (b) the 3 subjects are a mix of National + Classical languages
      (c) 2 subjects are from Basket 04 (Languages) and the 3rd is from
          Basket 02 (Religions/Civilizations) or Basket 03 (Aesthetic)
  - At most 2 subjects from Basket 02, and a religion + its own civilization
    (e.g. Buddhism + Buddhist Civilization) may not both be offered.
  - At most 2 subjects from Basket 03 (Aesthetic), and not 2 from the SAME
    of the 4 aesthetic areas (Art / Dancing / Music / Drama & Theatre).
  - At most 2 subjects from Basket 04 (Languages), EXCEPT the explicit
    exemptions: 3 National Languages, or 1+ National + up to 2 Classical.
    Never 3 Classical languages or 3 Foreign languages.
"""

from __future__ import annotations

from core.eligibility.subject_requirements import GRADE_RANK, SubjectResult

BASKET_01 = {
    "Economics", "Geography", "History", "Home Economics",
    "Agricultural Science", "Mathematics", "Combined Mathematics",
    "Communication & Media Studies", "Information & Communication Technology",
    "Accounting", "Business Statistics", "Political Science", "Logic & Scientific Method",
    "Civil Technology", "Electrical, Electronic and Information Technology",
    "Agro Technology", "Mechanical Technology", "Food Technology", "Bio-Resource Technology",
}

BASKET_02_RELIGIONS = {"Buddhism", "Hinduism", "Christianity", "Islam"}
BASKET_02_CIVILIZATIONS = {
    "Buddhist Civilization", "Hindu Civilization", "Christian Civilization",
    "Islamic Civilization", "Greek & Roman Civilization",
}
BASKET_02 = BASKET_02_RELIGIONS | BASKET_02_CIVILIZATIONS
_RELIGION_CIVILIZATION_PAIRS = {
    "Buddhism": "Buddhist Civilization",
    "Hinduism": "Hindu Civilization",
    "Christianity": "Christian Civilization",
    "Islam": "Islamic Civilization",
}

# area name -> subjects in that area (no 2 subjects from the same area)
BASKET_03_AREAS: dict[str, set[str]] = {
    "art": {"Art"},
    "dancing": {"Dancing - Sinhala", "Dancing - Bharatha"},
    "music": {"Music - Oriental", "Music - Carnatic", "Music - Western"},
    "drama_theatre": {"Drama & Theatre - Sinhala", "Drama & Theatre - Tamil", "Drama & Theatre - English"},
}
BASKET_03 = set().union(*BASKET_03_AREAS.values())

NATIONAL_LANGUAGES = {"Sinhala", "Tamil", "English"}
CLASSICAL_LANGUAGES = {"Arabic", "Pali", "Sanskrit"}
FOREIGN_LANGUAGES = {"Chinese", "French", "German", "Hindi", "Japanese", "Malay", "Russian", "Korean"}
BASKET_04 = NATIONAL_LANGUAGES | CLASSICAL_LANGUAGES | FOREIGN_LANGUAGES


def _passing(subjects: list[SubjectResult], min_grade: str = "S") -> list[str]:
    need = GRADE_RANK[min_grade]
    return [s.subject for s in subjects if GRADE_RANK.get(s.grade.upper(), -1) >= need]


def check_arts_eligibility(subjects: list[SubjectResult]) -> bool:
    """True if the student's subjects satisfy Arts (019)'s 4-basket rule."""
    names = _passing(subjects, "S")
    if len(names) != 3:
        return False
    name_set = set(names)

    in_b1 = name_set & BASKET_01
    in_b2 = name_set & BASKET_02
    in_b4 = name_set & BASKET_04
    # subjects outside all 4 baskets (e.g. unrecognised) are simply not counted
    # toward any basket -- they don't independently satisfy anything below.

    # --- Basket 02 caps ---
    if len(in_b2) > 2:
        return False
    for religion, civilization in _RELIGION_CIVILIZATION_PAIRS.items():
        if religion in name_set and civilization in name_set:
            return False

    # --- Basket 03 caps ---
    in_b3 = name_set & BASKET_03
    if len(in_b3) > 2:
        return False
    for area_subjects in BASKET_03_AREAS.values():
        if len(name_set & area_subjects) > 1:
            return False

    # --- Basket 04 caps + exemptions ---
    classical_count = len(name_set & CLASSICAL_LANGUAGES)
    foreign_count = len(name_set & FOREIGN_LANGUAGES)
    national_count = len(name_set & NATIONAL_LANGUAGES)
    if classical_count == 3 or foreign_count == 3:
        return False

    exception_a = name_set == NATIONAL_LANGUAGES  # 3 national languages exactly
    exception_b = (
        len(in_b4) == 3 and national_count >= 1 and classical_count >= 1 and foreign_count == 0
    )  # national + classical mix
    exception_c = (
        len(in_b4) == 2 and len(in_b2 | in_b3) == 1
    )  # 2 languages + 1 religion/civ-or-aesthetic subject

    if not (exception_a or exception_b):
        # basket 04 cap of 2 applies unless covered by an explicit exemption
        if len(in_b4) > 2:
            return False

    # --- Basket 01 minimum, unless an exception applies ---
    if not in_b1 and not (exception_a or exception_b or exception_c):
        return False

    return True
