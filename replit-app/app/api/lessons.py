"""
Lessons API Routes

Read-only endpoints for UFLI lessons and skill sections.
Lessons are seeded and not modified through the API.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lesson, SkillSection
from app.schemas.lesson import (
    LessonResponse, LessonListResponse, SkillSectionResponse,
    SkillSectionWithLessons, SkillSectionListResponse
)
from app.api.auth import get_current_active_user, User

router = APIRouter()


@router.get("", response_model=LessonListResponse)
async def list_lessons(
    section_id: Optional[UUID] = None,
    is_foundational: Optional[bool] = None,
    is_review: Optional[bool] = None,
    start: Optional[int] = Query(None, ge=1, le=128),
    end: Optional[int] = Query(None, ge=1, le=128),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all UFLI lessons with optional filtering.

    - **section_id**: Filter by skill section
    - **is_foundational**: Filter foundational lessons (1-34)
    - **is_review**: Filter review lessons
    - **start**: Starting lesson number
    - **end**: Ending lesson number
    """
    query = db.query(Lesson)

    if section_id:
        query = query.filter(Lesson.section_id == section_id)
    if is_foundational is not None:
        query = query.filter(Lesson.is_foundational == is_foundational)
    if is_review is not None:
        query = query.filter(Lesson.is_review == is_review)
    if start is not None:
        query = query.filter(Lesson.number >= start)
    if end is not None:
        query = query.filter(Lesson.number <= end)

    lessons = query.order_by(Lesson.number).all()

    return LessonListResponse(
        items=[LessonResponse(**l.to_dict()) for l in lessons],
        total=len(lessons)
    )


@router.get("/for-form")
async def get_lessons_for_form(
    grade: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get lessons formatted for lesson entry form dropdown.

    - **grade**: Optional grade to filter relevant lessons
    """
    lessons = db.query(Lesson).order_by(Lesson.number).all()

    return [
        {
            "lesson_id": str(l.lesson_id),
            "number": l.number,
            "name": l.name,
            "short_name": l.short_name
        }
        for l in lessons
    ]


@router.get("/sections", response_model=SkillSectionListResponse)
async def list_skill_sections(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all skill sections."""
    sections = db.query(SkillSection).order_by(SkillSection.seq_order).all()

    return SkillSectionListResponse(
        items=[SkillSectionResponse(**s.to_dict()) for s in sections],
        total=len(sections)
    )


@router.get("/sections/{section_id}", response_model=SkillSectionWithLessons)
async def get_skill_section(
    section_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a skill section with its lessons."""
    section = db.query(SkillSection).filter(
        SkillSection.section_id == section_id
    ).first()

    if not section:
        raise HTTPException(status_code=404, detail="Skill section not found")

    response = section.to_dict()
    response["lessons"] = [LessonResponse(**l.to_dict()) for l in section.lessons]

    return SkillSectionWithLessons(**response)


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single lesson by ID."""
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return LessonResponse(**lesson.to_dict())


@router.get("/by-number/{number}", response_model=LessonResponse)
async def get_lesson_by_number(
    number: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a lesson by its number (1-128)."""
    if number < 1 or number > 128:
        raise HTTPException(status_code=400, detail="Lesson number must be between 1 and 128")

    lesson = db.query(Lesson).filter(Lesson.number == number).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return LessonResponse(**lesson.to_dict())
