"""
Unenrollment Models

Models for tracking student unenrollments and archiving:
- UnenrollmentLog: Tracks unenrollment events
- StudentArchive: Preserves complete student data after unenrollment
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class UnenrollmentStatus(enum.Enum):
    """Status of unenrollment processing."""
    pending = "pending"  # Reported, awaiting confirmation
    confirmed = "confirmed"  # Confirmed, processing complete
    resolved = "resolved"  # Issue resolved (student returned)
    error = "error"  # Error during processing


class UnenrollmentLog(Base):
    """
    UnenrollmentLog model tracking student unenrollment events.

    Equivalent to the Unenrolled Log sheet in Google Sheets.
    Created when a student is marked with status 'U' (Unenrolled).
    """
    __tablename__ = "unenrollment_log"

    # Primary key
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.student_id"), nullable=False)
    reported_by_id = Column(UUID(as_uuid=True), ForeignKey("teacher.teacher_id"), nullable=True)

    # Event details
    reported_date = Column(DateTime(timezone=True), server_default=func.now())
    lesson_at_unenroll = Column(String(50), nullable=True)  # Lesson when unenrollment was noted
    status = Column(Enum(UnenrollmentStatus), default=UnenrollmentStatus.pending)
    notes = Column(Text, nullable=True)

    # Integration tracking
    monday_task_id = Column(String(100), nullable=True)  # Monday.com task ID if created

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="unenrollment_logs")
    reported_by = relationship("Teacher")

    def __repr__(self):
        return f"<UnenrollmentLog(student_id='{self.student_id}', status='{self.status.value}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "log_id": str(self.log_id),
            "student_id": str(self.student_id),
            "reported_by_id": str(self.reported_by_id) if self.reported_by_id else None,
            "reported_date": self.reported_date.isoformat() if self.reported_date else None,
            "lesson_at_unenroll": self.lesson_at_unenroll,
            "status": self.status.value,
            "notes": self.notes,
            "monday_task_id": self.monday_task_id,
            "student_name": self.student.name if self.student else None,
            "reported_by_name": self.reported_by.name if self.reported_by else None,
        }


class StudentArchive(Base):
    """
    StudentArchive model preserving complete student data.

    When a student is unenrolled, their complete data is archived here
    as JSON snapshots for potential restoration or historical reference.

    Archives three types of data:
    - Initial Assessment data
    - UFLI MAP (current progress) data
    - Grade Summary data
    """
    __tablename__ = "student_archive"

    # Primary key
    archive_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.student_id"), nullable=False)
    unenrollment_log_id = Column(UUID(as_uuid=True), ForeignKey("unenrollment_log.log_id"), nullable=True)

    # Archived data snapshots (JSONB for flexibility)
    initial_assessment_data = Column(JSONB, nullable=True)  # IA snapshot
    ufli_map_data = Column(JSONB, nullable=True)  # UFLI MAP snapshot
    grade_summary_data = Column(JSONB, nullable=True)  # Grade Summary snapshot
    tutoring_data = Column(JSONB, nullable=True)  # Tutoring data if applicable

    # Archive metadata
    archived_at = Column(DateTime(timezone=True), server_default=func.now())
    archived_by = Column(String(255), nullable=True)  # User who triggered archive

    # Relationships
    student = relationship("Student", back_populates="archives")
    unenrollment_log = relationship("UnenrollmentLog")

    def __repr__(self):
        return f"<StudentArchive(student_id='{self.student_id}', archived_at='{self.archived_at}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "archive_id": str(self.archive_id),
            "student_id": str(self.student_id),
            "unenrollment_log_id": str(self.unenrollment_log_id) if self.unenrollment_log_id else None,
            "initial_assessment_data": self.initial_assessment_data,
            "ufli_map_data": self.ufli_map_data,
            "grade_summary_data": self.grade_summary_data,
            "tutoring_data": self.tutoring_data,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "archived_by": self.archived_by,
            "student_name": self.student.name if self.student else None,
        }
