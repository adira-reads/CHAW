"""
API Routes Package

All FastAPI route handlers are organized here.
"""

from app.api import auth, students, groups, teachers, lessons, lesson_entries, progress, admin

__all__ = [
    "auth",
    "students",
    "groups",
    "teachers",
    "lessons",
    "lesson_entries",
    "progress",
    "admin",
]
