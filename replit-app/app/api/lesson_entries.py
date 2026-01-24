"""
Lesson Entries API Routes

Handles lesson entry submissions (Small Group Progress equivalent).
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    LessonEntry, EntryType, TutoringLessonType,
    Student, Group, Teacher, Lesson, LessonStatus, LessonStatusEnum,
    StudentStatus
)
from app.schemas.lesson_entry import (
    LessonEntryCreate, LessonEntryBatchCreate, LessonEntryResponse,
    LessonEntryListResponse, RecentEntryResponse
)
from app.api.auth import get_current_active_user, User
from app.services.progress_calculator import ProgressCalculator

router = APIRouter()


def get_site_id(current_user: User) -> UUID:
    """Get site ID from current user."""
    return current_user.site_id


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_lesson_entries(
    entry_data: LessonEntryBatchCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit lesson entries for a group (batch submission).

    This is the primary endpoint for lesson data entry. Teachers select:
    - Group
    - Lesson
    - Date
    - Status for each student (Y/N/A/U)

    The system will:
    1. Create LessonEntry records for each student
    2. Update LessonStatus records
    3. Recalculate progress metrics
    4. Handle unenrollments (U status)
    """
    site_id = get_site_id(current_user)
    entry_date = entry_data.entry_date or datetime.utcnow()

    # Verify group exists
    group = db.query(Group).filter(
        Group.group_id == entry_data.group_id,
        Group.site_id == site_id
    ).first()
    if not group:
        raise HTTPException(status_code=400, detail="Invalid group_id")

    # Verify teacher exists
    teacher = db.query(Teacher).filter(
        Teacher.teacher_id == entry_data.teacher_id,
        Teacher.site_id == site_id
    ).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="Invalid teacher_id")

    # Verify lesson exists
    lesson = db.query(Lesson).filter(
        Lesson.lesson_id == entry_data.lesson_id
    ).first()
    if not lesson:
        raise HTTPException(status_code=400, detail="Invalid lesson_id")

    # Determine entry type
    entry_type = EntryType(entry_data.entry_type) if entry_data.entry_type else EntryType.small_group
    if group.is_tutoring_group:
        entry_type = EntryType.tutoring

    # Process each student entry
    created_count = 0
    updated_count = 0
    unenrolled_count = 0
    errors = []
    students_to_recalculate = []

    for student_entry in entry_data.students:
        try:
            # Verify student exists and is in this group
            student = db.query(Student).filter(
                Student.student_id == student_entry.student_id,
                Student.site_id == site_id
            ).first()

            if not student:
                errors.append({"student_id": str(student_entry.student_id), "error": "Student not found"})
                continue

            # Handle unenrollment
            if student_entry.status == "U":
                student.status = StudentStatus.unenrolled
                student.unenrollment_date = entry_date.date()
                unenrolled_count += 1
                # TODO: Create unenrollment log and archive
                continue

            # Create lesson entry record
            lesson_entry = LessonEntry(
                site_id=site_id,
                student_id=student.student_id,
                group_id=group.group_id,
                teacher_id=teacher.teacher_id,
                lesson_id=lesson.lesson_id,
                entry_date=entry_date,
                status=student_entry.status,
                entry_type=entry_type
            )
            db.add(lesson_entry)

            # Update or create lesson status
            existing_status = db.query(LessonStatus).filter(
                LessonStatus.student_id == student.student_id,
                LessonStatus.lesson_id == lesson.lesson_id,
                LessonStatus.is_initial_assessment == False
            ).first()

            if existing_status:
                existing_status.status = LessonStatusEnum(student_entry.status)
                existing_status.completed_date = entry_date.date()
                existing_status.group_id = group.group_id
                existing_status.teacher_id = teacher.teacher_id
                updated_count += 1
            else:
                new_status = LessonStatus(
                    student_id=student.student_id,
                    lesson_id=lesson.lesson_id,
                    group_id=group.group_id,
                    teacher_id=teacher.teacher_id,
                    status=LessonStatusEnum(student_entry.status),
                    completed_date=entry_date.date(),
                    is_initial_assessment=False
                )
                db.add(new_status)
                created_count += 1

            # Update student's last activity
            student.last_activity_date = entry_date.date()

            # Update current lesson if passed
            if student_entry.status == "Y":
                if student.current_lesson is None or lesson.number > student.current_lesson:
                    student.current_lesson = lesson.number

            students_to_recalculate.append(student)

        except Exception as e:
            errors.append({"student_id": str(student_entry.student_id), "error": str(e)})

    db.commit()

    # Recalculate progress for affected students
    calculator = ProgressCalculator(db)
    for student in students_to_recalculate:
        try:
            calculator.calculate_student_progress(student)
        except Exception as e:
            errors.append({"student_id": str(student.student_id), "error": f"Progress calculation failed: {e}"})

    db.commit()

    return {
        "message": "Lesson entries processed",
        "created": created_count,
        "updated": updated_count,
        "unenrolled": unenrolled_count,
        "errors": errors if errors else None,
        "lesson": {
            "number": lesson.number,
            "name": lesson.name
        },
        "group": group.name,
        "date": entry_date.isoformat()
    }


@router.get("", response_model=LessonEntryListResponse)
async def list_lesson_entries(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    student_id: Optional[UUID] = None,
    group_id: Optional[UUID] = None,
    teacher_id: Optional[UUID] = None,
    lesson_id: Optional[UUID] = None,
    entry_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List lesson entries with optional filtering.

    - **student_id**: Filter by student
    - **group_id**: Filter by group
    - **teacher_id**: Filter by teacher
    - **lesson_id**: Filter by lesson
    - **entry_type**: Filter by type (small_group, tutoring)
    - **date_from/date_to**: Filter by date range
    """
    site_id = get_site_id(current_user)

    query = db.query(LessonEntry).filter(LessonEntry.site_id == site_id)

    if student_id:
        query = query.filter(LessonEntry.student_id == student_id)
    if group_id:
        query = query.filter(LessonEntry.group_id == group_id)
    if teacher_id:
        query = query.filter(LessonEntry.teacher_id == teacher_id)
    if lesson_id:
        query = query.filter(LessonEntry.lesson_id == lesson_id)
    if entry_type:
        query = query.filter(LessonEntry.entry_type == EntryType(entry_type))
    if date_from:
        query = query.filter(LessonEntry.entry_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(LessonEntry.entry_date <= datetime.combine(date_to, datetime.max.time()))

    total = query.count()
    pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    entries = query.order_by(LessonEntry.entry_date.desc()).offset(offset).limit(page_size).all()

    return LessonEntryListResponse(
        items=[LessonEntryResponse(**e.to_dict()) for e in entries],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/recent")
async def get_recent_entries(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get recent lesson entries for dashboard display.

    Returns aggregated entries grouped by date/group/lesson.
    """
    site_id = get_site_id(current_user)

    # Get recent entries grouped
    from sqlalchemy import func

    # Simple approach: get most recent entries
    entries = db.query(LessonEntry).filter(
        LessonEntry.site_id == site_id
    ).order_by(LessonEntry.entry_date.desc()).limit(limit * 10).all()

    # Aggregate by date/group/lesson
    aggregated = {}
    for entry in entries:
        key = (entry.entry_date.date(), entry.group_id, entry.lesson_id)
        if key not in aggregated:
            aggregated[key] = {
                "entry_date": entry.entry_date,
                "group_name": entry.group.name if entry.group else "Unknown",
                "lesson_name": entry.lesson.short_name if entry.lesson else "Unknown",
                "teacher_name": entry.teacher.name if entry.teacher else "Unknown",
                "student_count": 0,
                "pass_count": 0
            }
        aggregated[key]["student_count"] += 1
        if entry.status == "Y":
            aggregated[key]["pass_count"] += 1

    # Sort and limit
    recent = sorted(aggregated.values(), key=lambda x: x["entry_date"], reverse=True)[:limit]

    return recent


@router.get("/{entry_id}", response_model=LessonEntryResponse)
async def get_lesson_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single lesson entry by ID."""
    site_id = get_site_id(current_user)

    entry = db.query(LessonEntry).filter(
        LessonEntry.entry_id == entry_id,
        LessonEntry.site_id == site_id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Lesson entry not found")

    return LessonEntryResponse(**entry.to_dict())


@router.delete("/{entry_id}")
async def delete_lesson_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a lesson entry (admin only)."""
    from app.api.auth import require_admin
    await require_admin(current_user)

    site_id = get_site_id(current_user)

    entry = db.query(LessonEntry).filter(
        LessonEntry.entry_id == entry_id,
        LessonEntry.site_id == site_id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Lesson entry not found")

    db.delete(entry)
    db.commit()

    return {"message": "Lesson entry deleted"}
