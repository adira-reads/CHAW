"""
Groups API Routes

CRUD operations for instructional groups.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Group, Grade, Teacher, Student, StudentStatus, Lesson
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse, GroupWithStudents,
    GroupListResponse, GroupLessonsAndStudents
)
from app.api.auth import get_current_active_user, User

router = APIRouter()


def get_site_id(current_user: User) -> UUID:
    """Get site ID from current user."""
    return current_user.site_id


@router.get("", response_model=GroupListResponse)
async def list_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    grade_id: Optional[UUID] = None,
    teacher_id: Optional[UUID] = None,
    is_tutoring: Optional[bool] = None,
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all groups with optional filtering.

    - **grade_id**: Filter by grade
    - **teacher_id**: Filter by teacher
    - **is_tutoring**: Filter tutoring groups
    - **is_active**: Filter by active status (default: true)
    """
    site_id = get_site_id(current_user)

    query = db.query(Group).filter(Group.site_id == site_id)

    if grade_id:
        query = query.filter(Group.grade_id == grade_id)
    if teacher_id:
        query = query.filter(Group.teacher_id == teacher_id)
    if is_tutoring is not None:
        query = query.filter(Group.is_tutoring_group == is_tutoring)
    if is_active is not None:
        query = query.filter(Group.is_active == is_active)

    total = query.count()
    pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    groups = query.order_by(Group.name).offset(offset).limit(page_size).all()

    return GroupListResponse(
        items=[GroupResponse(**g.to_dict()) for g in groups],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/for-form")
async def get_groups_for_form(
    include_tutoring: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get groups formatted for lesson entry form dropdown.

    Returns simplified list of active groups.
    """
    site_id = get_site_id(current_user)

    query = db.query(Group).filter(
        Group.site_id == site_id,
        Group.is_active == True
    )

    if not include_tutoring:
        query = query.filter(Group.is_tutoring_group == False)

    groups = query.order_by(Group.name).all()

    return [
        {
            "group_id": str(g.group_id),
            "name": g.name,
            "grade": g.grade.name if g.grade else None,
            "teacher": g.teacher.name if g.teacher else None
        }
        for g in groups
    ]


@router.get("/{group_id}", response_model=GroupWithStudents)
async def get_group(
    group_id: UUID,
    include_students: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single group by ID."""
    site_id = get_site_id(current_user)

    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.site_id == site_id
    ).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return GroupWithStudents(**group.to_dict(include_students=include_students))


@router.get("/{group_id}/lessons-and-students", response_model=GroupLessonsAndStudents)
async def get_lessons_and_students_for_group(
    group_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get lessons and students for a group.

    This is the primary endpoint for the lesson entry form.
    Returns all available lessons and active students in the group.
    """
    site_id = get_site_id(current_user)

    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.site_id == site_id
    ).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get all lessons (could filter based on grade later)
    lessons = db.query(Lesson).order_by(Lesson.number).all()

    # Get active students in this group
    students = db.query(Student).filter(
        Student.group_id == group_id,
        Student.status == StudentStatus.active
    ).order_by(Student.name).all()

    return GroupLessonsAndStudents(
        group_id=group.group_id,
        group_name=group.name,
        lessons=[
            {
                "id": str(l.lesson_id),
                "number": l.number,
                "name": l.name,
                "short_name": l.short_name
            }
            for l in lessons
        ],
        students=[s.name for s in students]
    )


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new group."""
    site_id = get_site_id(current_user)

    # Check for duplicate name
    existing = db.query(Group).filter(
        Group.site_id == site_id,
        func.lower(Group.name) == func.lower(group_data.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Group with this name already exists")

    # Verify grade if provided
    if group_data.grade_id:
        grade = db.query(Grade).filter(
            Grade.grade_id == group_data.grade_id,
            Grade.site_id == site_id
        ).first()
        if not grade:
            raise HTTPException(status_code=400, detail="Invalid grade_id")

    # Verify teacher if provided
    if group_data.teacher_id:
        teacher = db.query(Teacher).filter(
            Teacher.teacher_id == group_data.teacher_id,
            Teacher.site_id == site_id
        ).first()
        if not teacher:
            raise HTTPException(status_code=400, detail="Invalid teacher_id")

    # Auto-detect tutoring group
    is_tutoring = group_data.is_tutoring_group or Group.is_tutoring_group_name(group_data.name)

    group = Group(
        site_id=site_id,
        name=group_data.name,
        grade_id=group_data.grade_id,
        teacher_id=group_data.teacher_id,
        is_mixed_grade=group_data.is_mixed_grade,
        mixed_grades=group_data.mixed_grades,
        is_tutoring_group=is_tutoring,
        expected_student_count=group_data.expected_student_count
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return GroupResponse(**group.to_dict())


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: UUID,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing group."""
    site_id = get_site_id(current_user)

    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.site_id == site_id
    ).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Update fields
    if group_data.name is not None:
        existing = db.query(Group).filter(
            Group.site_id == site_id,
            Group.group_id != group_id,
            func.lower(Group.name) == func.lower(group_data.name)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Group with this name already exists")
        group.name = group_data.name

    if group_data.grade_id is not None:
        group.grade_id = group_data.grade_id
    if group_data.teacher_id is not None:
        group.teacher_id = group_data.teacher_id
    if group_data.is_mixed_grade is not None:
        group.is_mixed_grade = group_data.is_mixed_grade
    if group_data.mixed_grades is not None:
        group.mixed_grades = group_data.mixed_grades
    if group_data.is_tutoring_group is not None:
        group.is_tutoring_group = group_data.is_tutoring_group
    if group_data.expected_student_count is not None:
        group.expected_student_count = group_data.expected_student_count
    if group_data.is_active is not None:
        group.is_active = group_data.is_active

    db.commit()
    db.refresh(group)

    return GroupResponse(**group.to_dict())


@router.delete("/{group_id}")
async def delete_group(
    group_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a group (soft delete - marks as inactive)."""
    site_id = get_site_id(current_user)

    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.site_id == site_id
    ).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if group has students
    student_count = db.query(Student).filter(
        Student.group_id == group_id,
        Student.status == StudentStatus.active
    ).count()

    if student_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete group with {student_count} active students. Reassign students first."
        )

    group.is_active = False
    db.commit()

    return {"message": "Group deleted successfully"}
