# UFLI Master Tracking System - Data Model

## Version 1.0 | January 2026

This document provides complete documentation for migrating the UFLI Master Tracking System from Google Sheets to a relational database.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Entity Relationship Diagram](#2-entity-relationship-diagram)
3. [Database Schema (SQL)](#3-database-schema-sql)
4. [Data Dictionary](#4-data-dictionary)
5. [Business Rules & Constraints](#5-business-rules--constraints)
6. [Migration Mapping](#6-migration-mapping)
7. [Calculated Fields & Formulas](#7-calculated-fields--formulas)

---

## 1. System Overview

### Purpose
The UFLI Master Tracking System tracks student progress through the 128-lesson UFLI (University of Florida Literacy Institute) phonics curriculum. It supports:

- **Small Group Instruction**: Primary UFLI lesson delivery
- **Tutoring Interventions**: Supplemental instruction tracking
- **Progress Monitoring**: Multi-level aggregation (student → group → grade → school)
- **Mixed-Grade Groups**: Cross-grade instructional groupings
- **Pacing Management**: Curriculum pacing vs. calendar schedule

### Core Entities
| Entity | Description |
|--------|-------------|
| Site | School/organization using the system |
| Student | Individual learner being tracked |
| Teacher | Instructor delivering lessons |
| Group | Instructional grouping of students |
| Lesson | Individual UFLI curriculum lesson (1-128) |
| Lesson Entry | Single progress record (student + lesson + status) |
| Progress Record | Aggregated student progress across all lessons |
| Tutoring Session | Intervention instruction record |

---

## 2. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           UFLI TRACKING SYSTEM ERD                               │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────┐
                                    │     SITE     │
                                    │──────────────│
                                    │ PK site_id   │
                                    │    name      │
                                    │    config    │
                                    └──────┬───────┘
                                           │
                     ┌─────────────────────┼─────────────────────┐
                     │                     │                     │
                     ▼                     ▼                     ▼
              ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
              │   TEACHER    │     │    GRADE     │     │ SKILL_SECTION│
              │──────────────│     │──────────────│     │──────────────│
              │ PK teacher_id│     │ PK grade_id  │     │ PK section_id│
              │ FK site_id   │     │ FK site_id   │     │    name      │
              │    name      │     │    name      │     │    seq_order │
              │    email     │     │    seq_order │     │    lessons[] │
              └──────┬───────┘     └──────┬───────┘     └──────────────┘
                     │                     │                     │
                     │                     │                     │
                     ▼                     ▼                     │
              ┌──────────────┐     ┌──────────────┐              │
              │    GROUP     │◄────│   STUDENT    │              │
              │──────────────│     │──────────────│              │
              │ PK group_id  │     │ PK student_id│              │
              │ FK site_id   │     │ FK site_id   │              │
              │ FK teacher_id│     │ FK grade_id  │              │
              │ FK grade_id  │     │ FK group_id  │              │
              │    name      │     │    name      │              │
              │    is_mixed  │     │    status    │              │
              │    is_tutor  │     │    enrolled  │              │
              └──────┬───────┘     └──────┬───────┘              │
                     │                     │                     │
                     │         ┌───────────┴───────────┐         │
                     │         │                       │         │
                     │         ▼                       ▼         │
                     │  ┌──────────────┐       ┌──────────────┐  │
                     │  │PROGRESS_REC  │       │TUTORING_REC  │  │
                     │  │──────────────│       │──────────────│  │
                     │  │PK progress_id│       │PK tutor_rec_id│ │
                     │  │FK student_id │       │FK student_id │  │
                     │  │   type       │       │FK tutor_grp_id│ │
                     │  │   metrics    │       │   metrics    │  │
                     │  └──────┬───────┘       └──────────────┘  │
                     │         │                                 │
                     │         ▼                                 │
                     │  ┌──────────────┐       ┌──────────────┐  │
                     │  │LESSON_STATUS │       │    LESSON    │◄─┘
                     │  │──────────────│       │──────────────│
                     │  │PK status_id  │       │ PK lesson_id │
                     └─►│FK student_id │◄──────│    number    │
                        │FK lesson_id  │       │    name      │
                        │FK group_id   │       │ FK section_id│
                        │   status     │       │   is_review  │
                        │   date       │       └──────────────┘
                        │   teacher_id │
                        └──────────────┘

                        ┌──────────────┐       ┌──────────────┐
                        │ LESSON_ENTRY │       │UNENROLL_LOG  │
                        │──────────────│       │──────────────│
                        │PK entry_id   │       │PK log_id     │
                        │FK student_id │       │FK student_id │
                        │FK group_id   │       │FK teacher_id │
                        │FK teacher_id │       │   date       │
                        │FK lesson_id  │       │   reason     │
                        │   date       │       │   status     │
                        │   status     │       │   archive_ref│
                        │   entry_type │       └──────────────┘
                        └──────────────┘

                        ┌──────────────┐
                        │STUDENT_ARCHIVE│
                        │──────────────│
                        │PK archive_id │
                        │FK student_id │
                        │   ia_data    │
                        │   map_data   │
                        │   gs_data    │
                        │   archived_at│
                        └──────────────┘


RELATIONSHIP LEGEND:
────────────────────
PK = Primary Key
FK = Foreign Key
─── = One-to-Many relationship
◄── = Many-to-One (belongs to)

CARDINALITY:
────────────
Site ──(1:N)──► Teacher, Grade, Group
Teacher ──(1:N)──► Group, Lesson Entry
Grade ──(1:N)──► Student, Group
Group ──(1:N)──► Student (primary), Lesson Status
Student ──(1:N)──► Lesson Status, Lesson Entry, Tutoring Record
Student ──(1:1)──► Progress Record (per type: IA, MAP, GS)
Lesson ──(1:N)──► Lesson Status, Lesson Entry
Skill Section ──(1:N)──► Lesson
```

---

## 3. Database Schema (SQL)

### PostgreSQL Schema

```sql
-- ═══════════════════════════════════════════════════════════════════════════
-- UFLI MASTER TRACKING SYSTEM - DATABASE SCHEMA
-- PostgreSQL 14+
-- ═══════════════════════════════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════════════════════
-- ENUMERATED TYPES
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TYPE student_status AS ENUM ('active', 'inactive', 'unenrolled', 'transferred');
CREATE TYPE lesson_status AS ENUM ('Y', 'N', 'A', 'U');  -- Yes/No/Absent/Unenrolled
CREATE TYPE progress_type AS ENUM ('initial_assessment', 'ufli_map', 'grade_summary');
CREATE TYPE entry_type AS ENUM ('small_group', 'tutoring', 'prek');
CREATE TYPE tutoring_lesson_type AS ENUM ('ufli_reteach', 'comprehension', 'other');
CREATE TYPE unenroll_status AS ENUM ('pending', 'confirmed', 'resolved', 'error');
CREATE TYPE group_format AS ENUM ('standard', 'sankofa');

-- ═══════════════════════════════════════════════════════════════════════════
-- CORE TABLES
-- ═══════════════════════════════════════════════════════════════════════════

-- SITE: Organization/school using the system
CREATE TABLE site (
    site_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,

    -- Configuration
    allow_grade_mixing BOOLEAN DEFAULT FALSE,
    mixed_grade_config JSONB,  -- e.g., {"G6 to G8 Groups": ["G6","G7","G8"]}
    sheet_format group_format DEFAULT 'standard',
    group_naming_pattern VARCHAR(50) DEFAULT 'GRADE_GROUP_TEACHER',

    -- Feature flags
    feature_tutoring BOOLEAN DEFAULT FALSE,
    feature_pacing BOOLEAN DEFAULT FALSE,
    feature_parent_reports BOOLEAN DEFAULT FALSE,
    feature_monday_integration BOOLEAN DEFAULT FALSE,

    -- Integration settings
    monday_api_key VARCHAR(255),
    monday_board_id VARCHAR(100),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version VARCHAR(20) DEFAULT '2.0'
);

-- GRADE: Grade levels served by the site
CREATE TABLE grade (
    grade_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES site(site_id) ON DELETE CASCADE,

    name VARCHAR(10) NOT NULL,  -- PreK, KG, G1-G8
    display_name VARCHAR(50),   -- Pre-Kindergarten, Kindergarten, Grade 1, etc.
    seq_order INTEGER NOT NULL, -- For sorting: PreK=0, KG=1, G1=2, etc.

    -- Grade-specific lesson requirements
    foundational_max INTEGER DEFAULT 34,      -- Lessons 1-34
    min_grade_lessons INTEGER[],              -- Array of required lesson numbers
    current_year_lessons INTEGER[],           -- Array of current year lesson numbers
    benchmark_denominator INTEGER,            -- Denominator for benchmark calculation

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(site_id, name)
);

-- TEACHER: Instructors
CREATE TABLE teacher (
    teacher_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES site(site_id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(site_id, name)
);

-- SKILL_SECTION: UFLI curriculum skill sections
CREATE TABLE skill_section (
    section_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    name VARCHAR(100) NOT NULL,
    seq_order INTEGER NOT NULL,  -- 1-17
    lesson_range_start INTEGER,
    lesson_range_end INTEGER,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(name)
);

-- LESSON: UFLI curriculum lessons (1-128)
CREATE TABLE lesson (
    lesson_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID REFERENCES skill_section(section_id),

    number INTEGER NOT NULL UNIQUE CHECK (number >= 1 AND number <= 128),
    name VARCHAR(100) NOT NULL,        -- e.g., "UFLI L1 a/ā/"
    short_name VARCHAR(20) NOT NULL,   -- e.g., "L1"

    is_review BOOLEAN DEFAULT FALSE,
    is_foundational BOOLEAN DEFAULT FALSE,  -- Lessons 1-34

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- GROUP: Instructional groups
CREATE TABLE "group" (
    group_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES site(site_id) ON DELETE CASCADE,
    grade_id UUID REFERENCES grade(grade_id),
    teacher_id UUID REFERENCES teacher(teacher_id),

    name VARCHAR(255) NOT NULL,

    -- Mixed-grade support
    is_mixed_grade BOOLEAN DEFAULT FALSE,
    mixed_grades VARCHAR(50)[],  -- e.g., ['G6', 'G7', 'G8']
    sheet_name VARCHAR(100),     -- Name of containing sheet

    -- Tutoring group flag
    is_tutoring_group BOOLEAN DEFAULT FALSE,

    -- Expected enrollment
    expected_student_count INTEGER,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(site_id, name)
);

-- STUDENT: Individual learners
CREATE TABLE student (
    student_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES site(site_id) ON DELETE CASCADE,
    grade_id UUID NOT NULL REFERENCES grade(grade_id),
    group_id UUID REFERENCES "group"(group_id),

    name VARCHAR(255) NOT NULL,

    -- Status tracking
    status student_status DEFAULT 'active',
    enrollment_date DATE DEFAULT CURRENT_DATE,
    unenrollment_date DATE,

    -- Calculated current lesson (denormalized for performance)
    current_lesson INTEGER,
    last_activity_date DATE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(site_id, name)  -- Names must be unique within a site
);

-- ═══════════════════════════════════════════════════════════════════════════
-- PROGRESS TRACKING TABLES
-- ═══════════════════════════════════════════════════════════════════════════

-- LESSON_STATUS: Individual lesson completion status per student
CREATE TABLE lesson_status (
    status_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL REFERENCES lesson(lesson_id),
    group_id UUID REFERENCES "group"(group_id),  -- Group when lesson was completed
    teacher_id UUID REFERENCES teacher(teacher_id),

    status lesson_status NOT NULL,
    completed_date DATE,

    -- For tracking history
    is_initial_assessment BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(student_id, lesson_id, is_initial_assessment)
);

-- PROGRESS_RECORD: Aggregated progress metrics (replaces UFLI MAP, Grade Summary)
CREATE TABLE progress_record (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,

    record_type progress_type NOT NULL,

    -- Cached metrics (recalculated periodically)
    foundational_count INTEGER DEFAULT 0,
    foundational_pct DECIMAL(5,2) DEFAULT 0,

    min_grade_count INTEGER DEFAULT 0,
    min_grade_pct DECIMAL(5,2) DEFAULT 0,

    full_grade_count INTEGER DEFAULT 0,
    full_grade_pct DECIMAL(5,2) DEFAULT 0,

    benchmark_count INTEGER DEFAULT 0,
    benchmark_pct DECIMAL(5,2) DEFAULT 0,

    -- For PreK (letter tracking)
    form_count INTEGER,
    form_pct DECIMAL(5,2),
    name_sound_count INTEGER,
    name_sound_pct DECIMAL(5,2),

    -- Skill section percentages (JSON for flexibility)
    skill_sections JSONB,  -- {"section_1": 85.5, "section_2": 92.0, ...}

    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(student_id, record_type)
);

-- LESSON_ENTRY: Raw lesson entry log (Small Group Progress equivalent)
CREATE TABLE lesson_entry (
    entry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES site(site_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    group_id UUID NOT NULL REFERENCES "group"(group_id),
    teacher_id UUID NOT NULL REFERENCES teacher(teacher_id),
    lesson_id UUID NOT NULL REFERENCES lesson(lesson_id),

    entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status lesson_status NOT NULL,
    entry_type entry_type DEFAULT 'small_group',

    -- For tutoring entries
    tutoring_lesson_type tutoring_lesson_type,
    lesson_detail VARCHAR(255),  -- Full lesson description for tutoring

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Index for common queries
    INDEX idx_entry_date (entry_date),
    INDEX idx_entry_student (student_id),
    INDEX idx_entry_group (group_id)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- TUTORING TABLES
-- ═══════════════════════════════════════════════════════════════════════════

-- STUDENT_TUTORING_GROUP: Many-to-many relationship for tutoring groups
CREATE TABLE student_tutoring_group (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    group_id UUID NOT NULL REFERENCES "group"(group_id) ON DELETE CASCADE,

    assigned_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE(student_id, group_id)
);

-- TUTORING_SUMMARY: Aggregated tutoring metrics per student
CREATE TABLE tutoring_summary (
    summary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,

    -- Session counts
    total_sessions INTEGER DEFAULT 0,

    -- UFLI Reteach metrics
    reteach_count INTEGER DEFAULT 0,
    reteach_pass_count INTEGER DEFAULT 0,
    reteach_pass_pct DECIMAL(5,2) DEFAULT 0,

    -- Comprehension metrics
    comprehension_count INTEGER DEFAULT 0,
    comprehension_pass_count INTEGER DEFAULT 0,
    comprehension_pass_pct DECIMAL(5,2) DEFAULT 0,

    -- Other intervention metrics
    other_count INTEGER DEFAULT 0,
    other_pass_count INTEGER DEFAULT 0,
    other_pass_pct DECIMAL(5,2) DEFAULT 0,

    -- Overall
    overall_pass_pct DECIMAL(5,2) DEFAULT 0,
    last_session_date DATE,

    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(student_id)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- UNENROLLMENT & ARCHIVE TABLES
-- ═══════════════════════════════════════════════════════════════════════════

-- UNENROLLMENT_LOG: Track student unenrollments
CREATE TABLE unenrollment_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student(student_id),
    reported_by_id UUID REFERENCES teacher(teacher_id),

    reported_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    lesson_at_unenroll VARCHAR(50),
    status unenroll_status DEFAULT 'pending',
    notes TEXT,

    -- Monday.com integration
    monday_task_id VARCHAR(100),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- STUDENT_ARCHIVE: Complete data preservation for unenrolled students
CREATE TABLE student_archive (
    archive_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES student(student_id),
    unenrollment_log_id UUID REFERENCES unenrollment_log(log_id),

    -- Preserved data snapshots (JSONB for flexibility)
    initial_assessment_data JSONB,
    ufli_map_data JSONB,
    grade_summary_data JSONB,
    tutoring_data JSONB,

    -- Metadata
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    archived_by VARCHAR(255)
);

-- ARCHIVE_AUDIT_LOG: Audit trail for archival actions
CREATE TABLE archive_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID,
    action VARCHAR(50) NOT NULL,  -- 'archive', 'restore', 'delete'
    performed_by VARCHAR(255),
    details JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════
-- PACING TABLES
-- ═══════════════════════════════════════════════════════════════════════════

-- PACING_SCHEDULE: Expected curriculum pacing
CREATE TABLE pacing_schedule (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES site(site_id) ON DELETE CASCADE,

    week_number INTEGER NOT NULL,
    week_start_date DATE NOT NULL,
    expected_lesson INTEGER NOT NULL,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(site_id, week_number)
);

-- PACING_LOG: Historical pacing entries per group
CREATE TABLE pacing_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID NOT NULL REFERENCES "group"(group_id) ON DELETE CASCADE,

    log_date DATE NOT NULL,
    current_lesson INTEGER NOT NULL,
    expected_lesson INTEGER,
    variance INTEGER,  -- current - expected

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_pacing_group_date (group_id, log_date)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- INDEXES FOR PERFORMANCE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE INDEX idx_student_site ON student(site_id);
CREATE INDEX idx_student_grade ON student(grade_id);
CREATE INDEX idx_student_group ON student(group_id);
CREATE INDEX idx_student_status ON student(status);
CREATE INDEX idx_student_name ON student(name);

CREATE INDEX idx_lesson_status_student ON lesson_status(student_id);
CREATE INDEX idx_lesson_status_lesson ON lesson_status(lesson_id);

CREATE INDEX idx_lesson_entry_site ON lesson_entry(site_id);
CREATE INDEX idx_lesson_entry_date ON lesson_entry(entry_date);
CREATE INDEX idx_lesson_entry_student ON lesson_entry(student_id);
CREATE INDEX idx_lesson_entry_group ON lesson_entry(group_id);

CREATE INDEX idx_group_site ON "group"(site_id);
CREATE INDEX idx_group_grade ON "group"(grade_id);
CREATE INDEX idx_group_teacher ON "group"(teacher_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS FOR COMMON QUERIES
-- ═══════════════════════════════════════════════════════════════════════════

-- UFLI MAP equivalent view
CREATE VIEW v_ufli_map AS
SELECT
    s.student_id,
    s.name AS student_name,
    g.name AS grade,
    t.name AS teacher,
    grp.name AS group_name,
    s.current_lesson,
    pr.foundational_pct,
    pr.min_grade_pct,
    pr.full_grade_pct,
    pr.benchmark_pct,
    pr.skill_sections
FROM student s
JOIN grade g ON s.grade_id = g.grade_id
LEFT JOIN "group" grp ON s.group_id = grp.group_id
LEFT JOIN teacher t ON grp.teacher_id = t.teacher_id
LEFT JOIN progress_record pr ON s.student_id = pr.student_id
    AND pr.record_type = 'ufli_map'
WHERE s.status = 'active';

-- Grade Summary equivalent view
CREATE VIEW v_grade_summary AS
SELECT
    g.name AS grade,
    COUNT(s.student_id) AS total_students,
    AVG(pr.foundational_pct) AS avg_foundational,
    AVG(pr.min_grade_pct) AS avg_min_grade,
    AVG(pr.full_grade_pct) AS avg_full_grade,
    AVG(pr.benchmark_pct) AS avg_benchmark
FROM grade g
JOIN student s ON g.grade_id = s.grade_id
LEFT JOIN progress_record pr ON s.student_id = pr.student_id
    AND pr.record_type = 'ufli_map'
WHERE s.status = 'active'
GROUP BY g.grade_id, g.name, g.seq_order
ORDER BY g.seq_order;

-- Group Progress view
CREATE VIEW v_group_progress AS
SELECT
    grp.group_id,
    grp.name AS group_name,
    g.name AS grade,
    t.name AS teacher,
    COUNT(s.student_id) AS student_count,
    AVG(s.current_lesson) AS avg_current_lesson,
    MIN(s.current_lesson) AS min_lesson,
    MAX(s.current_lesson) AS max_lesson,
    AVG(pr.benchmark_pct) AS avg_benchmark
FROM "group" grp
JOIN grade g ON grp.grade_id = g.grade_id
LEFT JOIN teacher t ON grp.teacher_id = t.teacher_id
LEFT JOIN student s ON grp.group_id = s.group_id AND s.status = 'active'
LEFT JOIN progress_record pr ON s.student_id = pr.student_id
    AND pr.record_type = 'ufli_map'
WHERE grp.is_active = TRUE AND grp.is_tutoring_group = FALSE
GROUP BY grp.group_id, grp.name, g.name, t.name;

-- Tutoring Summary view
CREATE VIEW v_tutoring_summary AS
SELECT
    s.student_id,
    s.name AS student_name,
    g.name AS grade,
    grp.name AS primary_group,
    STRING_AGG(DISTINCT tg.name, ', ') AS tutoring_groups,
    ts.total_sessions,
    ts.reteach_pass_pct,
    ts.comprehension_pass_pct,
    ts.other_pass_pct,
    ts.overall_pass_pct,
    ts.last_session_date
FROM student s
JOIN grade g ON s.grade_id = g.grade_id
LEFT JOIN "group" grp ON s.group_id = grp.group_id
LEFT JOIN student_tutoring_group stg ON s.student_id = stg.student_id
LEFT JOIN "group" tg ON stg.group_id = tg.group_id
LEFT JOIN tutoring_summary ts ON s.student_id = ts.student_id
WHERE s.status = 'active'
GROUP BY s.student_id, s.name, g.name, grp.name,
         ts.total_sessions, ts.reteach_pass_pct, ts.comprehension_pass_pct,
         ts.other_pass_pct, ts.overall_pass_pct, ts.last_session_date;

-- ═══════════════════════════════════════════════════════════════════════════
-- TRIGGERS FOR DATA INTEGRITY
-- ═══════════════════════════════════════════════════════════════════════════

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_site_updated
    BEFORE UPDATE ON site
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_student_updated
    BEFORE UPDATE ON student
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_teacher_updated
    BEFORE UPDATE ON teacher
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_group_updated
    BEFORE UPDATE ON "group"
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_lesson_status_updated
    BEFORE UPDATE ON lesson_status
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER tr_unenrollment_log_updated
    BEFORE UPDATE ON unenrollment_log
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Update current lesson when lesson_status changes
CREATE OR REPLACE FUNCTION update_student_current_lesson()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE student
    SET current_lesson = (
        SELECT MAX(l.number)
        FROM lesson_status ls
        JOIN lesson l ON ls.lesson_id = l.lesson_id
        WHERE ls.student_id = NEW.student_id
        AND ls.status = 'Y'
        AND ls.is_initial_assessment = FALSE
    ),
    last_activity_date = CURRENT_DATE,
    updated_at = CURRENT_TIMESTAMP
    WHERE student_id = NEW.student_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_current_lesson
    AFTER INSERT OR UPDATE ON lesson_status
    FOR EACH ROW EXECUTE FUNCTION update_student_current_lesson();
```

---

## 4. Data Dictionary

### 4.1 Core Entities

#### SITE
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| site_id | UUID | NO | Primary key |
| name | VARCHAR(255) | NO | School/organization name |
| allow_grade_mixing | BOOLEAN | YES | Enable mixed-grade groups |
| mixed_grade_config | JSONB | YES | Configuration for mixed-grade sheets |
| sheet_format | ENUM | YES | 'standard' or 'sankofa' |
| group_naming_pattern | VARCHAR(50) | YES | Pattern for group names |
| feature_tutoring | BOOLEAN | YES | Enable tutoring module |
| feature_pacing | BOOLEAN | YES | Enable pacing dashboard |
| feature_parent_reports | BOOLEAN | YES | Enable parent reports |
| feature_monday_integration | BOOLEAN | YES | Enable Monday.com integration |
| monday_api_key | VARCHAR(255) | YES | Monday.com API key |
| monday_board_id | VARCHAR(100) | YES | Monday.com board ID |
| created_at | TIMESTAMP | NO | Record creation timestamp |
| updated_at | TIMESTAMP | NO | Last update timestamp |
| version | VARCHAR(20) | YES | System version |

#### STUDENT
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| student_id | UUID | NO | Primary key |
| site_id | UUID | NO | FK to site |
| grade_id | UUID | NO | FK to grade |
| group_id | UUID | YES | FK to primary group |
| name | VARCHAR(255) | NO | Student full name (unique per site) |
| status | ENUM | NO | 'active', 'inactive', 'unenrolled', 'transferred' |
| enrollment_date | DATE | YES | Date student enrolled |
| unenrollment_date | DATE | YES | Date student unenrolled |
| current_lesson | INTEGER | YES | Highest completed lesson (1-128) |
| last_activity_date | DATE | YES | Date of last lesson entry |
| created_at | TIMESTAMP | NO | Record creation timestamp |
| updated_at | TIMESTAMP | NO | Last update timestamp |

#### GROUP
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| group_id | UUID | NO | Primary key |
| site_id | UUID | NO | FK to site |
| grade_id | UUID | YES | FK to grade (null for mixed-grade) |
| teacher_id | UUID | YES | FK to primary teacher |
| name | VARCHAR(255) | NO | Group name (unique per site) |
| is_mixed_grade | BOOLEAN | NO | True if cross-grade group |
| mixed_grades | VARCHAR[] | YES | Array of grades if mixed |
| sheet_name | VARCHAR(100) | YES | Source sheet name |
| is_tutoring_group | BOOLEAN | NO | True if tutoring intervention group |
| expected_student_count | INTEGER | YES | Expected enrollment |
| is_active | BOOLEAN | NO | Active status |
| created_at | TIMESTAMP | NO | Record creation timestamp |
| updated_at | TIMESTAMP | NO | Last update timestamp |

#### LESSON
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| lesson_id | UUID | NO | Primary key |
| section_id | UUID | YES | FK to skill_section |
| number | INTEGER | NO | Lesson number (1-128, unique) |
| name | VARCHAR(100) | NO | Full lesson name (e.g., "UFLI L1 a/ā/") |
| short_name | VARCHAR(20) | NO | Short name (e.g., "L1") |
| is_review | BOOLEAN | NO | True if review lesson |
| is_foundational | BOOLEAN | NO | True if lessons 1-34 |
| created_at | TIMESTAMP | NO | Record creation timestamp |

### 4.2 Progress Tracking

#### LESSON_STATUS
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| status_id | UUID | NO | Primary key |
| student_id | UUID | NO | FK to student |
| lesson_id | UUID | NO | FK to lesson |
| group_id | UUID | YES | Group when completed |
| teacher_id | UUID | YES | Teacher who recorded |
| status | ENUM | NO | 'Y' (pass), 'N' (fail), 'A' (absent), 'U' (unenrolled) |
| completed_date | DATE | YES | Date of completion |
| is_initial_assessment | BOOLEAN | NO | True if from initial assessment |
| created_at | TIMESTAMP | NO | Record creation timestamp |
| updated_at | TIMESTAMP | NO | Last update timestamp |

#### PROGRESS_RECORD
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| progress_id | UUID | NO | Primary key |
| student_id | UUID | NO | FK to student |
| record_type | ENUM | NO | 'initial_assessment', 'ufli_map', 'grade_summary' |
| foundational_count | INTEGER | YES | Count of Y in lessons 1-34 |
| foundational_pct | DECIMAL | YES | foundational_count / 34 |
| min_grade_count | INTEGER | YES | Count of Y in min grade lessons |
| min_grade_pct | DECIMAL | YES | Percentage of min grade |
| full_grade_count | INTEGER | YES | Count of Y in current year lessons |
| full_grade_pct | DECIMAL | YES | Percentage of current year |
| benchmark_count | INTEGER | YES | Count for benchmark calc |
| benchmark_pct | DECIMAL | YES | Benchmark percentage |
| skill_sections | JSONB | YES | Per-section percentages |
| calculated_at | TIMESTAMP | NO | Last calculation timestamp |
| created_at | TIMESTAMP | NO | Record creation timestamp |

#### LESSON_ENTRY
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| entry_id | UUID | NO | Primary key |
| site_id | UUID | NO | FK to site |
| student_id | UUID | NO | FK to student |
| group_id | UUID | NO | FK to group |
| teacher_id | UUID | NO | FK to teacher |
| lesson_id | UUID | NO | FK to lesson |
| entry_date | TIMESTAMP | NO | Date/time of entry |
| status | ENUM | NO | 'Y', 'N', 'A', 'U' |
| entry_type | ENUM | NO | 'small_group', 'tutoring', 'prek' |
| tutoring_lesson_type | ENUM | YES | For tutoring: 'ufli_reteach', 'comprehension', 'other' |
| lesson_detail | VARCHAR | YES | Full description for tutoring |
| created_at | TIMESTAMP | NO | Record creation timestamp |

### 4.3 Tutoring

#### TUTORING_SUMMARY
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| summary_id | UUID | NO | Primary key |
| student_id | UUID | NO | FK to student (unique) |
| total_sessions | INTEGER | NO | Total tutoring sessions |
| reteach_count | INTEGER | NO | UFLI reteach attempts |
| reteach_pass_count | INTEGER | NO | UFLI reteach passes |
| reteach_pass_pct | DECIMAL | NO | Reteach pass rate |
| comprehension_count | INTEGER | NO | Comprehension attempts |
| comprehension_pass_count | INTEGER | NO | Comprehension passes |
| comprehension_pass_pct | DECIMAL | NO | Comprehension pass rate |
| other_count | INTEGER | NO | Other intervention attempts |
| other_pass_count | INTEGER | NO | Other intervention passes |
| other_pass_pct | DECIMAL | NO | Other pass rate |
| overall_pass_pct | DECIMAL | NO | Overall pass rate |
| last_session_date | DATE | YES | Most recent session |
| calculated_at | TIMESTAMP | NO | Last calculation timestamp |

---

## 5. Business Rules & Constraints

### 5.1 Student Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| SR-001 | Student names must be unique within a site | UNIQUE constraint on (site_id, name) |
| SR-002 | Student must be assigned to exactly one primary group | group_id FK, application logic |
| SR-003 | Student can be in multiple tutoring groups | student_tutoring_group junction table |
| SR-004 | Status changes to 'unenrolled' trigger archival | Application trigger + unenrollment_log |
| SR-005 | Current lesson = max lesson number where status = 'Y' | Trigger on lesson_status |

### 5.2 Lesson Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| LR-001 | Lesson numbers must be 1-128 | CHECK constraint |
| LR-002 | Review lessons: 35-41, 49, 53, 57, 59, 62, 71, 76, 79, 83, 88, 92, 97, 102, 104-106, 128 | is_review flag |
| LR-003 | Foundational lessons: 1-34 | is_foundational flag |
| LR-004 | Status must be Y, N, A, or U | ENUM constraint |

### 5.3 Group Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| GR-001 | Tutoring groups detected by name containing "tutoring" | Application logic + is_tutoring_group flag |
| GR-002 | Mixed-grade groups span multiple grades | is_mixed_grade flag, mixed_grades array |
| GR-003 | Group names must be unique within a site | UNIQUE constraint |

### 5.4 Progress Calculation Rules

| Rule | Description | Formula |
|------|-------------|---------|
| PR-001 | Foundational % | COUNT(Y in L1-34) / 34 |
| PR-002 | Min Grade % (KG) | COUNT(Y in L1-34) / 34 |
| PR-003 | Min Grade % (G1) | COUNT(Y in L1-44 excluding reviews) / 44 |
| PR-004 | Min Grade % (G2-G3) | COUNT(Y in L1-56 excluding reviews) / 56 |
| PR-005 | Min Grade % (G4+) | COUNT(Y in L1-103 excluding reviews) / 103 |
| PR-006 | Review section rule | If any review in section: all pass = 100%, else calculate non-review only |

### 5.5 Grade-Specific Lesson Requirements

| Grade | Foundational | Minimum Set | Benchmark Denominator |
|-------|--------------|-------------|----------------------|
| PreK | N/A | Letters a-z | 26 (forms), 52 (name+sound), 78 (full) |
| KG | L1-34 | L1-34 | 34 |
| G1 | L1-34 | L1-34 + L42-53 | 44 |
| G2-G3 | L1-34 | L1-34 + L42-62 | 56 |
| G4-G8 | L1-34 | L1-34 + L42-110 | 103 |

---

## 6. Migration Mapping

### 6.1 Sheet to Table Mapping

| Google Sheet | Database Table(s) | Notes |
|--------------|-------------------|-------|
| Site Configuration | site | One row per site |
| Student Roster | student | One row per student |
| Teacher Roster | teacher | One row per teacher |
| Group Configuration | group | One row per group |
| UFLI MAP | student, lesson_status, progress_record | Denormalized → normalized |
| Small Group Progress | lesson_entry | Raw log entries |
| Grade Summary | progress_record (type='grade_summary') | Calculated view |
| Initial Assessment | lesson_status (is_initial_assessment=true), progress_record | Baseline data |
| Tutoring Progress Log | lesson_entry (entry_type='tutoring') | Filtered entries |
| Tutoring Summary | tutoring_summary | Calculated summary |
| Unenrolled Log | unenrollment_log | Status tracking |
| Student Archive | student_archive | JSONB preservation |
| Pacing Dashboard | pacing_log | Time-series data |
| KG Groups, G1 Groups, etc. | Derived from student + group | Denormalized in sheets |
| SC Classroom | group (is_mixed_grade=true) | Mixed-grade group |
| G6 to G8 Groups | group (is_mixed_grade=true) | Mixed-grade group |

### 6.2 Column Mapping: UFLI MAP → Database

| Sheet Column | Table.Column | Transformation |
|--------------|--------------|----------------|
| Student Name | student.name | Direct |
| Grade | grade.name (via grade_id) | Lookup/create grade |
| Teacher | teacher.name (via group.teacher_id) | Lookup/create teacher |
| Group | group.name (via group_id) | Lookup/create group |
| Current Lesson | student.current_lesson | Calculated from lesson_status |
| Columns F-CI (L1-L128) | lesson_status rows | Pivot: 1 row per lesson with status |

### 6.3 Column Mapping: Small Group Progress → Database

| Sheet Column | Table.Column | Transformation |
|--------------|--------------|----------------|
| Date | lesson_entry.entry_date | Parse timestamp |
| Teacher | lesson_entry.teacher_id | Lookup teacher |
| Group | lesson_entry.group_id | Lookup group |
| Student | lesson_entry.student_id | Lookup student |
| Lesson | lesson_entry.lesson_id | Parse "UFLI L##" → lesson number |
| Status | lesson_entry.status | Map Y/N/A/U to enum |

### 6.4 Migration Script Pseudocode

```python
# Migration Order (respects foreign key dependencies):
# 1. site
# 2. grade, teacher, skill_section, lesson
# 3. group
# 4. student
# 5. lesson_status (from UFLI MAP + Initial Assessment)
# 6. lesson_entry (from Small Group Progress + Tutoring Progress Log)
# 7. progress_record (calculate from lesson_status)
# 8. tutoring_summary (calculate from lesson_entry)
# 9. unenrollment_log, student_archive

def migrate_ufli_system(spreadsheet_id):
    # Phase 1: Core entities
    site = create_site_from_config(read_sheet("Site Configuration"))

    grades = create_grades(site, get_unique_grades())
    teachers = create_teachers(site, read_sheet("Teacher Roster"))
    lessons = create_lessons()  # Static 128 lessons

    # Phase 2: Groups
    groups = create_groups(site, read_sheet("Group Configuration"), teachers, grades)

    # Phase 3: Students
    students = create_students(site, read_sheet("Student Roster"), grades, groups)

    # Phase 4: Progress data
    for student in students:
        # Import Initial Assessment
        ia_data = get_student_row("Initial Assessment", student.name)
        create_lesson_statuses(student, ia_data, is_initial=True)

        # Import UFLI MAP (current progress)
        map_data = get_student_row("UFLI MAP", student.name)
        create_lesson_statuses(student, map_data, is_initial=False)

    # Phase 5: Lesson entries (historical log)
    for row in read_sheet("Small Group Progress"):
        create_lesson_entry(row, entry_type='small_group')

    for row in read_sheet("Tutoring Progress Log"):
        create_lesson_entry(row, entry_type='tutoring')

    # Phase 6: Calculate aggregates
    calculate_all_progress_records()
    calculate_all_tutoring_summaries()

    # Phase 7: Archive data
    migrate_unenrollment_logs()
    migrate_student_archives()
```

---

## 7. Calculated Fields & Formulas

### 7.1 Current Lesson Calculation

```sql
-- Get current lesson for a student
SELECT MAX(l.number) AS current_lesson
FROM lesson_status ls
JOIN lesson l ON ls.lesson_id = l.lesson_id
WHERE ls.student_id = :student_id
  AND ls.status = 'Y'
  AND ls.is_initial_assessment = FALSE;
```

### 7.2 Foundational Percentage

```sql
-- Calculate foundational % (lessons 1-34)
SELECT
    COUNT(CASE WHEN ls.status = 'Y' THEN 1 END)::DECIMAL / 34 * 100 AS foundational_pct
FROM lesson_status ls
JOIN lesson l ON ls.lesson_id = l.lesson_id
WHERE ls.student_id = :student_id
  AND ls.is_initial_assessment = FALSE
  AND l.number BETWEEN 1 AND 34;
```

### 7.3 Grade-Specific Minimum Percentage

```sql
-- Calculate min grade % for a G1 student
WITH grade_lessons AS (
    SELECT unnest(min_grade_lessons) AS lesson_num
    FROM grade WHERE name = 'G1'
)
SELECT
    COUNT(CASE WHEN ls.status = 'Y' THEN 1 END)::DECIMAL /
    (SELECT COUNT(*) FROM grade_lessons) * 100 AS min_grade_pct
FROM lesson_status ls
JOIN lesson l ON ls.lesson_id = l.lesson_id
JOIN grade_lessons gl ON l.number = gl.lesson_num
WHERE ls.student_id = :student_id
  AND ls.is_initial_assessment = FALSE;
```

### 7.4 Skill Section Percentage with Review Logic

```sql
-- Calculate section percentage with review lesson handling
WITH section_lessons AS (
    SELECT l.lesson_id, l.number, l.is_review, ls.status
    FROM lesson l
    LEFT JOIN lesson_status ls ON l.lesson_id = ls.lesson_id
        AND ls.student_id = :student_id
        AND ls.is_initial_assessment = FALSE
    WHERE l.section_id = :section_id
),
review_check AS (
    SELECT
        COUNT(CASE WHEN is_review THEN 1 END) AS review_count,
        COUNT(CASE WHEN is_review AND status = 'Y' THEN 1 END) AS review_pass_count
    FROM section_lessons
)
SELECT
    CASE
        WHEN rc.review_count > 0 AND rc.review_count = rc.review_pass_count
        THEN 100.0
        ELSE (
            SELECT COUNT(CASE WHEN status = 'Y' THEN 1 END)::DECIMAL /
                   NULLIF(COUNT(CASE WHEN NOT is_review THEN 1 END), 0) * 100
            FROM section_lessons
            WHERE NOT is_review
        )
    END AS section_pct
FROM review_check rc;
```

### 7.5 Tutoring Pass Rate

```sql
-- Calculate tutoring pass rates
SELECT
    s.student_id,
    COUNT(*) AS total_sessions,

    -- UFLI Reteach
    COUNT(CASE WHEN le.tutoring_lesson_type = 'ufli_reteach' THEN 1 END) AS reteach_count,
    COUNT(CASE WHEN le.tutoring_lesson_type = 'ufli_reteach' AND le.status = 'Y' THEN 1 END)::DECIMAL /
    NULLIF(COUNT(CASE WHEN le.tutoring_lesson_type = 'ufli_reteach' AND le.status IN ('Y','N') THEN 1 END), 0) * 100 AS reteach_pass_pct,

    -- Comprehension
    COUNT(CASE WHEN le.tutoring_lesson_type = 'comprehension' THEN 1 END) AS comp_count,
    COUNT(CASE WHEN le.tutoring_lesson_type = 'comprehension' AND le.status = 'Y' THEN 1 END)::DECIMAL /
    NULLIF(COUNT(CASE WHEN le.tutoring_lesson_type = 'comprehension' AND le.status IN ('Y','N') THEN 1 END), 0) * 100 AS comp_pass_pct,

    -- Overall
    COUNT(CASE WHEN le.status = 'Y' THEN 1 END)::DECIMAL /
    NULLIF(COUNT(CASE WHEN le.status IN ('Y','N') THEN 1 END), 0) * 100 AS overall_pass_pct

FROM student s
JOIN lesson_entry le ON s.student_id = le.student_id
WHERE le.entry_type = 'tutoring'
GROUP BY s.student_id;
```

---

## Appendix A: Review Lessons

The following lesson numbers are review lessons and have special handling in calculations:

```
35, 36, 37, 39, 40, 41, 49, 53, 57, 59, 62, 71, 76, 79, 83, 88, 92, 97, 102, 104, 105, 106, 128
```

## Appendix B: Skill Sections

| Section | Name | Lessons |
|---------|------|---------|
| 1 | Single Consonants & Short Vowels | 1-34 |
| 2 | Blends | 25, 27 |
| 3 | Alphabet Review | 35-41 |
| 4 | Digraphs | 42-53 |
| 5 | VCE (Vowel-Consonant-E) | 54-62 |
| 6 | Reading Longer Words | 63-68 |
| 7 | Ending Spelling Patterns | 69-76 |
| 8 | R-Controlled Vowels | 77-83 |
| 9 | Long Vowel Teams | 84-88 |
| 10 | Other Vowel Teams | 89-94 |
| 11 | Diphthongs | 95-97 |
| 12 | Silent Letters | 98 |
| 13 | Suffixes & Prefixes | 99-106 |
| 14 | Suffix Spelling Changes | 107-110 |
| 15 | Low Frequency Spellings | 111-118 |
| 16 | Additional Affixes | 119-126 |
| 17 | Affixes Review 2 | 127-128 |

---

## Appendix C: Status Codes

| Code | Meaning | Color (Sheets) | Use Cases |
|------|---------|----------------|-----------|
| Y | Yes/Pass | Light Green (#d4edda) | Student passed the lesson |
| N | No/Fail | Light Red (#f8d7da) | Student did not pass |
| A | Absent | Light Yellow (#fff3cd) | Student was absent |
| U | Unenrolled | Teal (#98D4BB) | Student left the program |

---

*Document generated: January 2026*
*System Version: 2.0*
