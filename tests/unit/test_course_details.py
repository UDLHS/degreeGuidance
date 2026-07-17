"""Reading Section 2.2 of the handbook (Phase 9.1) + the catalog audit.

Every case below is quoted from a real book, because every one of them was a
bug first:

- "Art Stream" / "Biosystem Technology Stream" — the book is inconsistent about
  plurals, and demanding the plural silently lost a stream (131, 121);
- "the Commerce, Biological Science and Physical Science Streams" — one trailing
  "Streams" shared across a list; matching name-adjacent-to-Stream kept only the
  last of them (092);
- "Engineering Technology"/"Biosystems Technology" are also SUBJECT names, so a
  bare mention in a subject list is not an eligibility statement (030);
- a section's stream must come from its printed banner, never its number, or a
  renumbered book silently relabels every course.

These are pure-function tests: no PDF, no DB.
"""

from __future__ import annotations

from core.ingestion.course_details import (
    ALL_SIX_STREAMS,
    cross_stream_eligibility,
    stream_of_banner,
    streams_named_in,
    subject_only_alternative,
)


class TestBannerStream:
    def test_reads_the_printed_name_not_the_number(self):
        assert stream_of_banner("2.2.1 ARTS STREAM") == "ARTS"
        assert stream_of_banner("2.2.4 PHYSICAL SCIENCE STREAM") == "PHYSICAL_SCIENCE"

    def test_a_renumbered_section_still_reads_correctly(self):
        # the whole point of reading the banner: numbers may move, words don't
        assert stream_of_banner("2.2.9 COMMERCE STREAM") == "COMMERCE"

    def test_ict_is_a_subject_not_a_stream(self):
        # the book classifies A/L subjects into SIX streams (2024 p.28); ICT is
        # §2.2.7, a subject. It must never resolve to a stream.
        assert stream_of_banner("2.2.7 Information Communication Technology") is None
        assert "ICT" not in ALL_SIX_STREAMS

    def test_cross_stream_banner_is_not_a_single_stream(self):
        banner = "2.2.8 COURSES OF STUDY FOR WHICH STUDENTS FROM DIFFERENT SUBJECT STREAMS"
        assert stream_of_banner(banner) is None


class TestCrossStreamEligibility:
    def test_singular_art_stream(self):
        # 131 Financial Economics, 2024 p.117 — "Art", not "Arts"
        text = (
            "At least a 'B' grade in Economics and at least 'S' grades for any other "
            "two subjects in Art Stream or Commerce Stream at the G.C.E. (A/L) Examination."
        )
        assert cross_stream_eligibility(text) == ["ARTS", "COMMERCE"]

    def test_singular_biosystem_technology(self):
        # 121, 2024 p.114 — "Biosystem", not "Biosystems"
        text = (
            "At least 'S' grades in any three subjects in Engineering Technology Stream "
            "or Biosystem Technology Stream at the G.C.E. (A/L) Examination."
        )
        assert cross_stream_eligibility(text) == ["BIOSYSTEMS_TECH", "ENGINEERING_TECH"]

    def test_a_list_sharing_one_trailing_streams(self):
        # 092, 2024 p.107 — three names, one "Streams" at the end
        text = "Any three subjects in the Commerce, Biological Science and Physical Science Streams"
        assert cross_stream_eligibility(text) == [
            "BIO_SCIENCE",
            "COMMERCE",
            "PHYSICAL_SCIENCE",
        ]

    def test_subject_names_alone_are_not_an_eligibility_statement(self):
        # 030 Urban Informatics — "Engineering Technology" and "Biosystems
        # Technology" appear as SUBJECTS. Reading them as streams narrowed a
        # course that is actually open to all six.
        text = (
            "Minimum eligibility requirements for admission : Three passes including "
            "at least a 'C' grade in one of the following subjects; Engineering Technology "
            "Biosystems Technology Combined Mathematics Physics"
        )
        assert cross_stream_eligibility(text) == ALL_SIX_STREAMS

    def test_no_stream_named_means_all_six(self):
        # §2.2.8's own heading is the statement: students from different subject
        # streams are eligible. The SUBJECT rules do the filtering downstream.
        text = "Three passes including at least a 'C' grade in Combined Mathematics."
        assert cross_stream_eligibility(text) == ALL_SIX_STREAMS


class TestSubjectOnlyAlternative:
    def test_flags_the_case_it_cannot_read(self):
        # 124, 2024 p.116: one route names streams, the other grants entry by a
        # SUBJECT list naming none. Reporting only the named streams would hide
        # the course from students who qualify via the second route.
        text = (
            "At least 'S' grades in any three subjects in Engineering Technology Stream "
            "or Biosystem Technology Stream at the G.C.E. (Advanced Level) Examination\n"
            "or\n"
            "At least 'S' grades in any three of the following list of subjects at the "
            "G.C.E. (Advanced Level) Examination.\n Chemistry\n Physics\n Biology\n"
            " Agricultural Science\n"
            "Degree Programme : Bachelor of Health Science Honours"
        )
        assert subject_only_alternative(text) is True

    def test_does_not_flag_when_every_route_names_a_stream(self):
        text = (
            "Any three subjects in the Commerce Stream\n"
            "or\n"
            "any other two subjects in the Arts Stream\n"
            "Degree Programme : Bachelor of Science"
        )
        assert subject_only_alternative(text) is False

    def test_does_not_flag_a_single_route(self):
        text = "At least 'S' grades for any other two subjects in Art Stream or Commerce Stream."
        assert subject_only_alternative(text) is False

    def test_does_not_flag_when_no_route_names_a_stream(self):
        # nothing named anywhere -> the all-six default already covers everyone,
        # so there is nothing for a human to widen.
        text = (
            "Three passes in Combined Mathematics\n"
            "or\n"
            "Three passes in Physics\n"
            "Degree Programme : Bachelor of Science"
        )
        assert subject_only_alternative(text) is False


class TestStreamsNamedIn:
    def test_longest_name_wins_over_its_substring(self):
        # "Biosystems Technology" must not degrade to "Technology", and
        # "Biological Science"/"Physical Science" must stay distinct
        assert streams_named_in("Biosystems Technology") == ["BIOSYSTEMS_TECH"]
        assert streams_named_in("Engineering Technology") == ["ENGINEERING_TECH"]
        assert streams_named_in("Biological Science and Physical Science") == [
            "BIO_SCIENCE",
            "PHYSICAL_SCIENCE",
        ]


# -- Phase 9.6: duration, medium, and the anchor shapes -----------------------

from core.ingestion.aptitude_section import parse_aptitude_codes  # noqa: E402
from core.ingestion.course_details import parse_medium_codes, parse_section_22  # noqa: E402


def _one_page(text: str) -> list[tuple[int, str]]:
    return [(58, text)]


class TestDurationAndMedium:
    def test_reads_the_plain_block(self):
        # 131 Financial Economics, 2024 p.117 (bullet glyph stripped by pdfminer
        # on some lines -- both forms are real)
        page = """2.2.8.42 Financial Economics
(Course Code - 131)
(Proposed Intake - 50)
Minimum eligibility requirements for admission :
At least a B grade in Economics in Art Stream or Commerce Stream.
 Degree Programme : Bachelor of Arts Honours in Financial Economics
 Available University : University of Sri Jayewardenepura
 Duration : 04 years
 Medium : English
"""
        d = parse_section_22(_one_page(page))["131"]
        assert d.duration_years == 4.0
        assert d.medium_text == "English"
        assert d.medium_codes == ["EN"]
        assert d.medium_needs_review is False

    def test_duration_survives_the_internship_suffix(self):
        # Siddha/036, 2024 p.62
        page = """2.2.3.10 Siddha Medicine and Surgery
(Course Code - 036)
 Duration : 06 years [05 academic years and 01-year (final) internship]
"""
        assert parse_section_22(_one_page(page))["036"].duration_years == 6.0

    def test_per_institution_medium_is_flagged_never_parsed(self):
        # Siddha/036, 2024 p.62 -- Jaffna teaches in Tamil, Trincomalee in
        # English; one course-wide code list would be a lie for both campuses
        page = """2.2.3.10 Siddha Medicine and Surgery
(Course Code - 036)
 Duration : 06 years
 Medium : University of Jaffna - Tamil
Trincomalee Campus, Eastern University, Sri Lanka -
English
2.2.3.11 Biological Science
(Course Code - 006)
"""
        d = parse_section_22(_one_page(page))["036"]
        assert d.medium_codes == []
        assert d.medium_needs_review is True
        assert "Trincomalee" in d.medium_text

    def test_medium_capture_never_swallows_the_sections_closing_prose(self):
        # 137 Primary Education, 2024 p.119 -- the O/L requirements follow the
        # Medium line; an early build captured them all as "the medium"
        page = """2.2.8.47 Primary Education
(Course Code - 137)
 Duration : 04 years
 Medium : Sinhala
In addition to that, candidates must fulfill the following requirements at the G.C.E.
(Ordinary Level) Examination.
"""
        d = parse_section_22(_one_page(page))["137"]
        assert d.medium_text == "Sinhala"
        assert d.medium_codes == ["SI"]

    def test_split_medium_list(self):
        assert parse_medium_codes("Sinhala / English") == (["EN", "SI"], False)
        assert parse_medium_codes("English") == (["EN"], False)
        assert parse_medium_codes("University of Jaffna - Tamil") == ([], True)


class TestAnchorShapes:
    def test_colon_anchor_reads_medicine(self):
        # 2024 p.58 -- Medicine and Dental use : where every other block
        # uses -; missing this hid the book two flagship courses entirely
        page = """2.2.3 BIOLOGICAL SCIENCE STREAM
2.2.3.1 Medicine
(Course Code : 001)
(Proposed Intake : 2095)
Minimum eligibility requirements for admission :
At least two C grades and a S grade in Biology, Chemistry and Physics.
 Duration : 05 years
"""
        d = parse_section_22(_one_page(page))["001"]
        assert d.stream_codes == ["BIO_SCIENCE"]
        assert d.streams_are_stated is True
        assert d.proposed_intake == 2095
        assert d.duration_years == 5.0

    def test_plural_anchor_documents_both_courses(self):
        # 2024 p.43 -- one block, two courses of study (Arts SP)
        page = """2.2.1 ARTS STREAM
2.2.1.2 Arts (SP)
(Course Codes : Mass Media - 020; Performing Arts - 041)
Minimum eligibility requirements for admission :
At least three S grades in Arts subjects.
 Duration : 04 years
"""
        out = parse_section_22(_one_page(page))
        assert out["020"].duration_years == 4.0
        assert out["041"].duration_years == 4.0
        assert out["020"].stream_codes == ["ARTS"] and out["041"].stream_codes == ["ARTS"]


class TestAptitudeTable:
    PAGES = [
        (5, "Requirement to pass the practical/ aptitude test 152"),  # TOC decoy
        (159, """REQUIREMENT TO PASS THE PRACTICAL/ APTITUDE TEST
Every candidate who has listed undermentioned courses of study should pass the test.
Course of Study University / Campus / Institute Uni-Code
ARTS (SP) - MASS MEDIA SRIPALEE CAMPUS, UNIVERSITY OF COLOMBO 020S
ARCHITECTURE UNIVERSITY OF MORATUWA 023G
MUSIC UNIVERSITY OF SRI JAYEWARDENEPURA 068C
"""),
        (160, "Submitting your application: no codes on this page."),
    ]

    def test_reads_the_table_and_skips_the_toc_decoy(self):
        codes, page, warnings = parse_aptitude_codes(self.PAGES)
        assert codes == ["020S", "023G", "068C"]
        assert page == 159
        assert warnings == []

    def test_missing_table_is_a_warning_never_a_claim(self):
        codes, page, warnings = parse_aptitude_codes([(1, "nothing here")])
        assert codes == [] and page is None
        assert warnings and "left untouched" in warnings[0]

    def test_table_spanning_a_page_break(self):
        pages = [
            (159, "REQUIREMENT TO PASS THE PRACTICAL/ APTITUDE TEST\nMUSIC X 068C"),
            (160, "DANCE Y 069E"),
            (161, "no more codes"),
            (162, "STRAY CODE FAR AWAY 999Z"),
        ]
        codes, _page, _w = parse_aptitude_codes(pages)
        assert codes == ["068C", "069E"]  # 999Z is beyond the table end
