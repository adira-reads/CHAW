"""
Tutoring Models

Models for tracking tutoring/intervention sessions:
- StudentTutoringGroup: Many-to-many relationship for tutoring group assignments
- TutoringSummary: Aggregated tutoring metrics per student
"""

from sqlalchemy import Column, Integer, Date, Boolean, DateTime, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class StudentTutoringGroup(Base):
    """
    Junction table for student-tutoring group many-to-many relationship.

    Students can be assigned to multiple tutoring groups simultaneously,
    unlike their single primary instructional group.
    """
    __tablename__ = "student_tutoring_group"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.group_id", ondelete="CASCADE"), nullable=False)

    # Assignment details
    assigned_date = Column(Date, default=func.current_date())
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="tutoring_groups")
    group = relationship("Group")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('student_id', 'group_id', name='uq_student_tutoring_group'),
    )

    def __repr__(self):
        return f"<StudentTutoringGroup(student_id='{self.student_id}', group_id='{self.group_id}')>"


class TutoringSummary(Base):
    """
    TutoringSummary model storing aggregated tutoring metrics.

    Equivalent to the Tutoring Summary sheet in Google Sheets.
    Tracks pass rates for different tutoring lesson types:
    - UFLI Reteach: Retaught UFLI lessons
    - Comprehension: Comprehension practice
    - Other: Other interventions
    """
    __tablename__ = "tutoring_summary"

    # Primary key
    summary_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key (one-to-one with student)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False, unique=True)

    # Session counts
    total_sessions = Column(Integer, default=0)

    # UFLI Reteach metrics
    reteach_count = Column(Integer, default=0)  # Total attempts
    reteach_pass_count = Column(Integer, default=0)  # Passed attempts
    reteach_pass_pct = Column(Numeric(5, 2), default=0)  # Pass rate

    # Comprehension metrics
    comprehension_count = Column(Integer, default=0)
    comprehension_pass_count = Column(Integer, default=0)
    comprehension_pass_pct = Column(Numeric(5, 2), default=0)

    # Other intervention metrics
    other_count = Column(Integer, default=0)
    other_pass_count = Column(Integer, default=0)
    other_pass_pct = Column(Numeric(5, 2), default=0)

    # Overall metrics
    overall_pass_pct = Column(Numeric(5, 2), default=0)
    last_session_date = Column(Date, nullable=True)

    # Metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="tutoring_summary")

    def __repr__(self):
        return f"<TutoringSummary(student_id='{self.student_id}', sessions={self.total_sessions}, overall={self.overall_pass_pct}%)>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "summary_id": str(self.summary_id),
            "student_id": str(self.student_id),
            "total_sessions": self.total_sessions,
            "reteach_count": self.reteach_count,
            "reteach_pass_count": self.reteach_pass_count,
            "reteach_pass_pct": float(self.reteach_pass_pct) if self.reteach_pass_pct else 0,
            "comprehension_count": self.comprehension_count,
            "comprehension_pass_count": self.comprehension_pass_count,
            "comprehension_pass_pct": float(self.comprehension_pass_pct) if self.comprehension_pass_pct else 0,
            "other_count": self.other_count,
            "other_pass_count": self.other_pass_count,
            "other_pass_pct": float(self.other_pass_pct) if self.other_pass_pct else 0,
            "overall_pass_pct": float(self.overall_pass_pct) if self.overall_pass_pct else 0,
            "last_session_date": self.last_session_date.isoformat() if self.last_session_date else None,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }
