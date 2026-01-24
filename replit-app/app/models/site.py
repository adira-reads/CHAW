"""
Site Model

Represents a school/organization using the UFLI tracking system.
Each site has its own configuration and isolated data.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Site(Base):
    """
    Site model representing a school or organization.

    A site is the top-level entity that contains all other data.
    Multi-tenancy is achieved by filtering all queries by site_id.
    """
    __tablename__ = "site"

    # Primary key
    site_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Configuration
    allow_grade_mixing = Column(Boolean, default=False)
    mixed_grade_config = Column(JSONB, nullable=True)
    # Example: {"G6 to G8 Groups": ["G6", "G7", "G8"], "SC Classroom": ["G1", "G2", "G3", "G4"]}

    sheet_format = Column(String(20), default="standard")  # 'standard' or 'sankofa'
    group_naming_pattern = Column(String(50), default="GRADE_GROUP_TEACHER")

    # Feature flags
    feature_tutoring = Column(Boolean, default=False)
    feature_pacing = Column(Boolean, default=False)
    feature_parent_reports = Column(Boolean, default=False)
    feature_monday_integration = Column(Boolean, default=False)

    # Integration settings
    monday_api_key = Column(String(255), nullable=True)
    monday_board_id = Column(String(100), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="2.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    grades = relationship("Grade", back_populates="site", cascade="all, delete-orphan")
    teachers = relationship("Teacher", back_populates="site", cascade="all, delete-orphan")
    groups = relationship("Group", back_populates="site", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="site", cascade="all, delete-orphan")
    users = relationship("User", back_populates="site", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Site(name='{self.name}', id='{self.site_id}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "site_id": str(self.site_id),
            "name": self.name,
            "description": self.description,
            "allow_grade_mixing": self.allow_grade_mixing,
            "mixed_grade_config": self.mixed_grade_config,
            "feature_tutoring": self.feature_tutoring,
            "feature_pacing": self.feature_pacing,
            "feature_parent_reports": self.feature_parent_reports,
            "is_active": self.is_active,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
