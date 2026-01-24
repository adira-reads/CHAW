# UFLI Tracking System - Replit Build Guide

A comprehensive guide to building and deploying the UFLI Progress Tracking application on Replit.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Creating Your Replit Project](#creating-your-replit-project)
4. [Project Structure](#project-structure)
5. [Database Setup](#database-setup)
6. [Backend Configuration](#backend-configuration)
7. [Frontend Configuration](#frontend-configuration)
8. [Running the Application](#running-the-application)
9. [Initial Data Setup](#initial-data-setup)
10. [Testing Your Application](#testing-your-application)
11. [Deployment](#deployment)
12. [Environment Variables](#environment-variables)
13. [Troubleshooting](#troubleshooting)
14. [Maintenance](#maintenance)

---

## Overview

The UFLI Tracking System is a web application for tracking student progress through the UFLI (University of Florida Literacy Institute) Foundations curriculum. It replaces the existing Google Sheets-based system with a proper database-backed web application.

### Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Authentication | JWT (JSON Web Tokens) |
| Migrations | Alembic |

### Key Features

- **Lesson Entry**: Record Y/N/A/U status for students
- **Progress Tracking**: Foundational %, Min Grade %, Benchmark %
- **17 Skill Sections**: Detailed breakdown by curriculum area
- **128 UFLI Lessons**: Complete curriculum coverage
- **Mixed-Grade Support**: G6+G7+G8, SC Classroom configurations
- **Student Management**: Enrollment, unenrollment, archiving

---

## Prerequisites

Before starting, ensure you have:

1. **A Replit account** (free tier works, but paid recommended for databases)
2. **Basic familiarity with**:
   - Command line/terminal
   - Python and JavaScript/TypeScript
   - Git version control

---

## Creating Your Replit Project

### Step 1: Create a New Repl

1. Go to [replit.com](https://replit.com) and log in
2. Click **"+ Create Repl"**
3. Choose **"Python"** as the template
4. Name your project (e.g., "ufli-tracker")
5. Click **"Create Repl"**

### Step 2: Set Up the Project Structure

In the Replit shell, create the directory structure:

```bash
# Create main directories
mkdir -p app/models app/schemas app/api app/services
mkdir -p alembic/versions
mkdir -p scripts
mkdir -p frontend/src/pages frontend/src/components frontend/src/api frontend/src/contexts

# Create __init__.py files for Python packages
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/api/__init__.py
touch app/services/__init__.py
touch scripts/__init__.py
```

### Step 3: Upload or Create Files

You have two options:

**Option A: Upload from GitHub/Local**
If you have the codebase in a repository:
```bash
# In Replit shell
git clone https://github.com/your-repo/ufli-tracker.git .
```

**Option B: Create files manually**
Use Replit's file editor to create each file. The complete file list is in the [Project Structure](#project-structure) section.

---

## Project Structure

```
replit-app/
├── .replit                    # Replit configuration
├── replit.nix                 # Nix packages for Replit
├── requirements.txt           # Python dependencies
├── main.py                    # FastAPI application entry point
├── alembic.ini               # Alembic migration config
│
├── alembic/
│   ├── env.py                # Migration environment
│   ├── script.py.mako        # Migration template
│   └── versions/             # Migration files
│
├── app/
│   ├── __init__.py
│   ├── config.py             # Settings and UFLI constants
│   ├── database.py           # Database connection
│   │
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── site.py
│   │   ├── grade.py
│   │   ├── teacher.py
│   │   ├── group.py
│   │   ├── student.py
│   │   ├── lesson.py
│   │   ├── lesson_status.py
│   │   ├── lesson_entry.py
│   │   ├── progress.py
│   │   ├── tutoring.py
│   │   ├── unenrollment.py
│   │   └── user.py
│   │
│   ├── schemas/              # Pydantic schemas (API validation)
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── group.py
│   │   ├── teacher.py
│   │   ├── lesson.py
│   │   ├── lesson_entry.py
│   │   └── progress.py
│   │
│   ├── api/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── groups.py
│   │   ├── teachers.py
│   │   ├── lessons.py
│   │   ├── lesson_entries.py
│   │   ├── progress.py
│   │   └── admin.py
│   │
│   └── services/             # Business logic
│       ├── __init__.py
│       ├── progress_calculator.py
│       ├── seed_service.py
│       └── unenrollment_service.py
│
├── scripts/
│   ├── __init__.py
│   └── init_db.py            # Database initialization script
│
└── frontend/                 # React frontend
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    │
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        │
        ├── api/
        │   └── client.ts
        │
        ├── contexts/
        │   └── AuthContext.tsx
        │
        ├── components/
        │   ├── Layout.tsx
        │   ├── ProtectedRoute.tsx
        │   └── StatusBadge.tsx
        │
        └── pages/
            ├── Login.tsx
            ├── Dashboard.tsx
            ├── LessonEntry.tsx
            ├── Students.tsx
            ├── StudentDetail.tsx
            └── Groups.tsx
```

---

## Database Setup

### Option 1: Replit PostgreSQL (Recommended)

Replit offers built-in PostgreSQL databases:

1. In your Repl, click **"Tools"** in the left sidebar
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Click **"Create Database"**
5. Replit will automatically set the `DATABASE_URL` secret

### Option 2: External PostgreSQL

Use a free PostgreSQL provider:

**Neon (neon.tech)**:
1. Create account at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string
4. Add to Replit Secrets as `DATABASE_URL`

**Supabase**:
1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database → Connection string
4. Copy the URI and add to Replit Secrets

### Connection String Format

```
postgresql://username:password@hostname:5432/database_name
```

---

## Backend Configuration

### Step 1: Create `.replit` File

```toml
run = "uvicorn main:app --host 0.0.0.0 --port 8080"
entrypoint = "main.py"
modules = ["python-3.11"]

[nix]
channel = "stable-23_11"

[deployment]
run = ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]

[[ports]]
localPort = 8080
externalPort = 80
```

### Step 2: Create `replit.nix` File

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.postgresql
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
  ];
}
```

### Step 3: Create `requirements.txt`

```txt
# Web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Validation
pydantic==2.5.2
pydantic-settings==2.1.0
email-validator==2.1.0

# Utilities
python-dotenv==1.0.0
```

### Step 4: Install Dependencies

In the Replit shell:

```bash
pip install -r requirements.txt
```

### Step 5: Create `main.py`

```python
"""
UFLI Tracking System - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api import (
    auth, students, groups, teachers,
    lessons, lesson_entries, progress, admin
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
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
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## Frontend Configuration

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Node Dependencies

```bash
npm install
```

### Step 3: Configure Vite Proxy

The `vite.config.ts` proxies API calls to the backend:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
```

### Step 4: Build for Production

```bash
npm run build
```

This creates a `dist/` folder with static files.

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
# From project root
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Production Mode (Replit)

1. Build the frontend:
   ```bash
   cd frontend && npm run build
   ```

2. Configure FastAPI to serve static files (add to `main.py`):
   ```python
   from fastapi.staticfiles import StaticFiles

   # Serve frontend build
   app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
   ```

3. Click the **"Run"** button in Replit

---

## Initial Data Setup

### Step 1: Run Database Migrations

```bash
# Create initial migration (if not exists)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Step 2: Initialize Database with Seed Data

```bash
python scripts/init_db.py --site-name "Your School Name" --admin-email admin@school.org --admin-password YourSecurePassword123
```

This will:
- Create all 128 UFLI lessons
- Create 17 skill sections
- Create grade levels (PreK through G8)
- Create your default site
- Create an admin user

### Step 3: Verify Setup

Visit the API documentation:
```
https://your-repl-name.your-username.repl.co/api/docs
```

You should see the Swagger UI with all endpoints.

---

## Testing Your Application

### Test 1: Health Check

```bash
curl https://your-repl.repl.co/api/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### Test 2: Login

```bash
curl -X POST https://your-repl.repl.co/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@school.org", "password": "YourSecurePassword123"}'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "user_id": "...",
    "email": "admin@school.org",
    "name": "Admin",
    "role": "admin"
  }
}
```

### Test 3: List Lessons

```bash
curl https://your-repl.repl.co/api/lessons \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Should return 128 lessons.

### Test 4: Frontend

1. Navigate to your Replit URL
2. You should see the login page
3. Log in with your admin credentials
4. Verify dashboard loads with stats

---

## Deployment

### Replit Deployment

1. **Enable Always On** (requires paid plan):
   - Go to your Repl settings
   - Enable "Always On"

2. **Custom Domain** (optional):
   - Go to your Repl settings
   - Add a custom domain

3. **Environment Variables**:
   - Use Replit Secrets for sensitive data
   - Never commit credentials to code

### Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Use strong `SECRET_KEY` (32+ characters)
- [ ] Enable HTTPS (automatic on Replit)
- [ ] Set up database backups
- [ ] Configure proper CORS origins
- [ ] Test all API endpoints
- [ ] Verify frontend builds correctly

---

## Environment Variables

Set these in **Replit Secrets** (Tools → Secrets):

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing key (32+ chars) | `your-super-secret-key-min-32-characters` |
| `DEBUG` | Enable debug mode | `False` |
| `CORS_ORIGINS` | Allowed frontend origins | `["https://your-app.repl.co"]` |

### Generating a Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Database connection errors

- Verify `DATABASE_URL` is set correctly
- Check database is running
- Test connection:
  ```python
  from app.database import engine
  engine.connect()
  ```

#### 3. CORS errors in browser

Add your frontend URL to `CORS_ORIGINS`:
```python
CORS_ORIGINS = ["https://your-repl.repl.co", "http://localhost:5173"]
```

#### 4. "Relation does not exist" errors

Run migrations:
```bash
alembic upgrade head
```

Or recreate tables:
```python
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
```

#### 5. Frontend not loading

- Check `npm run build` completed successfully
- Verify static files mount in `main.py`
- Check browser console for errors

#### 6. JWT token errors

- Verify `SECRET_KEY` is set
- Check token hasn't expired
- Ensure Authorization header format: `Bearer <token>`

### Logs

View application logs in Replit console or add logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## Maintenance

### Database Backups

**Manual backup:**
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

**Restore:**
```bash
psql $DATABASE_URL < backup_20240115.sql
```

### Updating Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Node packages
cd frontend && npm update
```

### Adding New Features

1. **New API endpoint:**
   - Add route in `app/api/`
   - Add schema in `app/schemas/`
   - Register router in `main.py`

2. **New database model:**
   - Create model in `app/models/`
   - Export in `app/models/__init__.py`
   - Run: `alembic revision --autogenerate -m "Add new model"`
   - Apply: `alembic upgrade head`

3. **New frontend page:**
   - Create component in `frontend/src/pages/`
   - Add route in `App.tsx`

### Monitoring

Add health monitoring endpoint:
```python
@app.get("/api/health/detailed")
def detailed_health():
    return {
        "status": "healthy",
        "database": check_db_connection(),
        "version": settings.VERSION,
        "uptime": get_uptime()
    }
```

---

## Quick Reference

### Useful Commands

```bash
# Start backend (development)
uvicorn main:app --reload --port 8080

# Start frontend (development)
cd frontend && npm run dev

# Build frontend (production)
cd frontend && npm run build

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Initialize database
python scripts/init_db.py

# Check database
python -c "from app.database import engine; print(engine.connect())"
```

### API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/refresh` | Refresh token |
| GET | `/api/students` | List students |
| GET | `/api/students/{id}` | Get student detail |
| GET | `/api/groups` | List groups |
| GET | `/api/groups/{id}/students` | Get group students |
| GET | `/api/lessons` | List all 128 lessons |
| POST | `/api/lesson-entries/batch` | Submit lesson entries |
| GET | `/api/progress/students/{id}` | Get student progress |
| GET | `/api/progress/school-summary` | Get school overview |

---

## Support

For issues with this application:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Replit documentation: [docs.replit.com](https://docs.replit.com)
3. FastAPI documentation: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

*Last updated: January 2026*
