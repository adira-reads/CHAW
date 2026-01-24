import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

// API base URL - uses proxy in development, direct in production
const API_BASE_URL = '/api'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config

    // If 401 and not already retrying, try to refresh token
    if (error.response?.status === 401 && originalRequest) {
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token: newRefreshToken } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', newRefreshToken)

          // Retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return apiClient(originalRequest)
        } catch {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient

// Type definitions for API responses
export interface ApiError {
  detail: string
  status_code?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// Auth types
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: {
    user_id: string
    email: string
    name: string
    role: string
  }
}

// Entity types
export interface Student {
  student_id: string
  name: string
  grade: string
  group_name: string | null
  teacher_name: string | null
  current_lesson: number | null
  is_active: boolean
}

export interface Group {
  group_id: string
  name: string
  grade: string | null
  teacher_name: string | null
  student_count: number
  is_active: boolean
}

export interface Lesson {
  lesson_id: string
  number: number
  name: string
  short_name: string
  is_review: boolean
  is_foundational: boolean
}

export interface StudentStatus {
  student_id: string
  status: 'Y' | 'N' | 'A' | 'U'
}

export interface LessonEntryBatch {
  group_id: string
  teacher_id: string
  lesson_id: string
  entry_date?: string
  students: StudentStatus[]
  entry_type: string
}
