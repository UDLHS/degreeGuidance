"""Tests for the Arts (019) 4-basket eligibility rule, tracing the real
exceptions stated in handbook §2.2.1.1 directly (not invented scenarios)."""

from __future__ import annotations

from core.eligibility.arts_basket import check_arts_eligibility
from core.eligibility.subject_requirements import SubjectResult


def _s(*names: str, grade: str = "S") -> list[SubjectResult]:
    return [SubjectResult(subject=n, grade=grade) for n in names]


def test_one_basket01_plus_two_others_qualifies():
    # Economics (B01) + Sinhala (B04) + Geography (B01) -- has >=1 from B01
    assert check_arts_eligibility(_s("Economics", "Sinhala", "Geography")) is True


def test_all_three_from_basket01_explicitly_allowed():
    """'Students can also select all three subjects only from basket 01.'"""
    assert check_arts_eligibility(_s("Economics", "Geography", "History")) is True


def test_exception_a_three_national_languages():
    """'Students selecting three National Languages... need not select any
    subject from basket 01.'"""
    assert check_arts_eligibility(_s("Sinhala", "Tamil", "English")) is True


def test_exception_b_national_plus_classical_mix():
    """'Students selecting a combination of National and Classical languages
    need not select any subject from basket 01.' Example given: Sinhala, Pali
    and Sanskrit."""
    assert check_arts_eligibility(_s("Sinhala", "Pali", "Sanskrit")) is True


def test_three_classical_languages_explicitly_disallowed():
    """'No candidate can select three classical languages as three subjects.'"""
    assert check_arts_eligibility(_s("Arabic", "Pali", "Sanskrit")) is False


def test_three_foreign_languages_disallowed():
    assert check_arts_eligibility(_s("Chinese", "French", "German")) is False


def test_exception_c_two_languages_plus_religion():
    """'Students selecting two languages from basket 04 and the third subject
    from Religions and Civilizations... need not select any subject from
    basket 01.'"""
    assert check_arts_eligibility(_s("Sinhala", "English", "Buddhism")) is True


def test_exception_c_two_languages_plus_aesthetic():
    assert check_arts_eligibility(_s("Sinhala", "English", "Art")) is True


def test_religion_and_its_own_civilization_together_disallowed():
    """'If a religion is selected, the related civilization of the selected
    religion cannot be offered as another subject.'"""
    assert check_arts_eligibility(_s("Buddhism", "Buddhist Civilization", "Economics")) is False


def test_religion_and_different_civilization_allowed():
    assert check_arts_eligibility(_s("Buddhism", "Hindu Civilization", "Economics")) is True


def test_more_than_two_basket02_subjects_disallowed():
    assert check_arts_eligibility(_s("Buddhism", "Hinduism", "Christianity")) is False


def test_two_aesthetic_subjects_same_area_disallowed():
    """'No student is allowed to select the two subjects from one subject area.'"""
    assert check_arts_eligibility(_s("Music - Oriental", "Music - Carnatic", "Economics")) is False


def test_two_aesthetic_subjects_different_areas_allowed():
    assert check_arts_eligibility(_s("Art", "Music - Western", "Economics")) is True


def test_more_than_two_basket04_languages_without_exemption_disallowed():
    # 3 languages that are neither all-national nor national+classical
    # (2 national + 1 foreign) -- no exemption applies, basket04 cap is 2.
    assert check_arts_eligibility(_s("Sinhala", "English", "Chinese")) is False


def test_fewer_than_three_passing_subjects_fails():
    assert check_arts_eligibility(_s("Economics", "Geography", grade="S") + [SubjectResult("History", "F")]) is False


def test_exactly_three_subjects_required_not_more():
    assert check_arts_eligibility(_s("Economics", "Geography", "History", "Sinhala")) is False
