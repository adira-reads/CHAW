"""
Teacher Schemas

Schemas for teacher CRUD operations and responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID


class TeacherBase(BaseModel):
    """Base teacher schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class TeacherCreate(TeacherBase):
    """Create teacher request."""
    phone: Optional[str] = None


class TeacherUpdate(BaseModel):
    """Update teacher request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherResponse(BaseModel):
    """Teacher response."""
    teacher_id: UUID
    site_id: UUID
    name: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    group_count: int = 0

    class Config:
        from_attributes = True


class TeacherWithGroups(TeacherResponse):
    """Teacher response with assigned groups."""
    groups: List[dict] = []  # [{group_id, name, grade_name, student_count}, ...]


class TeacherListResponse(BaseModel):
    """Paginated teacher list response."""
    items: List[TeacherResponse]
    total: int
    page: int
    page_size: int
    pages: int
