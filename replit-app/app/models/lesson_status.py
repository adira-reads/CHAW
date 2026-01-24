"""
LessonStatus Model

Represents the completion status of a single lesson for a student.
This is the normalized form of the Y/N/A data from UFLI MAP sheets.
"""

from sqlalchemy import Column, Date, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class LessonStatusEnum(enum.Enum):
    """Lesson completion status values."""
    Y = "Y"  # Yes/Passed
    N = "N"  # No/Failed
    A = "A"  # Absent
    U = "U"  # Unenrolled


class LessonStatus(Base):
    """
    LessonStatus model representing a student's status on a single lesson.

    This table stores the normalized version of the UFLI MAP data.
    Each row represents one student's status on one lesson.

    For initial assessment data, is_initial_assessment=True.
    For current progress, is_initial_assessment=False.
    """
    __tablename__ = "lesson_status"

    # Primary key
    status_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lesson.lesson_id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.group_id"), nullable=True)  # Group when completed
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher.teacher_id"), nullable=True)  # Teacher who recorded

    # Status
    status = Column(Enum(LessonStatusEnum), nullable=False)
    completed_date = Column(Date, nullable=True)

    # Initial assessment flag
    is_initial_assessment = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="lesson_statuses")
    lesson = relationship("Lesson", back_populates="lesson_statuses")
    group = relationship("Group", back_populates="lesson_statuses")
    teacher = relationship("Teacher", back_populates="lesson_statuses")

    # Unique constraint: one status per student per lesson per assessment type
    __table_args__ = (
        UniqueConstraint('student_id', 'lesson_id', 'is_initial_assessment', name='uq_student_lesson_assessment'),
    )

    def __repr__(self):
        return f"<LessonStatus(student_id='{self.student_id}', lesson={self.lesson.number if self.lesson else None}, status='{self.status.value}')>"

    @property
    def is_passed(self) -> bool:
        """Check if lesson was passed."""
        return self.status == LessonStatusEnum.Y

    @property
    def is_attempted(self) -> bool:
        """Check if lesson was attempted (Y or N, not A)."""
        return self.status in [LessonStatusEnum.Y, LessonStatusEnum.N]

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "status_id": str(self.status_id),
            "student_id": str(self.student_id),
            "lesson_id": str(self.lesson_id),
            "lesson_number": self.lesson.number if self.lesson else None,
            "status": self.status.value,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "is_initial_assessment": self.is_initial_assessment,
            "group_id": str(self.group_id) if self.group_id else None,
            "teacher_id": str(self.teacher_id) if self.teacher_id else None,
        }
