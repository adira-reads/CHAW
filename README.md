# CHAW - Christel House West Academy
## Adira Reads Progress Report System

A comprehensive Google Apps Script-based student literacy progress tracking system designed for schools implementing the UFLI (University of Florida Literacy Institute) Foundations curriculum and Pre-K Handwriting Without Tears program.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Modules](#core-modules)
4. [Sheet Structure](#sheet-structure)
5. [Key Features](#key-features)
6. [Setup & Configuration](#setup--configuration)
7. [User Workflows](#user-workflows)
8. [Technical Reference](#technical-reference)

---

## Overview

This system provides:

- **Dual-track progress monitoring** for whole-group UFLI instruction and small-group tutoring interventions
- **Real-time lesson data entry** via web app interface
- **Automated calculations** for benchmark percentages, skill mastery, and grade-level metrics
- **Mixed-grade group support** for schools that combine grades by skill level
- **Unenrollment automation** with Monday.com integration and archival
- **Exception reporting** for data quality management
- **Pre-K support** using Handwriting Without Tears curriculum tracking

### Version Information

| Module | Version | Last Updated |
|--------|---------|--------------|
| Setup Wizard | 3.2 | January 2026 |
| Progress Tracking | 5.2 | January 2026 |
| Tutoring System | 1.1 | January 2026 |
| Mixed Grade Support | 2.0 | January 2026 |
| Unenrollment Automation | 2.0 | January 2026 |
| Admin Import | 3.0 | January 2026 |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                               │
├─────────────────────────────────────────────────────────────────────┤
│  LessonEntryForm.html  │  SetUpWizardUI.html  │  ManageStudentUI.html│
│  (Web App - Daily)     │  (Initial Config)    │  (Student CRUD)      │
├─────────────────────────────────────────────────────────────────────┤
│  ManageGroupsUI.html   │  GenerateReportsUI.html                     │
│  (Group Management)    │  (Report Generation)                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CORE ENGINE                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Setupwizard.gs           │  Phase2_ProgressTracking.gs             │
│  - Menu integration       │  - Sheet generation                      │
│  - Web app entry point    │  - Sync engine                          │
│  - Config management      │  - Benchmark calculations               │
│  - Save routing           │  - Skill tracking                       │
├─────────────────────────────────────────────────────────────────────┤
│  TutoringSystem.gs        │  MixedGradeSupport_Enhanced.gs          │
│  - Tutoring detection     │  - Multi-grade group handling           │
│  - Intervention tracking  │  - Sankofa/Standard format support      │
│  - Unenrolled logging     │  - Cross-grade student lookups          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SUPPORT MODULES                                 │
├─────────────────────────────────────────────────────────────────────┤
│  UnenrollmentAutomation.gs │  AdminImport_v1.gs                      │
│  - Monday.com API          │  - CSV/Grid import                      │
│  - Student archival        │  - Data validation                      │
│  - Workflow automation     │  - Exception reporting                  │
├─────────────────────────────────────────────────────────────────────┤
│  MissingStudents.gs        │  studentrecon.gs                        │
│  - Cross-sheet validation  │  - Group count validation               │
│  - Exception highlighting  │  - Duplicate detection                  │
├─────────────────────────────────────────────────────────────────────┤
│  Utilities.gs                                                        │
│  - Group name synchronization across sheets                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. Setupwizard.gs (Phase 1)
**Purpose:** Configuration, student/group management, reports, and web app entry

Key Functions:
- `onOpen()` - Creates the custom menu system
- `doGet()` - Serves the lesson entry web app
- `startSetupWizard()` - Launches configuration wizard
- `getWizardData()` - Retrieves all configuration data
- `saveLessonData()` - Master router for lesson data (routes to PreK, Tutoring, or UFLI)

Constants Defined:
- `SHEET_NAMES` - Configuration sheet names
- `GRADE_OPTIONS` - PreK through G8
- `FEATURE_OPTIONS` - Optional feature toggles
- `CONFIG_LAYOUT` - Centralized layout configuration

### 2. Phase2_ProgressTracking.gs (Phase 2)
**Purpose:** Sheet generation, progress tracking, sync engine, and pacing

Key Functions:
- `generateSystemSheets()` - Creates all tracking sheets
- `syncSmallGroupProgress()` - Syncs lesson data to UFLI MAP
- `calculateBenchmark()` - Computes grade-level benchmarks with gateway logic
- `calculateSectionPercentage()` - Skill section calculations with review lesson handling
- `calculatePreKScores()` - HWT Pre-K score calculations

Constants Defined:
- `SHEET_NAMES_V2` - System sheet names (UFLI MAP, Grade Summary, etc.)
- `LESSON_LABELS` - All 128 UFLI lesson names
- `SKILL_SECTIONS` - Lesson groupings by skill category
- `REVIEW_LESSONS` - Gateway/review lesson numbers
- `GRADE_METRICS` - Grade-specific benchmark configurations

### 3. TutoringSystem.gs
**Purpose:** Dual-track progress for whole-group vs. tutoring interventions

Key Functions:
- `isTutoringGroup()` - Detects tutoring groups by name
- `categorizeTutoringLesson()` - Categorizes lessons (UFLI Reteach, Comprehension, Other)
- `saveTutoringData()` - Saves to both Small Group Progress and Tutoring Log
- `syncTutoringProgress()` - Aggregates tutoring data per student
- `sendWeeklyUnenrolledReport()` - Emails weekly exception reports

Sheets Created:
- **Tutoring Progress Log** - Raw tutoring session data
- **Tutoring Summary** - Per-student intervention metrics
- **Unenrolled Log** - Exception tracking

### 4. MixedGradeSupport_Enhanced.gs
**Purpose:** Support for schools combining grades in skill-based groups

Key Functions:
- `getSheetNameForGrade()` - Maps grade to appropriate sheet
- `getSheetNameForGroup()` - Finds sheet containing a group
- `getGroupsForForm_MixedGrade()` - Gets all groups for lesson entry dropdown
- `getLessonsAndStudentsForGroup_MixedGrade()` - Retrieves group data

Supports Two Formats:
- **STANDARD** - Group header in column A (wizard-created sheets)
- **SANKOFA** - Group name in column D with "Student Name" header rows

### 5. UnenrollmentAutomation.gs
**Purpose:** Automated workflow when students unenroll

Key Functions:
- `createMondayTask()` - Creates task in Monday.com board
- `archiveStudent()` - Archives student data from all tracking sheets
- `processUnenrolledStudents()` - Batch processes unenrollment queue

Features:
- Monday.com API integration
- Complete data archival (3 rows per student)
- Audit logging

### 6. AdminImport_v1.gs
**Purpose:** Historical data import with validation

Key Functions:
- `showImportDialog()` - Opens import UI
- `importCsvToStaging()` - Parses and stages import data
- `validateImportData()` - Validates before commit
- `processImportData()` - Commits staged data to system

Import Types:
- **Initial Assessment - Grid Format** - UFLI MAP-like layout
- **Initial Assessment - Row Format** - One row per lesson entry
- **Lesson Progress** - Updates UFLI MAP only

### 7. Support Utilities

**MissingStudents.gs:**
- `highlightAndCreateExceptionReport()` - Cross-validates students between Initial Assessment and Group sheets

**Utilities.gs:**
- `syncGroupNamesFromSheets()` - Syncs group names from Grade sheets to Summary sheets

**studentrecon.gs:**
- `generateExceptionReport()` - Validates counts vs Config, School Summary, Grade Summary
- `updateGroupConfigurationCounts()` - Updates config with actual counts
- `highlightDuplicates()` - Finds students in multiple groups

---

## Sheet Structure

### Configuration Sheets
| Sheet Name | Purpose |
|------------|---------|
| Site Configuration | School name, grades served, grade mixing settings |
| Student Roster | Master student list with grade, teacher, group |
| Teacher Roster | Teachers and their assigned grades |
| Group Configuration | Groups per grade with student counts |
| Feature Settings | Optional feature toggles |

### Tracking Sheets (K-8)
| Sheet Name | Purpose |
|------------|---------|
| UFLI MAP | Master progress grid - student × 128 lessons |
| Initial Assessment | Baseline assessment data (static after setup) |
| Grade Summary | Per-student metrics (Foundational %, Min Grade %, Full Grade %) |
| Skills Tracker | Skill section breakdown per student |
| Small Group Progress | Raw lesson entry log |
| School Summary | School-wide metrics and group listings |

### Tracking Sheets (Pre-K)
| Sheet Name | Purpose |
|------------|---------|
| Pre-K Data | Letter knowledge tracking (Name, Sound, Form per letter) |

### Tutoring Sheets
| Sheet Name | Purpose |
|------------|---------|
| Tutoring Progress Log | Raw tutoring session data |
| Tutoring Summary | Per-student intervention metrics |
| Unenrolled Log | Exception tracking for unenrolled students |

### Grade-Level Group Sheets
| Sheet Name | Purpose |
|------------|---------|
| PreK Groups, KG Groups, G1-G8 Groups | Student groupings with rolling lesson windows |

### Support Sheets
| Sheet Name | Purpose |
|------------|---------|
| Student Archive | Archived data for unenrolled students |
| Exception Report | Data quality issues |
| Import Staging | Staging area for data imports |
| Import Exceptions | Import validation errors |

---

## Key Features

### 1. Benchmark Calculation System

The system uses a **gateway logic** for benchmark calculations:

```
For each skill section:
1. If review lesson(s) are ASSIGNED (Y or N) AND ALL passed → 100% section credit
2. Otherwise → Count actual Y's in non-review lessons

Blanks = Not assigned (ignored, not counted as failed)
```

**Grade Metrics:**
| Grade | Foundational | Minimum | Current Year |
|-------|-------------|---------|--------------|
| PreK | 26 letters | 26 letters | 26 letters |
| KG | L1-34 | L1-34 | L1-34 |
| G1 | L1-34 | L1-34 + Digraphs (44) | L35-62 (23) |
| G2 | L1-34 | L1-68 (56) | L38, L63-83 (18) |
| G3 | L1-34 | L1-68 (56) | All non-review (107) |
| G4-G8 | L1-34 | L1-110 (103) | All non-review (107) |

### 2. Skill Sections

16 skill categories mapping to UFLI lessons:

1. Single Consonants & Vowels (L1-34)
2. Blends (L25, L27)
3. Alphabet Review & Longer Words (L35-41)
4. Digraphs (L42-53)
5. VCE (L54-62)
6. Reading Longer Words (L63-68)
7. Ending Spelling Patterns (L69-76)
8. R-Controlled Vowels (L77-83)
9. Long Vowel Teams (L84-88)
10. Other Vowel Teams (L89-94)
11. Diphthongs (L95-97)
12. Silent Letters (L98)
13. Suffixes & Prefixes (L99-106)
14. Suffix Spelling Changes (L107-110)
15. Low Frequency Spellings (L111-118)
16. Additional Affixes (L119-128)

### 3. Pre-K Handwriting Without Tears Tracking

Three metrics per student:
- **Foundational (Form):** Motor integration - `/26 letters`
- **Min Grade (Name + Sound):** Literacy knowledge - `/52`
- **Full Grade (All):** K-readiness - `/78`

### 4. Status Codes

| Code | Meaning | Color |
|------|---------|-------|
| Y | Yes/Pass | Green (#d4edda) |
| N | No/Fail | Red (#f8d7da) |
| A | Absent | Yellow (#fff3cd) |
| U | Unenrolled | Triggers archival workflow |

### 5. Data Routing

The `saveLessonData()` function routes based on:
1. **Grade = "PreK"** → `savePreKData()` (Pre-K Data matrix)
2. **Group name contains "Tutoring"** → `saveTutoringData()` (Both logs)
3. **Otherwise** → `saveStandardUFLIData()` (Small Group Progress → UFLI MAP)

### 6. Performance Architecture (Deferred Sync)

To improve teacher experience, lesson saves use a **deferred sync** pattern:

```
Teacher Submits Lesson Check (~3-4 seconds total)
        │
        ├── 1. Append to "Small Group Progress"     [~1 sec]
        │      └── Raw log of all lesson entries
        │
        ├── 2. Update Grade Group Sheet             [~2-3 sec]
        │      └── Teachers see this immediately
        │
        └── 3. Queue UFLI MAP Update                [~0.5 sec]
               └── Added to "Sync Queue" sheet
                          │
                          ▼
              ┌─────────────────────────┐
              │  Every 60 min trigger   │
              │  processSyncQueue()     │
              │  └── Batch update UFLI  │
              └─────────────────────────┘
```

**Why this matters:**
- Previous save time: ~16 seconds (teachers waiting)
- New save time: ~3-4 seconds (teachers happy)
- UFLI MAP updates within 60 minutes automatically

**Sync Queue Sheet Columns:**
| Column | Content |
|--------|---------|
| Timestamp | When the lesson was submitted |
| Group Name | The group that was taught |
| Lesson Name | e.g., "UFLI L42" |
| Lesson # | Extracted number (42) |
| Student Data | JSON array of {name, status} |
| Processed | Timestamp when processed |

---

## Setup & Configuration

### Initial Setup

1. **Run Setup Wizard:**
   - Open spreadsheet → Menu: `Adira Reads Progress Report` → `🚀 Start Setup Wizard`

2. **Configure School:**
   - Enter school name
   - Select grades served
   - Configure grade mixing if applicable

3. **Add Students:**
   - Import from CSV or add manually
   - Assign to grades and teachers

4. **Create Groups:**
   - Define groups per grade
   - Assign students to groups

5. **Generate System Sheets:**
   - Wizard creates all tracking sheets
   - Initial Assessment sheet populated

### Post-Setup Tasks

1. **Deploy Web App:**
   - Publish script as web app
   - Share URL with teachers for lesson entry

2. **Configure Triggers:**
   - Enable nightly sync: Menu → `Sync & Performance` → `Enable Nightly Sync`
   - Setup unenrolled report: Run `setupUnenrolledReportTrigger()`

3. **Monday.com Integration (Optional):**
   - Add `MONDAY_API_KEY` to Script Properties
   - Configure board/column IDs in `MONDAY_CONFIG`

---

## User Workflows

### Daily: Lesson Entry

1. Teacher opens web app (LessonEntryForm)
2. Selects their group from dropdown
3. Selects lesson being taught
4. Marks each student: Y (passed), N (not yet), A (absent), U (unenrolled)
5. Submits form → Data saved, UFLI MAP updated

### Weekly: Review Progress

1. Menu → `📊 View School Summary`
2. Review group progress
3. Menu → `📈 Generate Reports` for detailed reports

### As Needed: Student Management

1. Menu → `👥 Manage Students` (add/edit/remove)
2. Menu → `👨‍🏫 Manage Groups` (reassign students)

### Monthly: Data Quality

1. Run `generateExceptionReport()` to check discrepancies
2. Run `highlightAndCreateExceptionReport()` for missing students
3. Run `highlightDuplicates()` to find students in multiple groups

---

## Technical Reference

### Data Layout Constants

```javascript
const LAYOUT = {
  DATA_START_ROW: 6,           // First data row
  HEADER_ROW_COUNT: 5,         // Header rows
  LESSON_COLUMN_OFFSET: 5,     // Lessons start at column F
  TOTAL_LESSONS: 128,          // UFLI lessons
  COL_STUDENT_NAME: 1,         // Column A
  COL_GRADE: 2,                // Column B
  COL_TEACHER: 3,              // Column C
  COL_GROUP: 4,                // Column D
  COL_CURRENT_LESSON: 5,       // Column E
  COL_FIRST_LESSON: 6          // Column F
};
```

### Key Sheet Names

```javascript
const SHEET_NAMES_V2 = {
  SMALL_GROUP_PROGRESS: "Small Group Progress",
  UFLI_MAP: "UFLI MAP",
  SKILLS: "Skills Tracker",
  GRADE_SUMMARY: "Grade Summary",
  INITIAL_ASSESSMENT: "Initial Assessment",
  SCHOOL_SUMMARY: "School Summary"
};
```

### Menu Structure

```
Adira Reads Progress Report
├── 📊 View School Summary
├── 📈 Generate Reports
├── 👥 Manage Students
├── 👨‍🏫 Manage Groups
├── 🔄 Sync & Performance
│   ├── ⚡ Recalculate All Stats Now
│   ├── ▶️ Process UFLI MAP Queue Now
│   ├── ✅ Enable Hourly UFLI Sync
│   ├── ❌ Disable Hourly UFLI Sync
│   ├── ✅ Enable Nightly Full Sync
│   ├── ❌ Disable Nightly Full Sync
│   └── ℹ️ Check Sync Status
├── 📚 Tutoring
│   ├── 📋 View Tutoring Summary
│   ├── 📝 View Tutoring Log
│   └── 🔄 Sync Tutoring Data
├── 🛠️ Admin Tools
│   ├── 📂 Import Data...
│   ├── ✅ Validate Import
│   ├── 📦 Manual Archive Student
│   ├── 📄 View Archive
│   ├── 🔧 Repair All Formulas
│   ├── ⚠️ Fix Missing Teachers
│   └── 🎨 Repair Formatting
├── ⚙️ System Settings
└── 🔄 Re-run Setup Wizard
```

---

## File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `Setupwizard.gs` | ~2,600 | Core wizard, menu, web app, management |
| `Phase2_ProgressTracking.gs` | ~3,400 | Sheet generation, sync, calculations |
| `TutoringSystem.gs` | ~1,500 | Tutoring dual-track system |
| `MixedGradeSupport_Enhanced.gs` | ~1,900 | Multi-grade group support |
| `SyncQueueProcessor.gs` | ~350 | Deferred UFLI MAP sync for fast saves |
| `UnenrollmentAutomation.gs` | ~1,100 | Monday.com integration, archival |
| `AdminImport_v1.gs` | ~1,000 | Data import utility |
| `MissingStudents.gs` | ~200 | Cross-sheet validation |
| `Utilities.gs` | ~130 | Group name sync |
| `studentrecon.gs` | ~320 | Exception reports, duplicates |
| `SetUpWizardUI.html` | ~1,300 | Setup wizard interface |
| `ManageStudentUI.html` | ~1,500 | Student management interface |
| `ManageGroupsUI.html` | ~1,300 | Group management interface |
| `GenerateReportsUI.html` | ~1,400 | Report generation interface |
| `LessonEntryForm.html` | ~1,000 | Teacher lesson entry web app |

---

## License

This project is proprietary software developed for Christel House West Academy and The Indy Learning Team (TILT).

---

## Support

For issues or questions, contact: ckelley@theindylearningteam.org
