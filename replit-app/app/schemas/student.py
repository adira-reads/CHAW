"""
Student Schemas

Schemas for student CRUD operations and responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID


class StudentBase(BaseModel):
    """Base student schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    grade_id: UUID
    group_id: Optional[UUID] = None


class StudentCreate(StudentBase):
    """Create student request."""
    enrollment_date: Optional[date] = None
    status: str = "active"


class StudentUpdate(BaseModel):
    """Update student request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    grade_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    status: Optional[str] = None


class StudentResponse(BaseModel):
    """Student response."""
    student_id: UUID
    site_id: UUID
    grade_id: UUID
    group_id: Optional[UUID] = None
    name: str
    status: str
    enrollment_date: Optional[date] = None
    current_lesson: Optional[int] = None
    last_activity_date: Optional[date] = None
    created_at: datetime
    grade_name: Optional[str] = None
    group_name: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


class ProgressMetrics(BaseModel):
    """Progress metrics summary."""
    foundational_pct: float = 0
    min_grade_pct: float = 0
    full_grade_pct: float = 0
    benchmark_pct: float = 0


class StudentWithProgress(StudentResponse):
    """Student response with progress metrics."""
    progress: Optional[ProgressMetrics] = None
    lesson_statuses: Optional[Dict[int, str]] = None  # {lesson_number: status}


class StudentListResponse(BaseModel):
    """Paginated student list response."""
    items: List[StudentResponse]
    total: int
    page: int
    page_size: int
    pages: int


class StudentBulkCreate(BaseModel):
    """Bulk create students request."""
    students: List[StudentCreate]


class StudentImport(BaseModel):
    """Import student from CSV/Sheets."""
    name: str
    grade: str  # Grade name (KG, G1, etc.)
    group: Optional[str] = None  # Group name
    teacher: Optional[str] = None  # Teacher name
    status: str = "active"
    enrollment_date: Optional[date] = None


class StudentImportRequest(BaseModel):
    """Bulk import students request."""
    students: List[StudentImport]
    update_existing: bool = False  # Update if student exists


class StudentUnenroll(BaseModel):
    """Unenroll student request."""
    reason: Optional[str] = None
    notes: Optional[str] = None
    lesson_at_unenroll: Optional[str] = None


class StudentLessonMatrix(BaseModel):
    """Student with full lesson matrix (UFLI MAP equivalent)."""
    student_id: UUID
    name: str
    grade: str
    group: Optional[str] = None
    teacher: Optional[str] = None
    current_lesson: Optional[int] = None
    lessons: Dict[int, str]  # {1: "Y", 2: "N", 3: "A", ...}
    progress: ProgressMetrics

    class Config:
        from_attributes = True
