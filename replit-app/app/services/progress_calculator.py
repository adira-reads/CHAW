"""
Progress Calculator Service

Handles all progress metric calculations for students.
This is the core business logic for the UFLI tracking system.

Calculations follow the same logic as the Google Apps Script version:
- Foundational %: Lessons 1-34
- Min Grade %: Grade-specific minimum requirements
- Benchmark %: Grade-appropriate targets
- Skill Section %: Per-section breakdown with review lesson handling
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models import (
    Student, LessonStatus, LessonStatusEnum, ProgressRecord, ProgressType,
    Lesson, Grade
)
from app.config import (
    REVIEW_LESSONS, FOUNDATIONAL_LESSONS, GRADE_LESSON_CONFIG, SKILL_SECTIONS
)


class ProgressCalculator:
    """
    Calculates and updates progress metrics for students.

    Usage:
        calculator = ProgressCalculator(db)
        progress = calculator.calculate_student_progress(student)
    """

    def __init__(self, db: Session):
        self.db = db
        self._lesson_cache = None

    def _get_lessons(self) -> Dict[int, Lesson]:
        """Get all lessons indexed by number (cached)."""
        if self._lesson_cache is None:
            lessons = self.db.query(Lesson).all()
            self._lesson_cache = {l.number: l for l in lessons}
        return self._lesson_cache

    def _get_student_statuses(self, student_id, is_initial: bool = False) -> Dict[int, str]:
        """Get all lesson statuses for a student as a dict {lesson_number: status}."""
        statuses = self.db.query(LessonStatus).filter(
            LessonStatus.student_id == student_id,
            LessonStatus.is_initial_assessment == is_initial
        ).all()

        return {
            ls.lesson.number: ls.status.value
            for ls in statuses
            if ls.lesson
        }

    def calculate_student_progress(self, student: Student) -> Dict:
        """
        Calculate all progress metrics for a student.

        Returns dict with all calculated metrics.
        Also updates the ProgressRecord in database.
        """
        # Get lesson statuses
        status_map = self._get_student_statuses(student.student_id)

        # Get grade config
        grade_name = student.grade.name if student.grade else "KG"
        grade_config = GRADE_LESSON_CONFIG.get(grade_name, GRADE_LESSON_CONFIG.get("KG"))

        # Calculate foundational (lessons 1-34)
        foundational = self._calculate_foundational(status_map)

        # Calculate min grade (grade-specific)
        min_grade = self._calculate_min_grade(status_map, grade_config)

        # Calculate full grade (current year)
        full_grade = self._calculate_full_grade(status_map, grade_config)

        # Calculate benchmark
        benchmark = self._calculate_benchmark(status_map, grade_config)

        # Calculate skill sections
        skill_sections = self._calculate_all_skill_sections(status_map)

        # Update current lesson
        current_lesson = self._calculate_current_lesson(status_map)

        # Update student record
        student.current_lesson = current_lesson
        self.db.add(student)

        # Update or create progress record
        progress_record = self.db.query(ProgressRecord).filter(
            ProgressRecord.student_id == student.student_id,
            ProgressRecord.record_type == ProgressType.ufli_map
        ).first()

        if not progress_record:
            progress_record = ProgressRecord(
                student_id=student.student_id,
                record_type=ProgressType.ufli_map
            )
            self.db.add(progress_record)

        # Update progress record
        progress_record.foundational_count = foundational["count"]
        progress_record.foundational_pct = Decimal(str(round(foundational["pct"], 2)))
        progress_record.min_grade_count = min_grade["count"]
        progress_record.min_grade_pct = Decimal(str(round(min_grade["pct"], 2)))
        progress_record.full_grade_count = full_grade["count"]
        progress_record.full_grade_pct = Decimal(str(round(full_grade["pct"], 2)))
        progress_record.benchmark_count = benchmark["count"]
        progress_record.benchmark_pct = Decimal(str(round(benchmark["pct"], 2)))
        progress_record.skill_sections = skill_sections

        self.db.commit()

        return {
            "current_lesson": current_lesson,
            "foundational_count": foundational["count"],
            "foundational_pct": foundational["pct"],
            "min_grade_count": min_grade["count"],
            "min_grade_pct": min_grade["pct"],
            "full_grade_count": full_grade["count"],
            "full_grade_pct": full_grade["pct"],
            "benchmark_count": benchmark["count"],
            "benchmark_pct": benchmark["pct"],
            "skill_sections": skill_sections
        }

    def _calculate_foundational(self, status_map: Dict[int, str]) -> Dict:
        """Calculate foundational percentage (lessons 1-34)."""
        count = sum(1 for i in FOUNDATIONAL_LESSONS if status_map.get(i) == "Y")
        pct = (count / 34) * 100 if 34 > 0 else 0
        return {"count": count, "pct": pct}

    def _calculate_min_grade(self, status_map: Dict[int, str], grade_config: Dict) -> Dict:
        """Calculate minimum grade percentage."""
        min_lessons = grade_config.get("min_lessons", FOUNDATIONAL_LESSONS)

        # Exclude review lessons from count
        non_review_lessons = [l for l in min_lessons if l not in REVIEW_LESSONS]

        count = sum(1 for l in non_review_lessons if status_map.get(l) == "Y")
        denominator = len(non_review_lessons)
        pct = (count / denominator) * 100 if denominator > 0 else 0

        return {"count": count, "pct": pct}

    def _calculate_full_grade(self, status_map: Dict[int, str], grade_config: Dict) -> Dict:
        """Calculate full grade percentage (current year lessons)."""
        current_year = grade_config.get("current_year_lessons", [])
        if not current_year:
            return {"count": 0, "pct": 0}

        count = sum(1 for l in current_year if status_map.get(l) == "Y")
        pct = (count / len(current_year)) * 100 if len(current_year) > 0 else 0

        return {"count": count, "pct": pct}

    def _calculate_benchmark(self, status_map: Dict[int, str], grade_config: Dict) -> Dict:
        """Calculate benchmark percentage using grade-specific denominator."""
        denominator = grade_config.get("benchmark_denominator", 34)
        min_lessons = grade_config.get("min_lessons", FOUNDATIONAL_LESSONS)

        # Count passed lessons in min set (excluding reviews)
        non_review_lessons = [l for l in min_lessons if l not in REVIEW_LESSONS]
        count = sum(1 for l in non_review_lessons if status_map.get(l) == "Y")

        pct = (count / denominator) * 100 if denominator > 0 else 0

        return {"count": count, "pct": pct}

    def _calculate_current_lesson(self, status_map: Dict[int, str]) -> Optional[int]:
        """Calculate current lesson (highest passed lesson number)."""
        passed_lessons = [l for l, s in status_map.items() if s == "Y"]
        return max(passed_lessons) if passed_lessons else None

    def _calculate_all_skill_sections(self, status_map: Dict[int, str]) -> Dict[str, float]:
        """Calculate percentage for all skill sections."""
        result = {}

        for section in SKILL_SECTIONS:
            section_pct = self._calculate_section_percentage(
                status_map,
                section["lessons"],
                section["name"]
            )
            result[f"section_{section['id']}"] = section_pct

        return result

    def _calculate_section_percentage(
        self,
        status_map: Dict[int, str],
        section_lessons: List[int],
        section_name: str
    ) -> float:
        """
        Calculate percentage for a single skill section.

        Special handling for review lessons:
        - If ANY review lesson in section is populated (Y/N/A):
          - If ALL reviews pass -> 100% for section
          - Otherwise calculate only non-review lessons
        """
        if not section_lessons:
            return 0.0

        # Separate review and non-review lessons
        review_lessons = [l for l in section_lessons if l in REVIEW_LESSONS]
        non_review_lessons = [l for l in section_lessons if l not in REVIEW_LESSONS]

        # Check review lessons
        if review_lessons:
            review_statuses = [status_map.get(l) for l in review_lessons if status_map.get(l)]

            if review_statuses:  # At least one review lesson has data
                # Check if ALL reviews passed
                all_reviews_passed = all(s == "Y" for s in review_statuses)
                if all_reviews_passed:
                    return 100.0

        # Calculate based on non-review lessons only
        if not non_review_lessons:
            return 0.0

        passed_count = sum(1 for l in non_review_lessons if status_map.get(l) == "Y")
        return (passed_count / len(non_review_lessons)) * 100

    def calculate_skill_sections(self, student: Student) -> List[Dict]:
        """
        Get skill section progress for a student (for API response).

        Returns list of SkillSectionProgress dicts.
        """
        status_map = self._get_student_statuses(student.student_id)
        result = []

        for section in SKILL_SECTIONS:
            non_review = [l for l in section["lessons"] if l not in REVIEW_LESSONS]
            completed = sum(1 for l in non_review if status_map.get(l) == "Y")
            pct = self._calculate_section_percentage(
                status_map,
                section["lessons"],
                section["name"]
            )

            result.append({
                "section_id": section["id"],
                "section_name": section["name"],
                "lesson_count": len(non_review),
                "completed_count": completed,
                "percentage": round(pct, 1)
            })

        return result
