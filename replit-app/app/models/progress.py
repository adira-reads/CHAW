"""
ProgressRecord Model

Represents aggregated progress metrics for a student.
This is the calculated summary equivalent to UFLI MAP and Grade Summary sheets.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class ProgressType(enum.Enum):
    """Type of progress record."""
    initial_assessment = "initial_assessment"  # Baseline at enrollment
    ufli_map = "ufli_map"  # Current progress (UFLI MAP equivalent)
    grade_summary = "grade_summary"  # Grade-level aggregation


class ProgressRecord(Base):
    """
    ProgressRecord model storing calculated progress metrics.

    Metrics are calculated from LessonStatus data and cached here
    for performance. Records should be recalculated when lesson
    statuses change.

    Three types of records:
    - initial_assessment: Snapshot of progress at enrollment
    - ufli_map: Current progress (updated after each lesson entry)
    - grade_summary: Aggregated for grade-level reporting
    """
    __tablename__ = "progress_record"

    # Primary key
    progress_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False)

    # Record type
    record_type = Column(Enum(ProgressType), nullable=False)

    # Foundational metrics (Lessons 1-34)
    foundational_count = Column(Integer, default=0)  # Count of Y statuses
    foundational_pct = Column(Numeric(5, 2), default=0)  # Percentage (count/34*100)

    # Minimum grade metrics (varies by grade)
    min_grade_count = Column(Integer, default=0)
    min_grade_pct = Column(Numeric(5, 2), default=0)

    # Full grade metrics (all current year lessons)
    full_grade_count = Column(Integer, default=0)
    full_grade_pct = Column(Numeric(5, 2), default=0)

    # Benchmark metrics (grade-specific denominator)
    benchmark_count = Column(Integer, default=0)
    benchmark_pct = Column(Numeric(5, 2), default=0)

    # PreK-specific metrics (letter tracking)
    form_count = Column(Integer, nullable=True)  # Letter forms recognized
    form_pct = Column(Numeric(5, 2), nullable=True)
    name_sound_count = Column(Integer, nullable=True)  # Letter names and sounds
    name_sound_pct = Column(Numeric(5, 2), nullable=True)

    # Skill section percentages (stored as JSON for flexibility)
    # Example: {"section_1": 85.5, "section_2": 92.0, ...}
    skill_sections = Column(JSONB, nullable=True)

    # Metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="progress_records")

    # Unique constraint: one record per student per type
    __table_args__ = (
        UniqueConstraint('student_id', 'record_type', name='uq_student_progress_type'),
    )

    def __repr__(self):
        return f"<ProgressRecord(student_id='{self.student_id}', type='{self.record_type.value}', benchmark={self.benchmark_pct}%)>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "progress_id": str(self.progress_id),
            "student_id": str(self.student_id),
            "record_type": self.record_type.value,
            "foundational_count": self.foundational_count,
            "foundational_pct": float(self.foundational_pct) if self.foundational_pct else 0,
            "min_grade_count": self.min_grade_count,
            "min_grade_pct": float(self.min_grade_pct) if self.min_grade_pct else 0,
            "full_grade_count": self.full_grade_count,
            "full_grade_pct": float(self.full_grade_pct) if self.full_grade_pct else 0,
            "benchmark_count": self.benchmark_count,
            "benchmark_pct": float(self.benchmark_pct) if self.benchmark_pct else 0,
            "form_count": self.form_count,
            "form_pct": float(self.form_pct) if self.form_pct else None,
            "name_sound_count": self.name_sound_count,
            "name_sound_pct": float(self.name_sound_pct) if self.name_sound_pct else None,
            "skill_sections": self.skill_sections,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }
