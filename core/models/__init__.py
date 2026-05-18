"""Model exports.

Every model in the project should be importable from `core.models`.
This is what makes Alembic's autogenerate see them via Base.metadata.
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

__all__ = [
    "District",
    "Faculty",
    "Medium",
    "SpecialProvisionCategory",
    "Stream",
    "StreamSubject",
    "Subject",
    "University",
]
