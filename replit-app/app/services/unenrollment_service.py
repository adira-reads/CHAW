"""
Unenrollment Service

Handles student unenrollment processing and archival.
Replicates the unenrollment workflow from the Google Apps Script version.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.models import (
    Student, UnenrollmentLog, StudentArchive, UnenrollmentStatus,
    LessonStatus, ProgressRecord, LessonEntry, Teacher
)


class UnenrollmentService:
    """
    Service for handling student unenrollments.

    Workflow:
    1. Teacher marks student as 'U' (Unenrolled) in lesson entry
    2. System creates UnenrollmentLog entry
    3. System archives student data (preserves for potential restoration)
    4. Student is marked as inactive
    """

    def __init__(self, db: Session):
        self.db = db

    def unenroll_student(
        self,
        student_id: UUID,
        reported_by_id: Optional[UUID] = None,
        lesson_at_unenroll: Optional[str] = None,
        notes: Optional[str] = None
    ) -> UnenrollmentLog:
        """
        Process student unenrollment.

        Args:
            student_id: UUID of the student to unenroll
            reported_by_id: UUID of teacher reporting the unenrollment
            lesson_at_unenroll: Lesson number/name when unenrollment was noted
            notes: Optional notes about the unenrollment

        Returns:
            UnenrollmentLog record
        """
        # Get student
        student = self.db.query(Student).filter(
            Student.student_id == student_id
        ).first()

        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Create unenrollment log
        log = UnenrollmentLog(
            log_id=uuid4(),
            student_id=student_id,
            reported_by_id=reported_by_id,
            reported_date=datetime.now(),
            lesson_at_unenroll=lesson_at_unenroll,
            status=UnenrollmentStatus.pending,
            notes=notes
        )
        self.db.add(log)
        self.db.flush()

        # Archive student data
        self._archive_student_data(student, log.log_id)

        # Mark student as inactive
        student.is_active = False
        self.db.add(student)

        self.db.commit()

        return log

    def _archive_student_data(
        self,
        student: Student,
        unenrollment_log_id: UUID
    ) -> StudentArchive:
        """
        Create archive snapshot of student data.

        Preserves:
        - All lesson statuses (initial assessment and current progress)
        - Progress records
        - Lesson entry history
        """
        # Gather initial assessment data
        ia_statuses = self.db.query(LessonStatus).filter(
            LessonStatus.student_id == student.student_id,
            LessonStatus.is_initial_assessment == True
        ).all()

        ia_data = {
            ls.lesson.number: {
                "status": ls.status.value,
                "notes": ls.notes
            }
            for ls in ia_statuses if ls.lesson
        }

        # Gather UFLI MAP data (current progress)
        map_statuses = self.db.query(LessonStatus).filter(
            LessonStatus.student_id == student.student_id,
            LessonStatus.is_initial_assessment == False
        ).all()

        map_data = {
            ls.lesson.number: {
                "status": ls.status.value,
                "notes": ls.notes
            }
            for ls in map_statuses if ls.lesson
        }

        # Gather progress records
        progress_records = self.db.query(ProgressRecord).filter(
            ProgressRecord.student_id == student.student_id
        ).all()

        grade_summary = {
            "progress_records": [
                {
                    "record_type": pr.record_type.value,
                    "foundational_pct": float(pr.foundational_pct) if pr.foundational_pct else 0,
                    "min_grade_pct": float(pr.min_grade_pct) if pr.min_grade_pct else 0,
                    "benchmark_pct": float(pr.benchmark_pct) if pr.benchmark_pct else 0,
                    "skill_sections": pr.skill_sections
                }
                for pr in progress_records
            ],
            "current_lesson": student.current_lesson,
            "grade": student.grade.name if student.grade else None,
            "group": student.group.name if student.group else None
        }

        # Create archive
        archive = StudentArchive(
            archive_id=uuid4(),
            student_id=student.student_id,
            unenrollment_log_id=unenrollment_log_id,
            initial_assessment_data=ia_data if ia_data else None,
            ufli_map_data=map_data if map_data else None,
            grade_summary_data=grade_summary,
            archived_at=datetime.now()
        )
        self.db.add(archive)

        return archive

    def confirm_unenrollment(self, log_id: UUID) -> UnenrollmentLog:
        """
        Confirm a pending unenrollment.

        Args:
            log_id: UUID of the unenrollment log to confirm

        Returns:
            Updated UnenrollmentLog
        """
        log = self.db.query(UnenrollmentLog).filter(
            UnenrollmentLog.log_id == log_id
        ).first()

        if not log:
            raise ValueError(f"UnenrollmentLog {log_id} not found")

        log.status = UnenrollmentStatus.confirmed
        self.db.commit()

        return log

    def resolve_unenrollment(
        self,
        log_id: UUID,
        notes: Optional[str] = None
    ) -> UnenrollmentLog:
        """
        Resolve an unenrollment (student returned).

        Args:
            log_id: UUID of the unenrollment log
            notes: Optional resolution notes

        Returns:
            Updated UnenrollmentLog
        """
        log = self.db.query(UnenrollmentLog).filter(
            UnenrollmentLog.log_id == log_id
        ).first()

        if not log:
            raise ValueError(f"UnenrollmentLog {log_id} not found")

        log.status = UnenrollmentStatus.resolved
        if notes:
            log.notes = (log.notes or "") + f"\nResolution: {notes}"

        # Reactivate student
        student = log.student
        if student:
            student.is_active = True

        self.db.commit()

        return log

    def get_pending_unenrollments(self, site_id: Optional[UUID] = None) -> List[UnenrollmentLog]:
        """
        Get all pending unenrollments.

        Args:
            site_id: Optional site filter

        Returns:
            List of pending UnenrollmentLog records
        """
        query = self.db.query(UnenrollmentLog).filter(
            UnenrollmentLog.status == UnenrollmentStatus.pending
        )

        if site_id:
            query = query.join(Student).filter(Student.site_id == site_id)

        return query.order_by(UnenrollmentLog.reported_date.desc()).all()

    def get_unenrolled_students(
        self,
        site_id: Optional[UUID] = None,
        include_resolved: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all unenrolled students with their archive data.

        Args:
            site_id: Optional site filter
            include_resolved: Include resolved (returned) students

        Returns:
            List of student unenrollment records with details
        """
        query = self.db.query(UnenrollmentLog)

        if not include_resolved:
            query = query.filter(
                UnenrollmentLog.status.in_([
                    UnenrollmentStatus.pending,
                    UnenrollmentStatus.confirmed
                ])
            )

        if site_id:
            query = query.join(Student).filter(Student.site_id == site_id)

        logs = query.order_by(UnenrollmentLog.reported_date.desc()).all()

        return [log.to_dict() for log in logs]

    def restore_student(
        self,
        student_id: UUID,
        restore_data: bool = True
    ) -> Student:
        """
        Restore an unenrolled student.

        Args:
            student_id: UUID of student to restore
            restore_data: If True, restore archived lesson data

        Returns:
            Restored Student object
        """
        student = self.db.query(Student).filter(
            Student.student_id == student_id
        ).first()

        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Reactivate
        student.is_active = True

        # Optionally restore data from most recent archive
        if restore_data:
            archive = self.db.query(StudentArchive).filter(
                StudentArchive.student_id == student_id
            ).order_by(StudentArchive.archived_at.desc()).first()

            if archive:
                # Data was preserved (not deleted), so nothing to restore
                # The lesson statuses should still exist in the database
                pass

        # Mark any pending unenrollment logs as resolved
        pending_logs = self.db.query(UnenrollmentLog).filter(
            UnenrollmentLog.student_id == student_id,
            UnenrollmentLog.status == UnenrollmentStatus.pending
        ).all()

        for log in pending_logs:
            log.status = UnenrollmentStatus.resolved
            log.notes = (log.notes or "") + "\nAuto-resolved: Student restored"

        self.db.commit()

        return student
