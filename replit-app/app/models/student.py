"""
Student Model

Represents an individual student being tracked in the UFLI system.
Students are assigned to grades and groups, with progress tracked per lesson.
"""

from sqlalchemy import Column, String, Integer, Date, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class StudentStatus(enum.Enum):
    """Student enrollment status."""
    active = "active"
    inactive = "inactive"
    unenrolled = "unenrolled"
    transferred = "transferred"


class Student(Base):
    """
    Student model representing a learner.

    Each student belongs to exactly one site, one grade, and one primary group.
    Students can also be assigned to multiple tutoring groups.

    Progress is tracked through:
    - LessonStatus: Individual lesson completion (Y/N/A)
    - ProgressRecord: Aggregated metrics (foundational %, benchmark %, etc.)
    """
    __tablename__ = "student"

    # Primary key
    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    site_id = Column(UUID(as_uuid=True), ForeignKey("site.site_id", ondelete="CASCADE"), nullable=False)
    grade_id = Column(UUID(as_uuid=True), ForeignKey("grade.grade_id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.group_id"), nullable=True)

    # Student identification
    name = Column(String(255), nullable=False)

    # Status tracking
    status = Column(Enum(StudentStatus), default=StudentStatus.active, nullable=False)
    enrollment_date = Column(Date, nullable=True)
    unenrollment_date = Column(Date, nullable=True)

    # Cached current progress (denormalized for performance)
    # Updated via trigger/service when lesson status changes
    current_lesson = Column(Integer, nullable=True)  # Highest lesson number passed
    last_activity_date = Column(Date, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="students")
    grade = relationship("Grade", back_populates="students")
    group = relationship("Group", back_populates="students", foreign_keys=[group_id])
    lesson_statuses = relationship("LessonStatus", back_populates="student", cascade="all, delete-orphan")
    lesson_entries = relationship("LessonEntry", back_populates="student", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="student", cascade="all, delete-orphan")
    tutoring_summary = relationship("TutoringSummary", back_populates="student", uselist=False, cascade="all, delete-orphan")
    tutoring_groups = relationship("StudentTutoringGroup", back_populates="student", cascade="all, delete-orphan")
    unenrollment_logs = relationship("UnenrollmentLog", back_populates="student")
    archives = relationship("StudentArchive", back_populates="student")

    def __repr__(self):
        return f"<Student(name='{self.name}', grade='{self.grade.name if self.grade else None}', id='{self.student_id}')>"

    @property
    def is_active(self) -> bool:
        """Check if student is active."""
        return self.status == StudentStatus.active

    def to_dict(self, include_progress: bool = False):
        """Convert to dictionary for API responses."""
        result = {
            "student_id": str(self.student_id),
            "site_id": str(self.site_id),
            "grade_id": str(self.grade_id),
            "group_id": str(self.group_id) if self.group_id else None,
            "name": self.name,
            "status": self.status.value,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "current_lesson": self.current_lesson,
            "last_activity_date": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "grade_name": self.grade.name if self.grade else None,
            "group_name": self.group.name if self.group else None,
            "teacher_name": self.group.teacher.name if self.group and self.group.teacher else None,
        }

        if include_progress:
            # Include progress metrics from progress_records
            ufli_map = next(
                (pr for pr in self.progress_records if pr.record_type.value == "ufli_map"),
                None
            )
            if ufli_map:
                result["progress"] = {
                    "foundational_pct": float(ufli_map.foundational_pct) if ufli_map.foundational_pct else 0,
                    "min_grade_pct": float(ufli_map.min_grade_pct) if ufli_map.min_grade_pct else 0,
                    "benchmark_pct": float(ufli_map.benchmark_pct) if ufli_map.benchmark_pct else 0,
                }

        return result

    def to_dict_full(self):
        """Convert to dictionary with all details."""
        result = self.to_dict(include_progress=True)

        # Add lesson statuses
        result["lesson_statuses"] = {
            ls.lesson.number: ls.status.value
            for ls in self.lesson_statuses
            if not ls.is_initial_assessment
        }

        # Add initial assessment
        result["initial_assessment"] = {
            ls.lesson.number: ls.status.value
            for ls in self.lesson_statuses
            if ls.is_initial_assessment
        }

        return result
