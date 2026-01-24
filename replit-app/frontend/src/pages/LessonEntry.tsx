import { useState, useEffect, useCallback } from 'react'
import apiClient, { Group, Lesson, Student, LessonEntryBatch } from '../api/client'
import { StatusSelector } from '../components/StatusBadge'
import { useAuth } from '../contexts/AuthContext'

type StudentStatus = 'Y' | 'N' | 'A' | 'U' | null

interface StudentWithStatus {
  student_id: string
  name: string
  current_lesson: number | null
  status: StudentStatus
}

export default function LessonEntry() {
  const { user } = useAuth()

  // Selection state
  const [groups, setGroups] = useState<Group[]>([])
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [selectedGroupId, setSelectedGroupId] = useState<string>('')
  const [selectedLessonId, setSelectedLessonId] = useState<string>('')
  const [entryDate, setEntryDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  )

  // Students and their statuses
  const [students, setStudents] = useState<StudentWithStatus[]>([])

  // UI state
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
    null
  )

  // Load groups on mount
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await apiClient.get('/groups')
        setGroups(response.data.items || response.data)
      } catch (error) {
        console.error('Failed to fetch groups:', error)
      }
    }
    fetchGroups()
  }, [])

  // Load lessons on mount
  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const response = await apiClient.get('/lessons')
        setLessons(response.data.items || response.data)
      } catch (error) {
        console.error('Failed to fetch lessons:', error)
      }
    }
    fetchLessons()
  }, [])

  // Load students when group is selected
  useEffect(() => {
    if (!selectedGroupId) {
      setStudents([])
      return
    }

    const fetchStudents = async () => {
      setIsLoading(true)
      try {
        const response = await apiClient.get(`/groups/${selectedGroupId}/students`)
        const studentData = response.data.items || response.data
        setStudents(
          studentData.map((s: Student) => ({
            student_id: s.student_id,
            name: s.name,
            current_lesson: s.current_lesson,
            status: null,
          }))
        )
      } catch (error) {
        console.error('Failed to fetch students:', error)
        setStudents([])
      } finally {
        setIsLoading(false)
      }
    }
    fetchStudents()
  }, [selectedGroupId])

  // Update student status
  const handleStatusChange = useCallback(
    (studentId: string, status: 'Y' | 'N' | 'A' | 'U') => {
      setStudents((prev) =>
        prev.map((s) =>
          s.student_id === studentId ? { ...s, status } : s
        )
      )
    },
    []
  )

  // Set all students to a status
  const setAllStatus = (status: 'Y' | 'N' | 'A' | 'U') => {
    setStudents((prev) => prev.map((s) => ({ ...s, status })))
  }

  // Submit lesson entries
  const handleSubmit = async () => {
    if (!selectedGroupId || !selectedLessonId) {
      setMessage({ type: 'error', text: 'Please select a group and lesson' })
      return
    }

    const studentsWithStatus = students.filter((s) => s.status !== null)
    if (studentsWithStatus.length === 0) {
      setMessage({ type: 'error', text: 'Please mark at least one student' })
      return
    }

    setIsSaving(true)
    setMessage(null)

    try {
      const payload: LessonEntryBatch = {
        group_id: selectedGroupId,
        teacher_id: user?.user_id || '',
        lesson_id: selectedLessonId,
        entry_date: entryDate,
        students: studentsWithStatus.map((s) => ({
          student_id: s.student_id,
          status: s.status as 'Y' | 'N' | 'A' | 'U',
        })),
        entry_type: 'small_group',
      }

      await apiClient.post('/lesson-entries/batch', payload)

      setMessage({
        type: 'success',
        text: `Saved ${studentsWithStatus.length} student entries!`,
      })

      // Reset statuses but keep selection
      setStudents((prev) => prev.map((s) => ({ ...s, status: null })))
    } catch (error) {
      console.error('Failed to save entries:', error)
      setMessage({ type: 'error', text: 'Failed to save entries. Please try again.' })
    } finally {
      setIsSaving(false)
    }
  }

  // Get selected lesson name
  const selectedLesson = lessons.find((l) => l.lesson_id === selectedLessonId)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Lesson Entry</h1>
        <p className="text-gray-600">Record student progress for a lesson</p>
      </div>

      {/* Selection form */}
      <div className="card">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {/* Group selection */}
          <div>
            <label
              htmlFor="group"
              className="block text-sm font-medium text-gray-700"
            >
              Group
            </label>
            <select
              id="group"
              value={selectedGroupId}
              onChange={(e) => setSelectedGroupId(e.target.value)}
              className="input-field mt-1"
            >
              <option value="">Select a group...</option>
              {groups.map((group) => (
                <option key={group.group_id} value={group.group_id}>
                  {group.name} ({group.grade})
                </option>
              ))}
            </select>
          </div>

          {/* Lesson selection */}
          <div>
            <label
              htmlFor="lesson"
              className="block text-sm font-medium text-gray-700"
            >
              Lesson
            </label>
            <select
              id="lesson"
              value={selectedLessonId}
              onChange={(e) => setSelectedLessonId(e.target.value)}
              className="input-field mt-1"
            >
              <option value="">Select a lesson...</option>
              {lessons.map((lesson) => (
                <option key={lesson.lesson_id} value={lesson.lesson_id}>
                  {lesson.number}. {lesson.short_name}
                  {lesson.is_review ? ' (Review)' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Date */}
          <div>
            <label
              htmlFor="date"
              className="block text-sm font-medium text-gray-700"
            >
              Date
            </label>
            <input
              id="date"
              type="date"
              value={entryDate}
              onChange={(e) => setEntryDate(e.target.value)}
              className="input-field mt-1"
            />
          </div>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`rounded-lg p-4 ${
            message.type === 'success'
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Students list */}
      {selectedGroupId && (
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Students
              {selectedLesson && (
                <span className="ml-2 text-sm font-normal text-gray-500">
                  - Lesson {selectedLesson.number}: {selectedLesson.short_name}
                </span>
              )}
            </h2>

            {/* Quick actions */}
            <div className="flex gap-2">
              <button
                onClick={() => setAllStatus('Y')}
                className="rounded bg-status-passed px-3 py-1 text-sm font-medium text-white hover:opacity-80"
              >
                All Y
              </button>
              <button
                onClick={() => setAllStatus('N')}
                className="rounded bg-status-failed px-3 py-1 text-sm font-medium text-white hover:opacity-80"
              >
                All N
              </button>
              <button
                onClick={() => setStudents((prev) => prev.map((s) => ({ ...s, status: null })))}
                className="rounded bg-gray-200 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-300"
              >
                Clear
              </button>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-ufli-primary border-t-transparent"></div>
            </div>
          ) : students.length > 0 ? (
            <div className="space-y-2">
              {students.map((student) => (
                <div
                  key={student.student_id}
                  className="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-3"
                >
                  <div>
                    <span className="font-medium text-gray-900">{student.name}</span>
                    {student.current_lesson && (
                      <span className="ml-2 text-sm text-gray-500">
                        (Current: L{student.current_lesson})
                      </span>
                    )}
                  </div>
                  <StatusSelector
                    currentStatus={student.status}
                    onSelect={(status) => handleStatusChange(student.student_id, status)}
                  />
                </div>
              ))}
            </div>
          ) : (
            <p className="py-8 text-center text-gray-500">
              No students in this group
            </p>
          )}

          {/* Submit button */}
          {students.length > 0 && (
            <div className="mt-6 flex justify-end">
              <button
                onClick={handleSubmit}
                disabled={isSaving || !selectedLessonId}
                className="btn-primary disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Entries'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
