"""The deterministic rule suggester (9.6b) — every sentence quoted from the
2024 book, because the suggester exists only for shapes the book actually
prints. The safety property under test throughout: a sentence either parses
COMPLETELY into one unconditional rule, or yields None. Never partial, never
a guess.

Measured against the live catalog: 52 of 52 valid suggestions agreed
semantically with the hand-curated rules; the two invalid ones (slash-composite
subject names, 094/095) are dropped by name validation downstream.
"""

from __future__ import annotations

from core.ingestion.rule_suggest import suggest_subject_rule


class TestSafeShapes:
    def test_any_three_subjects(self):
        # 126 / 132 / 137, verbatim
        text = "At least ‘S’ grades in any three subjects at the G.C.E. (Advanced Level) Examination."
        assert suggest_subject_rule(text) == {
            "type": "any_n_subjects", "count": 3, "min_grade": "S",
        }

    def test_any_three_with_ol_tail_is_cut(self):
        # 024 — the O/L conditions after "In addition" are not A/L subject rules
        text = (
            "At least ‘S’ grades in any three subjects at the G.C.E. (Advanced Level) "
            "Examination. In addition to that, candidates must fulfill the following "
            "requirements; (a) At least an Ordinary Pass (S) in English at the G.C.E. "
            "(Ordinary Level) Examination"
        )
        assert suggest_subject_rule(text) == {
            "type": "any_n_subjects", "count": 3, "min_grade": "S",
        }

    def test_three_named_subjects(self):
        # 002 Dental Surgery, verbatim
        text = (
            "At least three ‘S’ grades in Chemistry, Physics and Biology at the "
            "G.C.E. (Advanced Level) Examination."
        )
        assert suggest_subject_rule(text) == {
            "type": "and",
            "conditions": [
                {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
            ],
        }

    def test_medicine_two_c_and_one_s(self):
        # 001 Medicine, verbatim
        text = (
            "At least two ‘C’ grades and a ‘S’ grade in Biology, Chemistry and Physics "
            "at the G.C.E. (Advanced Level) Examination."
        )
        rule = suggest_subject_rule(text)
        assert rule == {
            "type": "and",
            "conditions": [
                {
                    "type": "count_from_list",
                    "subjects": ["Biology", "Chemistry", "Physics"],
                    "count": 2, "min_grade": "C",
                },
                {
                    "type": "count_from_list",
                    "subjects": ["Biology", "Chemistry", "Physics"],
                    "count": 3, "min_grade": "S",
                },
            ],
        }

    def test_two_named_plus_third_from_list(self):
        # 006 Biological Science, verbatim incl. the bullet glyphs
        text = (
            "At least ‘S’ grades in Biology, Chemistry and the third subject from the "
            "following subjects at the G.C.E. (Advanced Level) Examination; "
            " Agricultural Science  Higher Mathematics  Mathematics "
            " Combined Mathematics  Physics"
        )
        rule = suggest_subject_rule(text)
        assert rule is not None and rule["type"] == "and"
        assert rule["conditions"][0] == {
            "type": "subject_min_grade", "subject": "Biology", "min_grade": "S",
        }
        assert rule["conditions"][2]["type"] == "one_of_min_grade"
        assert "Combined Mathematics" in rule["conditions"][2]["subjects"]

    def test_graded_one_of_plus_any_two(self):
        # 096 / 038, verbatim
        text = (
            "At least a ‘C’ grade in Combined Mathematics or Physics or Information & "
            "Communication Technology at the G.C.E. (Advanced Level) Examination; and "
            "‘S’ grades for any other two subjects available at the G.C.E. (Advanced "
            "Level) Examination."
        )
        rule = suggest_subject_rule(text)
        assert rule == {
            "type": "and",
            "conditions": [
                {
                    "type": "one_of_min_grade",
                    "subjects": [
                        "Combined Mathematics", "Physics",
                        "Information & Communication Technology",
                    ],
                    "min_grade": "C",
                },
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ],
        }

    def test_any_three_from_explicit_list(self):
        # 120, verbatim
        text = (
            "At least ‘S’ grades for any three subjects from the following list of "
            "subjects at the G.C.E. (Advanced Level) Examination;  Chemistry "
            " Physics  Biology  Agricultural Science"
        )
        assert suggest_subject_rule(text) == {
            "type": "count_from_list",
            "subjects": ["Chemistry", "Physics", "Biology", "Agricultural Science"],
            "count": 3, "min_grade": "S",
        }


class TestNeverGuesses:
    def test_multi_route_or_returns_none(self):
        # 064 — a second "or At least…" route; only a human can weigh routes
        text = (
            "At least ‘S’ grades in Biology, Chemistry and the third subject from the "
            "following subjects at the G.C.E. (Advanced Level) Examination;  Physics "
            "or At least ‘S’ grades in following subjects…"
        )
        assert suggest_subject_rule(text) is None

    def test_stream_conditions_return_none(self):
        # 131, verbatim — the stream restriction is not expressible here safely
        text = (
            "At least a ‘B’ grade in Economics and at least ‘S’ grades for any other "
            "two subjects in Art Stream or Commerce Stream at the G.C.E. (Advanced "
            "Level) Examination."
        )
        assert suggest_subject_rule(text) is None

    def test_combination_lists_return_none(self):
        # 004 Agriculture, verbatim start
        text = (
            "At least three ‘S’ grades for one of the following combinations of "
            "subjects at the G.C.E. (Advanced Level) Examination. (i) Chemistry; "
            "Physics; and Biology (ii) Chemistry; Physics or Mathematics; Biology"
        )
        assert suggest_subject_rule(text) is None

    def test_leftover_prose_kills_the_parse_not_the_meaning(self):
        # the 079 regression: "any three subjects" followed by unrelated prose
        # once parsed the prose word "This" as a SUBJECT. Now the tail marker
        # cuts it (correct parse), and any UNKNOWN leftover kills the parse.
        text = (
            "At least ‘S’ grades in any three subjects at the G.C.E. (Advanced Level) "
            "Examination. This course of study is offered at two universities."
        )
        assert suggest_subject_rule(text) == {
            "type": "any_n_subjects", "count": 3, "min_grade": "S",
        }
        weird = "At least ‘S’ grades in any three subjects somewhere unusual"
        assert suggest_subject_rule(weird) is None

    def test_empty_and_garbage_return_none(self):
        assert suggest_subject_rule("") is None
        assert suggest_subject_rule("Name of the university") is None
