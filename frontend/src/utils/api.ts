import axios from 'axios'
import type { LoginRequest, RegisterRequest, AuthResponse, ApiResponse, User } from '@/types/user'

// API基础地址（支持环境变量配置，用于外网访问）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 获取上传文件的基础URL（用于头像等静态资源）
export const getUploadBaseUrl = () => {
  const apiUrl = import.meta.env.VITE_API_BASE_URL
  if (apiUrl && apiUrl.startsWith('http')) {
    // 外网环境：使用API地址的域名部分
    return apiUrl.replace('/api', '')
  }
  // 本地开发环境：使用代理
  return ''
}

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,  // 增加超时时间到30秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理token过期
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post('/api/auth/refresh', {
            refresh_token: refreshToken
          })

          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)

          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // 刷新失败，清除tokens并跳转到登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // 处理其他错误
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('API错误:', error.response.status, error.response.data)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('网络错误:', error.message)
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message)
    }

    return Promise.reject(error)
  }
)

// 用户认证API
export const authApi = {
  // 用户登录
  login: async (data: LoginRequest): Promise<ApiResponse<AuthResponse>> => {
    return await api.post('/auth/login', data)
  },

  // 用户注册
  register: async (data: RegisterRequest): Promise<ApiResponse<AuthResponse>> => {
    return await api.post('/auth/register', data)
  },

  // 刷新token
  refreshToken: async (refreshToken: string): Promise<ApiResponse<{ access_token: string }>> => {
    return await api.post('/auth/refresh', { refresh_token: refreshToken })
  },

  // 用户登出
  logout: async (): Promise<ApiResponse> => {
    return await api.post('/auth/logout')
  },

  // 获取当前用户信息
  getCurrentUser: async (): Promise<ApiResponse> => {
    return await api.get('/auth/me')
  },

  // 更新用户信息
  updateProfile: async (data: Partial<User>): Promise<ApiResponse<User>> => {
    return await api.put('/auth/profile', data)
  },

  // 上传头像
  uploadAvatar: async (avatarBase64: string): Promise<ApiResponse<{ avatar: string }>> => {
    return await api.post('/auth/upload-avatar', { avatar: avatarBase64 })
  }
}

// 统计数据API
export const statsApi = {
  // 获取今日统计
  getTodayStats: async (): Promise<ApiResponse<any>> => {
    return await api.get('/stats/today')
  },

  // 获取本周统计
  getWeekStats: async (): Promise<ApiResponse<any>> => {
    return await api.get('/stats/week')
  },

  // 获取最近活动
  getRecentActivities: async (limit: number = 10): Promise<ApiResponse<any[]>> => {
    return await api.get(`/stats/recent-activities?limit=${limit}`)
  },

  // 获取连续打卡天数
  getStreakDays: async (): Promise<ApiResponse<{ streak_days: number }>> => {
    return await api.get('/stats/streak-days')
  },

  // 获取AI方案数量
  getAiPlansCount: async (): Promise<ApiResponse<{ count: number }>> => {
    return await api.get('/stats/ai-plans-count')
  }
}

// 运动库API
export const exerciseApi = {
  // 获取运动列表
  getExercises: async (params?: {
    search?: string
    category?: string
    difficulty_level?: string
    muscle_group?: string
    page?: number
    limit?: number
  }): Promise<ApiResponse<{
    exercises: any[]
    pagination: {
      page: number
      limit: number
      total: number
      pages: number
    }
  }>> => {
    const queryParams = new URLSearchParams()
    if (params?.search) queryParams.append('search', params.search)
    if (params?.category) queryParams.append('category', params.category)
    if (params?.difficulty_level) queryParams.append('difficulty_level', params.difficulty_level)
    if (params?.muscle_group) queryParams.append('muscle_group', params.muscle_group)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    
    return await api.get(`/exercises?${queryParams.toString()}`)
  },

  // 获取单个运动详情
  getExerciseById: async (id: number): Promise<ApiResponse<any>> => {
    return await api.get(`/exercises/${id}`)
  },

  // 获取运动记录
  getExerciseLogs: async (params?: {
    user_id?: number
    date_from?: string
    date_to?: string
    exercise_id?: number
    page?: number
    limit?: number
  }): Promise<ApiResponse<{
    logs: any[]
    pagination: {
      page: number
      limit: number
      total: number
      pages: number
    }
  }>> => {
    const queryParams = new URLSearchParams()
    if (params?.user_id) queryParams.append('user_id', params.user_id.toString())
    if (params?.date_from) queryParams.append('date_from', params.date_from)
    if (params?.date_to) queryParams.append('date_to', params.date_to)
    if (params?.exercise_id) queryParams.append('exercise_id', params.exercise_id.toString())
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    
    return await api.get(`/exercise-logs?${queryParams.toString()}`)
  },

  // 创建运动记录
  createExerciseLog: async (data: {
    exercise_id: number
    duration_minutes: number
    intensity_level?: string
    calories_burned?: number
    notes?: string
    heart_rate?: number
    user_id?: number
  }): Promise<ApiResponse<any>> => {
    return await api.post('/exercise-logs', data)
  },

  // 更新运动记录
  updateExerciseLog: async (id: number, data: {
    duration_minutes?: number
    intensity_level?: string
    calories_burned?: number
    notes?: string
    heart_rate?: number
  }): Promise<ApiResponse<any>> => {
    return await api.put(`/exercise-logs/${id}`, data)
  },

  // 删除运动记录
  deleteExerciseLog: async (id: number): Promise<ApiResponse> => {
    return await api.delete(`/exercise-logs/${id}`)
  },

  // 获取运动统计
  getExerciseStats: async (params?: {
    period?: string
    user_id?: number
  }): Promise<ApiResponse<any>> => {
    const queryParams = new URLSearchParams()
    if (params?.period) queryParams.append('period', params.period)
    if (params?.user_id) queryParams.append('user_id', params.user_id.toString())
    
    return await api.get(`/exercise-stats?${queryParams.toString()}`)
  }
}

// AI健身方案API
export const aiPlanApi = {
  // 获取AI方案列表
  getPlans: async (params?: {
    page?: number
    limit?: number
    status?: string
  }): Promise<ApiResponse<{
    plans: any[]
    pagination: {
      page: number
      limit: number
      total: number
      pages: number
    }
  }>> => {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.status) queryParams.append('status', params.status)
    
    return await api.get(`/ai-plans?${queryParams.toString()}`)
  },

  // 获取单个AI方案详情
  getPlanById: async (id: number): Promise<ApiResponse<any>> => {
    return await api.get(`/ai-plans/${id}`)
  },

  // 生成AI健身方案
  generatePlan: async (data: {
    fitness_goal: string
    experience_level: string
    weekly_frequency: string
    session_duration: string
    preferred_types?: string
    health_condition?: string
    special_requirements?: string
  }): Promise<ApiResponse<any>> => {
    return await api.post('/ai-plans/generate', data)
  },

  // 更新AI方案状态
  updatePlanStatus: async (id: number, status: string): Promise<ApiResponse<any>> => {
    return await api.put(`/ai-plans/${id}/status`, { status })
  },

  // 删除AI方案 (使用POST方式，兼容性更好)
  deletePlan: async (id: number): Promise<ApiResponse> => {
    return await api.post(`/ai-plans/delete/${id}`)
  },

  // 获取AI方案执行统计
  getPlanStats: async (planId: number): Promise<ApiResponse<any>> => {
    return await api.get(`/ai-plans/${planId}/stats`)
  }
}

// 饮食记录API
export const dietApi = {
  // 获取食物列表
  getFoods: async (params?: {
    search?: string
    category?: string
    page?: number
    limit?: number
  }): Promise<ApiResponse<{
    foods: any[]
    pagination: {
      page: number
      limit: number
      total: number
      pages: number
    }
  }>> => {
    const queryParams = new URLSearchParams()
    if (params?.search) queryParams.append('search', params.search)
    if (params?.category) queryParams.append('category', params.category)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    
    return await api.get(`/foods?${queryParams.toString()}`)
  },

  // 获取饮食记录
  getDietRecords: async (params?: {
    user_id?: number
    date_from?: string
    date_to?: string
    page?: number
    limit?: number
  }): Promise<ApiResponse<{
    records: any[]
    pagination: {
      page: number
      limit: number
      total: number
      pages: number
    }
  }>> => {
    const queryParams = new URLSearchParams()
    if (params?.user_id) queryParams.append('user_id', params.user_id.toString())
    if (params?.date_from) queryParams.append('date_from', params.date_from)
    if (params?.date_to) queryParams.append('date_to', params.date_to)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    
    return await api.get(`/diet-records?${queryParams.toString()}`)
  },

  // 创建饮食记录
  createDietRecord: async (data: {
    food_id: number
    quantity: number
    meal_type: string
    notes?: string
    user_id?: number
  }): Promise<ApiResponse<any>> => {
    return await api.post('/diet-records', data)
  },

  // 更新饮食记录
  updateDietRecord: async (id: number, data: {
    quantity?: number
    meal_type?: string
    notes?: string
  }): Promise<ApiResponse<any>> => {
    return await api.put(`/diet-records/${id}`, data)
  },

  // 删除饮食记录
  deleteDietRecord: async (id: number): Promise<ApiResponse> => {
    return await api.delete(`/diet-records/${id}`)
  }
}

export default api