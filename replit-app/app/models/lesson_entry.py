"""
LessonEntry Model

Represents a raw lesson entry from the Lesson Entry Form.
This is equivalent to the Small Group Progress sheet in Google Sheets.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class EntryType(enum.Enum):
    """Type of lesson entry."""
    small_group = "small_group"  # Regular UFLI instruction
    tutoring = "tutoring"  # Tutoring/intervention session
    prek = "prek"  # PreK letter tracking


class TutoringLessonType(enum.Enum):
    """Type of tutoring lesson (for tutoring entries only)."""
    ufli_reteach = "ufli_reteach"  # UFLI lesson reteach
    comprehension = "comprehension"  # Comprehension practice
    other = "other"  # Other intervention


class LessonEntry(Base):
    """
    LessonEntry model representing a single lesson entry submission.

    This is the raw log of all lesson entries, equivalent to the
    "Small Group Progress" sheet. Entries are processed to update
    LessonStatus records and progress metrics.

    For tutoring entries:
    - entry_type = 'tutoring'
    - tutoring_lesson_type indicates the type of tutoring
    - lesson_detail provides additional description
    """
    __tablename__ = "lesson_entry"

    # Primary key
    entry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    site_id = Column(UUID(as_uuid=True), ForeignKey("site.site_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.group_id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher.teacher_id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lesson.lesson_id"), nullable=False)

    # Entry details
    entry_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(1), nullable=False)  # Y, N, A, U
    entry_type = Column(Enum(EntryType), default=EntryType.small_group, nullable=False)

    # Tutoring-specific fields
    tutoring_lesson_type = Column(Enum(TutoringLessonType), nullable=True)
    lesson_detail = Column(String(255), nullable=True)  # Full description for tutoring

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="lesson_entries")
    group = relationship("Group", back_populates="lesson_entries")
    teacher = relationship("Teacher", back_populates="lesson_entries")
    lesson = relationship("Lesson", back_populates="lesson_entries")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_entry_site_date', 'site_id', 'entry_date'),
        Index('idx_entry_student', 'student_id'),
        Index('idx_entry_group', 'group_id'),
        Index('idx_entry_teacher', 'teacher_id'),
    )

    def __repr__(self):
        return f"<LessonEntry(student_id='{self.student_id}', lesson={self.lesson.number if self.lesson else None}, status='{self.status}', date='{self.entry_date}')>"

    @property
    def is_tutoring(self) -> bool:
        """Check if this is a tutoring entry."""
        return self.entry_type == EntryType.tutoring

    @property
    def is_passed(self) -> bool:
        """Check if the entry status is passed."""
        return self.status == "Y"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "entry_id": str(self.entry_id),
            "site_id": str(self.site_id),
            "student_id": str(self.student_id),
            "group_id": str(self.group_id),
            "teacher_id": str(self.teacher_id),
            "lesson_id": str(self.lesson_id),
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "status": self.status,
            "entry_type": self.entry_type.value,
            "tutoring_lesson_type": self.tutoring_lesson_type.value if self.tutoring_lesson_type else None,
            "lesson_detail": self.lesson_detail,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Include related names for display
            "student_name": self.student.name if self.student else None,
            "group_name": self.group.name if self.group else None,
            "teacher_name": self.teacher.name if self.teacher else None,
            "lesson_number": self.lesson.number if self.lesson else None,
            "lesson_name": self.lesson.short_name if self.lesson else None,
        }
