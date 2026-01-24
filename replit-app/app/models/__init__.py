"""
SQLAlchemy Models Package

All database models are imported here for easy access.
"""

from app.models.site import Site
from app.models.grade import Grade
from app.models.teacher import Teacher
from app.models.group import Group
from app.models.student import Student, StudentStatus
from app.models.lesson import Lesson, SkillSection
from app.models.lesson_status import LessonStatus, LessonStatusEnum
from app.models.lesson_entry import LessonEntry, EntryType, TutoringLessonType
from app.models.progress import ProgressRecord, ProgressType
from app.models.tutoring import TutoringSummary, StudentTutoringGroup
from app.models.unenrollment import UnenrollmentLog, StudentArchive, UnenrollmentStatus
from app.models.user import User, UserRole

# Re-export Base for migrations
from app.database import Base

__all__ = [
    "Base",
    "Site",
    "Grade",
    "Teacher",
    "Group",
    "Student",
    "StudentStatus",
    "Lesson",
    "SkillSection",
    "LessonStatus",
    "LessonStatusEnum",
    "LessonEntry",
    "EntryType",
    "TutoringLessonType",
    "ProgressRecord",
    "ProgressType",
    "TutoringSummary",
    "StudentTutoringGroup",
    "UnenrollmentLog",
    "StudentArchive",
    "UnenrollmentStatus",
    "User",
    "UserRole",
]
