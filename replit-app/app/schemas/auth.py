"""
Authentication Schemas

Schemas for user authentication and authorization.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    role: Optional[str] = None
    site_id: Optional[UUID] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """Create new user request."""
    email: EmailStr
    password: str
    name: str
    role: str = "teacher"  # admin, coordinator, teacher, viewer
    teacher_id: Optional[UUID] = None  # Link to teacher record


class UserUpdate(BaseModel):
    """Update user request."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    teacher_id: Optional[UUID] = None


class UserResponse(BaseModel):
    """User response."""
    user_id: UUID
    site_id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    teacher_id: Optional[UUID] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str


class PasswordReset(BaseModel):
    """Password reset request."""
    email: EmailStr
