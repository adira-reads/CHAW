# UFLI Tracking System - Application Requirements

## For Building in Replit

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [API Endpoints](#3-api-endpoints)
4. [User Roles & Permissions](#4-user-roles--permissions)
5. [UI/UX Requirements](#5-uiux-requirements)
6. [Data Import/Export](#6-data-importexport)
7. [Replit Setup Guide](#7-replit-setup-guide)
8. [Project Structure](#8-project-structure)
9. [Environment Variables](#9-environment-variables)
10. [Development Roadmap](#10-development-roadmap)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UFLI TRACKING SYSTEM                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Database   │
│   (React)   │◀────│  (FastAPI)  │◀────│ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │                   ▼
       │            ┌─────────────┐
       │            │    Auth     │
       │            │  (Replit)   │
       │            └─────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                            │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┤
│   Lesson    │   Student   │   Progress  │   Reports   │   Admin     │
│   Entry     │   Roster    │  Dashboard  │   Center    │   Panel     │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## 2. Technology Stack

### Recommended Stack (Python)

```
Backend:
├── Python 3.11+
├── FastAPI (web framework)
├── SQLAlchemy 2.0 (ORM)
├── Alembic (database migrations)
├── Pydantic (data validation)
├── uvicorn (ASGI server)
└── python-jose (JWT auth)

Frontend:
├── React 18+
├── TypeScript
├── Vite (build tool)
├── TanStack Query (data fetching)
├── React Router (navigation)
├── Tailwind CSS (styling)
└── Recharts (visualizations)

Database:
├── PostgreSQL 14+
└── Redis (optional, for caching)

DevOps:
├── Replit Deployments
├── Replit Database (PostgreSQL)
└── Replit Secrets (env vars)
```

### Alternative Stack (Node.js)

```
Backend:
├── Node.js 18+
├── Express.js or Fastify
├── Prisma (ORM)
├── Zod (validation)
└── Passport.js (auth)

Frontend:
├── Same as above
```

---

## 3. API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/refresh` | Refresh token |

### Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students` | List all students (with filters) |
| GET | `/api/students/:id` | Get student details |
| POST | `/api/students` | Create student |
| PUT | `/api/students/:id` | Update student |
| DELETE | `/api/students/:id` | Soft delete (unenroll) |
| GET | `/api/students/:id/progress` | Get student progress |
| GET | `/api/students/:id/lessons` | Get lesson statuses |

### Groups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/groups` | List all groups |
| GET | `/api/groups/:id` | Get group details |
| POST | `/api/groups` | Create group |
| PUT | `/api/groups/:id` | Update group |
| DELETE | `/api/groups/:id` | Delete group |
| GET | `/api/groups/:id/students` | Get students in group |
| GET | `/api/groups/:id/progress` | Get group progress summary |

### Lessons & Progress

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lessons` | List all 128 lessons |
| GET | `/api/lessons/:id` | Get lesson details |
| POST | `/api/lesson-entries` | Record lesson entry (batch) |
| GET | `/api/lesson-entries` | Get lesson entries (with filters) |
| PUT | `/api/lesson-status/:id` | Update single status |

### Progress & Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/progress/student/:id` | Student progress record |
| GET | `/api/progress/group/:id` | Group progress summary |
| GET | `/api/progress/grade/:id` | Grade progress summary |
| GET | `/api/progress/school` | School-wide summary |
| GET | `/api/reports/skills/:studentId` | Skills tracker |
| GET | `/api/reports/pacing/:groupId` | Pacing report |

### Tutoring (if enabled)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tutoring/groups` | List tutoring groups |
| POST | `/api/tutoring/entries` | Record tutoring session |
| GET | `/api/tutoring/summary/:studentId` | Student tutoring summary |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/site` | Get site configuration |
| PUT | `/api/admin/site` | Update site configuration |
| GET | `/api/admin/users` | List users |
| POST | `/api/admin/users` | Create user |
| PUT | `/api/admin/users/:id` | Update user |
| POST | `/api/admin/import` | Import data from CSV/Sheets |
| GET | `/api/admin/export` | Export data |
| POST | `/api/admin/recalculate` | Recalculate all progress |

---

## 4. User Roles & Permissions

### Role Definitions

| Role | Description | Access Level |
|------|-------------|--------------|
| **Admin** | Site administrator | Full access |
| **Coordinator** | Grade-level coordinator | Read all, write assigned grades |
| **Teacher** | Classroom teacher | Read/write own groups only |
| **Viewer** | Read-only access | View dashboards only |

### Permission Matrix

| Action | Admin | Coordinator | Teacher | Viewer |
|--------|-------|-------------|---------|--------|
| View all students | ✅ | ✅ | ❌ | ✅ |
| View own group students | ✅ | ✅ | ✅ | ✅ |
| Enter lesson data | ✅ | ✅ | ✅ | ❌ |
| Create/edit students | ✅ | ✅ | ❌ | ❌ |
| Create/edit groups | ✅ | ✅ | ❌ | ❌ |
| Manage teachers | ✅ | ❌ | ❌ | ❌ |
| Site configuration | ✅ | ❌ | ❌ | ❌ |
| Import/export data | ✅ | ✅ | ❌ | ❌ |
| View reports | ✅ | ✅ | ✅ | ✅ |

### Database Schema Addition

```sql
-- User management tables
CREATE TYPE user_role AS ENUM ('admin', 'coordinator', 'teacher', 'viewer');

CREATE TABLE app_user (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES site(site_id),

    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),  -- NULL if using Replit Auth
    replit_user_id VARCHAR(100), -- For Replit Auth

    name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'teacher',

    -- Teacher linkage (for role-based filtering)
    teacher_id UUID REFERENCES teacher(teacher_id),

    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grade assignments for coordinators
CREATE TABLE user_grade_assignment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES app_user(user_id),
    grade_id UUID NOT NULL REFERENCES grade(grade_id),

    UNIQUE(user_id, grade_id)
);
```

---

## 5. UI/UX Requirements

### Core Screens

#### 5.1 Dashboard (Home)
```
┌─────────────────────────────────────────────────────────────────┐
│  UFLI Tracking System                    [User Menu] [Logout]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Welcome, [Teacher Name]                    Today: Jan 24, 2026 │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ My Groups   │  │ Students    │  │ Avg Progress│             │
│  │     3       │  │    18       │  │    67%      │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  Quick Actions:                                                 │
│  [📝 Enter Lesson Data]  [📊 View Progress]  [👥 My Students]  │
│                                                                 │
│  Recent Activity:                                               │
│  ├─ KG Group 1: Completed L42 (5 students)         10:30 AM    │
│  ├─ G1 Group 2: Completed L38 (6 students)         9:45 AM     │
│  └─ G2 Group 1: Completed L56 (4 students)         Yesterday   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2 Lesson Entry Form
```
┌─────────────────────────────────────────────────────────────────┐
│  Enter Lesson Data                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Select Group                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [Dropdown: KG Group 1 - Garcia                       ▼] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Step 2: Select Lesson                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [Dropdown: UFLI L42 - Digraphs ch                    ▼] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Step 3: Mark Student Progress                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Student Name          │  Y  │  N  │  A  │  U  │        │   │
│  │ ───────────────────────┼─────┼─────┼─────┼─────┤        │   │
│  │  Adams, John           │ (●) │ ( ) │ ( ) │ ( ) │        │   │
│  │  Baker, Sarah          │ (●) │ ( ) │ ( ) │ ( ) │        │   │
│  │  Clark, Michael        │ ( ) │ (●) │ ( ) │ ( ) │        │   │
│  │  Davis, Emma           │ ( ) │ ( ) │ (●) │ ( ) │        │   │
│  │  Evans, James          │ (●) │ ( ) │ ( ) │ ( ) │        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Mark All Y] [Mark All N] [Mark All A]                        │
│                                                                 │
│                              [Cancel]  [💾 Save & Continue]     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.3 Student Progress View
```
┌─────────────────────────────────────────────────────────────────┐
│  Student Progress: Adams, John                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Grade: KG  │  Group: KG Group 1  │  Teacher: Garcia           │
│  Current Lesson: L42  │  Status: Active                         │
│                                                                 │
│  Progress Overview:                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Foundational (L1-34)    ████████████████████░░░░  85%   │   │
│  │ Min Grade (KG)          ████████████████████░░░░  85%   │   │
│  │ Benchmark               ████████████████████░░░░  85%   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Skills Breakdown:                          [Chart View 📊]     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Single Consonants & Vowels  ████████████████████  100%  │   │
│  │ Blends                      ████████████████░░░░   80%  │   │
│  │ Digraphs                    ████████░░░░░░░░░░░░   40%  │   │
│  │ VCE                         ░░░░░░░░░░░░░░░░░░░░    0%  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Lesson History:                           [View All]           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Date       │ Lesson │ Status │ Teacher │ Group          │   │
│  │ 01/24/26   │ L42    │   Y    │ Garcia  │ KG Group 1     │   │
│  │ 01/23/26   │ L41    │   Y    │ Garcia  │ KG Group 1     │   │
│  │ 01/22/26   │ L40    │   N    │ Garcia  │ KG Group 1     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.4 Group Progress Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│  Group Progress: KG Group 1 - Garcia                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Students: 6  │  Avg Lesson: L38  │  Pacing: On Track (+2)     │
│                                                                 │
│  Student Progress Matrix:                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Student      │L38│L39│L40│L41│L42│L43│L44│ Progress    │   │
│  │──────────────┼───┼───┼───┼───┼───┼───┼───┼─────────────│   │
│  │ Adams, John  │ Y │ Y │ Y │ Y │ Y │   │   │ ████░ 75%   │   │
│  │ Baker, Sarah │ Y │ Y │ Y │ Y │   │   │   │ ████░ 72%   │   │
│  │ Clark, M.    │ Y │ Y │ N │ Y │   │   │   │ ███░░ 68%   │   │
│  │ Davis, Emma  │ Y │ Y │ Y │ A │ Y │   │   │ ████░ 74%   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Group Statistics:                                              │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │ Foundational │   Min Grade  │   Benchmark  │                │
│  │     82%      │     78%      │     75%      │                │
│  └──────────────┴──────────────┴──────────────┘                │
│                                                                 │
│  [📝 Enter Lesson]  [📊 Full Report]  [📤 Export]              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.5 School Summary Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│  School Summary Dashboard                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Filter: All Grades ▼]  [Date Range: This Year ▼]  [🔄 Refresh]│
│                                                                 │
│  Overview Cards:                                                │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │ Students  │ │  Groups   │ │ Avg Prog  │ │ On Track  │       │
│  │   245     │ │    32     │ │   68%     │ │   78%     │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│                                                                 │
│  Progress by Grade:                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │      │Students│Groups│Foundational│Min Grade│Benchmark │   │
│  │──────┼────────┼──────┼────────────┼─────────┼──────────│   │
│  │ PreK │   28   │   4  │    N/A     │   62%   │   58%    │   │
│  │ KG   │   42   │   6  │    78%     │   78%   │   72%    │   │
│  │ G1   │   38   │   5  │    85%     │   71%   │   68%    │   │
│  │ G2   │   35   │   5  │    92%     │   76%   │   70%    │   │
│  │ G3   │   30   │   4  │    94%     │   82%   │   75%    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Progress Chart]                                               │
│  100%│                                                          │
│   80%│    ████                                                  │
│   60%│████████████████                                          │
│   40%│████████████████████                                      │
│   20%│████████████████████████                                  │
│    0%└────────────────────────                                  │
│       PreK  KG   G1   G2   G3                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation Structure

```
📱 Main Navigation
├── 🏠 Dashboard (Home)
├── 📝 Lesson Entry
│   ├── Small Group Entry
│   └── Tutoring Entry (if enabled)
├── 👥 Students
│   ├── All Students
│   ├── By Grade
│   └── By Group
├── 📊 Progress
│   ├── Student Progress
│   ├── Group Progress
│   ├── Grade Summary
│   └── School Summary
├── 📈 Reports
│   ├── Skills Tracker
│   ├── Pacing Dashboard
│   └── Export Data
└── ⚙️ Admin (if admin)
    ├── Site Settings
    ├── User Management
    ├── Groups & Teachers
    └── Import Data
```

---

## 6. Data Import/Export

### Import Formats

#### CSV Import Structure

**students.csv**
```csv
name,grade,group,teacher,status
"Adams, John",KG,"KG Group 1",Garcia,active
"Baker, Sarah",KG,"KG Group 1",Garcia,active
```

**lesson_entries.csv**
```csv
date,teacher,group,student,lesson,status
2026-01-24,Garcia,"KG Group 1","Adams, John",L42,Y
2026-01-24,Garcia,"KG Group 1","Baker, Sarah",L42,Y
```

**progress_matrix.csv** (UFLI MAP format)
```csv
student,grade,teacher,group,L1,L2,L3,...,L128
"Adams, John",KG,Garcia,"KG Group 1",Y,Y,Y,...,
```

### Google Sheets Migration

```python
# API endpoint for Google Sheets import
POST /api/admin/import/google-sheets
{
    "spreadsheet_id": "1abc...",
    "sheets_to_import": [
        "Student Roster",
        "UFLI MAP",
        "Small Group Progress",
        "Group Configuration"
    ],
    "options": {
        "overwrite_existing": false,
        "validate_only": false
    }
}
```

### Export Formats

- **CSV**: All data tables
- **Excel**: Formatted workbook with multiple sheets
- **PDF**: Progress reports for parents
- **JSON**: Full data export for backup

---

## 7. Replit Setup Guide

### Step 1: Create Replit Project

```bash
# In Replit, create a new Python project
# Or use the template: Python + PostgreSQL

# Project structure will be created automatically
```

### Step 2: Configure Database

```python
# In Replit Secrets, add:
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Replit provides PostgreSQL - just enable it in the Tools panel
```

### Step 3: Install Dependencies

**requirements.txt**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
```

**package.json** (for frontend)
```json
{
  "name": "ufli-frontend",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.5"
  },
  "devDependencies": {
    "vite": "^5.0.11",
    "@vitejs/plugin-react": "^4.2.1",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3"
  }
}
```

### Step 4: Configure Replit

**.replit**
```toml
run = "uvicorn main:app --host 0.0.0.0 --port 8080"
entrypoint = "main.py"

[nix]
channel = "stable-23_11"

[deployment]
run = ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]

[[ports]]
localPort = 8080
externalPort = 80
```

**replit.nix**
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.postgresql
    pkgs.nodejs_20
  ];
}
```

---

## 8. Project Structure

```
ufli-tracker/
├── .replit
├── replit.nix
├── requirements.txt
├── main.py                 # FastAPI entry point
│
├── alembic/                # Database migrations
│   ├── versions/
│   └── env.py
│
├── app/
│   ├── __init__.py
│   ├── config.py           # Settings & env vars
│   ├── database.py         # Database connection
│   │
│   ├── models/             # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── site.py
│   │   ├── student.py
│   │   ├── teacher.py
│   │   ├── group.py
│   │   ├── lesson.py
│   │   ├── progress.py
│   │   └── user.py
│   │
│   ├── schemas/            # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── lesson.py
│   │   └── progress.py
│   │
│   ├── api/                # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── groups.py
│   │   ├── lessons.py
│   │   ├── progress.py
│   │   └── admin.py
│   │
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   ├── progress_calculator.py
│   │   ├── import_service.py
│   │   └── export_service.py
│   │
│   └── utils/              # Utilities
│       ├── __init__.py
│       ├── auth.py
│       └── validators.py
│
├── frontend/               # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/            # API client
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   └── utils/          # Utilities
│   └── public/
│
├── tests/                  # Test files
│   ├── test_api/
│   └── test_services/
│
└── scripts/                # Utility scripts
    ├── seed_lessons.py     # Seed 128 lessons
    ├── migrate_sheets.py   # Google Sheets migration
    └── calculate_progress.py
```

---

## 9. Environment Variables

### Required Variables (Replit Secrets)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/ufli_db

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Site Configuration
SITE_NAME="UFLI Tracking System"
DEFAULT_TIMEZONE=America/New_York

# Optional: Google Sheets Migration
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}

# Optional: Monday.com Integration
MONDAY_API_KEY=your-monday-api-key
MONDAY_BOARD_ID=your-board-id

# Optional: Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 10. Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up Replit project with PostgreSQL
- [ ] Implement database models (SQLAlchemy)
- [ ] Create database migrations (Alembic)
- [ ] Seed lesson data (128 lessons + sections)
- [ ] Basic authentication (Replit Auth or JWT)

### Phase 2: Core API (Weeks 3-4)
- [ ] Student CRUD endpoints
- [ ] Group CRUD endpoints
- [ ] Teacher CRUD endpoints
- [ ] Lesson entry endpoints
- [ ] Basic progress calculation

### Phase 3: Frontend - MVP (Weeks 5-7)
- [ ] Authentication flow
- [ ] Dashboard page
- [ ] Lesson entry form
- [ ] Student list & detail views
- [ ] Group progress view

### Phase 4: Progress & Reports (Weeks 8-9)
- [ ] Full progress calculations
- [ ] Skills tracker
- [ ] Grade summary view
- [ ] School summary dashboard
- [ ] Export functionality

### Phase 5: Advanced Features (Weeks 10-12)
- [ ] Tutoring module
- [ ] Pacing dashboard
- [ ] Google Sheets import
- [ ] Bulk operations
- [ ] Email notifications

### Phase 6: Polish & Deploy (Week 13+)
- [ ] UI/UX refinements
- [ ] Performance optimization
- [ ] Documentation
- [ ] User training materials
- [ ] Production deployment

---

## Appendix A: Sample Code Snippets

### FastAPI Main Entry Point

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, students, groups, lessons, progress, admin
from app.database import engine
from app.models import Base

app = FastAPI(
    title="UFLI Tracking System",
    description="Student progress tracking for UFLI curriculum",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.on_event("startup")
async def startup():
    # Create tables
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "UFLI Tracking System API", "version": "1.0.0"}
```

### SQLAlchemy Student Model

```python
# app/models/student.py
from sqlalchemy import Column, String, Date, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base

class StudentStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    unenrolled = "unenrolled"
    transferred = "transferred"

class Student(Base):
    __tablename__ = "student"

    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("site.site_id"), nullable=False)
    grade_id = Column(UUID(as_uuid=True), ForeignKey("grade.grade_id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.group_id"))

    name = Column(String(255), nullable=False)
    status = Column(Enum(StudentStatus), default=StudentStatus.active)
    enrollment_date = Column(Date)
    unenrollment_date = Column(Date)
    current_lesson = Column(Integer)
    last_activity_date = Column(Date)

    # Relationships
    grade = relationship("Grade", back_populates="students")
    group = relationship("Group", back_populates="students")
    lesson_statuses = relationship("LessonStatus", back_populates="student")
    lesson_entries = relationship("LessonEntry", back_populates="student")
```

### Progress Calculator Service

```python
# app/services/progress_calculator.py
from sqlalchemy.orm import Session
from app.models import Student, LessonStatus, Lesson, ProgressRecord

class ProgressCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_student_progress(self, student_id: str) -> dict:
        """Calculate all progress metrics for a student."""
        student = self.db.query(Student).filter(
            Student.student_id == student_id
        ).first()

        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Get all lesson statuses
        statuses = self.db.query(LessonStatus).filter(
            LessonStatus.student_id == student_id,
            LessonStatus.is_initial_assessment == False
        ).all()

        # Build status map
        status_map = {ls.lesson.number: ls.status for ls in statuses}

        # Calculate metrics
        foundational = self._calculate_foundational(status_map)
        min_grade = self._calculate_min_grade(status_map, student.grade.name)
        benchmark = self._calculate_benchmark(status_map, student.grade.name)

        return {
            "foundational_count": foundational["count"],
            "foundational_pct": foundational["pct"],
            "min_grade_count": min_grade["count"],
            "min_grade_pct": min_grade["pct"],
            "benchmark_count": benchmark["count"],
            "benchmark_pct": benchmark["pct"],
        }

    def _calculate_foundational(self, status_map: dict) -> dict:
        """Calculate foundational percentage (lessons 1-34)."""
        count = sum(1 for i in range(1, 35) if status_map.get(i) == 'Y')
        return {"count": count, "pct": round(count / 34 * 100, 2)}

    def _calculate_min_grade(self, status_map: dict, grade: str) -> dict:
        """Calculate minimum grade percentage based on grade level."""
        # Define grade-specific lesson sets
        grade_lessons = {
            "KG": list(range(1, 35)),  # 1-34
            "G1": list(range(1, 35)) + list(range(42, 54)),  # 1-34 + 42-53
            "G2": list(range(1, 35)) + list(range(42, 63)),  # 1-34 + 42-62
            # ... etc
        }

        lessons = grade_lessons.get(grade, list(range(1, 35)))
        count = sum(1 for l in lessons if status_map.get(l) == 'Y')
        denominator = len(lessons)

        return {"count": count, "pct": round(count / denominator * 100, 2)}
```

---

*Document Version: 1.0*
*Last Updated: January 2026*
