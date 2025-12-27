// 用户相关类型定义
export interface User {
  id: number
  username: string
  email: string
  age?: number
  gender?: 'male' | 'female'
  height?: number
  weight?: number
  fitness_goal?: string
  avatar?: string
  created_at: string
  updated_at: string
}

// 登录请求参数
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求参数
export interface RegisterRequest {
  username: string
  email: string
  password: string
  age?: number
  gender?: 'male' | 'female'
  height?: number
  weight?: number
  fitness_goal?: string
}

// 认证响应
export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: User
}

// API响应格式
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
  error?: string
}