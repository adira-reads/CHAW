"""
Database Configuration

SQLAlchemy database setup with PostgreSQL support.
Provides session management and base model class.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.config import settings

# Create database engine
# For PostgreSQL, we use the psycopg2 driver
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connection before using
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator:
    """
    Database session dependency.

    Usage in FastAPI routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables. Use with caution!"""
    Base.metadata.drop_all(bind=engine)
