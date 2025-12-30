import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '../utils/authApi'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('authToken'))
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // 登录
  const login = async (username, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.login(username, password)
      token.value = response.data.auth_token
      localStorage.setItem('authToken', token.value)
      
      // 获取用户信息
      await fetchCurrentUser()
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || '登录失败'
      token.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (username, email, password, re_password) => {
    loading.value = true
    error.value = null
    try {
      await authApi.register(username, email, password, re_password)
      return true
    } catch (err) {
      error.value = err.response?.data || '注册失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    loading.value = true
    error.value = null
    try {
      await authApi.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('authToken')
      loading.value = false
    }
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!token.value) return
    
    loading.value = true
    error.value = null
    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || '获取用户信息失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新用户信息
  const updateUser = async (userData) => {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.updateUser(userData)
      user.value = response.data
      return true
    } catch (err) {
      error.value = err.response?.data || '更新失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 修改密码
  const changePassword = async (new_password, re_new_password, current_password) => {
    loading.value = true
    error.value = null
    try {
      await authApi.changePassword(new_password, re_new_password, current_password)
      return true
    } catch (err) {
      error.value = err.response?.data || '密码修改失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 初始化用户（从存储的令牌恢复）
  const initializeUser = async () => {
    if (token.value) {
      await fetchCurrentUser()
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser,
    updateUser,
    changePassword,
    initializeUser,
  }
})
