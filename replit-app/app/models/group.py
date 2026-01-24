"""
Group Model

Represents an instructional group of students.
Groups can be regular grade-level groups, mixed-grade groups, or tutoring groups.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Group(Base):
    """
    Group model representing an instructional grouping.

    Groups are the primary organizational unit for instruction.
    Students are assigned to exactly one primary group, but can
    be in multiple tutoring groups.

    Group naming conventions:
    - Standard: "{Grade} Group {N} {Teacher}" (e.g., "KG Group 1 Garcia")
    - Mixed-grade: "{N} - {Teacher}" (e.g., "1 - T. Jones")
    - Tutoring: Contains word "tutoring" (e.g., "Reading Tutoring Group 1")
    """
    __tablename__ = "group"

    # Primary key
    group_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    site_id = Column(UUID(as_uuid=True), ForeignKey("site.site_id", ondelete="CASCADE"), nullable=False)
    grade_id = Column(UUID(as_uuid=True), ForeignKey("grade.grade_id"), nullable=True)  # Null for mixed-grade
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher.teacher_id"), nullable=True)

    # Group identification
    name = Column(String(255), nullable=False)

    # Mixed-grade support
    is_mixed_grade = Column(Boolean, default=False)
    mixed_grades = Column(ARRAY(String), nullable=True)  # e.g., ['G6', 'G7', 'G8']
    sheet_name = Column(String(100), nullable=True)  # Source sheet name (for migration reference)

    # Tutoring group flag
    is_tutoring_group = Column(Boolean, default=False)

    # Expected enrollment (for validation/reporting)
    expected_student_count = Column(Integer, nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="groups")
    grade = relationship("Grade", back_populates="groups")
    teacher = relationship("Teacher", back_populates="groups")
    students = relationship("Student", back_populates="group", foreign_keys="Student.group_id")
    lesson_entries = relationship("LessonEntry", back_populates="group")
    lesson_statuses = relationship("LessonStatus", back_populates="group")

    def __repr__(self):
        return f"<Group(name='{self.name}', id='{self.group_id}')>"

    @property
    def student_count(self) -> int:
        """Get current student count."""
        return len([s for s in self.students if s.status.value == "active"]) if self.students else 0

    @staticmethod
    def is_tutoring_group_name(name: str) -> bool:
        """Check if a group name indicates a tutoring group."""
        return "tutoring" in name.lower()

    def to_dict(self, include_students: bool = False):
        """Convert to dictionary for API responses."""
        result = {
            "group_id": str(self.group_id),
            "site_id": str(self.site_id),
            "grade_id": str(self.grade_id) if self.grade_id else None,
            "teacher_id": str(self.teacher_id) if self.teacher_id else None,
            "name": self.name,
            "is_mixed_grade": self.is_mixed_grade,
            "mixed_grades": self.mixed_grades,
            "is_tutoring_group": self.is_tutoring_group,
            "expected_student_count": self.expected_student_count,
            "actual_student_count": self.student_count,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "teacher_name": self.teacher.name if self.teacher else None,
            "grade_name": self.grade.name if self.grade else None,
        }

        if include_students:
            result["students"] = [
                {"student_id": str(s.student_id), "name": s.name, "status": s.status.value}
                for s in self.students
            ]

        return result
