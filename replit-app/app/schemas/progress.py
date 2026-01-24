"""
Progress Schemas

Schemas for progress tracking and reporting.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ProgressRecordResponse(BaseModel):
    """Progress record response."""
    progress_id: UUID
    student_id: UUID
    record_type: str
    foundational_count: int = 0
    foundational_pct: float = 0
    min_grade_count: int = 0
    min_grade_pct: float = 0
    full_grade_count: int = 0
    full_grade_pct: float = 0
    benchmark_count: int = 0
    benchmark_pct: float = 0
    form_count: Optional[int] = None
    form_pct: Optional[float] = None
    name_sound_count: Optional[int] = None
    name_sound_pct: Optional[float] = None
    skill_sections: Optional[Dict[str, float]] = None
    calculated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SkillSectionProgress(BaseModel):
    """Progress for a single skill section."""
    section_id: int
    section_name: str
    lesson_count: int
    completed_count: int
    percentage: float


class StudentProgressResponse(BaseModel):
    """Complete student progress response."""
    student_id: UUID
    name: str
    grade: str
    group: Optional[str] = None
    teacher: Optional[str] = None
    current_lesson: Optional[int] = None
    # Progress metrics
    foundational_pct: float = 0
    min_grade_pct: float = 0
    full_grade_pct: float = 0
    benchmark_pct: float = 0
    # Skill sections breakdown
    skill_sections: List[SkillSectionProgress] = []
    # Lesson matrix (optional, for detailed view)
    lessons: Optional[Dict[int, str]] = None  # {1: "Y", 2: "N", ...}
    # Initial assessment (optional)
    initial_assessment: Optional[Dict[int, str]] = None

    class Config:
        from_attributes = True


class GroupProgressResponse(BaseModel):
    """Group progress summary."""
    group_id: UUID
    name: str
    grade: Optional[str] = None
    teacher: Optional[str] = None
    student_count: int
    avg_current_lesson: Optional[float] = None
    min_lesson: Optional[int] = None
    max_lesson: Optional[int] = None
    # Average metrics
    avg_foundational_pct: float = 0
    avg_min_grade_pct: float = 0
    avg_benchmark_pct: float = 0
    # Student breakdown (optional)
    students: Optional[List[StudentProgressResponse]] = None

    class Config:
        from_attributes = True


class GradeProgressResponse(BaseModel):
    """Grade-level progress summary."""
    grade_id: UUID
    grade_name: str
    display_name: str
    student_count: int
    group_count: int
    # Average metrics
    avg_foundational_pct: float = 0
    avg_min_grade_pct: float = 0
    avg_full_grade_pct: float = 0
    avg_benchmark_pct: float = 0
    # Distribution (optional)
    benchmark_distribution: Optional[Dict[str, int]] = None  # {"0-25": 5, "26-50": 10, ...}

    class Config:
        from_attributes = True


class SchoolProgressResponse(BaseModel):
    """School-wide progress summary."""
    site_id: UUID
    site_name: str
    total_students: int
    total_groups: int
    total_teachers: int
    # Overall metrics
    avg_foundational_pct: float = 0
    avg_min_grade_pct: float = 0
    avg_benchmark_pct: float = 0
    # By grade breakdown
    grades: List[GradeProgressResponse] = []

    class Config:
        from_attributes = True


class PacingStatus(BaseModel):
    """Pacing status for a group."""
    group_id: UUID
    group_name: str
    current_lesson: int
    expected_lesson: int
    variance: int  # current - expected
    status: str  # "ahead", "on_track", "behind"


class PacingDashboardResponse(BaseModel):
    """Pacing dashboard for all groups."""
    site_id: UUID
    as_of_date: datetime
    week_number: int
    groups: List[PacingStatus]
    summary: Dict[str, int]  # {"ahead": 5, "on_track": 10, "behind": 3}


class TutoringProgressResponse(BaseModel):
    """Tutoring progress for a student."""
    student_id: UUID
    name: str
    grade: str
    primary_group: Optional[str] = None
    tutoring_groups: List[str] = []
    total_sessions: int = 0
    reteach_count: int = 0
    reteach_pass_pct: float = 0
    comprehension_count: int = 0
    comprehension_pass_pct: float = 0
    other_count: int = 0
    other_pass_pct: float = 0
    overall_pass_pct: float = 0
    last_session_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProgressRecalculateRequest(BaseModel):
    """Request to recalculate progress."""
    student_ids: Optional[List[UUID]] = None  # Specific students, or all if None
    recalculate_all: bool = False


class ProgressRecalculateResponse(BaseModel):
    """Response from progress recalculation."""
    students_processed: int
    success_count: int
    error_count: int
    errors: Optional[List[dict]] = None
    duration_seconds: float
