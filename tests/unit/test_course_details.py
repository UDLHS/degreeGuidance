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
