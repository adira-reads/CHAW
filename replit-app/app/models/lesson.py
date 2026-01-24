"""
Lesson and SkillSection Models

Represents the UFLI curriculum structure:
- 128 lessons organized into 17 skill sections
- Includes review lesson flags and foundational markers
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class SkillSection(Base):
    """
    SkillSection model representing a group of related lessons.

    The 128 UFLI lessons are organized into 17 skill sections,
    each focusing on a specific phonics concept.
    """
    __tablename__ = "skill_section"

    # Primary key
    section_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Section information
    name = Column(String(100), nullable=False, unique=True)
    seq_order = Column(Integer, nullable=False)  # 1-17

    # Lesson range (for reference, actual mapping is in lessons)
    lesson_range_start = Column(Integer, nullable=True)
    lesson_range_end = Column(Integer, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lessons = relationship("Lesson", back_populates="section")

    def __repr__(self):
        return f"<SkillSection(name='{self.name}', order={self.seq_order})>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "section_id": str(self.section_id),
            "name": self.name,
            "seq_order": self.seq_order,
            "lesson_range_start": self.lesson_range_start,
            "lesson_range_end": self.lesson_range_end,
            "lesson_count": len(self.lessons) if self.lessons else 0,
        }


class Lesson(Base):
    """
    Lesson model representing a single UFLI lesson (1-128).

    Each lesson has:
    - A unique number (1-128)
    - A name/description
    - Association with a skill section
    - Flags for review lessons and foundational status
    """
    __tablename__ = "lesson"

    # Primary key
    lesson_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to skill section
    section_id = Column(UUID(as_uuid=True), ForeignKey("skill_section.section_id"), nullable=True)

    # Lesson identification
    number = Column(Integer, nullable=False, unique=True)  # 1-128
    name = Column(String(100), nullable=False)  # e.g., "UFLI L1 a/ā/"
    short_name = Column(String(20), nullable=False)  # e.g., "L1"
    description = Column(String(255), nullable=True)  # Optional detailed description

    # Lesson flags
    is_review = Column(Boolean, default=False)  # Review lessons have special handling
    is_foundational = Column(Boolean, default=False)  # Lessons 1-34

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    section = relationship("SkillSection", back_populates="lessons")
    lesson_statuses = relationship("LessonStatus", back_populates="lesson")
    lesson_entries = relationship("LessonEntry", back_populates="lesson")

    def __repr__(self):
        return f"<Lesson(number={self.number}, name='{self.short_name}')>"

    @staticmethod
    def get_full_name(number: int, description: str = None) -> str:
        """Generate full lesson name."""
        if description:
            return f"UFLI L{number} {description}"
        return f"UFLI L{number}"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "lesson_id": str(self.lesson_id),
            "section_id": str(self.section_id) if self.section_id else None,
            "number": self.number,
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "is_review": self.is_review,
            "is_foundational": self.is_foundational,
            "section_name": self.section.name if self.section else None,
        }
