"""Curated subject-combination prerequisites (handbook §2.2), Week 3 follow-up.

Hand-transcribed from a full read of the 2024/2025 handbook's Section 2.2 (every
subsection: 2.2.1 Arts through 2.2.8 cross-stream courses). Keyed by
course_number (3-digit course-of-study code) -- the rule applies identically
across every university offering that course type (verified directly from the
handbook text).

Format: list of dicts with course_number, subject_rule (the JSON condition tree
evaluated by core/eligibility/subject_requirements.py), source_section (the
exact §2.2.x.y this came from, for traceability), and optional notes (selection
quotas, O-Level gates as free text -- NOT evaluated by the engine per the
decision in this session).

Arts (course 019) is NOT here -- its 4-basket selection system needs its own
checker (see core/eligibility/arts_basket.py) and is curated separately.

A course_number with NO row here is ungated by design (stream-level check
only) -- curation is incremental and never breaks existing behaviour.

STREAM-ELIGIBILITY DISCREPANCIES FOUND DURING CURATION (not yet corrected --
flagged for review, see handoff notes): several §2.2.8 courses explicitly
restrict to a NAMED SUBSET of streams in the handbook text, but
course_stream_eligibility currently has them open to all 6 streams:
  066 Entrepreneurship and Management   -> text says Commerce/BioSci/PhysSci only
  090 Hospitality, Tourism & Events Mgmt -> text says Commerce/BioSci/PhysSci only
  092 Tourism & Hospitality Management   -> text says Commerce/BioSci/PhysSci, or specific Arts subjects
  107 Food Business Management           -> text says BioSci/PhysSci or Commerce (specific subjects), not Arts/EngTech/BiosystemsTech
  122 Health Tourism & Hospitality Mgmt  -> text says Commerce/BioSci/PhysSci/EngTech/BiosystemsTech, NOT Arts
"""

from __future__ import annotations

# ---- shared subject-list constants (reduce duplication, match handbook lists exactly) ----

_BIO_CORE = ["Biology", "Chemistry", "Physics"]
_BIO_THIRD_LIST = ["Agricultural Science", "Higher Mathematics", "Mathematics", "Combined Mathematics", "Physics"]
_MATHS_PHYS_GROUP = ["Higher Mathematics", "Combined Mathematics", "Mathematics", "Physics"]
_PHYS_SCI_CORE_OPTS = ["Combined Mathematics", "Higher Mathematics"]
_CHEM_PHYS_OPTS = ["Chemistry", "Physics"]

REQUIREMENTS: list[dict] = [
    # ---------------- COMMERCE STREAM (2.2.2) ----------------
    {
        "course_number": "016",  # Management
        "source_section": "2.2.2.4",
        "subject_rule": {
            "type": "or",
            "conditions": [
                {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 3, "min_grade": "S"},
                {
                    "type": "and",
                    "conditions": [
                        {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 2, "min_grade": "S"},
                        {"type": "count_from_list", "subjects": ["Agricultural Science", "Geography", "Business Statistics", "German", "Combined Mathematics", "Mathematics", "History", "Political Science", "English", "Logic & Scientific Method", "French", "Information & Communication Technology"], "count": 1, "min_grade": "S"},
                    ],
                },
            ],
        },
        "notes": "Shared rule for Management(016)/Mgmt & Public Policy(028)/Real Estate Mgmt & Valuation(017)/Commerce(018). Accounting specifically required for Accountancy/Auditing/Finance specializations (within-faculty selection, not a separate eligibility gate).",
    },
    {"course_number": "028", "source_section": "2.2.2.2", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 3, "min_grade": "S"},
        {"type": "and", "conditions": [
            {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 2, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Agricultural Science", "Geography", "Business Statistics", "German", "Combined Mathematics", "Mathematics", "History", "Political Science", "English", "Logic & Scientific Method", "French", "Information & Communication Technology"], "count": 1, "min_grade": "S"},
        ]},
    ]}},
    {"course_number": "017", "source_section": "2.2.2.3", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 3, "min_grade": "S"},
        {"type": "and", "conditions": [
            {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 2, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Agricultural Science", "Geography", "Business Statistics", "German", "Combined Mathematics", "Mathematics", "History", "Political Science", "English", "Logic & Scientific Method", "French", "Information & Communication Technology"], "count": 1, "min_grade": "S"},
        ]},
    ]}},
    {"course_number": "018", "source_section": "2.2.2.4", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 3, "min_grade": "S"},
        {"type": "and", "conditions": [
            {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 2, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Agricultural Science", "Geography", "Business Statistics", "German", "Combined Mathematics", "Mathematics", "History", "Political Science", "English", "Logic & Scientific Method", "French", "Information & Communication Technology"], "count": 1, "min_grade": "S"},
        ]},
    ]}},
    {
        "course_number": "022",  # Management Studies (TV)
        "source_section": "2.2.2.5",
        "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        "notes": "60% of Vavuniya intake / 40% of Trincomalee intake reserved for Commerce-stream students (selection quota, not an eligibility gate).",
    },
    {
        "course_number": "077",  # Business Information Systems (BIS)
        "source_section": "2.2.2.6",
        "subject_rule": {
            "type": "or",
            "conditions": [
                {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 3, "min_grade": "S"},
                {"type": "and", "conditions": [
                    {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 2, "min_grade": "S"},
                    {"type": "count_from_list", "subjects": ["Information & Communication Technology", "Combined Mathematics", "Logic & Scientific Method", "Business Statistics", "Physics"], "count": 1, "min_grade": "S"},
                ]},
            ],
        },
    },
    {
        "course_number": "127",  # Accounting Information Systems
        "source_section": "2.2.2.7",
        "subject_rule": {
            "type": "and",
            "conditions": [
                {"type": "subject_min_grade", "subject": "Accounting", "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Economics", "Business Studies"], "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Business Statistics", "Information & Communication Technology"], "min_grade": "S"},
            ],
        },
    },
    {
        "course_number": "133",  # Banking and Insurance
        "source_section": "2.2.2.8",
        "subject_rule": {
            "type": "and",
            "conditions": [
                {"type": "subject_min_grade", "subject": "Accounting", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Economics", "min_grade": "S"},
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ],
        },
        "notes": "Third subject: any other Commerce-stream subject.",
    },
    {
        "course_number": "140",  # Service Management
        "source_section": "2.2.2.9",
        "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        "notes": "Any 3 Commerce-stream subjects.",
    },

    # ---------------- BIOLOGICAL SCIENCE STREAM (2.2.3) ----------------
    {
        "course_number": "001",  # Medicine
        "source_section": "2.2.3.1",
        "subject_rule": {
            "type": "and",
            "conditions": [
                {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
                {"type": "count_from_list", "subjects": _BIO_CORE, "count": 2, "min_grade": "C"},
            ],
        },
    },
    {"course_number": "002", "source_section": "2.2.3.2", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Dental Surgery
    {"course_number": "003", "source_section": "2.2.3.3", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Veterinary Science
    {
        "course_number": "039",  # Agricultural Technology & Management
        "source_section": "2.2.3.4",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology"], "count": 3, "min_grade": "S"},
            {"type": "and", "conditions": [
                {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Physics", "Mathematics"], "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Biology", "Agricultural Science"], "min_grade": "S"},
            ]},
            {"type": "and", "conditions": [
                {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Mathematics"], "min_grade": "S"},
            ]},
        ]},
    },
    {"course_number": "004", "source_section": "2.2.3.5", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology"], "count": 3, "min_grade": "S"},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Physics", "Mathematics"], "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Biology", "Agricultural Science"], "min_grade": "S"}]},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Mathematics"], "min_grade": "S"}]},
    ]}},  # Agriculture
    {"course_number": "005", "source_section": "2.2.3.6", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology"], "count": 3, "min_grade": "S"},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Physics", "Mathematics"], "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Biology", "Agricultural Science"], "min_grade": "S"}]},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Mathematics"], "min_grade": "S"}]},
    ]}},  # Food Science & Nutrition
    {"course_number": "035", "source_section": "2.2.3.7", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Food Science & Technology
    {"course_number": "032", "source_section": "2.2.3.8", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Ayurveda Medicine and Surgery
    {"course_number": "033", "source_section": "2.2.3.9", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Unani Medicine and Surgery
    {"course_number": "036", "source_section": "2.2.3.10", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Siddha Medicine and Surgery
    {
        "course_number": "006",  # Biological Science
        "source_section": "2.2.3.11",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": _BIO_THIRD_LIST, "min_grade": "S"},
        ]},
    },
    {"course_number": "007", "source_section": "2.2.3.12", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": _BIO_THIRD_LIST, "min_grade": "S"},
    ]}},  # Applied Sciences (Bio Sc)
    {"course_number": "050", "source_section": "2.2.3.13", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": _BIO_THIRD_LIST, "min_grade": "S"},
    ]}},  # Health Promotion
    {"course_number": "037", "source_section": "2.2.3.14", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}, "ol_requirements": "At least Ordinary Pass (S) in English."},  # Nursing
    {"course_number": "051", "source_section": "2.2.3.15", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "C"},
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
    ]}, "ol_requirements": "At least Ordinary Pass (S) in English."},  # Pharmacy
    {"course_number": "052", "source_section": "2.2.3.16", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}, "ol_requirements": "At least Ordinary Pass (S) in English."},  # Medical Laboratory Sciences
    {"course_number": "053", "source_section": "2.2.3.17", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}, "ol_requirements": "At least Ordinary Pass (S) in English."},  # Radiography
    {"course_number": "054", "source_section": "2.2.3.18", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": ["Biology", "Mathematics", "Higher Mathematics", "Combined Mathematics"], "min_grade": "S"},
    ]}, "ol_requirements": "At least Ordinary Pass (S) in English."},  # Physiotherapy
    {"course_number": "058", "source_section": "2.2.3.19", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Biochemistry & Molecular Biology
    {"course_number": "062", "source_section": "2.2.3.20", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Fisheries & Marine Sciences
    {"course_number": "055", "source_section": "2.2.3.21", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": ["Physics", "Combined Mathematics", "Mathematics", "Agricultural Science"], "min_grade": "S"},
    ]}},  # Environmental Conservation & Management
    {"course_number": "086", "source_section": "2.2.3.22", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Chemistry", "Biology", "Physics"], "count": 3, "min_grade": "S"},
        {"type": "count_from_list", "subjects": ["Chemistry", "Biology", "Agricultural Science"], "count": 3, "min_grade": "S"},
    ]}},  # Animal Science & Fisheries
    {"course_number": "087", "source_section": "2.2.3.23", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology"], "count": 3, "min_grade": "S"},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Physics", "Mathematics"], "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Biology", "Agricultural Science"], "min_grade": "S"}]},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Mathematics"], "min_grade": "S"}]},
    ]}},  # Food Production & Technology Management
    {"course_number": "093", "source_section": "2.2.3.24", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology"], "count": 3, "min_grade": "S"},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Physics", "Mathematics"], "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Biology", "Agricultural Science"], "min_grade": "S"}]},
        {"type": "and", "conditions": [{"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"}, {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"}, {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Mathematics"], "min_grade": "S"}]},
    ]}},  # Agricultural Resource Management and Technology
    {"course_number": "094", "source_section": "2.2.3.25", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": ["Physics", "Agricultural Science", "Food Technology", "Bio-Resource Technology", "Agro Technology"], "min_grade": "S"},
    ]}},  # Agribusiness Management
    {"course_number": "095", "source_section": "2.2.3.26", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": ["Physics", "Agricultural Science", "Food Technology", "Bio-Resource Technology", "Agro Technology"], "min_grade": "S"},
    ]}, "ol_requirements": "At least Credit Pass (C) in English."},  # Green Technology
    {"course_number": "067", "source_section": "2.2.3.27", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": _BIO_THIRD_LIST, "min_grade": "S"},
    ]}},  # Animal Production and Food Technology
    {"course_number": "073", "source_section": "2.2.3.28", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": _BIO_THIRD_LIST, "min_grade": "S"},
    ]}},  # Export Agriculture
    {"course_number": "088", "source_section": "2.2.3.29", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": _BIO_THIRD_LIST, "min_grade": "S"},
    ]}},  # Aquatic Resources Technology
    {"course_number": "115", "source_section": "2.2.3.30", "subject_rule": {"type": "count_from_list", "subjects": ["Physics", "Biology", "Chemistry"], "count": 3, "min_grade": "S"}},  # Occupational Therapy
    {"course_number": "116", "source_section": "2.2.3.31", "subject_rule": {"type": "count_from_list", "subjects": _BIO_CORE, "count": 3, "min_grade": "S"}},  # Optometry
    {"course_number": "118", "source_section": "2.2.3.32", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": ["Biology", "Combined Mathematics", "Mathematics", "Higher Mathematics", "Agricultural Science"], "min_grade": "S"},
    ]}},  # Applied Chemistry
    {"course_number": "120", "source_section": "2.2.3.33", "subject_rule": {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology", "Agricultural Science"], "count": 3, "min_grade": "S"}},  # Indigenous Medicinal Resources
    {"course_number": "129", "source_section": "2.2.3.34", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Any 3 Biological-Science-stream subjects."},  # Aquatic Bioresources
    {"course_number": "130", "source_section": "2.2.3.35", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Any 3 Biological-Science-stream subjects."},  # Urban Bioresources
    {"course_number": "138", "source_section": "2.2.3.36", "subject_rule": {"type": "count_from_list", "subjects": ["Physics", "Biology", "Chemistry"], "count": 3, "min_grade": "S"}},  # Medical Imaging Technology
    {"course_number": "083", "source_section": "2.2.3.37", "subject_rule": {"type": "count_from_list", "subjects": ["Biology", "Physics", "Chemistry"], "count": 3, "min_grade": "S"}, "ol_requirements": "At least Ordinary Pass (S) in English."},  # Speech and Hearing Sciences

    # ---------------- PHYSICAL SCIENCE STREAM (2.2.4) ----------------
    {
        "course_number": "008",  # Engineering -- the proven, user-confirmed example
        "source_section": "2.2.4.1",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
        ]},
    },
    {"course_number": "009", "source_section": "2.2.4.2", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
    ]}},  # Engineering (EM) - Earth Resources Engineering
    {"course_number": "010", "source_section": "2.2.4.3", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
    ]}},  # Engineering (TM) - Textile & Apparel Engineering
    {"course_number": "057", "source_section": "2.2.4.4", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
    ]}},  # Transport Management & Logistics Engineering (TMLE)
    {
        "course_number": "013",  # Physical Science
        "source_section": "2.2.4.5",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": _PHYS_SCI_CORE_OPTS, "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": _CHEM_PHYS_OPTS, "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Combined Mathematics", "Biology", "Higher Mathematics", "Chemistry", "Physics"], "min_grade": "S"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
    },
    {
        "course_number": "012",  # Computer Science
        "source_section": "2.2.4.6",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Physics", "Higher Mathematics"], "min_grade": "C"},
            {"type": "count_from_list", "subjects": ["Combined Mathematics", "Higher Mathematics", "Mathematics", "Physics", "Chemistry", "Information & Communication Technology"], "count": 2, "min_grade": "S"},
        ]},
    },
    {"course_number": "015", "source_section": "2.2.4.7", "subject_rule": {"type": "and", "conditions": [
        {"type": "one_of_min_grade", "subjects": _PHYS_SCI_CORE_OPTS, "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": _CHEM_PHYS_OPTS, "min_grade": "S"},
        {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Combined Mathematics", "Biology", "Higher Mathematics", "Chemistry", "Physics", "Information & Communication Technology"], "min_grade": "S"},
        {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
    ]}},  # Applied Sciences (Physical Science)
    {
        "course_number": "059",  # Industrial Statistics & Mathematical Finance
        "source_section": "2.2.4.8",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Higher Mathematics", "Physics", "Chemistry", "Information & Communication Technology"], "count": 2, "min_grade": "S"},
        ]},
    },
    {
        "course_number": "060",  # Statistics & Operations Research
        "source_section": "2.2.4.9",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Biology", "Chemistry", "Physics", "Agricultural Science", "Mathematics", "Higher Mathematics", "Information & Communication Technology"], "count": 2, "min_grade": "S"},
        ]},
    },
    {
        "course_number": "108",  # Physical Science - ICT
        "source_section": "2.2.4.10",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Information & Communication Technology", "min_grade": "S"},
        ]},
    },
    {
        "course_number": "117",  # Artificial Intelligence
        "source_section": "2.2.4.11",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Physics", "Higher Mathematics"], "min_grade": "C"},
            {"type": "count_from_list", "subjects": ["Combined Mathematics", "Higher Mathematics", "Mathematics", "Physics", "Chemistry", "Information & Communication Technology"], "count": 2, "min_grade": "S"},
        ]},
    },
    {
        "course_number": "119",  # Electronics and Computer Science
        "source_section": "2.2.4.12",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Physics", "Higher Mathematics"], "min_grade": "C"},
            {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Higher Mathematics"], "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Chemistry", "Combined Mathematics", "Higher Mathematics", "Information & Communication Technology"], "min_grade": "S"},
        ]},
    },
    {
        "course_number": "136",  # Data Science
        "source_section": "2.2.4.13",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Physics", "Higher Mathematics"], "min_grade": "C"},
            {"type": "count_from_list", "subjects": ["Combined Mathematics", "Physics", "Higher Mathematics", "Chemistry", "Information & Communication Technology"], "count": 2, "min_grade": "S"},
        ]},
        "ol_requirements": "At least Credit Pass (C) in English.",
    },

    # ---------------- ENGINEERING TECH / BIOSYSTEMS TECH / ICT STREAMS (2.2.5-2.2.7) ----------------
    {
        "course_number": "102",  # Engineering Technology (ET)
        "source_section": "2.2.5.1",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Engineering Technology", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Science for Technology", "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Economics", "Geography", "Home Economics", "English", "Communication & Media Studies", "Information & Communication Technology", "Art", "Business Studies", "Agricultural Science", "Accounting", "Mathematics"], "min_grade": "S"},
        ]},
    },
    {
        "course_number": "103",  # Biosystems Technology (BST)
        "source_section": "2.2.6.1",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Biosystems Technology", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Science for Technology", "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Economics", "Geography", "Home Economics", "English", "Communication & Media Studies", "Information & Communication Technology", "Art", "Business Studies", "Agricultural Science", "Accounting", "Mathematics"], "min_grade": "S"},
        ]},
    },
    {
        "course_number": "104",  # ICT (stream course)
        "source_section": "2.2.7",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Information & Communication Technology", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Science for Technology", "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Engineering Technology", "Biosystems Technology"], "min_grade": "S"},
        ]},
    },

    # ---------------- CROSS-STREAM COURSES (2.2.8) ----------------
    {
        "course_number": "026",  # Information Technology (IT)
        "source_section": "2.2.8.1",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": _MATHS_PHYS_GROUP, "min_grade": "C"},
        ]},
    },
    {
        "course_number": "027",  # Management and Information Technology (MIT)
        "source_section": "2.2.8.2",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": _MATHS_PHYS_GROUP, "min_grade": "C"},
            {"type": "or", "conditions": [
                {"type": "count_from_list", "subjects": ["Biology", "Chemistry", "Physics", "Combined Mathematics", "Mathematics", "Higher Mathematics"], "count": 3, "min_grade": "S"},
                {"type": "and", "conditions": [
                    {"type": "count_from_list", "subjects": ["Biology", "Chemistry", "Physics", "Combined Mathematics", "Mathematics", "Higher Mathematics"], "count": 2, "min_grade": "S"},
                    {"type": "subject_min_grade", "subject": "Information & Communication Technology", "min_grade": "S"},
                ]},
            ]},
        ]},
        "ol_requirements": "At least Very Good Pass (B) in Mathematics; at least Credit Pass (C) in English.",
        "notes": "40% of intake from Biological Science Stream, remainder from other relevant combinations (selection quota).",
    },
    {
        "course_number": "011",  # Quantity Surveying
        "source_section": "2.2.8.3",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Higher Mathematics"], "min_grade": "S"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
        "ol_requirements": "Credit (C) in Mathematics; Ordinary Pass (S) in Science; Credit (C) in English.",
        "notes": "Third subject from: Accounting, Economics, Business Statistics, Business Studies, Physics, Chemistry, ICT.",
    },
    {
        "course_number": "014",  # Surveying Science
        "source_section": "2.2.8.4",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
    },
    {
        "course_number": "030",  # Urban Informatics and Planning
        "source_section": "2.2.8.5",
        "subject_rule": {"type": "count_from_list", "subjects": ["Combined Mathematics", "Chemistry", "Physics", "Biology"], "count": 3, "min_grade": "S"},
        "notes": "Approximated: also accepts 1-2 from {Combined Maths, Chemistry, Physics, Biology} plus the rest from a long secondary list (Accounting, Agri Sci, Business Studies, Business Stats, ICT, Economics, Political Science, Geography, Higher Maths, Logic, Maths, Biosystems Tech, SFT, Eng Tech) -- needs admin review for full precision.",
        "ol_requirements": "At least Very Good Pass (B) in English; Credit Pass (C) in Mathematics.",
    },
    {
        "course_number": "023",  # Architecture
        "source_section": "2.2.8.6",
        "subject_rule": {"type": "one_of_min_grade", "subjects": ["Art", "Higher Mathematics", "Combined Mathematics", "Geography", "Chemistry", "Biology", "Physics"], "min_grade": "S"},
        "notes": "Approximated: also requires 2 more subjects from a ~30-item list (most other A/L subjects) -- needs admin review for full precision. Aptitude Test required (already captured via requires_aptitude_test).",
        "ol_requirements": "Ordinary Pass (S) in English; Credit (C) in Mathematics at O/L or Ordinary Pass (S) at A/L.",
    },
    {"course_number": "034", "source_section": "2.2.8.7", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "ol_requirements": "Credit (C) in English, Mathematics, Science."},  # Fashion Design & Product Development
    {
        "course_number": "097",  # Landscape Architecture
        "source_section": "2.2.8.8",
        "subject_rule": {"type": "one_of_min_grade", "subjects": ["Art", "Biology", "Chemistry", "Combined Mathematics", "Geography", "Higher Mathematics", "Physics", "Agricultural Science"], "min_grade": "S"},
        "notes": "Approximated: also requires other subjects from a long secondary list -- needs admin review for full precision. Aptitude Test required.",
        "ol_requirements": "Ordinary Pass (S) in English; Credit (C) in Mathematics at O/L or Ordinary Pass (S) at A/L.",
    },
    {"course_number": "024", "source_section": "2.2.8.9", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "ol_requirements": "Ordinary Pass (S) in English; Credit (C) in Mathematics at O/L or Ordinary Pass (S) at A/L; Credit (C) in Science."},  # Design
    {
        "course_number": "025",  # Law
        "source_section": "2.2.8.10",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "count_from_list", "subjects": ["Accounting", "Agricultural Science", "Biology", "Business Statistics", "Business Studies", "Chemistry", "Physics", "Communication & Media Studies", "Political Science", "Geography", "Higher Mathematics", "History", "Logic & Scientific Method", "Economics", "Mathematics", "Combined Mathematics", "Information & Communication Technology"], "count": 3, "min_grade": "S"},
            {"type": "and", "conditions": [
                {"type": "count_from_list", "subjects": ["Accounting", "Agricultural Science", "Biology", "Business Statistics", "Business Studies", "Chemistry", "Physics", "Communication & Media Studies", "Political Science", "Geography", "Higher Mathematics", "History", "Logic & Scientific Method", "Economics", "Mathematics", "Combined Mathematics", "Information & Communication Technology"], "count": 1, "min_grade": "S"},
                {"type": "count_from_list", "subjects": ["Buddhism", "Buddhist Civilization", "Christianity", "Christian Civilization", "Greek & Roman Civilization", "Japanese", "Pali", "Sanskrit", "Sinhala", "Tamil", "Hinduism", "Hindu Civilization", "Islam", "Islamic Civilization", "Chinese", "English", "French", "German", "Arabic", "Hindi", "Russian"], "count": 2, "min_grade": "S"},
            ]},
        ]},
        "ol_requirements": "Credit Pass (C) in English at O/L, or Ordinary Pass (S) in English at A/L.",
        "notes": "Requirements change for 2025/2026 intake onwards: 2 C-grades + 1 S-grade required (not just 3 S-grades), plus O/L Credit in Sinhala or Tamil. Needs a year-specific override row when we ingest a 2025+ handbook.",
    },
    {
        "course_number": "056",  # Facilities Management
        "source_section": "2.2.8.11",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "count_from_list", "subjects": ["Chemistry", "Combined Mathematics", "Physics"], "count": 3, "min_grade": "S"},
            {"type": "or", "conditions": [
                {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 3, "min_grade": "S"},
                {"type": "and", "conditions": [
                    {"type": "subject_min_grade", "subject": "Accounting", "min_grade": "S"},
                    {"type": "count_from_list", "subjects": ["Business Studies", "Economics"], "count": 1, "min_grade": "S"},
                    {"type": "count_from_list", "subjects": ["Agricultural Science", "Geography", "German", "Combined Mathematics", "History", "Political Science", "English", "Logic & Scientific Method", "French", "Physics", "Information & Communication Technology"], "count": 1, "min_grade": "S"},
                ]},
            ]},
        ]},
        "ol_requirements": "Credit (C) in English, Mathematics, Science.",
    },
    {"course_number": "079", "source_section": "2.2.8.12", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}},  # MIT (SEUSL)
    {
        "course_number": "064",  # Science and Technology
        "source_section": "2.2.8.13",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "and", "conditions": [
                {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": _BIO_THIRD_LIST, "min_grade": "S"},
            ]},
            {"type": "and", "conditions": [
                {"type": "one_of_min_grade", "subjects": _PHYS_SCI_CORE_OPTS, "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": _CHEM_PHYS_OPTS, "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Agricultural Science", "Combined Mathematics", "Biology", "Higher Mathematics", "Chemistry", "Physics"], "min_grade": "S"},
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ]},
        ]},
    },
    {
        "course_number": "065",  # Computer Science & Technology
        "source_section": "2.2.8.14",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "and", "conditions": [
                {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Higher Mathematics", "Mathematics", "Combined Mathematics", "Physics"], "min_grade": "S"},
            ]},
            {"type": "and", "conditions": [
                {"type": "one_of_min_grade", "subjects": _PHYS_SCI_CORE_OPTS, "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": _CHEM_PHYS_OPTS, "min_grade": "S"},
                {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Biology", "Higher Mathematics", "Chemistry", "Physics", "Information & Communication Technology"], "min_grade": "S"},
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ]},
        ]},
    },
    {"course_number": "066", "source_section": "2.2.8.15", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "STREAM CAVEAT: handbook text restricts to Commerce/BioSci/PhysSci stream only -- course_stream_eligibility currently allows all 6, needs review (see module docstring)."},  # Entrepreneurship and Management
    {
        "course_number": "075",  # Industrial Information Technology
        "source_section": "2.2.8.16",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Physics", "Information & Communication Technology"], "min_grade": "C"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
        "ol_requirements": "Credit (C) in English; Credit (C) in Mathematics.",
    },
    {"course_number": "076", "source_section": "2.2.8.17", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Biology", "Chemistry", "Physics"], "count": 3, "min_grade": "S"},
        {"type": "count_from_list", "subjects": ["Combined Mathematics", "Chemistry", "Physics"], "count": 3, "min_grade": "S"},
    ]}},  # Mineral Resources and Technology
    {"course_number": "090", "source_section": "2.2.8.18", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "STREAM CAVEAT: handbook text restricts to Commerce/BioSci/PhysSci stream only -- see module docstring."},  # Hospitality, Tourism and Events Management
    {"course_number": "081", "source_section": "2.2.8.19", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Plus shared Practical Test with Sports Science & Management."},  # Physical Education
    {"course_number": "082", "source_section": "2.2.8.20", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Plus shared Practical Test with Physical Education."},  # Sports Science & Management
    {
        "course_number": "091",  # Information Technology & Management
        "source_section": "2.2.8.21",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Higher Mathematics", "Combined Mathematics", "Mathematics", "Physics", "Chemistry", "Accounting", "Business Statistics", "Information & Communication Technology"], "count": 2, "min_grade": "C"},
        ]},
        "ol_requirements": "Credit (C) in English; Credit (C) in Mathematics.",
    },
    {
        "course_number": "092",  # Tourism & Hospitality Management
        "source_section": "2.2.8.22",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            {"type": "and", "conditions": [
                {"type": "one_of_min_grade", "subjects": ["Economics", "Geography", "Business Statistics"], "min_grade": "S"},
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ]},
        ]},
        "notes": "STREAM CAVEAT: handbook restricts path (i) to Commerce/BioSci/PhysSci; path (ii) is Arts-stream with at least 1 of {Economics,Geography,Business Statistics} + 2 more Arts subjects (per 2.2.1.1 rules). Approximated here as any_n -- needs admin review.",
    },
    {
        "course_number": "096",  # Information Systems
        "source_section": "2.2.8.23",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Physics", "Information & Communication Technology"], "min_grade": "C"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
        "ol_requirements": "Credit (C) in English; Credit (C) in Mathematics.",
    },
    {
        "course_number": "098",  # Translation Studies
        "source_section": "2.2.8.24",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "and", "conditions": [
                {"type": "one_of_min_grade", "subjects": ["Sinhala", "Tamil"], "min_grade": "C"},
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ]},
            {"type": "subject_min_grade", "subject": "English", "min_grade": "S"},
        ]},
        "ol_requirements": "B grade in (Sinhala Language & Lit. + English) or (Tamil Language & Lit. + English).",
        "notes": "Approximated -- the real rule combines an A/L Sinhala/Tamil-Credit condition with an O/L language-pair OR an A/L English-S alternative; needs admin review for exact precision.",
    },
    {"course_number": "100", "source_section": "2.2.8.25", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Plus Aptitude Test (Film & Television skills)."},  # Film & Television Studies
    {
        "course_number": "101",  # Project Management
        "source_section": "2.2.8.26",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Accounting", "Business Studies", "Business Statistics", "Economics", "Geography", "Information & Communication Technology", "Mathematics", "Combined Mathematics", "Biology", "Agricultural Science", "Engineering Technology", "Biosystems Technology"], "count": 2, "min_grade": "C"},
        ]},
    },
    {
        "course_number": "038",  # Information and Communication Technology (ICT, cross-stream)
        "source_section": "2.2.8.27",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Combined Mathematics", "Physics", "Information & Communication Technology"], "min_grade": "C"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
        "ol_requirements": "Credit (C) in English; Credit (C) in Mathematics.",
    },
    {
        "course_number": "099",  # Software Engineering
        "source_section": "2.2.8.28",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Chemistry", "Higher Mathematics", "Information & Communication Technology"], "min_grade": "S"},
        ]},
    },
    {
        "course_number": "107",  # Food Business Management
        "source_section": "2.2.8.29",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "count_from_list", "subjects": ["Chemistry", "Biology", "Physics", "Combined Mathematics", "Agricultural Science"], "count": 3, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Business Studies", "Economics", "Accounting"], "count": 3, "min_grade": "S"},
        ]},
        "ol_requirements": "Credit (C) in English, Mathematics, Science.",
        "notes": "50% of intake from Bio/Phys-Sci path, 50% from Commerce path (selection quota). STREAM CAVEAT: text restricts to BioSci/PhysSci/Commerce -- see module docstring.",
    },
    {"course_number": "106", "source_section": "2.2.8.30", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology"], "count": 3, "min_grade": "S"},
        {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Combined Mathematics"], "count": 3, "min_grade": "S"},
    ]}},  # Marine and Fresh Water Sciences
    {
        "course_number": "109",  # Business Science
        "source_section": "2.2.8.31",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            {"type": "and", "conditions": [
                {"type": "any_n_subjects", "count": 2, "min_grade": "S"},
                {"type": "subject_min_grade", "subject": "Information & Communication Technology", "min_grade": "S"},
            ]},
        ]},
        "ol_requirements": "Credit (C) in Mathematics.",
        "notes": "Approximated: real rule is 3 from Physical-Science-or-Commerce stream, OR 2 from that + ICT as third -- needs admin review for exact stream-list precision.",
    },
    {
        "course_number": "110",  # Financial Engineering
        "source_section": "2.2.8.32",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Economics", "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Accounting", "min_grade": "S"},
            {"type": "one_of_min_grade", "subjects": ["Business Studies", "Information & Communication Technology", "Business Statistics", "Agricultural Science", "Geography", "Combined Mathematics", "History", "Political Science", "Physics", "Logic & Scientific Method"], "min_grade": "S"},
        ]},
        "ol_requirements": "Credit (C) in English; Credit (C) in Mathematics.",
    },
    {"course_number": "111", "source_section": "2.2.8.33", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Any 3 from Arts (per 2.2.1.1)/BioSci/PhysSci stream."},  # Geographical Information Science
    {
        "course_number": "113",  # Financial Mathematics and Industrial Statistics
        "source_section": "2.2.8.34",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
    },
    {"course_number": "114", "source_section": "2.2.8.35", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}},  # Human Resource Development
    {"course_number": "121", "source_section": "2.2.8.36", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Any 3 from Engineering Tech or Biosystems Tech stream."},  # Health Information and Communication Technology
    {"course_number": "122", "source_section": "2.2.8.37", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "STREAM CAVEAT: handbook restricts to Commerce/BioSci/PhysSci/EngTech/BiosystemsTech stream -- NOT Arts. course_stream_eligibility currently allows all 6, needs review."},  # Health Tourism and Hospitality Management
    {"course_number": "123", "source_section": "2.2.8.38", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Any 3 from Engineering Tech or Biosystems Tech stream."},  # Biomedical Technology
    {
        "course_number": "124",  # Indigenous Pharmaceutical Technology
        "source_section": "2.2.8.39",
        "subject_rule": {"type": "or", "conditions": [
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Chemistry", "Physics", "Biology", "Agricultural Science"], "count": 3, "min_grade": "S"},
        ]},
        "notes": "Approximated: first path is any 3 from Eng Tech/Biosystems Tech stream specifically -- needs admin review for exact stream-list precision.",
    },
    {"course_number": "125", "source_section": "2.2.8.40", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}},  # Yoga and Parapsychology
    {"course_number": "126", "source_section": "2.2.8.41", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}},  # Social Studies in Indigenous Knowledge
    {
        "course_number": "131",  # Financial Economics
        "source_section": "2.2.8.42",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "subject_min_grade", "subject": "Economics", "min_grade": "B"},
            {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        ]},
        "notes": "Other 2 subjects from Arts or Commerce stream.",
    },
    {"course_number": "132", "source_section": "2.2.8.43", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "ol_requirements": "Credit (C) in English; Credit (C) in Mathematics."},  # English Language & Applied Linguistics
    {"course_number": "134", "source_section": "2.2.8.44", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}},  # Creative Music Technology and Production
    {"course_number": "135", "source_section": "2.2.8.45", "subject_rule": {"type": "or", "conditions": [
        {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 1, "min_grade": "S"},
            {"type": "count_from_list", "subjects": ["Biology", "Chemistry", "Physics", "Agricultural Science"], "count": 3, "min_grade": "S"},
        ]},
        {"type": "count_from_list", "subjects": ["Combined Mathematics", "Chemistry", "Physics"], "count": 3, "min_grade": "S"},
    ]}, "notes": "Approximated as: 3 of {Biology,Chemistry,Physics,Agricultural Science} OR {Combined Maths,Chemistry,Physics} -- needs admin review."},  # Plantation Management and Technology
    {"course_number": "137", "source_section": "2.2.8.46", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "ol_requirements": "Credit (C) in Sinhala Language & Lit.; Credit (C) in Mathematics; Credit (C) in Science; Ordinary Pass (S) in English."},  # Primary Education
    {"course_number": "139", "source_section": "2.2.8.47", "subject_rule": {"type": "or", "conditions": [
        {"type": "count_from_list", "subjects": ["Biology", "Physics", "Chemistry"], "count": 3, "min_grade": "S"},
        {"type": "count_from_list", "subjects": ["Combined Mathematics", "Physics", "Chemistry"], "count": 3, "min_grade": "S"},
    ]}},  # Polymer Science and Industrial Management

    # ---------------- ARTS STREAM SPECIAL VARIANTS (2.2.1, excluding base Arts 019 -- see arts_basket.py) ----------------
    {
        "course_number": "020",  # Arts (SP) - Mass Media
        "source_section": "2.2.1.1(1)",
        "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        "ol_requirements": "Ordinary Pass (S) in English.",
        "notes": "Approximated: real rule constrains to <=2 languages, <=1 Religion/Civ, <=1 Technological, <=1 of {Accounting,Business Stats,Economics} -- needs admin review. Plus Aptitude Test.",
    },
    {
        "course_number": "041",  # Arts (SP) - Performing Arts
        "source_section": "2.2.1.1(1)",
        "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        "ol_requirements": "Ordinary Pass (S) in English.",
        "notes": "Same constraints as Arts (SP) Mass Media -- needs admin review. Plus Aptitude Test.",
    },
    {"course_number": "021", "source_section": "2.2.1.1(2)", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Open to Arts or Commerce stream minimum requirements; 55%/45% Arts/Commerce quota."},  # Arts (SAB)
    {"course_number": "029", "source_section": "2.2.1.1(3)", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "ol_requirements": "Credit (C) in English.", "notes": "One of the 3 A/L subjects must be Credit(C) in Sinhala, Tamil or English."},  # Communication Studies (Trincomalee)
    {"course_number": "031", "source_section": "2.2.1.1(4)", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}},  # Peace and Conflict Resolution
    {"course_number": "063", "source_section": "2.2.1.1(5)", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Must include Islam or Islamic Civilization."},  # Islamic Studies
    {"course_number": "084", "source_section": "2.2.1.1(6)", "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"}, "notes": "Must include Arabic Language."},  # Arabic Language
    {"course_number": "105", "source_section": "2.2.1.1(7)", "subject_rule": {"type": "and", "conditions": [
        {"type": "subject_min_grade", "subject": "English", "min_grade": "S"},
        {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
    ]}},  # TESL
    {
        "course_number": "068",  # Music (multiple universities offer this code)
        "source_section": "2.2.1.1(8-11)",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 2, "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Music", "min_grade": "C"},
        ]},
        "notes": "Plus Practical/Aptitude Test. Shared pattern for UVPA/Jaffna/SVIAS/SJP Music programmes.",
    },
    {
        "course_number": "069",  # Dance
        "source_section": "2.2.1.1(8-10)",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 2, "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Dancing", "min_grade": "C"},
        ]},
        "notes": "Plus Practical/Aptitude Test.",
    },
    {
        "course_number": "071",  # Drama & Theatre
        "source_section": "2.2.1.1(8,10)",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 2, "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Drama & Theatre", "min_grade": "C"},
        ]},
        "notes": "Plus Practical/Aptitude Test.",
    },
    {
        "course_number": "085",  # Visual Arts
        "source_section": "2.2.1.1(8)",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 2, "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Art", "min_grade": "C"},
        ]},
        "notes": "Plus Practical/Aptitude Test.",
    },
    {
        "course_number": "070",  # Art & Design (Jaffna)
        "source_section": "2.2.1.1(9)",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 2, "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Art", "min_grade": "C"},
        ]},
        "notes": "Plus Practical/Aptitude Test.",
    },
    {
        "course_number": "072",  # Visual & Technological Arts (SVIAS)
        "source_section": "2.2.1.1(10)",
        "subject_rule": {"type": "and", "conditions": [
            {"type": "any_n_subjects", "count": 2, "min_grade": "S"},
            {"type": "subject_min_grade", "subject": "Art", "min_grade": "C"},
        ]},
        "notes": "Plus Practical/Aptitude Test.",
    },
    {
        "course_number": "112",  # Social Work
        "source_section": "2.2.1.2",
        "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        "notes": "Any 3 Arts-stream subjects per 2.2.1.1 basket rules.",
    },
    {
        "course_number": "128",  # Arts - Information Technology
        "source_section": "2.2.1.3",
        "subject_rule": {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        "ol_requirements": "Credit (C) in Mathematics.",
        "notes": "Any 3 Arts-stream subjects per 2.2.1.1 basket rules.",
    },
]
