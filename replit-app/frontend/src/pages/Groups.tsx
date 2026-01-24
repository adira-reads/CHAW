import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import apiClient, { Group } from '../api/client'
import { UserGroupIcon, UsersIcon } from '@heroicons/react/24/outline'

export default function Groups() {
  const [groups, setGroups] = useState<Group[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [gradeFilter, setGradeFilter] = useState('')

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await apiClient.get('/groups')
        setGroups(response.data.items || response.data)
      } catch (error) {
        console.error('Failed to fetch groups:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchGroups()
  }, [])

  // Get unique grades for filter
  const grades = [...new Set(groups.map((g) => g.grade))].filter(Boolean).sort()

  // Filter groups
  const filteredGroups = groups.filter((group) => {
    return !gradeFilter || group.grade === gradeFilter
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-ufli-primary border-t-transparent"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Groups</h1>
          <p className="text-gray-600">
            {filteredGroups.length} groups
            {gradeFilter ? ` (filtered by ${gradeFilter})` : ''}
          </p>
        </div>
      </div>

      {/* Grade filter */}
      <div className="card">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setGradeFilter('')}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              !gradeFilter
                ? 'bg-ufli-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All Grades
          </button>
          {grades.map((grade) => (
            <button
              key={grade}
              onClick={() => setGradeFilter(grade || '')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                gradeFilter === grade
                  ? 'bg-ufli-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {grade}
            </button>
          ))}
        </div>
      </div>

      {/* Groups grid */}
      {filteredGroups.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredGroups.map((group) => (
            <div
              key={group.group_id}
              className="card transition-shadow hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-ufli-primary/10 p-2">
                    <UserGroupIcon className="h-6 w-6 text-ufli-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{group.name}</h3>
                    <p className="text-sm text-gray-500">{group.grade}</p>
                  </div>
                </div>
                {!group.is_active && (
                  <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600">
                    Inactive
                  </span>
                )}
              </div>

              <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <UsersIcon className="h-4 w-4" />
                  <span>{group.student_count} students</span>
                </div>
                {group.teacher_name && (
                  <span className="truncate">{group.teacher_name}</span>
                )}
              </div>

              <div className="mt-4 flex gap-2">
                <Link
                  to={`/lesson-entry?group=${group.group_id}`}
                  className="btn-primary flex-1 text-center text-sm"
                >
                  Enter Lessons
                </Link>
                <Link
                  to={`/students?group=${group.group_id}`}
                  className="btn-secondary flex-1 text-center text-sm"
                >
                  View Students
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card py-12 text-center text-gray-500">
          {gradeFilter ? 'No groups match your filter' : 'No groups found'}
        </div>
      )}
    </div>
  )
}
