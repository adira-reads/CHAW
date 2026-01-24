import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import apiClient from '../api/client'
import StatusBadge from '../components/StatusBadge'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

interface StudentProgress {
  student_id: string
  name: string
  grade: string
  group: string | null
  teacher: string | null
  current_lesson: number | null
  foundational_pct: number
  min_grade_pct: number
  full_grade_pct: number
  benchmark_pct: number
  skill_sections: SkillSection[]
  lessons: Record<number, string> | null
}

interface SkillSection {
  section_id: number
  section_name: string
  lesson_count: number
  completed_count: number
  percentage: number
}

export default function StudentDetail() {
  const { id } = useParams<{ id: string }>()
  const [student, setStudent] = useState<StudentProgress | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStudent = async () => {
      if (!id) return

      try {
        const response = await apiClient.get(`/progress/students/${id}`)
        setStudent(response.data)
      } catch (err) {
        console.error('Failed to fetch student:', err)
        setError('Failed to load student data')
      } finally {
        setIsLoading(false)
      }
    }
    fetchStudent()
  }, [id])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-ufli-primary border-t-transparent"></div>
      </div>
    )
  }

  if (error || !student) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error || 'Student not found'}</p>
        <Link to="/students" className="mt-4 inline-block text-ufli-primary hover:underline">
          Back to Students
        </Link>
      </div>
    )
  }

  // Progress bar component
  const ProgressBar = ({ value, label }: { value: number; label: string }) => (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">{value.toFixed(1)}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full bg-ufli-primary transition-all"
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        to="/students"
        className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
      >
        <ArrowLeftIcon className="h-4 w-4" />
        Back to Students
      </Link>

      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{student.name}</h1>
            <div className="mt-1 flex flex-wrap gap-3 text-sm text-gray-600">
              <span>Grade: {student.grade}</span>
              {student.group && <span>Group: {student.group}</span>}
              {student.teacher && <span>Teacher: {student.teacher}</span>}
            </div>
          </div>
          {student.current_lesson && (
            <div className="text-right">
              <p className="text-sm text-gray-600">Current Lesson</p>
              <p className="text-3xl font-bold text-ufli-primary">
                {student.current_lesson}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Progress metrics */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Progress Metrics</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <ProgressBar value={student.foundational_pct} label="Foundational (L1-34)" />
          <ProgressBar value={student.min_grade_pct} label="Min Grade Requirement" />
          <ProgressBar value={student.full_grade_pct} label="Current Year" />
          <ProgressBar value={student.benchmark_pct} label="Benchmark" />
        </div>
      </div>

      {/* Skill sections */}
      {student.skill_sections && student.skill_sections.length > 0 && (
        <div className="card">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Skill Sections</h2>
          <div className="space-y-3">
            {student.skill_sections.map((section) => (
              <div key={section.section_id}>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-700">{section.section_name}</span>
                  <span className="text-gray-500">
                    {section.completed_count}/{section.lesson_count} ({section.percentage.toFixed(0)}%)
                  </span>
                </div>
                <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-gray-200">
                  <div
                    className="h-full bg-ufli-accent transition-all"
                    style={{ width: `${Math.min(section.percentage, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lesson matrix */}
      {student.lessons && (
        <div className="card">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Lesson Matrix</h2>
          <div className="grid grid-cols-10 gap-1 sm:grid-cols-16 md:grid-cols-20 lg:grid-cols-25">
            {Array.from({ length: 128 }, (_, i) => i + 1).map((lessonNum) => (
              <div
                key={lessonNum}
                className="relative group"
                title={`Lesson ${lessonNum}`}
              >
                <StatusBadge
                  status={student.lessons?.[lessonNum] as 'Y' | 'N' | 'A' | 'U' | null}
                  size="sm"
                />
                <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 hidden group-hover:block text-xs text-gray-500 whitespace-nowrap">
                  L{lessonNum}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <StatusBadge status="Y" size="sm" />
              <span>Passed</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status="N" size="sm" />
              <span>Not Yet</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status="A" size="sm" />
              <span>Absent</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status="U" size="sm" />
              <span>Unenrolled</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={null} size="sm" />
              <span>Not Entered</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
