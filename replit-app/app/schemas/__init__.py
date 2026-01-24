"""
Pydantic Schemas Package

All API validation schemas are imported here for easy access.
"""

from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.auth import Token, TokenData, UserLogin, UserCreate
from app.schemas.student import (
    StudentBase, StudentCreate, StudentUpdate, StudentResponse,
    StudentWithProgress, StudentListResponse
)
from app.schemas.group import (
    GroupBase, GroupCreate, GroupUpdate, GroupResponse,
    GroupWithStudents, GroupListResponse
)
from app.schemas.teacher import (
    TeacherBase, TeacherCreate, TeacherUpdate, TeacherResponse
)
from app.schemas.lesson import (
    LessonResponse, SkillSectionResponse, LessonListResponse
)
from app.schemas.lesson_entry import (
    LessonEntryCreate, LessonEntryBatchCreate, LessonEntryResponse,
    LessonEntryListResponse
)
from app.schemas.progress import (
    ProgressRecordResponse, StudentProgressResponse,
    GroupProgressResponse, GradeProgressResponse, SchoolProgressResponse
)

__all__ = [
    # Common
    "PaginatedResponse",
    "MessageResponse",
    # Auth
    "Token",
    "TokenData",
    "UserLogin",
    "UserCreate",
    # Student
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentWithProgress",
    "StudentListResponse",
    # Group
    "GroupBase",
    "GroupCreate",
    "GroupUpdate",
    "GroupResponse",
    "GroupWithStudents",
    "GroupListResponse",
    # Teacher
    "TeacherBase",
    "TeacherCreate",
    "TeacherUpdate",
    "TeacherResponse",
    # Lesson
    "LessonResponse",
    "SkillSectionResponse",
    "LessonListResponse",
    # Lesson Entry
    "LessonEntryCreate",
    "LessonEntryBatchCreate",
    "LessonEntryResponse",
    "LessonEntryListResponse",
    # Progress
    "ProgressRecordResponse",
    "StudentProgressResponse",
    "GroupProgressResponse",
    "GradeProgressResponse",
    "SchoolProgressResponse",
]
