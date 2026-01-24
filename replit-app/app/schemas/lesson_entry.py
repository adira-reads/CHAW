"""
Lesson Entry Schemas

Schemas for lesson entry (Small Group Progress) operations.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from uuid import UUID


class StudentStatusEntry(BaseModel):
    """Single student status in a lesson entry."""
    student_id: UUID
    status: str = Field(..., pattern="^[YNAU]$")  # Y, N, A, or U

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v.upper() not in ['Y', 'N', 'A', 'U']:
            raise ValueError('Status must be Y, N, A, or U')
        return v.upper()


class LessonEntryCreate(BaseModel):
    """Create single lesson entry."""
    student_id: UUID
    group_id: UUID
    teacher_id: UUID
    lesson_id: UUID
    entry_date: Optional[datetime] = None
    status: str = Field(..., pattern="^[YNAU]$")
    entry_type: str = "small_group"  # small_group, tutoring, prek
    tutoring_lesson_type: Optional[str] = None  # ufli_reteach, comprehension, other
    lesson_detail: Optional[str] = None


class LessonEntryBatchCreate(BaseModel):
    """
    Batch create lesson entries (typical lesson entry form submission).

    This is the primary way lessons are entered - a teacher selects:
    - Group
    - Lesson
    - Date
    - Status for each student
    """
    group_id: UUID
    teacher_id: UUID
    lesson_id: UUID
    entry_date: Optional[datetime] = None
    students: List[StudentStatusEntry]
    entry_type: str = "small_group"


class LessonEntryResponse(BaseModel):
    """Lesson entry response."""
    entry_id: UUID
    site_id: UUID
    student_id: UUID
    group_id: UUID
    teacher_id: UUID
    lesson_id: UUID
    entry_date: datetime
    status: str
    entry_type: str
    tutoring_lesson_type: Optional[str] = None
    lesson_detail: Optional[str] = None
    created_at: datetime
    # Related names for display
    student_name: Optional[str] = None
    group_name: Optional[str] = None
    teacher_name: Optional[str] = None
    lesson_number: Optional[int] = None
    lesson_name: Optional[str] = None

    class Config:
        from_attributes = True


class LessonEntryListResponse(BaseModel):
    """Paginated lesson entry list."""
    items: List[LessonEntryResponse]
    total: int
    page: int
    page_size: int
    pages: int


class LessonEntryFilter(BaseModel):
    """Filter parameters for lesson entries."""
    student_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    lesson_id: Optional[UUID] = None
    entry_type: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class TutoringEntryCreate(BaseModel):
    """Create tutoring entry with specific tutoring fields."""
    group_id: UUID
    teacher_id: UUID
    lesson_number: int  # UFLI lesson number for reteach
    entry_date: Optional[datetime] = None
    students: List[StudentStatusEntry]
    tutoring_lesson_type: str  # ufli_reteach, comprehension, other
    lesson_detail: Optional[str] = None


class RecentEntryResponse(BaseModel):
    """Recent entry for dashboard display."""
    entry_date: datetime
    group_name: str
    lesson_name: str
    student_count: int
    pass_count: int
    teacher_name: str
