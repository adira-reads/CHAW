"""
UFLI Master Tracking System - Main Application Entry Point

FastAPI application for tracking student progress through the 128-lesson
UFLI (University of Florida Literacy Institute) phonics curriculum.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.database import engine, Base
from app.api import auth, students, groups, teachers, lessons, progress, admin, lesson_entries

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown."""
    # Startup: Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    yield
    # Shutdown: cleanup if needed
    print("Application shutting down")


# Initialize FastAPI application
app = FastAPI(
    title="UFLI Tracking System",
    description="""
    ## Student Progress Tracking for UFLI Curriculum

    This API provides comprehensive tracking for the 128-lesson UFLI phonics curriculum.

    ### Features:
    - **Student Management**: Track students across grades and groups
    - **Lesson Entry**: Record daily lesson progress (Y/N/A status)
    - **Progress Tracking**: Automatic calculation of progress metrics
    - **Reports**: Grade summaries, school summaries, skill breakdowns
    - **Tutoring Support**: Track intervention sessions separately
    - **Mixed-Grade Groups**: Support for cross-grade instructional groupings

    ### Progress Metrics:
    - **Foundational %**: Lessons 1-34 completion
    - **Min Grade %**: Grade-specific minimum requirements
    - **Benchmark %**: Grade-appropriate benchmark targets
    - **Skill Sections**: 17 skill areas with individual tracking
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(lesson_entries.router, prefix="/api/lesson-entries", tags=["Lesson Entries"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "UFLI Tracking System"
    }


@app.get("/api")
async def api_root():
    """API root endpoint with basic information."""
    return {
        "message": "UFLI Tracking System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


# Serve static frontend files in production
# In development, the frontend runs on a separate dev server
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React frontend for non-API routes."""
        # Don't serve frontend for API routes
        if full_path.startswith("api"):
            return {"error": "Not found"}
        return FileResponse("frontend/dist/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG
    )
