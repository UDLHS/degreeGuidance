"""Populate career_tags and industry_tags for every course in the DB.

Run once after applying migration 33:
    uv run python scripts/populate_career_tags.py

Built from:
 - CSVs provided for Ruhuna, Sri Jayewardenepura, Colombo, Kelaniya
 - Canonical mapping by course_number so tags apply across all universities
   (a Computer Science course at Moratuwa gets the same career tags as one
    at Colombo or Kelaniya — the career paths don't change by institution)
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg


# ---------------------------------------------------------------------------
# Canonical career and industry tags by course_number
# ---------------------------------------------------------------------------
# career_tags : normalised job titles (lowercase, concise)
# industry_tags: short sector names used in INDUSTRY_DEMAND lookup

COURSE_TAGS: dict[str, dict[str, list[str]]] = {
    # --- Medical ---
    "001": {  # Medicine (MBBS)
        "career": [
            "medical officer", "doctor", "surgeon", "general practitioner",
            "specialist doctor", "pediatrician", "gynecologist", "psychiatrist",
            "cardiologist", "radiologist", "pathologist", "neurologist",
            "anesthesiologist", "emergency medical officer", "public health officer",
            "medical researcher", "medical lecturer", "occupational health physician",
            "telemedicine doctor",
        ],
        "industry": ["healthcare", "public health", "research", "pharmaceuticals", "education"],
    },
    "002": {  # Dental Surgery
        "career": [
            "dental surgeon", "general dentist", "orthodontist", "oral surgeon",
            "pediatric dentist", "prosthodontist", "periodontist", "endodontist",
            "public health dentist", "dental lecturer", "forensic odontologist",
            "dental administrator",
        ],
        "industry": ["healthcare", "dental care", "education", "public health"],
    },
    "003": {  # Veterinary Science
        "career": [
            "veterinary surgeon", "veterinary officer", "animal health officer",
            "veterinary researcher", "veterinary lecturer", "livestock officer",
            "zoo veterinarian", "meat inspector",
        ],
        "industry": ["agriculture", "livestock", "research", "education", "government"],
    },
    # --- Agriculture ---
    "004": {  # Agriculture
        "career": [
            "agriculture officer", "agronomist", "farm manager", "plantation manager",
            "research officer", "environmental officer", "agricultural extension officer",
            "irrigation officer", "export agriculture officer", "agricultural engineer",
            "natural resource manager", "agribusiness manager",
        ],
        "industry": ["agriculture", "plantation", "research", "government", "agribusiness", "export"],
    },
    "039": {  # Agricultural Technology & Management (PDN)
        "career": [
            "agricultural technologist", "farm manager", "irrigation engineer",
            "food processing technologist", "research assistant", "agricultural officer",
            "environmental officer", "soil conservation officer", "agro-industry officer",
        ],
        "industry": ["agriculture", "food", "irrigation", "environment", "research"],
    },
    "073": {  # Export Agriculture (UWU)
        "career": [
            "export agriculture officer", "agribusiness manager", "supply chain executive",
            "quality assurance officer", "export manager", "agricultural consultant",
        ],
        "industry": ["agriculture", "export", "agribusiness"],
    },
    "093": {  # Agricultural Resource Management and Technology (RUH)
        "career": [
            "agriculture officer", "agronomist", "farm manager", "plantation manager",
            "research officer", "environmental officer", "agricultural extension officer",
            "irrigation officer", "climate change analyst", "natural resource manager",
        ],
        "industry": ["agriculture", "plantation", "research", "environment", "government"],
    },
    "094": {  # Agribusiness Management (RUH)
        "career": [
            "agribusiness manager", "business development executive", "marketing executive",
            "sales manager", "supply chain manager", "export manager", "procurement officer",
            "farm business manager", "agricultural consultant", "financial analyst",
            "quality assurance officer", "entrepreneur",
        ],
        "industry": ["agribusiness", "agriculture", "export", "supply chain", "banking", "fmcg"],
    },
    # --- Biological Sciences ---
    "006": {  # Biological Science
        "career": [
            "research assistant", "laboratory technician", "microbiologist",
            "biotechnologist", "environmental scientist", "quality control officer",
            "science teacher", "lecturer", "wildlife officer", "forensic science assistant",
            "public health officer",
        ],
        "industry": ["research", "healthcare", "pharmaceuticals", "education", "environment", "food"],
    },
    "007": {  # Applied Sciences (Biological)
        "career": [
            "research assistant", "laboratory technician", "microbiologist",
            "environmental scientist", "quality control officer", "science teacher",
            "lecturer", "biotechnologist",
        ],
        "industry": ["research", "healthcare", "environment", "education", "pharmaceuticals"],
    },
    # --- Engineering ---
    "008": {  # Engineering (BSc Eng — general, covers civil/elec/mech/computer/marine at each uni)
        "career": [
            "civil engineer", "structural engineer", "electrical engineer",
            "electronics engineer", "mechanical engineer", "computer engineer",
            "project engineer", "design engineer", "maintenance engineer",
            "quality engineer", "research engineer", "automation engineer",
            "production engineer", "systems engineer", "network engineer",
            "embedded systems engineer", "site engineer", "marine engineer",
            "naval architect",
        ],
        "industry": [
            "engineering", "construction", "manufacturing", "power", "energy",
            "telecommunications", "it", "government", "consulting",
        ],
    },
    "009": {  # Engineering EM (Moratuwa — Mechanical/Manufacturing focus)
        "career": [
            "mechanical engineer", "manufacturing engineer", "production engineer",
            "maintenance engineer", "industrial engineer", "quality engineer",
            "design engineer", "cad engineer", "automation engineer", "research engineer",
        ],
        "industry": ["manufacturing", "engineering", "automotive", "energy", "construction"],
    },
    "010": {  # Engineering TM (Moratuwa — Textile/Materials)
        "career": [
            "textile engineer", "apparel engineer", "materials engineer",
            "production manager", "quality controller", "process engineer",
            "research officer",
        ],
        "industry": ["manufacturing", "textile", "apparel", "engineering"],
    },
    "011": {  # Quantity Surveying (Moratuwa)
        "career": [
            "quantity surveyor", "cost estimator", "construction project manager",
            "project coordinator", "commercial manager", "cost planner",
            "contracts manager", "tender estimator",
        ],
        "industry": ["construction", "real estate", "consulting", "engineering"],
    },
    # --- Computer Science / IT ---
    "012": {  # Computer Science
        "career": [
            "software engineer", "software developer", "web developer",
            "mobile app developer", "data analyst", "data scientist",
            "ai engineer", "machine learning engineer", "cybersecurity analyst",
            "database administrator", "systems analyst", "devops engineer",
            "cloud engineer", "it project manager", "qa engineer",
            "network engineer", "ui/ux developer", "it lecturer",
        ],
        "industry": ["it", "banking", "telecommunications", "startups", "e-commerce", "government"],
    },
    "026": {  # Information Technology (IT) — Moratuwa
        "career": [
            "software engineer", "software developer", "web developer",
            "mobile app developer", "data scientist", "ai engineer",
            "cybersecurity analyst", "database administrator", "systems analyst",
            "devops engineer", "cloud engineer", "it project manager",
            "qa engineer", "network engineer", "ui/ux developer",
        ],
        "industry": ["it", "banking", "telecommunications", "startups", "e-commerce"],
    },
    "065": {  # Computer Science & Technology (UWU)
        "career": [
            "software engineer", "software developer", "it officer",
            "data analyst", "technical officer", "lecturer",
        ],
        "industry": ["it", "technology", "education"],
    },
    "075": {  # Industrial Information Technology (UWU)
        "career": [
            "industrial it specialist", "software developer", "system analyst",
            "data analyst", "it officer", "technical officer",
        ],
        "industry": ["it", "manufacturing"],
    },
    "096": {  # Information Systems
        "career": [
            "systems analyst", "business analyst", "it business analyst",
            "software developer", "web developer", "database administrator",
            "systems administrator", "network administrator", "erp consultant",
            "data analyst", "qa engineer", "it project coordinator",
            "information systems manager", "ui/ux designer",
        ],
        "industry": ["it", "banking", "telecommunications", "consulting", "bpo", "startups"],
    },
    "099": {  # Software Engineering
        "career": [
            "software engineer", "software developer", "web developer",
            "mobile app developer", "front-end developer", "back-end developer",
            "full-stack developer", "qa engineer", "devops engineer",
            "cloud engineer", "systems engineer", "database developer",
            "application developer", "ui/ux developer", "embedded software engineer",
        ],
        "industry": ["it", "banking", "telecommunications", "startups", "bpo"],
    },
    "104": {  # Information Communication Technology (Faculty of Technology)
        "career": [
            "software developer", "web developer", "mobile app developer",
            "systems analyst", "business analyst", "data analyst",
            "network engineer", "system administrator", "database administrator",
            "cybersecurity analyst", "cloud engineer", "qa engineer",
            "it support officer", "devops engineer", "ui/ux designer",
            "it consultant", "it project manager",
        ],
        "industry": ["it", "telecommunications", "banking", "bpo", "government", "startups"],
    },
    "038": {  # ICT (Rajarata / Vavuniya — tech stream)
        "career": [
            "software developer", "web developer", "it support officer",
            "data analyst", "systems analyst", "network administrator",
            "database administrator", "it officer",
        ],
        "industry": ["it", "government", "banking"],
    },
    "117": {  # Artificial Intelligence (Moratuwa)
        "career": [
            "ai engineer", "machine learning engineer", "data scientist",
            "research scientist", "nlp engineer", "computer vision engineer",
            "ml ops engineer", "deep learning engineer", "data engineer",
            "software engineer",
        ],
        "industry": ["it", "research", "data", "ai", "health tech", "defence"],
    },
    "136": {  # Data Science (SUSL)
        "career": [
            "data scientist", "data analyst", "machine learning engineer",
            "business intelligence analyst", "database administrator",
            "data engineer", "research analyst", "statistical analyst",
            "big data specialist", "ai engineer",
        ],
        "industry": ["it", "banking", "research", "telecommunications", "healthcare", "insurance"],
    },
    # --- Physical Science ---
    "013": {  # Physical Science
        "career": [
            "data analyst", "software developer", "research assistant",
            "laboratory technician", "physics teacher", "lecturer",
            "quality control officer", "environmental analyst",
            "meteorological assistant", "banking officer", "actuarial assistant",
            "industrial analyst",
        ],
        "industry": ["research", "it", "education", "banking", "environment", "manufacturing"],
    },
    "015": {  # Applied Sciences (Physical)
        "career": [
            "research assistant", "laboratory technician", "quality control officer",
            "data analyst", "science teacher", "lecturer", "technical officer",
        ],
        "industry": ["research", "education", "manufacturing", "government"],
    },
    "108": {  # Physical Science - ICT (PICT)
        "career": [
            "data analyst", "software developer", "it support officer",
            "systems analyst", "network administrator", "laboratory technician",
            "research assistant", "electronics technician", "qa engineer",
            "web developer", "mobile app developer", "cybersecurity analyst",
            "database administrator", "cloud engineer", "devops engineer",
            "embedded systems engineer", "electronics engineer",
            "telecommunications engineer", "technical officer", "business analyst",
        ],
        "industry": ["it", "telecommunications", "electronics", "research", "education", "banking", "energy"],
    },
    # --- Management / Commerce ---
    "016": {  # Management
        "career": [
            "management trainee", "business analyst", "administrative officer",
            "human resource officer", "marketing executive", "sales executive",
            "operations manager", "financial analyst", "project manager",
            "supply chain executive", "customer relationship manager",
            "management consultant", "entrepreneur",
        ],
        "industry": ["corporate", "banking", "fmcg", "telecommunications", "retail", "consulting", "government"],
    },
    "018": {  # Commerce
        "career": [
            "accountant", "auditor", "financial analyst", "bank officer",
            "management trainee", "marketing executive", "sales executive",
            "operations manager", "business analyst", "tax consultant",
            "investment analyst", "entrepreneur",
        ],
        "industry": ["banking", "accounting", "corporate", "fmcg", "consulting", "insurance"],
    },
    "022": {  # Management Studies (TV/UOV)
        "career": [
            "management trainee", "business analyst", "administrative officer",
            "marketing executive", "operations manager", "entrepreneur",
        ],
        "industry": ["corporate", "banking", "fmcg", "retail"],
    },
    "40": {  # Management Studies (TV) — Vavuniya & Trincomalee campuses
        "career": [
            "management trainee", "business analyst", "administrative officer",
            "human resource officer", "marketing executive", "sales executive",
            "operations manager", "financial analyst", "project manager",
            "customer relationship manager", "entrepreneur",
        ],
        "industry": ["corporate", "banking", "fmcg", "retail", "government", "consulting"],
    },
    "42": {  # Arts (SAB) — Sabaragamuwa
        "career": [
            "teacher", "lecturer", "journalist", "content writer",
            "administrative officer", "translator", "development officer",
            "public relations officer", "human resource officer",
            "social worker", "research assistant", "customer service executive",
            "ngo program officer",
        ],
        "industry": ["education", "media", "government", "ngo", "banking"],
    },
    "271": {  # Management and Information Technology — Bio Science Stream (KLN)
        "career": [
            "business analyst", "systems analyst", "it business analyst",
            "software developer", "data analyst", "it project coordinator",
            "database administrator", "operations manager", "digital transformation specialist",
            "laboratory information systems officer", "health information officer",
        ],
        "industry": ["it", "banking", "corporate", "healthcare", "telecommunications"],
    },
    "027": {  # Management and IT (MIT — Kelaniya)
        "career": [
            "business analyst", "systems analyst", "it business analyst",
            "software developer", "data analyst", "it project coordinator",
            "database administrator", "operations manager", "digital transformation specialist",
        ],
        "industry": ["it", "banking", "corporate", "telecommunications"],
    },
    "028": {  # Management and Public Policy (SJP)
        "career": [
            "public policy analyst", "policy officer", "administrative officer",
            "development officer", "project coordinator",
            "monitoring and evaluation officer", "research analyst",
            "program officer", "governance analyst", "advisor",
        ],
        "industry": ["government", "ngo", "research", "corporate"],
    },
    "017": {  # Real Estate Management and Valuation
        "career": [
            "property valuer", "real estate manager", "estate officer",
            "property consultant", "valuation surveyor", "facilities manager",
            "real estate analyst", "leasing executive", "asset management officer",
        ],
        "industry": ["real estate", "construction", "banking", "government"],
    },
    "066": {  # Entrepreneurship and Management (UWU)
        "career": [
            "entrepreneur", "business owner", "business development executive",
            "management trainee", "startup founder", "operations manager",
        ],
        "industry": ["startups", "retail", "fmcg", "corporate"],
    },
    "077": {  # Business Information Systems (BIS — SJP)
        "career": [
            "business analyst", "systems analyst", "it business analyst",
            "data analyst", "database administrator", "systems administrator",
            "erp consultant", "project coordinator", "software developer",
            "business intelligence analyst", "qa engineer",
        ],
        "industry": ["it", "banking", "telecommunications", "consulting", "bpo"],
    },
    "079": {  # Management and IT (SEUSL)
        "career": [
            "business analyst", "it officer", "systems administrator",
            "software developer", "data analyst", "it project coordinator",
        ],
        "industry": ["it", "banking", "corporate"],
    },
    "091": {  # IT & Management (Moratuwa)
        "career": [
            "it manager", "business analyst", "systems analyst",
            "software developer", "data analyst", "erp consultant",
            "digital transformation specialist",
        ],
        "industry": ["it", "banking", "corporate", "telecommunications"],
    },
    "109": {  # Business Science (Moratuwa)
        "career": [
            "business analyst", "data scientist", "quantitative analyst",
            "financial analyst", "management consultant", "corporate strategy analyst",
            "business development executive",
        ],
        "industry": ["banking", "consulting", "it", "corporate", "insurance"],
    },
    "114": {  # Human Resource Development (UWU)
        "career": [
            "human resource officer", "hr executive", "hr manager",
            "recruitment officer", "talent acquisition specialist",
            "training and development officer", "payroll officer",
            "employee relations officer", "compensation and benefits specialist",
            "hr business partner", "administrative officer",
        ],
        "industry": ["corporate", "banking", "fmcg", "manufacturing", "it", "consulting", "government"],
    },
    # --- Arts / Humanities ---
    "019": {  # Arts
        "career": [
            "teacher", "lecturer", "journalist", "content writer",
            "social worker", "public relations officer", "human resource officer",
            "research assistant", "translator", "customer service executive",
            "administrative officer", "development officer", "ngo program officer",
        ],
        "industry": ["education", "media", "government", "ngo", "banking", "tourism"],
    },
    "021": {  # Arts (SAB — Sabaragamuwa)
        "career": [
            "teacher", "lecturer", "journalist", "content writer",
            "administrative officer", "translator", "development officer",
        ],
        "industry": ["education", "media", "government", "ngo"],
    },
    "105": {  # TESL
        "career": [
            "esl teacher", "english language teacher", "private tutor", "lecturer",
            "language instructor", "curriculum developer", "teacher trainer",
            "content writer", "editor", "proofreader", "translator",
            "corporate trainer", "instructional designer", "soft skills trainer",
        ],
        "industry": ["education", "media", "corporate", "bpo", "ngo"],
    },
    "098": {  # Translation Studies
        "career": [
            "translator", "interpreter", "language teacher", "lecturer",
            "content writer", "editor", "public relations officer",
            "international liaison officer",
        ],
        "industry": ["education", "media", "government", "ngo", "international"],
    },
    "132": {  # English Language & Applied Linguistics (UWU)
        "career": [
            "english teacher", "translator", "content writer", "journalist",
            "editor", "media officer", "lecturer", "customer service executive",
            "bpo executive", "corporate trainer",
        ],
        "industry": ["education", "media", "bpo", "corporate", "government"],
    },
    # --- Performing / Visual Arts ---
    "041": {  # Arts (SP) — Performing Arts
        "career": [
            "actor", "theatre artist", "drama teacher", "dance teacher",
            "choreographer", "musician", "singer", "stage performer",
            "director", "script writer", "drama coach", "voice artist",
            "radio presenter", "tv presenter", "arts instructor",
            "lecturer", "creative director", "event coordinator",
            "costume designer", "production assistant",
        ],
        "industry": ["arts", "entertainment", "education", "media", "events", "film"],
    },
    "020": {  # Arts (SP) — Mass Media
        "career": [
            "journalist", "news reporter", "news anchor", "tv presenter",
            "radio presenter", "content writer", "copywriter", "editor",
            "social media manager", "digital marketing executive",
            "public relations officer", "advertising executive",
            "creative director", "video producer", "script writer",
            "photographer", "videographer", "media researcher",
            "communication specialist", "event coordinator", "brand manager",
        ],
        "industry": ["media", "advertising", "digital marketing", "entertainment", "events"],
    },
    "068": {  # Music
        "career": [
            "music teacher", "music lecturer", "performer", "singer",
            "instrumentalist", "composer", "music director", "sound engineer",
            "music producer", "studio musician", "choir director",
            "recording engineer", "music instructor",
        ],
        "industry": ["education", "entertainment", "media", "events", "recording"],
    },
    "069": {  # Dance
        "career": [
            "dance teacher", "choreographer", "dancer", "dance instructor",
            "performing arts teacher", "lecturer",
        ],
        "industry": ["arts", "education", "entertainment", "events"],
    },
    "070": {  # Art & Design
        "career": [
            "artist", "graphic designer", "illustrator", "art teacher",
            "creative director", "visual artist", "lecturer",
        ],
        "industry": ["arts", "education", "design", "media", "advertising"],
    },
    "071": {  # Drama & Theatre
        "career": [
            "actor", "director", "playwright", "drama teacher",
            "stage performer", "theatre artist", "script writer",
            "drama coach", "production assistant", "lecturer",
        ],
        "industry": ["arts", "education", "entertainment", "film", "media"],
    },
    "072": {  # Visual & Technological Arts
        "career": [
            "visual artist", "digital artist", "multimedia designer",
            "arts educator", "creative designer", "lecturer",
        ],
        "industry": ["arts", "design", "media", "education"],
    },
    "085": {  # Visual Arts (UVPA)
        "career": [
            "visual artist", "painter", "sculptor", "art teacher",
            "art lecturer", "gallery curator", "arts administrator", "illustrator",
        ],
        "industry": ["arts", "education", "culture", "government"],
    },
    "134": {  # Creative Music Technology and Production (SJP)
        "career": [
            "music producer", "sound engineer", "audio engineer",
            "recording engineer", "mixing engineer", "mastering engineer",
            "music composer", "film tv sound designer", "studio technician",
            "live sound engineer", "dj", "music director",
            "audio post-production specialist", "multimedia content creator",
        ],
        "industry": ["media", "recording", "entertainment", "film", "advertising", "events"],
    },
    # --- Law ---
    "025": {  # Law
        "career": [
            "attorney-at-law", "legal officer", "corporate lawyer", "legal advisor",
            "prosecutor", "judge", "legal consultant", "compliance officer",
            "company secretary", "legal researcher",
        ],
        "industry": ["law", "corporate", "banking", "government", "ngo"],
    },
    # --- Nursing / Allied Health ---
    "037": {  # Nursing
        "career": [
            "registered nurse", "staff nurse", "nursing officer", "ward nurse",
            "icu nurse", "emergency nurse", "pediatric nurse", "maternity nurse",
            "community health nurse", "public health nurse", "nursing educator",
            "clinical instructor", "infection control nurse", "nursing supervisor",
            "home care nurse", "research nurse", "military nurse",
        ],
        "industry": ["healthcare", "public health", "education", "military", "ngo"],
    },
    "051": {  # Pharmacy
        "career": [
            "pharmacist", "hospital pharmacist", "clinical pharmacist",
            "industrial pharmacist", "drug quality control officer",
            "regulatory affairs officer", "medical representative",
            "research pharmacist", "drug safety officer", "production pharmacist",
            "formulation scientist", "lecturer", "clinical research associate",
            "supply chain pharmacist", "entrepreneur",
        ],
        "industry": ["pharmaceuticals", "healthcare", "manufacturing", "research", "retail"],
    },
    "052": {  # Medical Laboratory Sciences
        "career": [
            "medical laboratory technologist", "medical laboratory scientist",
            "clinical laboratory technologist", "pathology laboratory officer",
            "microbiology technologist", "hematology technologist",
            "biochemistry technologist", "histopathology technologist",
            "blood bank technologist", "research laboratory scientist",
            "laboratory supervisor", "infection control officer",
            "quality control officer", "lecturer",
        ],
        "industry": ["healthcare", "research", "pharmaceuticals", "education"],
    },
    "053": {  # Radiography
        "career": [
            "radiographer", "ct scan technologist", "mri technologist",
            "x-ray technologist", "diagnostic imaging specialist",
            "application specialist",
        ],
        "industry": ["healthcare", "medical equipment"],
    },
    "054": {  # Physiotherapy
        "career": [
            "physiotherapist", "sports physiotherapist", "rehabilitation therapist",
            "clinical physiotherapist", "pediatric physiotherapist",
            "geriatric physiotherapist", "orthopedic physiotherapist",
            "neurological physiotherapist", "occupational health physiotherapist",
            "fitness and wellness consultant", "exercise therapist", "lecturer",
        ],
        "industry": ["healthcare", "sports", "rehabilitation", "education", "corporate"],
    },
    "115": {  # Occupational Therapy
        "career": [
            "occupational therapist", "rehabilitation specialist",
            "pediatric occupational therapist", "geriatric occupational therapist",
            "mental health occupational therapist", "ergonomics consultant",
            "assistive technology specialist", "research assistant",
            "clinical educator", "community health worker",
        ],
        "industry": ["healthcare", "education", "rehabilitation", "research", "ngo"],
    },
    "116": {  # Optometry
        "career": [
            "optometrist", "clinical optometrist", "refractionist",
            "contact lens specialist", "low vision specialist",
            "vision therapy specialist", "pediatric optometrist",
            "optical store optometrist", "vision care consultant",
            "lecturer", "research optometrist",
        ],
        "industry": ["healthcare", "optical retail", "education", "research"],
    },
    "083": {  # Speech and Hearing Sciences
        "career": [
            "speech therapist", "audiologist", "hearing aid specialist",
            "speech and language pathologist", "pediatric speech therapist",
            "clinical therapist", "rehabilitation specialist",
            "special needs therapist", "ent clinic assistant",
            "research assistant", "lecturer", "community health officer",
            "early intervention specialist", "voice therapist",
        ],
        "industry": ["healthcare", "education", "rehabilitation", "research", "ngo"],
    },
    "138": {  # Medical Imaging Technology
        "career": [
            "radiographer", "mri technologist", "ct scan technologist",
            "ultrasound technologist", "x-ray technologist",
            "nuclear medicine technologist", "imaging technician",
            "interventional radiology technologist", "pacs administrator",
            "application specialist", "radiation safety officer", "lecturer",
        ],
        "industry": ["healthcare", "medical equipment", "education", "research"],
    },
    # --- Special medical ---
    "032": {  # Ayurveda Medicine and Surgery
        "career": [
            "ayurveda medical officer", "ayurvedic doctor", "panchakarma specialist",
            "ayurvedic consultant", "wellness doctor", "community medical officer",
            "research officer", "lecturer", "drug development officer", "health advisor",
        ],
        "industry": ["healthcare", "traditional medicine", "pharmaceuticals", "education", "ngo"],
    },
    "033": {  # Unani Medicine and Surgery
        "career": [
            "unani medical officer", "unani doctor", "unani consultant",
            "community medical officer", "research officer", "lecturer",
            "herbal drug development officer", "health advisor",
        ],
        "industry": ["healthcare", "traditional medicine", "pharmaceuticals", "education"],
    },
    "036": {  # Siddha Medicine and Surgery
        "career": [
            "siddha medical officer", "traditional medicine practitioner",
            "community medical officer", "lecturer", "research officer",
        ],
        "industry": ["healthcare", "traditional medicine", "education"],
    },
    "050": {  # Health Promotion
        "career": [
            "health promotion officer", "public health officer",
            "community health worker", "health educator",
            "disease prevention officer", "health researcher",
        ],
        "industry": ["public health", "healthcare", "ngo", "research"],
    },
    # --- Science specialisations ---
    "058": {  # Biochemistry & Molecular Biology
        "career": [
            "biochemist", "molecular biologist", "research scientist",
            "laboratory analyst", "clinical research associate",
            "quality control analyst", "pharmaceutical analyst",
            "biomedical scientist", "genetic analyst", "forensic scientist",
            "bioinformatics analyst", "drug development scientist",
            "immunologist", "toxicologist", "microbiologist", "laboratory manager",
        ],
        "industry": ["research", "pharmaceuticals", "healthcare", "biotechnology", "food"],
    },
    "118": {  # Applied Chemistry
        "career": [
            "chemist", "analytical chemist", "industrial chemist",
            "laboratory technologist", "quality control officer",
            "quality assurance officer", "research scientist",
            "environmental analyst", "food chemist", "pharmaceutical analyst",
            "forensic scientist", "materials chemist", "water quality analyst",
        ],
        "industry": ["chemicals", "pharmaceuticals", "food", "environment", "research", "manufacturing"],
    },
    "139": {  # Polymer Science and Industrial Management
        "career": [
            "polymer technologist", "materials engineer", "quality control officer",
            "quality assurance engineer", "production engineer", "process engineer",
            "industrial manager", "r&d officer", "product development scientist",
            "manufacturing supervisor", "lab technician", "supply chain executive",
            "technical sales engineer", "packaging technologist",
        ],
        "industry": ["manufacturing", "rubber", "packaging", "chemicals", "fmcg", "research", "apparel"],
    },
    "059": {  # Industrial Statistics & Mathematical Finance
        "career": [
            "statistician", "data analyst", "data scientist", "business analyst",
            "quantitative analyst", "actuarial analyst", "research analyst",
            "quality control analyst", "operations analyst", "risk analyst",
            "market research analyst", "forecasting analyst", "financial analyst",
        ],
        "industry": ["it", "finance", "insurance", "research", "manufacturing", "banking"],
    },
    "060": {  # Statistics & Operations Research (PDN)
        "career": [
            "statistician", "data analyst", "operations research analyst",
            "quality engineer", "business analyst", "actuary",
        ],
        "industry": ["research", "insurance", "manufacturing", "banking"],
    },
    "113": {  # Financial Mathematics and Industrial Statistics (RUH)
        "career": [
            "statistician", "data analyst", "financial analyst",
            "quantitative analyst", "actuarial analyst", "risk analyst",
            "business analyst", "research analyst", "quality control analyst",
        ],
        "industry": ["finance", "insurance", "research", "manufacturing", "banking"],
    },
    "110": {  # Financial Engineering (KLN)
        "career": [
            "financial engineer", "quantitative analyst", "financial analyst",
            "risk analyst", "portfolio manager", "investment analyst",
            "derivatives trader", "financial modeler", "actuary",
        ],
        "industry": ["finance", "banking", "insurance", "investment"],
    },
    "131": {  # Financial Economics (SJP)
        "career": [
            "financial analyst", "economic analyst", "investment analyst",
            "risk analyst", "credit analyst", "policy analyst", "business analyst",
            "market research analyst", "data analyst", "portfolio analyst",
            "banking officer", "treasury analyst", "economic consultant",
        ],
        "industry": ["banking", "finance", "investment", "insurance", "corporate", "consulting", "government"],
    },
    "133": {  # Banking and Insurance (UOV)
        "career": [
            "banking officer", "insurance officer", "underwriter",
            "credit analyst", "risk analyst", "investment analyst", "financial analyst",
            "actuarial analyst",
        ],
        "industry": ["banking", "insurance", "finance", "investment"],
    },
    # --- Technology stream ---
    "102": {  # Engineering Technology (ET)
        "career": [
            "engineering technologist", "project engineer", "site engineer",
            "maintenance engineer", "production engineer", "quality assurance engineer",
            "manufacturing engineer", "automation engineer", "electrical technologist",
            "technical officer", "operations engineer", "design engineer",
            "plant engineer", "process engineer", "facilities engineer",
        ],
        "industry": ["manufacturing", "construction", "power", "energy", "telecommunications", "it", "government"],
    },
    "103": {  # Biosystems Technology (BST)
        "career": [
            "agricultural technologist", "food quality control officer",
            "food safety officer", "biosystems technologist",
            "environmental technologist", "research assistant", "farm manager",
            "irrigation systems technician", "plantation supervisor",
            "laboratory technician", "agro-industry officer", "sustainability officer",
        ],
        "industry": ["agriculture", "food", "biotechnology", "environment", "research", "plantation"],
    },
    # --- Food / Nutrition ---
    "005": {  # Food Science & Nutrition (Wayamba)
        "career": [
            "food technologist", "nutritionist", "food scientist",
            "quality control officer", "production executive", "food safety officer",
        ],
        "industry": ["food", "healthcare", "manufacturing"],
    },
    "035": {  # Food Science & Technology
        "career": [
            "food technologist", "food scientist", "quality assurance officer",
            "quality control officer", "production executive", "food safety officer",
            "research officer", "nutritionist", "food microbiologist",
            "laboratory analyst", "product development officer",
            "packaging technologist", "regulatory affairs officer", "food inspector",
        ],
        "industry": ["food", "manufacturing", "research", "retail", "agriculture"],
    },
    "087": {  # Food Production & Technology Management (Wayamba)
        "career": [
            "food production manager", "food technologist", "quality control officer",
            "production supervisor", "plant manager", "entrepreneur",
        ],
        "industry": ["food", "manufacturing", "agriculture"],
    },
    "107": {  # Food Business Management (SUSL)
        "career": [
            "food business manager", "marketing executive", "sales manager",
            "production manager", "supply chain manager", "quality assurance officer",
            "retail manager", "entrepreneur",
        ],
        "industry": ["food", "retail", "fmcg", "supply chain", "agribusiness"],
    },
    # --- Architecture / Design / Planning ---
    "023": {  # Architecture (Moratuwa)
        "career": [
            "architect", "design engineer", "urban planner", "project manager",
            "interior designer", "construction manager", "cad designer",
            "architectural technician", "lecturer",
        ],
        "industry": ["construction", "urban development", "real estate", "design", "government"],
    },
    "024": {  # Design (Moratuwa)
        "career": [
            "designer", "graphic designer", "product designer",
            "industrial designer", "ux designer", "creative director",
            "visual artist", "brand consultant",
        ],
        "industry": ["design", "advertising", "manufacturing", "fashion", "technology"],
    },
    "034": {  # Fashion Design & Product Development
        "career": [
            "fashion designer", "product developer", "textile designer",
            "quality controller", "fashion buyer", "merchandiser",
            "brand manager", "creative director",
        ],
        "industry": ["fashion", "textile", "apparel", "retail", "design"],
    },
    "030": {  # Urban Informatics and Planning (Moratuwa)
        "career": [
            "urban planner", "gis analyst", "spatial data analyst",
            "environmental officer", "urban development officer",
            "town planner", "research analyst",
        ],
        "industry": ["urban development", "government", "environment", "technology"],
    },
    "097": {  # Landscape Architecture (Moratuwa)
        "career": [
            "landscape architect", "environmental designer", "urban planner",
            "park planner", "horticulturist", "landscape designer",
        ],
        "industry": ["urban development", "environment", "construction", "government"],
    },
    "014": {  # Surveying Science (Sabaragamuwa)
        "career": [
            "surveyor", "land surveyor", "spatial data analyst", "gis analyst",
            "urban planner", "cartographer",
        ],
        "industry": ["construction", "government", "land management"],
    },
    "111": {  # Geographical Information Science (PDN)
        "career": [
            "gis analyst", "spatial data scientist", "remote sensing specialist",
            "urban planner", "environmental officer", "surveyor", "cartographer",
        ],
        "industry": ["government", "environment", "construction", "urban development", "research"],
    },
    # --- Marine / Fisheries ---
    "062": {  # Fisheries & Marine Sciences
        "career": [
            "fisheries officer", "marine biologist", "aquaculture officer",
            "fish farm manager", "environmental scientist", "marine research scientist",
            "oceanographer", "quality control officer", "laboratory analyst",
            "marine conservation officer", "seafood inspector",
        ],
        "industry": ["fisheries", "aquaculture", "environment", "research", "export", "marine"],
    },
    "106": {  # Marine and Fresh Water Sciences
        "career": [
            "marine biologist", "aquaculture officer", "fisheries officer",
            "environmental scientist", "water quality analyst", "research scientist",
            "conservation officer", "oceanographer", "environmental consultant",
            "laboratory analyst",
        ],
        "industry": ["fisheries", "aquaculture", "environment", "research", "ngo", "marine"],
    },
    "088": {  # Aquatic Resources Technology (UWU)
        "career": [
            "fisheries officer", "aquaculture officer", "marine biologist",
            "water quality analyst", "hatchery manager",
        ],
        "industry": ["fisheries", "aquaculture", "environment"],
    },
    "129": {  # Aquatic Bioresources (SJP)
        "career": [
            "aquaculture officer", "fisheries officer", "marine biologist",
            "fish farm manager", "aquatic research assistant", "environmental officer",
            "water quality analyst", "hatchery manager", "seafood quality control officer",
            "coastal resource officer", "marine ecologist", "fisheries scientist",
        ],
        "industry": ["fisheries", "aquaculture", "environment", "export", "research", "marine"],
    },
    "130": {  # Urban Bio Resources (SJP)
        "career": [
            "urban agriculture officer", "environmental officer",
            "waste management officer", "urban planner assistant",
            "sustainability officer", "green space manager", "urban forestry officer",
            "water resource officer", "recycling program officer",
            "climate change analyst",
        ],
        "industry": ["urban development", "environment", "government", "ngo", "research"],
    },
    "055": {  # Environmental Conservation & Management (KLN)
        "career": [
            "environmental officer", "environmental scientist", "sustainability officer",
            "waste management officer", "water quality analyst",
            "environmental consultant", "climate change analyst", "eia officer",
            "pollution control officer", "conservation officer",
            "natural resource manager",
        ],
        "industry": ["environment", "research", "government", "ngo", "manufacturing"],
    },
    "095": {  # Green Technology (RUH)
        "career": [
            "environmental officer", "sustainability officer",
            "renewable energy specialist", "solar energy technician",
            "waste management officer", "environmental consultant",
            "climate change analyst", "energy auditor", "green building consultant",
            "eia officer", "project officer", "research officer",
            "carbon footprint analyst", "lecturer", "entrepreneur",
        ],
        "industry": ["environment", "renewable energy", "sustainability", "construction", "research", "ngo"],
    },
    # --- Tourism / Hospitality ---
    "090": {  # Hospitality, Tourism and Events Management (UWU)
        "career": [
            "hotel manager", "resort manager", "travel executive",
            "event coordinator", "food and beverage manager", "tourism officer",
            "front office manager", "guest relations manager",
            "hospitality consultant", "tour guide",
        ],
        "industry": ["tourism", "hospitality", "events", "aviation", "leisure"],
    },
    "092": {  # Tourism & Hospitality Management
        "career": [
            "hotel manager", "front office manager", "resort manager",
            "travel executive", "event coordinator", "food and beverage manager",
            "tourism officer", "airline service executive", "tour guide",
            "hospitality consultant",
        ],
        "industry": ["tourism", "hospitality", "events", "aviation", "leisure"],
    },
    # --- Social / Peace ---
    "031": {  # Peace and Conflict Resolution
        "career": [
            "peace analyst", "human rights officer", "community development officer",
            "diplomatic officer", "mediator", "policy researcher",
            "program officer", "social scientist", "lecturer",
        ],
        "industry": ["government", "ngo", "international", "research"],
    },
    "112": {  # Social Work
        "career": [
            "social worker", "community development officer", "case worker",
            "probation officer", "child protection officer", "rehabilitation officer",
            "ngo project officer", "counsellor", "welfare officer",
            "social research assistant",
        ],
        "industry": ["government", "ngo", "healthcare", "community development", "research", "education"],
    },
    # --- Specialised computing / management ---
    "127": {  # Accounting Information Systems
        "career": [
            "accounting information systems analyst", "financial systems analyst",
            "accounting software specialist", "erp consultant", "accountant",
            "internal auditor", "external auditor", "financial analyst",
            "cost accountant", "budget analyst", "tax consultant",
            "systems analyst", "business analyst", "data analyst",
            "it auditor", "it risk analyst", "erp implementation consultant",
            "management accountant", "mis executive", "fintech analyst",
        ],
        "industry": ["it", "banking", "accounting", "finance", "consulting", "manufacturing", "insurance"],
    },
    "128": {  # Arts — Information Technology (SJP)
        "career": [
            "software developer", "web developer", "it support officer",
            "system administrator", "network administrator",
            "database administrator", "business analyst", "systems analyst",
            "ui/ux designer", "qa engineer", "data analyst",
            "it project coordinator", "digital marketing executive",
        ],
        "industry": ["it", "banking", "telecommunications", "bpo", "startups", "government"],
    },
    # --- Logistics / Transport ---
    "057": {  # Transport Management & Logistics Engineering (MRT)
        "career": [
            "transport engineer", "logistics engineer", "supply chain manager",
            "operations analyst", "transportation planner", "fleet manager",
            "port operations manager",
        ],
        "industry": ["logistics", "transport", "engineering", "aviation"],
    },
    "056": {  # Facilities Management (Moratuwa)
        "career": [
            "facilities manager", "operations manager", "property manager",
            "estate manager", "maintenance engineer", "project coordinator",
        ],
        "industry": ["real estate", "construction", "corporate", "hospitality"],
    },
    "101": {  # Project Management (UOV)
        "career": [
            "project manager", "project coordinator", "operations manager",
            "risk analyst", "business analyst", "planning engineer",
        ],
        "industry": ["corporate", "construction", "it", "manufacturing", "government"],
    },
    # --- Sports / Education ---
    "082": {  # Sports Science & Management
        "career": [
            "sports coach", "fitness trainer", "personal trainer",
            "strength and conditioning coach", "sports scientist", "sports analyst",
            "sports manager", "sports event coordinator",
            "physical education instructor", "sports administrator",
            "athletic trainer", "rehabilitation assistant", "sports facility manager",
        ],
        "industry": ["sports", "fitness", "education", "healthcare", "events", "government"],
    },
    "081": {  # Physical Education
        "career": [
            "physical education teacher", "coach", "sports officer",
            "fitness trainer", "sports coordinator",
        ],
        "industry": ["education", "sports", "government"],
    },
    "137": {  # Primary Education (Colombo)
        "career": [
            "primary school teacher", "assistant teacher", "class teacher",
            "special education teacher", "pre-school teacher", "education officer",
            "curriculum developer", "teacher trainer", "educational consultant",
            "school coordinator",
        ],
        "industry": ["education", "government", "ngo"],
    },
    # --- Mineral / Plantation / Animal Science ---
    "076": {  # Mineral Resources and Technology (UWU)
        "career": [
            "mining engineer", "geological survey officer",
            "mineral processing technologist", "research officer",
            "environmental officer",
        ],
        "industry": ["mining", "minerals", "research", "environment", "government"],
    },
    "135": {  # Plantation Management and Technology (UWU)
        "career": [
            "plantation manager", "estate manager", "tea estate officer",
            "rubber estate officer", "agribusiness manager", "agricultural officer",
            "quality assurance officer", "research officer", "export executive",
        ],
        "industry": ["plantation", "agriculture", "export", "agribusiness"],
    },
    "086": {  # Animal Science & Fisheries (PDN)
        "career": [
            "animal science officer", "livestock officer", "fisheries officer",
            "veterinary assistant", "research officer", "farm manager",
        ],
        "industry": ["agriculture", "livestock", "fisheries", "research"],
    },
    "067": {  # Animal Production and Food Technology (UWU)
        "career": [
            "animal production officer", "food technologist", "livestock officer",
            "quality control officer", "research officer",
        ],
        "industry": ["agriculture", "livestock", "food", "research"],
    },
    # --- Misc / Specialised ---
    "029": {  # Communication Studies
        "career": [
            "journalist", "content writer", "media analyst", "public relations officer",
            "social media manager", "copywriter", "communication specialist",
            "broadcaster",
        ],
        "industry": ["media", "advertising", "communications", "entertainment"],
    },
    "119": {  # Electronics and Computer Science (KLN)
        "career": [
            "software engineer", "embedded systems engineer", "electronics engineer",
            "system analyst", "network engineer", "robotics engineer",
            "automation engineer", "iot specialist", "hardware designer",
            "control systems engineer", "data analyst", "ai engineer",
            "cybersecurity analyst", "technical consultant",
            "industrial automation engineer", "firmware developer",
        ],
        "industry": ["it", "electronics", "manufacturing", "telecommunications", "automation", "research"],
    },
    "064": {  # Science and Technology (UWU)
        "career": [
            "scientific officer", "laboratory technician", "research assistant",
            "quality control officer", "science teacher",
        ],
        "industry": ["research", "education", "manufacturing"],
    },
    "100": {  # Film & Television Studies (KLN)
        "career": [
            "filmmaker", "film director", "tv producer", "scriptwriter",
            "video editor", "cinematographer", "film lecturer", "media analyst",
        ],
        "industry": ["media", "film", "entertainment", "education"],
    },
    "084": {  # Arabic Language
        "career": [
            "arabic language teacher", "translator", "interpreter",
            "lecturer", "journalist", "diplomatic officer",
        ],
        "industry": ["education", "media", "government", "ngo", "international"],
    },
    "063": {  # Islamic Studies (SEUSL)
        "career": ["islamic studies teacher", "lecturer", "translator", "researcher"],
        "industry": ["education", "research", "ngo"],
    },
    # --- GWUIM (Indigenous Medicine) ---
    "120": {  # Indigenous Medicinal Resources
        "career": [
            "ayurvedic researcher", "indigenous medicine practitioner",
            "herbal product developer", "quality control officer", "lecturer",
        ],
        "industry": ["traditional medicine", "pharmaceuticals", "research", "education"],
    },
    "121": {  # Health Information and Communication Technology
        "career": [
            "health it officer", "medical records officer", "health data analyst",
            "e-health specialist", "it support officer",
        ],
        "industry": ["health tech", "government", "it"],
    },
    "122": {  # Health Tourism and Hospitality Management
        "career": [
            "wellness center manager", "health tourism officer",
            "hospitality manager", "tour guide", "spa manager",
        ],
        "industry": ["health tech", "hospitality", "tourism"],
    },
    "123": {  # Biomedical Technology
        "career": [
            "biomedical technologist", "medical equipment technician",
            "clinical engineer", "biomedical researcher",
        ],
        "industry": ["healthcare", "medical equipment", "research"],
    },
    "124": {  # Indigenous Pharmaceutical Technology
        "career": [
            "herbal pharmaceutical technologist", "quality control officer",
            "production officer", "researcher",
        ],
        "industry": ["traditional medicine", "pharmaceuticals", "manufacturing"],
    },
    "125": {  # Yoga and Parapsychology
        "career": ["yoga instructor", "wellness consultant", "researcher", "lecturer"],
        "industry": ["wellness", "education", "research"],
    },
    "126": {  # Social Studies in Indigenous Knowledge
        "career": [
            "social researcher", "lecturer", "community development officer",
            "cultural officer",
        ],
        "industry": ["research", "education", "ngo"],
    },
    "140": {  # Service Management (GWUIM)
        "career": [
            "service manager", "customer service manager", "operations manager",
            "hotel manager", "quality assurance manager", "administrative officer",
        ],
        "industry": ["healthcare", "hospitality", "service industry", "government"],
    },
}

# ---------------------------------------------------------------------------
# Additional course numbers that map to the same tags as another
# ---------------------------------------------------------------------------
ALIASES: dict[str, str] = {
    # SJP nursing campus is physically at Colombo — same career paths as 037
    "037": "037",
    # GWUIM Ayurveda shares paths with CMB Ayurveda
    "032P": "032",
}


async def main() -> None:
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        # Try to load from .env
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("DATABASE_URL="):
                    db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

    if not db_url:
        print("ERROR: DATABASE_URL not set. Export it or put it in .env")
        sys.exit(1)

    # asyncpg wants postgresql:// not postgresql+asyncpg://
    if "+asyncpg" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"Connecting to DB …")
    conn = await asyncpg.connect(db_url, ssl="require")

    try:
        # Fetch all courses: course_code → course_number
        rows = await conn.fetch("SELECT course_code, course_number FROM courses")
        updated = 0
        skipped = 0

        for row in rows:
            code: str = row["course_code"]
            num: str = (row["course_number"] or "").lstrip("0") or row["course_number"]

            tags = COURSE_TAGS.get(num)
            if tags is None:
                # Try zero-padded
                num_padded = (row["course_number"] or "").zfill(3)
                tags = COURSE_TAGS.get(num_padded)

            if tags is None:
                skipped += 1
                continue

            await conn.execute(
                "UPDATE courses SET career_tags = $1, industry_tags = $2 WHERE course_code = $3",
                tags["career"],
                tags["industry"],
                code,
            )
            updated += 1

        print(f"Done. Updated: {updated}  Skipped (no mapping): {skipped}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
