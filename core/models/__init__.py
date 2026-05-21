"""Model exports.

Every model in the project should be importable from `core.models`.
"""

from core.models.reference import (
    District,
    Faculty,
    Medium,
    SpecialProvisionCategory,
    Stream,
    StreamSubject,
    Subject,
    University,
)
from core.models.course import Course
from core.models.course_eligibility import CourseStreamEligibility, CourseAlias

__all__ = [
    "District",
    "Faculty",
    "Medium",
    "SpecialProvisionCategory",
    "Stream",
    "StreamSubject",
    "Subject",
    "University",
    "Course",
    "CourseStreamEligibility",
    "CourseAlias",
]
