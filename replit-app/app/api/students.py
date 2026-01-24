"""
Students API Routes

CRUD operations for students and student-related queries.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Student, StudentStatus, Grade, Group, LessonStatus, ProgressRecord, ProgressType
from app.schemas.student import (
    StudentCreate, StudentUpdate, StudentResponse, StudentWithProgress,
    StudentListResponse, StudentUnenroll, StudentLessonMatrix
)
from app.api.auth import get_current_active_user, User
from app.services.progress_calculator import ProgressCalculator

router = APIRouter()


def get_site_id(current_user: User) -> UUID:
    """Get site ID from current user."""
    return current_user.site_id


@router.get("", response_model=StudentListResponse)
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    grade_id: Optional[UUID] = None,
    group_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all students with optional filtering.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **grade_id**: Filter by grade
    - **group_id**: Filter by group
    - **status**: Filter by status (active, inactive, unenrolled)
    - **search**: Search by name (case-insensitive)
    """
    site_id = get_site_id(current_user)

    query = db.query(Student).filter(Student.site_id == site_id)

    # Apply filters
    if grade_id:
        query = query.filter(Student.grade_id == grade_id)
    if group_id:
        query = query.filter(Student.group_id == group_id)
    if status:
        query = query.filter(Student.status == StudentStatus(status))
    if search:
        query = query.filter(Student.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Calculate pagination
    pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    # Get paginated results
    students = query.order_by(Student.name).offset(offset).limit(page_size).all()

    return StudentListResponse(
        items=[StudentResponse(**s.to_dict()) for s in students],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{student_id}", response_model=StudentWithProgress)
async def get_student(
    student_id: UUID,
    include_lessons: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single student by ID.

    - **include_lessons**: Include full lesson status matrix
    """
    site_id = get_site_id(current_user)

    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.site_id == site_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    response_data = student.to_dict(include_progress=True)

    if include_lessons:
        # Get lesson statuses
        lesson_statuses = db.query(LessonStatus).filter(
            LessonStatus.student_id == student_id,
            LessonStatus.is_initial_assessment == False
        ).all()
        response_data["lesson_statuses"] = {
            ls.lesson.number: ls.status.value for ls in lesson_statuses
        }

    return StudentWithProgress(**response_data)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new student."""
    site_id = get_site_id(current_user)

    # Verify grade exists
    grade = db.query(Grade).filter(
        Grade.grade_id == student_data.grade_id,
        Grade.site_id == site_id
    ).first()
    if not grade:
        raise HTTPException(status_code=400, detail="Invalid grade_id")

    # Verify group exists if provided
    if student_data.group_id:
        group = db.query(Group).filter(
            Group.group_id == student_data.group_id,
            Group.site_id == site_id
        ).first()
        if not group:
            raise HTTPException(status_code=400, detail="Invalid group_id")

    # Check for duplicate name
    existing = db.query(Student).filter(
        Student.site_id == site_id,
        func.lower(Student.name) == func.lower(student_data.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this name already exists")

    # Create student
    student = Student(
        site_id=site_id,
        name=student_data.name,
        grade_id=student_data.grade_id,
        group_id=student_data.group_id,
        status=StudentStatus(student_data.status) if student_data.status else StudentStatus.active,
        enrollment_date=student_data.enrollment_date
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    # Create initial progress record
    progress_record = ProgressRecord(
        student_id=student.student_id,
        record_type=ProgressType.ufli_map
    )
    db.add(progress_record)
    db.commit()

    return StudentResponse(**student.to_dict())


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: UUID,
    student_data: StudentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing student."""
    site_id = get_site_id(current_user)

    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.site_id == site_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Update fields
    if student_data.name is not None:
        # Check for duplicate name
        existing = db.query(Student).filter(
            Student.site_id == site_id,
            Student.student_id != student_id,
            func.lower(Student.name) == func.lower(student_data.name)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student with this name already exists")
        student.name = student_data.name

    if student_data.grade_id is not None:
        grade = db.query(Grade).filter(
            Grade.grade_id == student_data.grade_id,
            Grade.site_id == site_id
        ).first()
        if not grade:
            raise HTTPException(status_code=400, detail="Invalid grade_id")
        student.grade_id = student_data.grade_id

    if student_data.group_id is not None:
        if student_data.group_id:
            group = db.query(Group).filter(
                Group.group_id == student_data.group_id,
                Group.site_id == site_id
            ).first()
            if not group:
                raise HTTPException(status_code=400, detail="Invalid group_id")
        student.group_id = student_data.group_id

    if student_data.status is not None:
        student.status = StudentStatus(student_data.status)

    db.commit()
    db.refresh(student)

    return StudentResponse(**student.to_dict())


@router.delete("/{student_id}")
async def delete_student(
    student_id: UUID,
    hard_delete: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a student (soft delete by default).

    - **hard_delete**: If true, permanently delete. Otherwise, mark as inactive.
    """
    site_id = get_site_id(current_user)

    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.site_id == site_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if hard_delete:
        db.delete(student)
    else:
        student.status = StudentStatus.inactive

    db.commit()

    return {"message": "Student deleted successfully"}


@router.post("/{student_id}/unenroll")
async def unenroll_student(
    student_id: UUID,
    unenroll_data: StudentUnenroll,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Unenroll a student.

    This will:
    - Change student status to 'unenrolled'
    - Create an unenrollment log entry
    - Archive student data
    """
    from app.services.unenrollment_service import UnenrollmentService

    site_id = get_site_id(current_user)

    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.site_id == site_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.status == StudentStatus.unenrolled:
        raise HTTPException(status_code=400, detail="Student is already unenrolled")

    # Process unenrollment
    service = UnenrollmentService(db)
    result = service.unenroll_student(
        student=student,
        reported_by_id=current_user.teacher_id,
        reason=unenroll_data.reason,
        notes=unenroll_data.notes,
        lesson_at_unenroll=unenroll_data.lesson_at_unenroll
    )

    return result


@router.get("/{student_id}/progress", response_model=StudentWithProgress)
async def get_student_progress(
    student_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a student."""
    site_id = get_site_id(current_user)

    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.site_id == site_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return StudentWithProgress(**student.to_dict(include_progress=True))


@router.post("/{student_id}/recalculate-progress")
async def recalculate_student_progress(
    student_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Recalculate progress metrics for a student."""
    site_id = get_site_id(current_user)

    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.site_id == site_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    calculator = ProgressCalculator(db)
    result = calculator.calculate_student_progress(student)

    return {"message": "Progress recalculated", "progress": result}
