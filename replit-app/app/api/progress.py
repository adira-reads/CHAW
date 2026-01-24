"""
Progress API Routes

Progress tracking, reporting, and analytics endpoints.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import (
    Student, StudentStatus, Group, Grade, Site,
    ProgressRecord, ProgressType, LessonStatus, LessonStatusEnum
)
from app.schemas.progress import (
    StudentProgressResponse, GroupProgressResponse,
    GradeProgressResponse, SchoolProgressResponse,
    SkillSectionProgress, ProgressRecalculateRequest, ProgressRecalculateResponse
)
from app.api.auth import get_current_active_user, User
from app.services.progress_calculator import ProgressCalculator
from app.config import SKILL_SECTIONS

router = APIRouter()


def get_site_id(current_user: User) -> UUID:
    """Get site ID from current user."""
    return current_user.site_id


@router.get("/student/{student_id}", response_model=StudentProgressResponse)
async def get_student_progress(
    student_id: UUID,
    include_lessons: bool = False,
    include_skills: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress for a single student.

    - **include_lessons**: Include full lesson status matrix
    - **include_skills**: Include skill section breakdown
    """
    site_id = get_site_id(current_user)

    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.site_id == site_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get progress record
    progress = db.query(ProgressRecord).filter(
        ProgressRecord.student_id == student_id,
        ProgressRecord.record_type == ProgressType.ufli_map
    ).first()

    # Build response
    response_data = {
        "student_id": student.student_id,
        "name": student.name,
        "grade": student.grade.name if student.grade else None,
        "group": student.group.name if student.group else None,
        "teacher": student.group.teacher.name if student.group and student.group.teacher else None,
        "current_lesson": student.current_lesson,
        "foundational_pct": float(progress.foundational_pct) if progress else 0,
        "min_grade_pct": float(progress.min_grade_pct) if progress else 0,
        "full_grade_pct": float(progress.full_grade_pct) if progress else 0,
        "benchmark_pct": float(progress.benchmark_pct) if progress else 0,
        "skill_sections": []
    }

    # Add skill section breakdown
    if include_skills:
        calculator = ProgressCalculator(db)
        skill_progress = calculator.calculate_skill_sections(student)
        response_data["skill_sections"] = skill_progress

    # Add lesson matrix
    if include_lessons:
        lesson_statuses = db.query(LessonStatus).filter(
            LessonStatus.student_id == student_id,
            LessonStatus.is_initial_assessment == False
        ).all()
        response_data["lessons"] = {
            ls.lesson.number: ls.status.value for ls in lesson_statuses
        }

    return StudentProgressResponse(**response_data)


@router.get("/group/{group_id}", response_model=GroupProgressResponse)
async def get_group_progress(
    group_id: UUID,
    include_students: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get progress summary for a group.

    - **include_students**: Include individual student progress
    """
    site_id = get_site_id(current_user)

    group = db.query(Group).filter(
        Group.group_id == group_id,
        Group.site_id == site_id
    ).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get active students in group
    students = db.query(Student).filter(
        Student.group_id == group_id,
        Student.status == StudentStatus.active
    ).all()

    # Calculate group metrics
    student_count = len(students)
    if student_count == 0:
        return GroupProgressResponse(
            group_id=group.group_id,
            name=group.name,
            grade=group.grade.name if group.grade else None,
            teacher=group.teacher.name if group.teacher else None,
            student_count=0,
            avg_current_lesson=None,
            min_lesson=None,
            max_lesson=None,
            avg_foundational_pct=0,
            avg_min_grade_pct=0,
            avg_benchmark_pct=0
        )

    # Get progress records for all students
    progress_records = db.query(ProgressRecord).filter(
        ProgressRecord.student_id.in_([s.student_id for s in students]),
        ProgressRecord.record_type == ProgressType.ufli_map
    ).all()
    progress_map = {pr.student_id: pr for pr in progress_records}

    # Calculate averages
    current_lessons = [s.current_lesson for s in students if s.current_lesson]
    foundational_pcts = []
    min_grade_pcts = []
    benchmark_pcts = []

    for student in students:
        pr = progress_map.get(student.student_id)
        if pr:
            foundational_pcts.append(float(pr.foundational_pct or 0))
            min_grade_pcts.append(float(pr.min_grade_pct or 0))
            benchmark_pcts.append(float(pr.benchmark_pct or 0))

    response_data = {
        "group_id": group.group_id,
        "name": group.name,
        "grade": group.grade.name if group.grade else None,
        "teacher": group.teacher.name if group.teacher else None,
        "student_count": student_count,
        "avg_current_lesson": sum(current_lessons) / len(current_lessons) if current_lessons else None,
        "min_lesson": min(current_lessons) if current_lessons else None,
        "max_lesson": max(current_lessons) if current_lessons else None,
        "avg_foundational_pct": sum(foundational_pcts) / len(foundational_pcts) if foundational_pcts else 0,
        "avg_min_grade_pct": sum(min_grade_pcts) / len(min_grade_pcts) if min_grade_pcts else 0,
        "avg_benchmark_pct": sum(benchmark_pcts) / len(benchmark_pcts) if benchmark_pcts else 0,
    }

    if include_students:
        response_data["students"] = [
            StudentProgressResponse(
                student_id=s.student_id,
                name=s.name,
                grade=s.grade.name if s.grade else None,
                group=group.name,
                teacher=group.teacher.name if group.teacher else None,
                current_lesson=s.current_lesson,
                foundational_pct=float(progress_map.get(s.student_id).foundational_pct or 0) if progress_map.get(s.student_id) else 0,
                min_grade_pct=float(progress_map.get(s.student_id).min_grade_pct or 0) if progress_map.get(s.student_id) else 0,
                full_grade_pct=float(progress_map.get(s.student_id).full_grade_pct or 0) if progress_map.get(s.student_id) else 0,
                benchmark_pct=float(progress_map.get(s.student_id).benchmark_pct or 0) if progress_map.get(s.student_id) else 0,
                skill_sections=[]
            )
            for s in students
        ]

    return GroupProgressResponse(**response_data)


@router.get("/grade/{grade_id}", response_model=GradeProgressResponse)
async def get_grade_progress(
    grade_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress summary for a grade level."""
    site_id = get_site_id(current_user)

    grade = db.query(Grade).filter(
        Grade.grade_id == grade_id,
        Grade.site_id == site_id
    ).first()

    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # Get active students in grade
    students = db.query(Student).filter(
        Student.grade_id == grade_id,
        Student.status == StudentStatus.active
    ).all()

    # Get groups in grade
    groups = db.query(Group).filter(
        Group.grade_id == grade_id,
        Group.is_active == True,
        Group.is_tutoring_group == False
    ).all()

    student_count = len(students)
    if student_count == 0:
        return GradeProgressResponse(
            grade_id=grade.grade_id,
            grade_name=grade.name,
            display_name=grade.display_name or Grade.get_display_name(grade.name),
            student_count=0,
            group_count=len(groups),
            avg_foundational_pct=0,
            avg_min_grade_pct=0,
            avg_full_grade_pct=0,
            avg_benchmark_pct=0
        )

    # Get progress records
    progress_records = db.query(ProgressRecord).filter(
        ProgressRecord.student_id.in_([s.student_id for s in students]),
        ProgressRecord.record_type == ProgressType.ufli_map
    ).all()

    foundational_pcts = [float(pr.foundational_pct or 0) for pr in progress_records]
    min_grade_pcts = [float(pr.min_grade_pct or 0) for pr in progress_records]
    full_grade_pcts = [float(pr.full_grade_pct or 0) for pr in progress_records]
    benchmark_pcts = [float(pr.benchmark_pct or 0) for pr in progress_records]

    return GradeProgressResponse(
        grade_id=grade.grade_id,
        grade_name=grade.name,
        display_name=grade.display_name or Grade.get_display_name(grade.name),
        student_count=student_count,
        group_count=len(groups),
        avg_foundational_pct=sum(foundational_pcts) / len(foundational_pcts) if foundational_pcts else 0,
        avg_min_grade_pct=sum(min_grade_pcts) / len(min_grade_pcts) if min_grade_pcts else 0,
        avg_full_grade_pct=sum(full_grade_pcts) / len(full_grade_pcts) if full_grade_pcts else 0,
        avg_benchmark_pct=sum(benchmark_pcts) / len(benchmark_pcts) if benchmark_pcts else 0
    )


@router.get("/school", response_model=SchoolProgressResponse)
async def get_school_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get school-wide progress summary."""
    site_id = get_site_id(current_user)

    site = db.query(Site).filter(Site.site_id == site_id).first()

    # Get counts
    total_students = db.query(Student).filter(
        Student.site_id == site_id,
        Student.status == StudentStatus.active
    ).count()

    total_groups = db.query(Group).filter(
        Group.site_id == site_id,
        Group.is_active == True,
        Group.is_tutoring_group == False
    ).count()

    total_teachers = db.query(func.count(func.distinct(Group.teacher_id))).filter(
        Group.site_id == site_id,
        Group.is_active == True
    ).scalar() or 0

    # Get overall progress
    students = db.query(Student).filter(
        Student.site_id == site_id,
        Student.status == StudentStatus.active
    ).all()

    progress_records = db.query(ProgressRecord).filter(
        ProgressRecord.student_id.in_([s.student_id for s in students]),
        ProgressRecord.record_type == ProgressType.ufli_map
    ).all()

    foundational_pcts = [float(pr.foundational_pct or 0) for pr in progress_records]
    min_grade_pcts = [float(pr.min_grade_pct or 0) for pr in progress_records]
    benchmark_pcts = [float(pr.benchmark_pct or 0) for pr in progress_records]

    # Get grade breakdown
    grades = db.query(Grade).filter(
        Grade.site_id == site_id,
        Grade.is_active == True
    ).order_by(Grade.seq_order).all()

    grade_summaries = []
    for grade in grades:
        grade_students = [s for s in students if s.grade_id == grade.grade_id]
        grade_progress = [pr for pr in progress_records if pr.student_id in [s.student_id for s in grade_students]]

        grade_groups = db.query(Group).filter(
            Group.grade_id == grade.grade_id,
            Group.is_active == True,
            Group.is_tutoring_group == False
        ).count()

        grade_summaries.append(GradeProgressResponse(
            grade_id=grade.grade_id,
            grade_name=grade.name,
            display_name=grade.display_name or Grade.get_display_name(grade.name),
            student_count=len(grade_students),
            group_count=grade_groups,
            avg_foundational_pct=sum(float(pr.foundational_pct or 0) for pr in grade_progress) / len(grade_progress) if grade_progress else 0,
            avg_min_grade_pct=sum(float(pr.min_grade_pct or 0) for pr in grade_progress) / len(grade_progress) if grade_progress else 0,
            avg_full_grade_pct=sum(float(pr.full_grade_pct or 0) for pr in grade_progress) / len(grade_progress) if grade_progress else 0,
            avg_benchmark_pct=sum(float(pr.benchmark_pct or 0) for pr in grade_progress) / len(grade_progress) if grade_progress else 0
        ))

    return SchoolProgressResponse(
        site_id=site_id,
        site_name=site.name if site else "Unknown",
        total_students=total_students,
        total_groups=total_groups,
        total_teachers=total_teachers,
        avg_foundational_pct=sum(foundational_pcts) / len(foundational_pcts) if foundational_pcts else 0,
        avg_min_grade_pct=sum(min_grade_pcts) / len(min_grade_pcts) if min_grade_pcts else 0,
        avg_benchmark_pct=sum(benchmark_pcts) / len(benchmark_pcts) if benchmark_pcts else 0,
        grades=grade_summaries
    )


@router.post("/recalculate", response_model=ProgressRecalculateResponse)
async def recalculate_progress(
    request: ProgressRecalculateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Recalculate progress metrics.

    - **student_ids**: Specific students to recalculate
    - **recalculate_all**: Recalculate all students in site
    """
    import time
    start_time = time.time()

    site_id = get_site_id(current_user)
    calculator = ProgressCalculator(db)

    if request.recalculate_all:
        students = db.query(Student).filter(
            Student.site_id == site_id,
            Student.status == StudentStatus.active
        ).all()
    elif request.student_ids:
        students = db.query(Student).filter(
            Student.student_id.in_(request.student_ids),
            Student.site_id == site_id
        ).all()
    else:
        raise HTTPException(status_code=400, detail="Specify student_ids or recalculate_all=true")

    success_count = 0
    error_count = 0
    errors = []

    for student in students:
        try:
            calculator.calculate_student_progress(student)
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append({"student_id": str(student.student_id), "error": str(e)})

    db.commit()

    duration = time.time() - start_time

    return ProgressRecalculateResponse(
        students_processed=len(students),
        success_count=success_count,
        error_count=error_count,
        errors=errors if errors else None,
        duration_seconds=round(duration, 2)
    )
