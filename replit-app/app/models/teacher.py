"""
Teacher Model

Represents an instructor who delivers UFLI lessons.
Teachers are assigned to groups and record lesson entries.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Teacher(Base):
    """
    Teacher model representing an instructor.

    Teachers can be assigned to multiple groups and are tracked
    for lesson entry attribution and reporting.
    """
    __tablename__ = "teacher"

    # Primary key
    teacher_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to site
    site_id = Column(UUID(as_uuid=True), ForeignKey("site.site_id", ondelete="CASCADE"), nullable=False)

    # Teacher information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="teachers")
    groups = relationship("Group", back_populates="teacher")
    lesson_entries = relationship("LessonEntry", back_populates="teacher")
    lesson_statuses = relationship("LessonStatus", back_populates="teacher")

    def __repr__(self):
        return f"<Teacher(name='{self.name}', id='{self.teacher_id}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "teacher_id": str(self.teacher_id),
            "site_id": str(self.site_id),
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "group_count": len(self.groups) if self.groups else 0,
        }
