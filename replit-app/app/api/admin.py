"""
Admin API Routes

Administrative functions: site management, user management, data import/export.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Site, User, UserRole, Grade, Teacher, Group, Student, Lesson
from app.schemas.auth import UserCreate, UserResponse, UserUpdate
from app.api.auth import get_current_active_user, require_admin, get_password_hash
from app.config import settings, GRADE_LESSON_CONFIG

router = APIRouter()


def get_site_id(current_user: User) -> UUID:
    """Get site ID from current user."""
    return current_user.site_id


# ═══════════════════════════════════════════════════════════════
# SITE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@router.get("/site")
async def get_site_config(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current site configuration."""
    site = db.query(Site).filter(Site.site_id == current_user.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site.to_dict()


@router.put("/site")
async def update_site_config(
    config: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update site configuration (admin only)."""
    site = db.query(Site).filter(Site.site_id == current_user.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Update allowed fields
    allowed_fields = [
        "name", "allow_grade_mixing", "mixed_grade_config",
        "feature_tutoring", "feature_pacing", "feature_parent_reports",
        "monday_api_key", "monday_board_id"
    ]

    for field in allowed_fields:
        if field in config:
            setattr(site, field, config[field])

    db.commit()
    db.refresh(site)

    return site.to_dict()


# ═══════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users in site (admin only)."""
    users = db.query(User).filter(User.site_id == current_user.site_id).all()
    return [UserResponse(**u.to_dict()) for u in users]


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)."""
    # Check for existing email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        site_id=current_user.site_id,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        role=UserRole(user_data.role),
        teacher_id=user_data.teacher_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(**user.to_dict())


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)."""
    user = db.query(User).filter(
        User.user_id == user_id,
        User.site_id == current_user.site_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email:
        user.email = user_data.email
    if user_data.name:
        user.name = user_data.name
    if user_data.role:
        user.role = UserRole(user_data.role)
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.teacher_id:
        user.teacher_id = user_data.teacher_id

    db.commit()
    db.refresh(user)

    return UserResponse(**user.to_dict())


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)."""
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = db.query(User).filter(
        User.user_id == user_id,
        User.site_id == current_user.site_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}


# ═══════════════════════════════════════════════════════════════
# DATA INITIALIZATION
# ═══════════════════════════════════════════════════════════════

@router.post("/initialize-grades")
async def initialize_grades(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Initialize grade levels for the site."""
    site_id = current_user.site_id

    # Check if grades already exist
    existing = db.query(Grade).filter(Grade.site_id == site_id).count()
    if existing > 0:
        raise HTTPException(status_code=400, detail="Grades already initialized")

    grades_created = []
    for grade_name, config in GRADE_LESSON_CONFIG.items():
        grade = Grade(
            site_id=site_id,
            name=grade_name,
            display_name=Grade.get_display_name(grade_name),
            seq_order=Grade.get_seq_order(grade_name),
            min_grade_lessons=config.get("min_lessons"),
            current_year_lessons=config.get("current_year_lessons"),
            benchmark_denominator=config.get("benchmark_denominator"),
            is_letter_based=config.get("is_letter_based", False)
        )
        db.add(grade)
        grades_created.append(grade_name)

    db.commit()

    return {"message": f"Created {len(grades_created)} grades", "grades": grades_created}


@router.post("/seed-lessons")
async def seed_lessons(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Seed all 128 UFLI lessons and skill sections."""
    from app.services.seed_service import seed_lessons_and_sections

    # Check if lessons already exist
    existing = db.query(Lesson).count()
    if existing > 0:
        raise HTTPException(status_code=400, detail="Lessons already seeded")

    result = seed_lessons_and_sections(db)
    return result


# ═══════════════════════════════════════════════════════════════
# DATA IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════════

@router.post("/import/students")
async def import_students(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Import students from CSV file."""
    from app.services.import_service import ImportService

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    service = ImportService(db, current_user.site_id)

    result = service.import_students_csv(content.decode('utf-8'))
    return result


@router.post("/import/lesson-entries")
async def import_lesson_entries(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Import lesson entries from CSV file."""
    from app.services.import_service import ImportService

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    service = ImportService(db, current_user.site_id)

    result = service.import_lesson_entries_csv(content.decode('utf-8'))
    return result


@router.get("/export/students")
async def export_students(
    format: str = "csv",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export all students to CSV."""
    from app.services.export_service import ExportService
    from fastapi.responses import StreamingResponse
    import io

    service = ExportService(db, current_user.site_id)

    if format == "csv":
        csv_content = service.export_students_csv()
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=students.csv"}
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@router.get("/export/ufli-map")
async def export_ufli_map(
    format: str = "csv",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export UFLI MAP (progress matrix) to CSV."""
    from app.services.export_service import ExportService
    from fastapi.responses import StreamingResponse
    import io

    service = ExportService(db, current_user.site_id)

    if format == "csv":
        csv_content = service.export_ufli_map_csv()
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=ufli_map.csv"}
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


# ═══════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════

@router.get("/stats")
async def get_site_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get site statistics."""
    from sqlalchemy import func
    from app.models import LessonEntry, StudentStatus

    site_id = current_user.site_id

    stats = {
        "students": {
            "total": db.query(Student).filter(Student.site_id == site_id).count(),
            "active": db.query(Student).filter(Student.site_id == site_id, Student.status == StudentStatus.active).count(),
            "unenrolled": db.query(Student).filter(Student.site_id == site_id, Student.status == StudentStatus.unenrolled).count(),
        },
        "groups": {
            "total": db.query(Group).filter(Group.site_id == site_id).count(),
            "active": db.query(Group).filter(Group.site_id == site_id, Group.is_active == True).count(),
            "tutoring": db.query(Group).filter(Group.site_id == site_id, Group.is_tutoring_group == True).count(),
        },
        "teachers": {
            "total": db.query(Teacher).filter(Teacher.site_id == site_id).count(),
            "active": db.query(Teacher).filter(Teacher.site_id == site_id, Teacher.is_active == True).count(),
        },
        "lesson_entries": {
            "total": db.query(LessonEntry).filter(LessonEntry.site_id == site_id).count(),
        },
        "users": {
            "total": db.query(User).filter(User.site_id == site_id).count(),
            "active": db.query(User).filter(User.site_id == site_id, User.is_active == True).count(),
        }
    }

    return stats
