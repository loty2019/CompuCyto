import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/client'

interface User {
  id: number
  email: string
  username: string
  role: string
  profile?: {
    id: number
    userId: number
    fullName?: string
    bio?: string
    avatarUrl?: string
    preferences?: Record<string, any>
  }
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value)
  const currentUser = computed(() => user.value)

  // Initialize from localStorage
  const initializeAuth = () => {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
    }
  }

  // Actions
  const login = async (email: string, password: string) => {
    try {
      if (window.__logToConsole) {
        window.__logToConsole(`🔐 Attempting login for ${email}`, 'info')
      }
      
      const response = await authAPI.login({ email, password })
      token.value = response.access_token
      user.value = response.user

      // Persist to localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      if (window.__logToConsole) {
        window.__logToConsole(`✅ Login successful: ${user.value.username}`, 'success')
      }

      return { success: true }
    } catch (error: any) {
      console.error('Login error:', error)
      if (window.__logToConsole) {
        window.__logToConsole(`❌ Login failed: ${error.response?.data?.message || 'Unknown error'}`, 'error')
      }
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed'
      }
    }
  }

  const register = async (email: string, username: string, password: string) => {
    try {
      if (window.__logToConsole) {
        window.__logToConsole(`📝 Attempting registration for ${email}`, 'info')
      }
      
      const response = await authAPI.register({ email, username, password })
      token.value = response.access_token
      user.value = response.user

      // Persist to localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      if (window.__logToConsole) {
        window.__logToConsole(`✅ Registration successful: ${user.value.username}`, 'success')
      }

      return { success: true }
    } catch (error: any) {
      console.error('Registration error:', error)
      if (window.__logToConsole) {
        window.__logToConsole(`❌ Registration failed: ${error.response?.data?.message || 'Unknown error'}`, 'error')
      }
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed'
      }
    }
  }

  const logout = () => {
    if (window.__logToConsole) {
      window.__logToConsole(`👋 User logged out: ${user.value?.username}`, 'info')
    }
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  const getProfile = async () => {
    try {
      const profile = await authAPI.getProfile()
      user.value = profile
      localStorage.setItem('user', JSON.stringify(profile))
      return { success: true }
    } catch (error: any) {
      console.error('Get profile error:', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch profile'
      }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    currentUser,
    initializeAuth,
    login,
    register,
    logout,
    getProfile
  }
})
