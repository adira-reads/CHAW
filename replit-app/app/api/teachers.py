"""
Teachers API Routes

CRUD operations for teachers.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Teacher, Group
from app.schemas.teacher import (
    TeacherCreate, TeacherUpdate, TeacherResponse, TeacherWithGroups, TeacherListResponse
)
from app.api.auth import get_current_active_user, User

router = APIRouter()


def get_site_id(current_user: User) -> UUID:
    """Get site ID from current user."""
    return current_user.site_id


@router.get("", response_model=TeacherListResponse)
async def list_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all teachers with optional filtering.

    - **is_active**: Filter by active status
    - **search**: Search by name
    """
    site_id = get_site_id(current_user)

    query = db.query(Teacher).filter(Teacher.site_id == site_id)

    if is_active is not None:
        query = query.filter(Teacher.is_active == is_active)
    if search:
        query = query.filter(Teacher.name.ilike(f"%{search}%"))

    total = query.count()
    pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    teachers = query.order_by(Teacher.name).offset(offset).limit(page_size).all()

    return TeacherListResponse(
        items=[TeacherResponse(**t.to_dict()) for t in teachers],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/for-form")
async def get_teachers_for_form(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get teachers for dropdown menus."""
    site_id = get_site_id(current_user)

    teachers = db.query(Teacher).filter(
        Teacher.site_id == site_id,
        Teacher.is_active == True
    ).order_by(Teacher.name).all()

    return [
        {"teacher_id": str(t.teacher_id), "name": t.name}
        for t in teachers
    ]


@router.get("/{teacher_id}", response_model=TeacherWithGroups)
async def get_teacher(
    teacher_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single teacher by ID with their assigned groups."""
    site_id = get_site_id(current_user)

    teacher = db.query(Teacher).filter(
        Teacher.teacher_id == teacher_id,
        Teacher.site_id == site_id
    ).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Get groups
    groups = db.query(Group).filter(
        Group.teacher_id == teacher_id,
        Group.is_active == True
    ).all()

    response = teacher.to_dict()
    response["groups"] = [
        {
            "group_id": str(g.group_id),
            "name": g.name,
            "grade_name": g.grade.name if g.grade else None,
            "student_count": g.student_count
        }
        for g in groups
    ]

    return TeacherWithGroups(**response)


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher_data: TeacherCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new teacher."""
    site_id = get_site_id(current_user)

    # Check for duplicate name
    existing = db.query(Teacher).filter(
        Teacher.site_id == site_id,
        func.lower(Teacher.name) == func.lower(teacher_data.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher with this name already exists")

    teacher = Teacher(
        site_id=site_id,
        name=teacher_data.name,
        email=teacher_data.email,
        phone=teacher_data.phone
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return TeacherResponse(**teacher.to_dict())


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: UUID,
    teacher_data: TeacherUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing teacher."""
    site_id = get_site_id(current_user)

    teacher = db.query(Teacher).filter(
        Teacher.teacher_id == teacher_id,
        Teacher.site_id == site_id
    ).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher_data.name is not None:
        existing = db.query(Teacher).filter(
            Teacher.site_id == site_id,
            Teacher.teacher_id != teacher_id,
            func.lower(Teacher.name) == func.lower(teacher_data.name)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Teacher with this name already exists")
        teacher.name = teacher_data.name

    if teacher_data.email is not None:
        teacher.email = teacher_data.email
    if teacher_data.phone is not None:
        teacher.phone = teacher_data.phone
    if teacher_data.is_active is not None:
        teacher.is_active = teacher_data.is_active

    db.commit()
    db.refresh(teacher)

    return TeacherResponse(**teacher.to_dict())


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a teacher (soft delete)."""
    site_id = get_site_id(current_user)

    teacher = db.query(Teacher).filter(
        Teacher.teacher_id == teacher_id,
        Teacher.site_id == site_id
    ).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.is_active = False
    db.commit()

    return {"message": "Teacher deleted successfully"}
