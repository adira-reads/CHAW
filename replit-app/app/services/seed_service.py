"""
Seed Service

Seeds the database with UFLI lessons and skill sections.
This is the foundational data needed for the tracking system.
"""

from sqlalchemy.orm import Session
from uuid import uuid4

from app.models import Lesson, SkillSection, Grade, Site
from app.config import (
    LESSON_NAMES, SKILL_SECTIONS, REVIEW_LESSONS, FOUNDATIONAL_LESSONS
)


def seed_lessons_and_sections(db: Session) -> dict:
    """
    Seed all 128 UFLI lessons and 17 skill sections.

    This function is idempotent - it won't create duplicates if data exists.

    Returns:
        dict with counts of created/existing items
    """
    result = {
        "lessons_created": 0,
        "lessons_existing": 0,
        "sections_created": 0,
        "sections_existing": 0
    }

    # Check if lessons already exist
    existing_lessons = db.query(Lesson).count()
    if existing_lessons >= 128:
        result["lessons_existing"] = existing_lessons
        result["sections_existing"] = db.query(SkillSection).count()
        return result

    # Create skill sections first (lessons reference them)
    section_map = {}  # id -> SkillSection object

    for section_data in SKILL_SECTIONS:
        existing = db.query(SkillSection).filter(
            SkillSection.name == section_data["name"]
        ).first()

        if existing:
            section_map[section_data["id"]] = existing
            result["sections_existing"] += 1
        else:
            # Determine lesson range for the section
            lessons = section_data["lessons"]
            section = SkillSection(
                section_id=uuid4(),
                name=section_data["name"],
                seq_order=section_data["id"],
                lesson_range_start=min(lessons) if lessons else None,
                lesson_range_end=max(lessons) if lessons else None
            )
            db.add(section)
            section_map[section_data["id"]] = section
            result["sections_created"] += 1

    db.flush()  # Ensure sections have IDs before creating lessons

    # Build a reverse lookup: lesson_number -> section_id
    lesson_to_section = {}
    for section_data in SKILL_SECTIONS:
        for lesson_num in section_data["lessons"]:
            # First section that contains the lesson wins
            if lesson_num not in lesson_to_section:
                lesson_to_section[lesson_num] = section_data["id"]

    # Create all 128 lessons
    for num in range(1, 129):
        existing = db.query(Lesson).filter(Lesson.number == num).first()

        if existing:
            result["lessons_existing"] += 1
            continue

        name = LESSON_NAMES.get(num, f"Lesson {num}")
        section_id_num = lesson_to_section.get(num)
        section = section_map.get(section_id_num) if section_id_num else None

        lesson = Lesson(
            lesson_id=uuid4(),
            section_id=section.section_id if section else None,
            number=num,
            name=f"Lesson {num}: {name}",
            short_name=name,
            description=None,
            is_review=num in REVIEW_LESSONS,
            is_foundational=num in FOUNDATIONAL_LESSONS
        )
        db.add(lesson)
        result["lessons_created"] += 1

    db.commit()
    return result


def seed_default_grades(db: Session) -> dict:
    """
    Seed default grade levels.

    Returns:
        dict with counts of created/existing grades
    """
    result = {
        "grades_created": 0,
        "grades_existing": 0
    }

    grades_data = [
        {"name": "PreK", "display_name": "Pre-Kindergarten", "seq_order": 0},
        {"name": "KG", "display_name": "Kindergarten", "seq_order": 1},
        {"name": "G1", "display_name": "1st Grade", "seq_order": 2},
        {"name": "G2", "display_name": "2nd Grade", "seq_order": 3},
        {"name": "G3", "display_name": "3rd Grade", "seq_order": 4},
        {"name": "G4", "display_name": "4th Grade", "seq_order": 5},
        {"name": "G5", "display_name": "5th Grade", "seq_order": 6},
        {"name": "G6", "display_name": "6th Grade", "seq_order": 7},
        {"name": "G7", "display_name": "7th Grade", "seq_order": 8},
        {"name": "G8", "display_name": "8th Grade", "seq_order": 9},
    ]

    for grade_data in grades_data:
        existing = db.query(Grade).filter(Grade.name == grade_data["name"]).first()

        if existing:
            result["grades_existing"] += 1
        else:
            grade = Grade(
                grade_id=uuid4(),
                name=grade_data["name"],
                display_name=grade_data["display_name"],
                seq_order=grade_data["seq_order"]
            )
            db.add(grade)
            result["grades_created"] += 1

    db.commit()
    return result


def seed_default_site(db: Session, site_name: str = "UFLI School") -> Site:
    """
    Create or get the default site.

    Returns:
        Site object
    """
    existing = db.query(Site).filter(Site.name == site_name).first()

    if existing:
        return existing

    site = Site(
        site_id=uuid4(),
        name=site_name,
        timezone="America/New_York",
        is_active=True
    )
    db.add(site)
    db.commit()

    return site


def seed_all(db: Session, site_name: str = "UFLI School") -> dict:
    """
    Run all seed operations.

    Returns:
        Combined results dict
    """
    results = {
        "site": None,
        "grades": None,
        "lessons": None
    }

    # Create site
    site = seed_default_site(db, site_name)
    results["site"] = {"name": site.name, "id": str(site.site_id)}

    # Create grades
    results["grades"] = seed_default_grades(db)

    # Create lessons and sections
    results["lessons"] = seed_lessons_and_sections(db)

    return results
