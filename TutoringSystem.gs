// ═══════════════════════════════════════════════════════════════════════════
// GLOBAL PREP - TUTORING TRACKING SYSTEM
// Dual-Track Progress: Whole Group UFLI vs. Tutoring Interventions
// ═══════════════════════════════════════════════════════════════════════════
// Version: 1.1
// Last Updated: January 2026
//
// PURPOSE:
// Students receive instruction in BOTH whole-group UFLI lessons AND smaller
// tutoring groups (reteach, comprehension, intervention). This module keeps
// those two tracks separate so:
//   - Whole Group progress feeds into UFLI MAP and benchmark calculations
//   - Tutoring progress is tracked separately for intervention monitoring
//   - Neither overwrites the other when the same lesson is taught in both contexts
//
// DETECTION LOGIC:
// - Group name contains "Tutoring" → Routes to Tutoring System
// - Group name does NOT contain "Tutoring" → Routes to Standard UFLI System
//
// NEW SHEETS CREATED:
// - "Tutoring Progress Log" - Raw data log (like Small Group Progress)
// - "Tutoring Summary" - Per-student intervention tracking with metrics
// - "Unenrolled Log" - Exception tracking for unenrolled students
//
// ═══════════════════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS - TUTORING SYSTEM
// ═══════════════════════════════════════════════════════════════════════════

const SHEET_NAMES_TUTORING = {
  PROGRESS_LOG: "Tutoring Progress Log",
  SUMMARY: "Tutoring Summary"
};

const TUTORING_LAYOUT = {
  DATA_START_ROW: 6,
  HEADER_ROW: 5,
  
  // Tutoring Progress Log columns
  LOG_COL_DATE: 1,
  LOG_COL_TEACHER: 2,
  LOG_COL_GROUP: 3,
  LOG_COL_STUDENT: 4,
  LOG_COL_LESSON_TYPE: 5,  // "UFLI Reteach", "Comprehension", etc.
  LOG_COL_LESSON_DETAIL: 6, // Specific lesson (e.g., "L42 reteach")
  LOG_COL_STATUS: 7,
  
  // Tutoring Summary columns
  SUM_COL_STUDENT: 1,
  SUM_COL_GRADE: 2,
  SUM_COL_PRIMARY_GROUP: 3,
  SUM_COL_TUTORING_GROUPS: 4,
  SUM_COL_TOTAL_SESSIONS: 5,
  SUM_COL_UFLI_RETEACH_COUNT: 6,
  SUM_COL_UFLI_RETEACH_PASS: 7,
  SUM_COL_COMPREHENSION_COUNT: 8,
  SUM_COL_COMPREHENSION_PASS: 9,
  SUM_COL_OTHER_COUNT: 10,
  SUM_COL_OTHER_PASS: 11,
  SUM_COL_OVERALL_PASS_RATE: 12,
  SUM_COL_LAST_SESSION: 13
};

const TUTORING_COLORS = {
  HEADER_BG: "#6a1b9a",      // Purple for tutoring distinction
  HEADER_FG: "#ffffff",
  TITLE_BG: "#e1bee7",       // Light purple
  TITLE_FG: "#000000",
  RETEACH_BG: "#fff3e0",     // Light orange for reteach
  COMPREHENSION_BG: "#e3f2fd", // Light blue for comprehension
  Y: "#c8e6c9",              // Light green
  N: "#ffcdd2",              // Light red
  A: "#fff9c4"               // Light yellow
};

// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS - UNENROLLED REPORTING SYSTEM
// ═══════════════════════════════════════════════════════════════════════════

const UNENROLLED_REPORT_CONFIG = {
  // Email recipients (comma-separated for multiple)
  recipientEmail: 'ckelley@theindylearningteam.org',
  
  // CC recipients (optional, leave empty string if none)
  ccEmail: '',
  
  // Report settings
  reportDayOfWeek: ScriptApp.WeekDay.MONDAY,  // Day to send report
  reportHour: 7,  // Hour to send (7 = 7 AM)
  
  // Sheet name for logging unenrolled students
  unenrolledLogSheetName: 'Unenrolled Log',
  
  // Include students from how many days back in the report
  reportLookbackDays: 7,
  
  // School name for email subject
  schoolName: 'Sankofa School of Success'
};

// ═══════════════════════════════════════════════════════════════════════════
// DETECTION UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Determines if a group is a tutoring group based on its name
 * @param {string} groupName - Name of the group
 * @returns {boolean} True if this is a tutoring group
 */
function isTutoringGroup(groupName) {
  if (!groupName) return false;
  return groupName.toString().toLowerCase().includes("tutoring");
}

/**
 * Categorizes a lesson for tutoring tracking
 * @param {string} lessonName - The lesson name (e.g., "UFLI L42 reteach", "Comprehension")
 * @returns {Object} {type: "UFLI Reteach"|"Comprehension"|"Other", lessonNum: number|null}
 */
function categorizeTutoringLesson(lessonName) {
  if (!lessonName) return { type: "Other", lessonNum: null };
  
  const lessonStr = lessonName.toString().toLowerCase().trim();
  
  // Check for Comprehension
  if (lessonStr.includes("comprehension")) {
    return { type: "Comprehension", lessonNum: null };
  }
  
  // Check for UFLI lesson (with or without "reteach")
  const ufliMatch = lessonStr.match(/(?:ufli\s*)?l\s*(\d+)/i);
  if (ufliMatch) {
    const lessonNum = parseInt(ufliMatch[1], 10);
    const isReteach = lessonStr.includes("reteach");
    return { 
      type: isReteach ? "UFLI Reteach" : "UFLI New", 
      lessonNum: lessonNum 
    };
  }
  
  return { type: "Other", lessonNum: null };
}

/**
 * Gets the primary (non-tutoring) group for a student
 * @param {string} studentName - Student name
 * @returns {string} Primary group name or empty string
 */
function getPrimaryGroupForStudent(studentName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const rosterSheet = ss.getSheetByName(SHEET_NAMES.STUDENT_ROSTER);
  
  if (!rosterSheet) return "";
  
  const data = rosterSheet.getDataRange().getValues();
  for (let i = LAYOUT.DATA_START_ROW - 1; i < data.length; i++) {
    if (data[i][0] && data[i][0].toString().trim() === studentName) {
      return data[i][3] ? data[i][3].toString() : "";
    }
  }
  return "";
}

// ═══════════════════════════════════════════════════════════════════════════
// SHEET CREATION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Creates all tutoring system sheets
 * Call this from your setup wizard or run manually
 */
function createTutoringSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  createTutoringProgressLogSheet(ss);
  createTutoringSummarySheet(ss);
  
  Logger.log("Tutoring sheets created successfully.");
}

/**
 * Creates the Tutoring Progress Log sheet
 * @param {Spreadsheet} ss - Active spreadsheet
 */
function createTutoringProgressLogSheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAMES_TUTORING.PROGRESS_LOG);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAMES_TUTORING.PROGRESS_LOG);
  } else {
    sheet.clear();
    sheet.clearConditionalFormatRules();
  }
  
  // Title row
  sheet.getRange(1, 1, 1, 7).merge()
    .setValue("TUTORING PROGRESS LOG")
    .setBackground(TUTORING_COLORS.TITLE_BG)
    .setFontColor(TUTORING_COLORS.TITLE_FG)
    .setFontWeight("bold")
    .setFontSize(14)
    .setFontFamily("Calibri");
  
  // Subtitle
  sheet.getRange(2, 1, 1, 7).merge()
    .setValue("Tracks all tutoring/intervention sessions separately from whole-group UFLI instruction")
    .setFontFamily("Calibri")
    .setFontSize(10)
    .setFontStyle("italic");
  
  // Headers
  const headers = ["Date", "Teacher", "Tutoring Group", "Student Name", "Lesson Type", "Lesson Detail", "Status"];
  sheet.getRange(TUTORING_LAYOUT.HEADER_ROW, 1, 1, headers.length)
    .setValues([headers])
    .setBackground(TUTORING_COLORS.HEADER_BG)
    .setFontColor(TUTORING_COLORS.HEADER_FG)
    .setFontWeight("bold")
    .setFontFamily("Calibri");
  
  // Column widths
  sheet.setColumnWidth(1, 100);  // Date
  sheet.setColumnWidth(2, 150);  // Teacher
  sheet.setColumnWidth(3, 200);  // Tutoring Group
  sheet.setColumnWidth(4, 180);  // Student Name
  sheet.setColumnWidth(5, 120);  // Lesson Type
  sheet.setColumnWidth(6, 150);  // Lesson Detail
  sheet.setColumnWidth(7, 70);   // Status
  
  sheet.setFrozenRows(TUTORING_LAYOUT.HEADER_ROW);
  
  // Conditional formatting for status column
  applyTutoringStatusFormatting(sheet);
}

/**
 * Creates the Tutoring Summary sheet
 * @param {Spreadsheet} ss - Active spreadsheet
 */
function createTutoringSummarySheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAMES_TUTORING.SUMMARY);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAMES_TUTORING.SUMMARY);
  } else {
    sheet.clear();
    sheet.clearConditionalFormatRules();
  }
  
  // Title row
  sheet.getRange(1, 1, 1, 13).merge()
    .setValue("TUTORING SUMMARY - INTERVENTION TRACKING")
    .setBackground(TUTORING_COLORS.TITLE_BG)
    .setFontColor(TUTORING_COLORS.TITLE_FG)
    .setFontWeight("bold")
    .setFontSize(14)
    .setFontFamily("Calibri");
  
  // Subtitle
  sheet.getRange(2, 1, 1, 13).merge()
    .setValue("Aggregated view of tutoring interventions by student (updates automatically when you sync)")
    .setFontFamily("Calibri")
    .setFontSize(10)
    .setFontStyle("italic");
  
  // Headers
  const headers = [
    "Student Name", 
    "Grade", 
    "Primary Group",
    "Tutoring Group(s)",
    "Total Sessions",
    "UFLI Reteach #",
    "Reteach Pass %",
    "Comprehension #",
    "Comp. Pass %",
    "Other #",
    "Other Pass %",
    "Overall Pass %",
    "Last Session"
  ];
  
  sheet.getRange(TUTORING_LAYOUT.HEADER_ROW, 1, 1, headers.length)
    .setValues([headers])
    .setBackground(TUTORING_COLORS.HEADER_BG)
    .setFontColor(TUTORING_COLORS.HEADER_FG)
    .setFontWeight("bold")
    .setFontFamily("Calibri")
    .setWrap(true);
  
  // Column widths
  sheet.setColumnWidth(1, 180);  // Student Name
  sheet.setColumnWidth(2, 60);   // Grade
  sheet.setColumnWidth(3, 150);  // Primary Group
  sheet.setColumnWidth(4, 200);  // Tutoring Groups
  sheet.setColumnWidth(5, 90);   // Total Sessions
  sheet.setColumnWidth(6, 100);  // UFLI Reteach #
  sheet.setColumnWidth(7, 100);  // Reteach Pass %
  sheet.setColumnWidth(8, 110);  // Comprehension #
  sheet.setColumnWidth(9, 100);  // Comp Pass %
  sheet.setColumnWidth(10, 80);  // Other #
  sheet.setColumnWidth(11, 90);  // Other Pass %
  sheet.setColumnWidth(12, 100); // Overall Pass %
  sheet.setColumnWidth(13, 100); // Last Session
  
  sheet.setFrozenRows(TUTORING_LAYOUT.HEADER_ROW);
  sheet.setRowHeight(TUTORING_LAYOUT.HEADER_ROW, 40);
}

/**
 * Applies conditional formatting for status column in tutoring log
 * @param {Sheet} sheet - Tutoring Progress Log sheet
 */
function applyTutoringStatusFormatting(sheet) {
  const statusCol = TUTORING_LAYOUT.LOG_COL_STATUS;
  const range = sheet.getRange(TUTORING_LAYOUT.DATA_START_ROW, statusCol, 1000, 1);
  
  const rules = [
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo('Y')
      .setBackground(TUTORING_COLORS.Y)
      .setRanges([range])
      .build(),
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo('N')
      .setBackground(TUTORING_COLORS.N)
      .setRanges([range])
      .build(),
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo('A')
      .setBackground(TUTORING_COLORS.A)
      .setRanges([range])
      .build()
  ];
  
  sheet.setConditionalFormatRules(rules);
}

// ═══════════════════════════════════════════════════════════════════════════
// UNENROLLED STUDENT LOGGING
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Logs unenrolled students to the tracking sheet
 * Called from save functions when students are marked as 'U'
 * 
 * @param {Object} data - Unenrollment data
 * @param {string} data.studentName - Name of the unenrolled student
 * @param {string} data.groupName - Group the student was in
 * @param {string} data.gradeSheet - Grade level sheet name
 * @param {string} data.teacherName - Teacher who reported the unenrollment
 * @param {string} data.lessonName - Lesson when unenrollment was noted
 */
function logUnenrolledStudent(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let logSheet = ss.getSheetByName(UNENROLLED_REPORT_CONFIG.unenrolledLogSheetName);
  
  // Create the log sheet if it doesn't exist
  if (!logSheet) {
    logSheet = createUnenrolledLogSheet_(ss);
  }
  
  // Add the log entry
  const timestamp = new Date();
  const newRow = [
    timestamp,                          // A: Timestamp
    data.studentName,                   // B: Student Name
    data.gradeSheet || '',              // C: Grade/Sheet
    data.groupName,                     // D: Group Name
    data.teacherName,                   // E: Reported By
    data.lessonName || '',              // F: Lesson (when noted)
    'Pending',                          // G: Status (Pending/Confirmed/Resolved)
    ''                                  // H: Notes
  ];
  
  logSheet.appendRow(newRow);
  
  // Format the new row
  const lastRow = logSheet.getLastRow();
  logSheet.getRange(lastRow, 1).setNumberFormat('MM/dd/yyyy HH:mm');
  
  return { success: true, message: 'Unenrollment logged' };
}

/**
 * Creates the Unenrolled Log sheet with proper headers and formatting
 * @private
 */
function createUnenrolledLogSheet_(ss) {
  const sheet = ss.insertSheet(UNENROLLED_REPORT_CONFIG.unenrolledLogSheetName);
  
  // Set up headers
  const headers = [
    'Date Reported',
    'Student Name',
    'Grade/Sheet',
    'Group',
    'Reported By',
    'Lesson',
    'Status',
    'Notes'
  ];
  
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // Format header row
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange
    .setBackground('#98D4BB')
    .setFontWeight('bold')
    .setFontFamily('Calibri')
    .setHorizontalAlignment('center');
  
  // Set column widths
  sheet.setColumnWidth(1, 140);  // Date
  sheet.setColumnWidth(2, 180);  // Student Name
  sheet.setColumnWidth(3, 120);  // Grade
  sheet.setColumnWidth(4, 180);  // Group
  sheet.setColumnWidth(5, 140);  // Reported By
  sheet.setColumnWidth(6, 100);  // Lesson
  sheet.setColumnWidth(7, 100);  // Status
  sheet.setColumnWidth(8, 250);  // Notes
  
  // Add data validation for Status column
  const statusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['Pending', 'Confirmed', 'Resolved', 'Error'], true)
    .build();
  sheet.getRange(2, 7, 500, 1).setDataValidation(statusRule);
  
  // Freeze header row
  sheet.setFrozenRows(1);
  
  return sheet;
}

// ═══════════════════════════════════════════════════════════════════════════
// SAVE FUNCTION - MASTER ROUTER
// ═══════════════════════════════════════════════════════════════════════════

// NOTE: The main saveLessonData() function is now in Setupwizard.gs
// It routes to saveTutoringData() below for tutoring groups.
// The duplicate here has been removed to avoid conflicts.

/**
 * Saves Pre-K data directly to the Pre-K Data matrix
 * @param {Object} formObject
 * @returns {Object}
 */
function savePreKData(formObject) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const { groupName, lessonName, teacherName, studentStatuses } = formObject;
  
  const sheet = ss.getSheetByName(SHEET_NAMES_PREK.DATA);
  if (!sheet) throw new Error(`Sheet '${SHEET_NAMES_PREK.DATA}' not found.`);
  
  const data = sheet.getDataRange().getValues();
  const headers = data[PREK_CONFIG.HEADER_ROW - 1];
  
  const colIndex = headers.indexOf(lessonName);
  if (colIndex === -1) throw new Error(`Column '${lessonName}' not found in Pre-K Data.`);
  
  studentStatuses.forEach(entry => {
    for (let i = PREK_CONFIG.DATA_START_ROW - 1; i < data.length; i++) {
      if (data[i][0] === entry.name) {
        sheet.getRange(i + 1, colIndex + 1).setValue(entry.status);
        break;
      }
    }
  });
  
  // ═══════════════════════════════════════════════════════════
  // Log unenrolled students (PreK)
  // ═══════════════════════════════════════════════════════════
  if (formObject.unenrolledStudents && formObject.unenrolledStudents.length > 0) {
    formObject.unenrolledStudents.forEach(function(studentName) {
      logUnenrolledStudent({
        studentName: studentName,
        groupName: groupName,
        gradeSheet: 'PreK',
        teacherName: teacherName,
        lessonName: lessonName
      });
    });
  }
  
  return { success: true, message: "Pre-K Data Saved Successfully!" };
}

/**
 * Saves tutoring data to BOTH systems:
 *   1. Small Group Progress → syncs to UFLI MAP (master progress)
 *   2. Tutoring Progress Log → syncs to Tutoring Summary (intervention tracking)
 * 
 * @param {Object} formObject - {groupName, lessonName, teacherName, studentStatuses, unenrolledStudents, gradeSheet}
 * @returns {Object} - {success: boolean, message: string}
 */
function saveTutoringData(formObject) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const { groupName, lessonName, teacherName, studentStatuses } = formObject;
  
  const timestamp = new Date();
  const lessonInfo = categorizeTutoringLesson(lessonName);
  
  // ═══════════════════════════════════════════════════════════════
  // PART 1: Write to Small Group Progress (feeds UFLI MAP)
  // ═══════════════════════════════════════════════════════════════
  const progressSheet = ss.getSheetByName(SHEET_NAMES_V2.SMALL_GROUP_PROGRESS);
  if (progressSheet) {
    const progressRows = studentStatuses.map(s => [
      timestamp,
      teacherName,
      groupName,
      s.name,
      lessonName,
      s.status
    ]);
    
    if (progressRows.length > 0) {
      const startRow = progressSheet.getLastRow() + 1;
      progressSheet.getRange(startRow, 1, progressRows.length, 6).setValues(progressRows);
    }
  }
  
  // ═══════════════════════════════════════════════════════════════
  // PART 2: Write to Tutoring Progress Log (intervention tracking)
  // ═══════════════════════════════════════════════════════════════
  let logSheet = ss.getSheetByName(SHEET_NAMES_TUTORING.PROGRESS_LOG);
  if (!logSheet) {
    createTutoringSheets();
    logSheet = ss.getSheetByName(SHEET_NAMES_TUTORING.PROGRESS_LOG);
  }
  
  const tutoringRows = studentStatuses.map(s => [
    timestamp,
    teacherName,
    groupName,
    s.name,
    lessonInfo.type,           // "UFLI Reteach", "Comprehension", "Other"
    lessonName,                // Full lesson detail
    s.status
  ]);
  
  if (tutoringRows.length > 0) {
    const startRow = logSheet.getLastRow() + 1;
    logSheet.getRange(startRow, 1, tutoringRows.length, 7).setValues(tutoringRows);
  }
  
  // ═══════════════════════════════════════════════════════════════
  // PART 3: Sync to update UFLI MAP and all related sheets
  // ═══════════════════════════════════════════════════════════════
  syncSmallGroupProgress();
  
  // ═══════════════════════════════════════════════════════════════
  // Log unenrolled students (Tutoring)
  // ═══════════════════════════════════════════════════════════════
  if (formObject.unenrolledStudents && formObject.unenrolledStudents.length > 0) {
    formObject.unenrolledStudents.forEach(function(studentName) {
      logUnenrolledStudent({
        studentName: studentName,
        groupName: groupName,
        gradeSheet: formObject.gradeSheet || 'Tutoring',
        teacherName: teacherName,
        lessonName: lessonName
      });
    });
  }
  
  Logger.log(`Saved ${studentStatuses.length} tutoring entries for group: ${groupName} (UFLI MAP + Tutoring Log)`);
  
  return { 
    success: true, 
    message: `Tutoring data saved! ${studentStatuses.length} student(s) recorded for ${lessonName}. Updated UFLI MAP and Tutoring Log.`
  };
}

/**
 * @deprecated This function is no longer used.
 * Standard UFLI saves now go through saveLessonData() in Setupwizard.gs
 * which uses the optimized deferred sync queue.
 * Kept for reference only - do not call directly.
 */
function saveStandardUFLIData_DEPRECATED(formObject) {
  // This function used the slow syncSmallGroupProgress() approach.
  // The new approach in Setupwizard.gs uses addToSyncQueue() for deferred processing.
  Logger.log("WARNING: saveStandardUFLIData_DEPRECATED was called - this should not happen");
  return { success: false, message: "This function is deprecated. Use saveLessonData() in Setupwizard.gs" };
}

// ═══════════════════════════════════════════════════════════════════════════
// SYNC TUTORING DATA
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Syncs Tutoring Progress Log to Tutoring Summary
 * Aggregates all tutoring sessions per student
 */
function syncTutoringProgress() {
  const functionName = 'syncTutoringProgress';
  Logger.log(`[${functionName}] Starting tutoring sync...`);
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  const logSheet = ss.getSheetByName(SHEET_NAMES_TUTORING.PROGRESS_LOG);
  const summarySheet = ss.getSheetByName(SHEET_NAMES_TUTORING.SUMMARY);
  
  if (!logSheet || !summarySheet) {
    Logger.log(`[${functionName}] Tutoring sheets not found. Creating...`);
    createTutoringSheets();
    return;
  }
  
  // Read all tutoring log data
  const lastRow = logSheet.getLastRow();
  if (lastRow < TUTORING_LAYOUT.DATA_START_ROW) {
    Logger.log(`[${functionName}] No tutoring data to sync.`);
    return;
  }
  
  const logData = logSheet.getRange(
    TUTORING_LAYOUT.DATA_START_ROW, 1, 
    lastRow - TUTORING_LAYOUT.DATA_START_ROW + 1, 7
  ).getValues();
  
  // Aggregate by student
  const studentStats = {};
  
  logData.forEach(row => {
    const [date, teacher, group, studentName, lessonType, lessonDetail, status] = row;
    
    if (!studentName) return;
    
    const key = studentName.toString().trim();
    
    if (!studentStats[key]) {
      studentStats[key] = {
        name: key,
        tutoringGroups: new Set(),
        totalSessions: 0,
        ufliReteach: { count: 0, pass: 0 },
        comprehension: { count: 0, pass: 0 },
        other: { count: 0, pass: 0 },
        lastSession: null
      };
    }
    
    const stats = studentStats[key];
    stats.tutoringGroups.add(group);
    stats.totalSessions++;
    
    // Track by lesson type
    const statusUpper = status ? status.toString().toUpperCase() : "";
    const isPass = statusUpper === "Y";
    const isAttempt = statusUpper === "Y" || statusUpper === "N";
    
    if (lessonType === "UFLI Reteach" || lessonType === "UFLI New") {
      if (isAttempt) stats.ufliReteach.count++;
      if (isPass) stats.ufliReteach.pass++;
    } else if (lessonType === "Comprehension") {
      if (isAttempt) stats.comprehension.count++;
      if (isPass) stats.comprehension.pass++;
    } else {
      if (isAttempt) stats.other.count++;
      if (isPass) stats.other.pass++;
    }
    
    // Track most recent session
    const sessionDate = new Date(date);
    if (!isNaN(sessionDate) && (!stats.lastSession || sessionDate > stats.lastSession)) {
      stats.lastSession = sessionDate;
    }
  });
  
  // Get student grade and primary group info from roster
  const rosterSheet = ss.getSheetByName(SHEET_NAMES.STUDENT_ROSTER);
  const rosterData = rosterSheet ? rosterSheet.getDataRange().getValues() : [];
  const rosterMap = {};
  
  for (let i = LAYOUT.DATA_START_ROW - 1; i < rosterData.length; i++) {
    const name = rosterData[i][0] ? rosterData[i][0].toString().trim() : "";
    if (name) {
      rosterMap[name] = {
        grade: rosterData[i][1] || "",
        primaryGroup: rosterData[i][3] || ""
      };
    }
  }
  
  // Build output rows
  const outputRows = Object.values(studentStats).map(stats => {
    const rosterInfo = rosterMap[stats.name] || { grade: "", primaryGroup: "" };
    
    const totalAttempts = stats.ufliReteach.count + stats.comprehension.count + stats.other.count;
    const totalPass = stats.ufliReteach.pass + stats.comprehension.pass + stats.other.pass;
    
    return [
      stats.name,
      rosterInfo.grade,
      rosterInfo.primaryGroup,
      Array.from(stats.tutoringGroups).join(", "),
      stats.totalSessions,
      stats.ufliReteach.count,
      stats.ufliReteach.count > 0 ? stats.ufliReteach.pass / stats.ufliReteach.count : "",
      stats.comprehension.count,
      stats.comprehension.count > 0 ? stats.comprehension.pass / stats.comprehension.count : "",
      stats.other.count,
      stats.other.count > 0 ? stats.other.pass / stats.other.count : "",
      totalAttempts > 0 ? totalPass / totalAttempts : "",
      stats.lastSession
    ];
  });
  
  // Sort by grade then name
  outputRows.sort((a, b) => {
    const gradeCompare = (a[1] || "").localeCompare(b[1] || "");
    if (gradeCompare !== 0) return gradeCompare;
    return (a[0] || "").localeCompare(b[0] || "");
  });
  
  // Write to summary sheet
  if (outputRows.length > 0) {
    // Clear existing data
    const lastSummaryRow = summarySheet.getLastRow();
    if (lastSummaryRow >= TUTORING_LAYOUT.DATA_START_ROW) {
      summarySheet.getRange(
        TUTORING_LAYOUT.DATA_START_ROW, 1, 
        lastSummaryRow - TUTORING_LAYOUT.DATA_START_ROW + 1, 13
      ).clearContent();
    }
    
    // Write new data
    summarySheet.getRange(
      TUTORING_LAYOUT.DATA_START_ROW, 1, 
      outputRows.length, outputRows[0].length
    ).setValues(outputRows);
    
    // Format percentage columns
    const pctCols = [7, 9, 11, 12]; // Reteach %, Comp %, Other %, Overall %
    pctCols.forEach(col => {
      summarySheet.getRange(TUTORING_LAYOUT.DATA_START_ROW, col, outputRows.length, 1)
        .setNumberFormat("0%");
    });
    
    // Format date column
    summarySheet.getRange(TUTORING_LAYOUT.DATA_START_ROW, 13, outputRows.length, 1)
      .setNumberFormat("yyyy-mm-dd");
  }
  
  Logger.log(`[${functionName}] Synced ${outputRows.length} students to Tutoring Summary.`);
}

// ═══════════════════════════════════════════════════════════════════════════
// COMBINED SYNC - UPDATES BOTH SYSTEMS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Master sync function - updates both UFLI and Tutoring systems
 * Call this from the menu or after data entry
 */
function syncAllProgress() {
  const functionName = 'syncAllProgress';
  Logger.log(`[${functionName}] Starting full sync...`);
  
  // Sync standard UFLI progress
  syncSmallGroupProgress();
  
  // Sync tutoring progress
  syncTutoringProgress();
  
  Logger.log(`[${functionName}] Full sync complete.`);
  
  SpreadsheetApp.getUi().alert(
    'Sync Complete', 
    'Both UFLI and Tutoring progress data have been synced.', 
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// WEEKLY UNENROLLED EXCEPTION REPORT
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generates and sends the weekly unenrolled student exception report
 * This is called by the weekly trigger
 */
function sendWeeklyUnenrolledReport() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const logSheet = ss.getSheetByName(UNENROLLED_REPORT_CONFIG.unenrolledLogSheetName);
  
  // If no log sheet exists, nothing to report
  if (!logSheet) {
    Logger.log('No unenrolled log sheet found - skipping report');
    return;
  }
  
  // Get data from the lookback period
  const lookbackDate = new Date();
  lookbackDate.setDate(lookbackDate.getDate() - UNENROLLED_REPORT_CONFIG.reportLookbackDays);
  
  const data = logSheet.getDataRange().getValues();
  const headers = data[0];
  
  // Filter to entries within the lookback period
  const recentEntries = [];
  const pendingEntries = [];
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const timestamp = row[0];
    const status = row[6];
    
    // Check if within lookback period
    if (timestamp instanceof Date && timestamp >= lookbackDate) {
      recentEntries.push({
        date: timestamp,
        studentName: row[1],
        grade: row[2],
        group: row[3],
        reportedBy: row[4],
        lesson: row[5],
        status: row[6],
        notes: row[7],
        rowNumber: i + 1
      });
    }
    
    // Also collect all pending entries (regardless of date)
    if (status === 'Pending') {
      pendingEntries.push({
        date: timestamp,
        studentName: row[1],
        grade: row[2],
        group: row[3],
        reportedBy: row[4],
        rowNumber: i + 1
      });
    }
  }
  
  // Generate the email
  const emailContent = generateReportEmail_(recentEntries, pendingEntries, ss.getUrl());
  
  // Send the email
  const subject = `[${UNENROLLED_REPORT_CONFIG.schoolName}] Weekly Unenrolled Students Report - ${formatDate_(new Date())}`;
  
  const options = {
    htmlBody: emailContent,
    name: 'TILT Progress Tracking System'
  };
  
  if (UNENROLLED_REPORT_CONFIG.ccEmail) {
    options.cc = UNENROLLED_REPORT_CONFIG.ccEmail;
  }
  
  MailApp.sendEmail(
    UNENROLLED_REPORT_CONFIG.recipientEmail,
    subject,
    'Please view this email in an HTML-capable email client.',
    options
  );
  
  Logger.log(`Weekly unenrolled report sent to ${UNENROLLED_REPORT_CONFIG.recipientEmail}`);
}

/**
 * Generates the HTML email content for the report
 * @private
 */
function generateReportEmail_(recentEntries, pendingEntries, sheetUrl) {
  const reportDate = formatDate_(new Date());
  const lookbackDays = UNENROLLED_REPORT_CONFIG.reportLookbackDays;
  
  let html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      font-family: Calibri, 'Segoe UI', Arial, sans-serif;
      line-height: 1.6;
      color: #2D3748;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    .header {
      background: linear-gradient(135deg, #98D4BB 0%, #7BC4A6 100%);
      padding: 24px;
      border-radius: 12px;
      margin-bottom: 24px;
      text-align: center;
    }
    .header h1 {
      color: white;
      margin: 0;
      font-size: 24px;
      text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .header p {
      color: rgba(255,255,255,0.9);
      margin: 8px 0 0 0;
      font-size: 14px;
    }
    .summary-box {
      display: flex;
      gap: 16px;
      margin-bottom: 24px;
    }
    .summary-card {
      flex: 1;
      background: #F7FAFC;
      border-radius: 8px;
      padding: 16px;
      text-align: center;
      border-left: 4px solid #98D4BB;
    }
    .summary-card.warning {
      border-left-color: #ED8936;
    }
    .summary-card h3 {
      margin: 0;
      font-size: 32px;
      color: #2D3748;
    }
    .summary-card p {
      margin: 4px 0 0 0;
      font-size: 13px;
      color: #718096;
    }
    .section {
      margin-bottom: 24px;
    }
    .section h2 {
      font-size: 18px;
      color: #2D3748;
      border-bottom: 2px solid #98D4BB;
      padding-bottom: 8px;
      margin-bottom: 16px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th {
      background: #98D4BB;
      color: white;
      padding: 12px 8px;
      text-align: left;
      font-weight: 600;
    }
    td {
      padding: 10px 8px;
      border-bottom: 1px solid #E2E8F0;
    }
    tr:nth-child(even) {
      background: #F7FAFC;
    }
    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }
    .status-pending {
      background: #FEEBC8;
      color: #C05621;
    }
    .status-confirmed {
      background: #C6F6D5;
      color: #22543D;
    }
    .status-resolved {
      background: #E2E8F0;
      color: #4A5568;
    }
    .empty-state {
      text-align: center;
      padding: 32px;
      color: #718096;
      background: #F7FAFC;
      border-radius: 8px;
    }
    .empty-state p {
      margin: 0;
    }
    .footer {
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid #E2E8F0;
      font-size: 12px;
      color: #718096;
      text-align: center;
    }
    .action-link {
      display: inline-block;
      background: #98D4BB;
      color: white;
      padding: 10px 24px;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 600;
      margin-top: 16px;
    }
    .action-link:hover {
      background: #7BC4A6;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>📋 Unenrolled Students Report</h1>
    <p>${UNENROLLED_REPORT_CONFIG.schoolName} • Week of ${reportDate}</p>
  </div>
  
  <table style="width:100%;border:none;margin-bottom:24px;">
    <tr>
      <td style="width:50%;padding:8px;border:none;">
        <div style="background:#F7FAFC;border-radius:8px;padding:16px;text-align:center;border-left:4px solid #98D4BB;">
          <div style="font-size:32px;font-weight:bold;color:#2D3748;">${recentEntries.length}</div>
          <div style="font-size:13px;color:#718096;">New This Week</div>
        </div>
      </td>
      <td style="width:50%;padding:8px;border:none;">
        <div style="background:#F7FAFC;border-radius:8px;padding:16px;text-align:center;border-left:4px solid #ED8936;">
          <div style="font-size:32px;font-weight:bold;color:#2D3748;">${pendingEntries.length}</div>
          <div style="font-size:13px;color:#718096;">Total Pending Review</div>
        </div>
      </td>
    </tr>
  </table>
`;

  // New entries this week section
  html += `
  <div class="section">
    <h2>🆕 New Unenrollments This Week</h2>
`;

  if (recentEntries.length === 0) {
    html += `
    <div class="empty-state">
      <p>✅ No new unenrollments reported in the last ${lookbackDays} days.</p>
    </div>
`;
  } else {
    html += `
    <table>
      <tr>
        <th>Date</th>
        <th>Student Name</th>
        <th>Grade</th>
        <th>Group</th>
        <th>Reported By</th>
        <th>Status</th>
      </tr>
`;
    
    recentEntries.forEach(function(entry) {
      const statusClass = 'status-' + entry.status.toLowerCase();
      html += `
      <tr>
        <td>${formatDate_(entry.date)}</td>
        <td><strong>${escapeHtml_(entry.studentName)}</strong></td>
        <td>${escapeHtml_(entry.grade)}</td>
        <td>${escapeHtml_(entry.group)}</td>
        <td>${escapeHtml_(entry.reportedBy)}</td>
        <td><span class="status-badge ${statusClass}">${entry.status}</span></td>
      </tr>
`;
    });
    
    html += `</table>`;
  }
  
  html += `</div>`;

  // Pending review section (if there are pending items)
  if (pendingEntries.length > 0 && pendingEntries.length !== recentEntries.length) {
    html += `
  <div class="section">
    <h2>⏳ All Pending Review</h2>
    <p style="color:#718096;font-size:13px;margin-bottom:12px;">
      These students have been flagged as unenrolled but haven't been confirmed in the system yet.
    </p>
    <table>
      <tr>
        <th>Date Reported</th>
        <th>Student Name</th>
        <th>Grade</th>
        <th>Group</th>
        <th>Reported By</th>
      </tr>
`;
    
    pendingEntries.forEach(function(entry) {
      html += `
      <tr>
        <td>${formatDate_(entry.date)}</td>
        <td><strong>${escapeHtml_(entry.studentName)}</strong></td>
        <td>${escapeHtml_(entry.grade)}</td>
        <td>${escapeHtml_(entry.group)}</td>
        <td>${escapeHtml_(entry.reportedBy)}</td>
      </tr>
`;
    });
    
    html += `</table></div>`;
  }

  // Action link and footer
  html += `
  <div style="text-align:center;margin-top:24px;">
    <a href="${sheetUrl}" class="action-link" style="color:white;">Open Tracking Sheet</a>
  </div>
  
  <div class="footer">
    <p>This is an automated report from the TILT Progress Tracking System.</p>
    <p>To update a student's status, open the Unenrolled Log sheet and change the Status column.</p>
  </div>
</body>
</html>
`;

  return html;
}

// ═══════════════════════════════════════════════════════════════════════════
// TRIGGER MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sets up the weekly trigger for the unenrolled report
 * RUN THIS ONCE to create the trigger
 */
function setupUnenrolledReportTrigger() {
  // Remove any existing triggers for this function
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'sendWeeklyUnenrolledReport') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Create new weekly trigger
  ScriptApp.newTrigger('sendWeeklyUnenrolledReport')
    .timeBased()
    .onWeekDay(UNENROLLED_REPORT_CONFIG.reportDayOfWeek)
    .atHour(UNENROLLED_REPORT_CONFIG.reportHour)
    .create();
  
  Logger.log('Weekly unenrolled report trigger created for ' + 
             UNENROLLED_REPORT_CONFIG.reportDayOfWeek + ' at ' + 
             UNENROLLED_REPORT_CONFIG.reportHour + ':00');
  
  // Show confirmation
  SpreadsheetApp.getUi().alert(
    'Trigger Created',
    'The weekly unenrolled student report will be sent every ' +
    getDayName_(UNENROLLED_REPORT_CONFIG.reportDayOfWeek) + 
    ' at ' + UNENROLLED_REPORT_CONFIG.reportHour + ':00 AM.\n\n' +
    'Reports will be sent to: ' + UNENROLLED_REPORT_CONFIG.recipientEmail,
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

/**
 * Removes the weekly trigger
 */
function removeUnenrolledReportTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  let removed = 0;
  
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'sendWeeklyUnenrolledReport') {
      ScriptApp.deleteTrigger(trigger);
      removed++;
    }
  });
  
  Logger.log('Removed ' + removed + ' trigger(s)');
  
  SpreadsheetApp.getUi().alert(
    'Trigger Removed',
    'The weekly unenrolled report trigger has been removed.',
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

/**
 * Manually run the report (for testing)
 */
function testUnenrolledReport() {
  sendWeeklyUnenrolledReport();
  SpreadsheetApp.getUi().alert(
    'Test Report Sent',
    'A test report has been sent to: ' + UNENROLLED_REPORT_CONFIG.recipientEmail,
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Formats a date as MM/DD/YYYY
 * @private
 */
function formatDate_(date) {
  if (!(date instanceof Date) || isNaN(date)) {
    return 'N/A';
  }
  return Utilities.formatDate(date, Session.getScriptTimeZone(), 'MM/dd/yyyy');
}

/**
 * Escapes HTML special characters
 * @private
 */
function escapeHtml_(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Gets the day name from ScriptApp.WeekDay enum
 * @private
 */
function getDayName_(weekDay) {
  const days = {
    [ScriptApp.WeekDay.SUNDAY]: 'Sunday',
    [ScriptApp.WeekDay.MONDAY]: 'Monday',
    [ScriptApp.WeekDay.TUESDAY]: 'Tuesday',
    [ScriptApp.WeekDay.WEDNESDAY]: 'Wednesday',
    [ScriptApp.WeekDay.THURSDAY]: 'Thursday',
    [ScriptApp.WeekDay.FRIDAY]: 'Friday',
    [ScriptApp.WeekDay.SATURDAY]: 'Saturday'
  };
  return days[weekDay] || 'Unknown';
}

// ═══════════════════════════════════════════════════════════════════════════
// MENU INTEGRATION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Add these items to your existing onOpen() function menu:
 * 
 * .addSubMenu(ui.createMenu('📚 Tutoring')
 *   .addItem('Create Tutoring Sheets', 'createTutoringSheets')
 *   .addItem('Sync Tutoring Data', 'syncTutoringProgress')
 *   .addItem('View Tutoring Summary', 'goToTutoringSummary'))
 * .addSubMenu(ui.createMenu('📋 Unenrolled Reports')
 *   .addItem('📧 Send Test Report', 'testUnenrolledReport')
 *   .addItem('⏰ Setup Weekly Trigger', 'setupUnenrolledReportTrigger')
 *   .addItem('🚫 Remove Trigger', 'removeUnenrolledReportTrigger'))
 */

/**
 * Navigates to the Tutoring Summary sheet
 */
function goToTutoringSummary() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAMES_TUTORING.SUMMARY);
  
  if (!sheet) {
    createTutoringSheets();
    sheet = ss.getSheetByName(SHEET_NAMES_TUTORING.SUMMARY);
  }
  
  ss.setActiveSheet(sheet);
}

/**
 * Navigates to the Tutoring Progress Log sheet
 */
function goToTutoringLog() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAMES_TUTORING.PROGRESS_LOG);
  
  if (!sheet) {
    createTutoringSheets();
    sheet = ss.getSheetByName(SHEET_NAMES_TUTORING.PROGRESS_LOG);
  }
  
  ss.setActiveSheet(sheet);
}

/**
 * Navigates to the Unenrolled Log sheet
 */
function goToUnenrolledLog() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(UNENROLLED_REPORT_CONFIG.unenrolledLogSheetName);
  
  if (!sheet) {
    sheet = createUnenrolledLogSheet_(ss);
  }
  
  ss.setActiveSheet(sheet);
}

// ═══════════════════════════════════════════════════════════════════════════
// REPORTING - COMBINED STUDENT VIEW
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generates a combined report showing both UFLI and Tutoring progress
 * for a specific student or all students
 * 
 * @param {string} studentName - Optional: specific student (null for all)
 * @returns {Object} Report data
 */
function getStudentCombinedProgress(studentName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // Get UFLI data from Grade Summary
  const summarySheet = ss.getSheetByName(SHEET_NAMES_V2.GRADE_SUMMARY);
  const summaryData = summarySheet ? summarySheet.getDataRange().getValues() : [];
  
  // Get Tutoring data from Tutoring Summary
  const tutoringSheet = ss.getSheetByName(SHEET_NAMES_TUTORING.SUMMARY);
  const tutoringData = tutoringSheet ? tutoringSheet.getDataRange().getValues() : [];
  
  // Build lookup maps
  const ufliMap = {};
  for (let i = LAYOUT.DATA_START_ROW - 1; i < summaryData.length; i++) {
    const name = summaryData[i][0];
    if (name) {
      ufliMap[name] = {
        grade: summaryData[i][1],
        group: summaryData[i][3],
        foundational: summaryData[i][4],
        minGrade: summaryData[i][5],
        fullGrade: summaryData[i][6],
        benchmark: summaryData[i][7]
      };
    }
  }
  
  const tutoringMap = {};
  for (let i = TUTORING_LAYOUT.DATA_START_ROW - 1; i < tutoringData.length; i++) {
    const name = tutoringData[i][0];
    if (name) {
      tutoringMap[name] = {
        tutoringGroups: tutoringData[i][3],
        totalSessions: tutoringData[i][4],
        reteachCount: tutoringData[i][5],
        reteachPassRate: tutoringData[i][6],
        comprehensionCount: tutoringData[i][7],
        comprehensionPassRate: tutoringData[i][8],
        overallPassRate: tutoringData[i][11],
        lastSession: tutoringData[i][12]
      };
    }
  }
  
  // Combine data
  const allStudents = new Set([...Object.keys(ufliMap), ...Object.keys(tutoringMap)]);
  const combinedData = [];
  
  allStudents.forEach(name => {
    if (studentName && name !== studentName) return;
    
    const ufli = ufliMap[name] || {};
    const tutoring = tutoringMap[name] || {};
    
    combinedData.push({
      name: name,
      grade: ufli.grade || "",
      primaryGroup: ufli.group || "",
      // UFLI Progress
      ufli: {
        foundational: ufli.foundational,
        minGrade: ufli.minGrade,
        fullGrade: ufli.fullGrade,
        benchmark: ufli.benchmark
      },
      // Tutoring Progress
      tutoring: {
        groups: tutoring.tutoringGroups,
        sessions: tutoring.totalSessions,
        reteachCount: tutoring.reteachCount,
        reteachPassRate: tutoring.reteachPassRate,
        comprehensionCount: tutoring.comprehensionCount,
        comprehensionPassRate: tutoring.comprehensionPassRate,
        overallPassRate: tutoring.overallPassRate,
        lastSession: tutoring.lastSession
      }
    });
  });
  
  return combinedData;
}

// ═══════════════════════════════════════════════════════════════════════════
// INITIALIZATION & TESTING
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Test function to verify tutoring system is working
 */
function testTutoringSystem() {
  Logger.log("=== TUTORING SYSTEM TEST ===");
  
  // Test 1: Detection
  Logger.log("\n--- Test 1: Group Detection ---");
  Logger.log("G3 Group 1 Galdamez → isTutoring: " + isTutoringGroup("G3 Group 1 Galdamez"));
  Logger.log("G3 Group 1 Tutoring Galdamez → isTutoring: " + isTutoringGroup("G3 Group 1 Tutoring Galdamez"));
  
  // Test 2: Lesson categorization
  Logger.log("\n--- Test 2: Lesson Categorization ---");
  Logger.log("UFLI L42: " + JSON.stringify(categorizeTutoringLesson("UFLI L42")));
  Logger.log("UFLI L42 reteach: " + JSON.stringify(categorizeTutoringLesson("UFLI L42 reteach")));
  Logger.log("Comprehension: " + JSON.stringify(categorizeTutoringLesson("Comprehension")));
  Logger.log("UFLI L41c: " + JSON.stringify(categorizeTutoringLesson("UFLI L41c")));
  
  // Test 3: Sheet creation
  Logger.log("\n--- Test 3: Creating Sheets ---");
  createTutoringSheets();
  
  Logger.log("\n=== TEST COMPLETE ===");
}
