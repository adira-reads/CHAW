"""
Group Schemas

Schemas for group CRUD operations and responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class GroupBase(BaseModel):
    """Base group schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    grade_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None


class GroupCreate(GroupBase):
    """Create group request."""
    is_mixed_grade: bool = False
    mixed_grades: Optional[List[str]] = None  # e.g., ["G6", "G7", "G8"]
    is_tutoring_group: bool = False
    expected_student_count: Optional[int] = None


class GroupUpdate(BaseModel):
    """Update group request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    grade_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    is_mixed_grade: Optional[bool] = None
    mixed_grades: Optional[List[str]] = None
    is_tutoring_group: Optional[bool] = None
    expected_student_count: Optional[int] = None
    is_active: Optional[bool] = None


class GroupResponse(BaseModel):
    """Group response."""
    group_id: UUID
    site_id: UUID
    grade_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    name: str
    is_mixed_grade: bool
    mixed_grades: Optional[List[str]] = None
    is_tutoring_group: bool
    expected_student_count: Optional[int] = None
    actual_student_count: int = 0
    is_active: bool
    created_at: datetime
    grade_name: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


class StudentSummary(BaseModel):
    """Brief student summary for group listing."""
    student_id: UUID
    name: str
    status: str
    current_lesson: Optional[int] = None


class GroupWithStudents(GroupResponse):
    """Group response with student list."""
    students: List[StudentSummary] = []


class GroupListResponse(BaseModel):
    """Paginated group list response."""
    items: List[GroupResponse]
    total: int
    page: int
    page_size: int
    pages: int


class GroupProgressSummary(BaseModel):
    """Group progress summary."""
    group_id: UUID
    group_name: str
    student_count: int
    avg_current_lesson: Optional[float] = None
    min_lesson: Optional[int] = None
    max_lesson: Optional[int] = None
    avg_foundational_pct: float = 0
    avg_min_grade_pct: float = 0
    avg_benchmark_pct: float = 0


class GroupLessonsAndStudents(BaseModel):
    """Response for lesson entry form - lessons and students for a group."""
    group_id: UUID
    group_name: str
    lessons: List[dict]  # [{id: lesson_id, number: 42, name: "UFLI L42"}, ...]
    students: List[str]  # ["Adams, John", "Baker, Sarah", ...]
