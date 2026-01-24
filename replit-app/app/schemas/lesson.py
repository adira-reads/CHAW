"""
Lesson Schemas

Schemas for lesson and skill section responses.
"""

from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID


class LessonResponse(BaseModel):
    """Lesson response."""
    lesson_id: UUID
    section_id: Optional[UUID] = None
    number: int
    name: str
    short_name: str
    description: Optional[str] = None
    is_review: bool
    is_foundational: bool
    section_name: Optional[str] = None

    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    """List of all lessons."""
    items: List[LessonResponse]
    total: int


class SkillSectionResponse(BaseModel):
    """Skill section response."""
    section_id: UUID
    name: str
    seq_order: int
    lesson_range_start: Optional[int] = None
    lesson_range_end: Optional[int] = None
    lesson_count: int = 0

    class Config:
        from_attributes = True


class SkillSectionWithLessons(SkillSectionResponse):
    """Skill section with lessons list."""
    lessons: List[LessonResponse] = []


class SkillSectionListResponse(BaseModel):
    """List of all skill sections."""
    items: List[SkillSectionResponse]
    total: int


class LessonDropdownItem(BaseModel):
    """Simplified lesson for dropdown menus."""
    lesson_id: UUID
    number: int
    name: str
    short_name: str


class LessonRangeRequest(BaseModel):
    """Request lessons in a range."""
    start: int = 1
    end: int = 128
    include_reviews: bool = True
