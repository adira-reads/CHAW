"""
User Model

Represents application users with role-based access control.
Users can be linked to teachers for role-based data filtering.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class UserRole(enum.Enum):
    """User role levels."""
    admin = "admin"  # Full access to site
    coordinator = "coordinator"  # Read all, write assigned grades
    teacher = "teacher"  # Read/write own groups only
    viewer = "viewer"  # Read-only access


class User(Base):
    """
    User model for application authentication and authorization.

    Users can be:
    - Linked to a teacher record (for teacher/coordinator roles)
    - Assigned to specific grades (for coordinators)
    - Independent (for admin/viewer roles)

    Authentication can be:
    - Local (email/password)
    - Replit Auth (replit_user_id)
    """
    __tablename__ = "app_user"

    # Primary key
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    site_id = Column(UUID(as_uuid=True), ForeignKey("site.site_id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher.teacher_id"), nullable=True)

    # Authentication
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=True)  # Null if using Replit Auth
    replit_user_id = Column(String(100), nullable=True)  # For Replit Auth

    # User information
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.teacher, nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="users")
    teacher = relationship("Teacher")

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role.value}')>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.admin

    @property
    def can_write(self) -> bool:
        """Check if user can write data."""
        return self.role in [UserRole.admin, UserRole.coordinator, UserRole.teacher]

    @property
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role == UserRole.admin

    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary for API responses."""
        result = {
            "user_id": str(self.user_id),
            "site_id": str(self.site_id),
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "teacher_id": str(self.teacher_id) if self.teacher_id else None,
            "teacher_name": self.teacher.name if self.teacher else None,
        }

        if include_sensitive:
            result["has_password"] = self.password_hash is not None
            result["has_replit_auth"] = self.replit_user_id is not None

        return result
