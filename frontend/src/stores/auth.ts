import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/utils/api'
import type { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  // 状态 - 从 localStorage 恢复用户数据
  const savedUser = localStorage.getItem('user')
  const user = ref<User | null>(savedUser ? JSON.parse(savedUser) : null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  // 初始化用户信息
  const initializeAuth = async () => {
    if (accessToken.value && !user.value) {
      try {
        const response = await authApi.getCurrentUser()
        if (response.success && response.data) {
          user.value = response.data
        }
      } catch (err) {
        // Token可能已过期，清除本地存储
        clearTokens()
      }
    }
  }

  // 清除tokens
  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // 保存认证信息
  const saveAuthData = (authData: AuthResponse) => {
    accessToken.value = authData.access_token
    refreshToken.value = authData.refresh_token
    user.value = authData.user

    localStorage.setItem('access_token', authData.access_token)
    localStorage.setItem('refresh_token', authData.refresh_token)
    localStorage.setItem('user', JSON.stringify(authData.user))
  }

  // 用户登录
  const login = async (credentials: LoginRequest) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authApi.login(credentials)
      
      if (response.success && response.data) {
        saveAuthData(response.data)
        return { success: true }
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '登录失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 用户注册
  const register = async (userData: RegisterRequest) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authApi.register(userData)
      
      if (response.success && response.data) {
        saveAuthData(response.data)
        return { success: true }
      } else {
        throw new Error(response.message || '注册失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '注册失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 用户登出
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearTokens()
    }
  }

  // 刷新token
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }
    
    try {
      const response = await authApi.refreshToken(refreshToken.value)
      
      if (response.success && response.data) {
        accessToken.value = response.data.access_token
        localStorage.setItem('access_token', response.data.access_token)
        return true
      } else {
        throw new Error('Token refresh failed')
      }
    } catch (err) {
      clearTokens()
      throw err
    }
  }

  // 更新用户信息
  const updateProfile = async (profileData: Partial<User>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.updateProfile(profileData)

      if (response.success && response.data) {
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        return { success: true }
      } else {
        throw new Error(response.message || '更新失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '更新失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // 获取用户信息（刷新用户数据）
  const fetchUser = async () => {
    if (!accessToken.value) {
      return { success: false, error: '未登录' }
    }

    try {
      const response = await authApi.getCurrentUser()
      if (response.success && response.data) {
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        return { success: true }
      } else {
        throw new Error(response.message || '获取用户信息失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '获取用户信息失败'
      return { success: false, error: error.value }
    }
  }

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // 计算属性
    isAuthenticated,
    
    // 方法
    initializeAuth,
    login,
    register,
    logout,
    refreshAccessToken,
    updateProfile,
    fetchUser,
    clearTokens
  }
})