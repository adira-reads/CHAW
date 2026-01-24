#!/usr/bin/env python3
"""
Database Initialization Script

This script:
1. Creates all database tables
2. Seeds UFLI lessons and skill sections (128 lessons, 17 sections)
3. Creates default grades (PreK through G8)
4. Creates a default site
5. Optionally creates an admin user

Usage:
    python scripts/init_db.py
    python scripts/init_db.py --admin-email admin@school.org --admin-password secure123
    python scripts/init_db.py --site-name "Oak Elementary"
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.models import User, UserRole
from app.services import seed_all
from uuid import uuid4


def create_tables(engine):
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def create_admin_user(db, email: str, password: str, name: str = "Admin"):
    """Create an admin user."""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"Admin user {email} already exists")
        return existing

    # Create user
    user = User(
        user_id=uuid4(),
        email=email,
        password_hash=pwd_context.hash(password),
        name=name,
        role=UserRole.admin,
        is_active=True
    )
    db.add(user)
    db.commit()

    print(f"Admin user created: {email}")
    return user


def main():
    parser = argparse.ArgumentParser(description="Initialize the UFLI database")
    parser.add_argument(
        "--site-name",
        default="UFLI School",
        help="Name for the default site (default: UFLI School)"
    )
    parser.add_argument(
        "--admin-email",
        help="Email for admin user (optional)"
    )
    parser.add_argument(
        "--admin-password",
        help="Password for admin user (required if --admin-email is provided)"
    )
    parser.add_argument(
        "--admin-name",
        default="Admin",
        help="Display name for admin user (default: Admin)"
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="Skip seeding lessons and grades"
    )

    args = parser.parse_args()

    # Validate admin args
    if args.admin_email and not args.admin_password:
        parser.error("--admin-password is required when --admin-email is provided")

    print(f"Connecting to database: {settings.DATABASE_URL[:50]}...")

    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    create_tables(engine)

    # Create session for seeding
    db = SessionLocal()

    try:
        if not args.skip_seed:
            # Seed data
            print(f"\nSeeding data for site: {args.site_name}")
            results = seed_all(db, args.site_name)

            print(f"\nSite created: {results['site']['name']}")
            print(f"Grades: {results['grades']['grades_created']} created, {results['grades']['grades_existing']} existing")
            print(f"Lessons: {results['lessons']['lessons_created']} created, {results['lessons']['lessons_existing']} existing")
            print(f"Sections: {results['lessons']['sections_created']} created, {results['lessons']['sections_existing']} existing")

        # Create admin user if requested
        if args.admin_email:
            print(f"\nCreating admin user: {args.admin_email}")
            create_admin_user(db, args.admin_email, args.admin_password, args.admin_name)

        print("\nDatabase initialization complete!")

    except Exception as e:
        print(f"\nError during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
