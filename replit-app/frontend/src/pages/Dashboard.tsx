import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'
import {
  UsersIcon,
  UserGroupIcon,
  BookOpenIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

interface DashboardStats {
  total_students: number
  total_groups: number
  total_teachers: number
  avg_benchmark_pct: number
}

interface RecentEntry {
  entry_date: string
  group_name: string
  lesson_name: string
  student_count: number
  pass_count: number
  teacher_name: string
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentEntries, setRecentEntries] = useState<RecentEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch stats
        const statsResponse = await apiClient.get('/progress/school-summary')
        setStats({
          total_students: statsResponse.data.total_students,
          total_groups: statsResponse.data.total_groups,
          total_teachers: statsResponse.data.total_teachers,
          avg_benchmark_pct: statsResponse.data.avg_benchmark_pct,
        })

        // Fetch recent entries
        const entriesResponse = await apiClient.get('/lesson-entries/recent')
        setRecentEntries(entriesResponse.data.slice(0, 5))
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
        // Set default values on error
        setStats({
          total_students: 0,
          total_groups: 0,
          total_teachers: 0,
          avg_benchmark_pct: 0,
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-ufli-primary border-t-transparent"></div>
      </div>
    )
  }

  const statCards = [
    {
      name: 'Total Students',
      value: stats?.total_students ?? 0,
      icon: UsersIcon,
      color: 'bg-blue-500',
      href: '/students',
    },
    {
      name: 'Total Groups',
      value: stats?.total_groups ?? 0,
      icon: UserGroupIcon,
      color: 'bg-purple-500',
      href: '/groups',
    },
    {
      name: 'Teachers',
      value: stats?.total_teachers ?? 0,
      icon: BookOpenIcon,
      color: 'bg-green-500',
      href: '#',
    },
    {
      name: 'Avg Benchmark',
      value: `${(stats?.avg_benchmark_pct ?? 0).toFixed(1)}%`,
      icon: ChartBarIcon,
      color: 'bg-amber-500',
      href: '#',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of UFLI progress tracking</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <Link
            key={stat.name}
            to={stat.href}
            className="card flex items-center gap-4 transition-shadow hover:shadow-md"
          >
            <div className={`rounded-lg p-3 ${stat.color}`}>
              <stat.icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">{stat.name}</p>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick actions */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Link
            to="/lesson-entry"
            className="flex items-center gap-3 rounded-lg border-2 border-dashed border-ufli-primary bg-blue-50 p-4 text-ufli-primary transition-colors hover:bg-blue-100"
          >
            <BookOpenIcon className="h-6 w-6" />
            <span className="font-medium">Enter Lessons</span>
          </Link>
          <Link
            to="/students"
            className="flex items-center gap-3 rounded-lg border-2 border-dashed border-gray-300 p-4 text-gray-600 transition-colors hover:border-gray-400 hover:bg-gray-50"
          >
            <UsersIcon className="h-6 w-6" />
            <span className="font-medium">View Students</span>
          </Link>
          <Link
            to="/groups"
            className="flex items-center gap-3 rounded-lg border-2 border-dashed border-gray-300 p-4 text-gray-600 transition-colors hover:border-gray-400 hover:bg-gray-50"
          >
            <UserGroupIcon className="h-6 w-6" />
            <span className="font-medium">View Groups</span>
          </Link>
        </div>
      </div>

      {/* Recent entries */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Recent Entries</h2>
        {recentEntries.length > 0 ? (
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Date
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Group
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Lesson
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Results
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Teacher
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {recentEntries.map((entry, idx) => (
                  <tr key={idx}>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">
                      {new Date(entry.entry_date).toLocaleDateString()}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">
                      {entry.group_name}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">
                      {entry.lesson_name}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">
                      <span className="text-status-passed">{entry.pass_count}</span>
                      <span className="text-gray-400"> / </span>
                      <span>{entry.student_count}</span>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
                      {entry.teacher_name}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-center text-gray-500 py-8">
            No recent entries. Start by entering lesson data!
          </p>
        )}
      </div>
    </div>
  )
}
