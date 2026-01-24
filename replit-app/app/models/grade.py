"""
Grade Model

Represents a grade level (PreK, KG, G1-G8) within a site.
Contains grade-specific lesson requirements and benchmarks.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Grade(Base):
    """
    Grade model representing a grade level.

    Each grade has specific lesson requirements for progress calculations:
    - Foundational lessons (1-34)
    - Minimum grade lessons (varies by grade)
    - Current year lessons (varies by grade)
    - Benchmark denominator (for percentage calculations)
    """
    __tablename__ = "grade"

    # Primary key
    grade_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to site
    site_id = Column(UUID(as_uuid=True), ForeignKey("site.site_id", ondelete="CASCADE"), nullable=False)

    # Grade identification
    name = Column(String(10), nullable=False)  # PreK, KG, G1-G8
    display_name = Column(String(50), nullable=True)  # Pre-Kindergarten, Kindergarten, etc.
    seq_order = Column(Integer, nullable=False)  # For sorting: PreK=0, KG=1, G1=2, etc.

    # Grade-specific lesson requirements (stored as arrays of lesson numbers)
    foundational_max = Column(Integer, default=34)  # Lessons 1-34
    min_grade_lessons = Column(ARRAY(Integer), nullable=True)  # Required lesson numbers
    current_year_lessons = Column(ARRAY(Integer), nullable=True)  # Current year lessons
    benchmark_denominator = Column(Integer, nullable=True)  # Denominator for benchmark calc

    # For PreK letter-based tracking
    is_letter_based = Column(Boolean, default=False)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("Site", back_populates="grades")
    students = relationship("Student", back_populates="grade")
    groups = relationship("Group", back_populates="grade")

    # Unique constraint: one grade per site with same name
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<Grade(name='{self.name}', site_id='{self.site_id}')>"

    @staticmethod
    def get_seq_order(grade_name: str) -> int:
        """Get sequence order for a grade name."""
        order_map = {
            "PreK": 0,
            "KG": 1,
            "G1": 2,
            "G2": 3,
            "G3": 4,
            "G4": 5,
            "G5": 6,
            "G6": 7,
            "G7": 8,
            "G8": 9,
        }
        return order_map.get(grade_name, 99)

    @staticmethod
    def get_display_name(grade_name: str) -> str:
        """Get display name for a grade."""
        display_map = {
            "PreK": "Pre-Kindergarten",
            "KG": "Kindergarten",
            "G1": "Grade 1",
            "G2": "Grade 2",
            "G3": "Grade 3",
            "G4": "Grade 4",
            "G5": "Grade 5",
            "G6": "Grade 6",
            "G7": "Grade 7",
            "G8": "Grade 8",
        }
        return display_map.get(grade_name, grade_name)

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "grade_id": str(self.grade_id),
            "site_id": str(self.site_id),
            "name": self.name,
            "display_name": self.display_name or self.get_display_name(self.name),
            "seq_order": self.seq_order,
            "benchmark_denominator": self.benchmark_denominator,
            "is_letter_based": self.is_letter_based,
            "is_active": self.is_active,
        }
