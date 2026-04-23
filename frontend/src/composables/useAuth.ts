import { ref } from 'vue'
import { adminApi } from '@/api/admin'
import type { LoginResponse } from '@/types'

const TOKEN_KEY = 'token'
const USERNAME_KEY = 'username'

// 模块级共享状态（单例）
const isAuthenticated = ref(!!localStorage.getItem(TOKEN_KEY))
const username = ref(localStorage.getItem(USERNAME_KEY) || '')
const loading = ref(false)
const error = ref('')

export function useAuth() {
  async function login(inputUsername: string, inputPassword: string): Promise<boolean> {
    loading.value = true
    error.value = ''
    try {
      const res = await adminApi.login(inputUsername, inputPassword)
      const data: LoginResponse = res.data
      localStorage.setItem(TOKEN_KEY, data.token)
      localStorage.setItem(USERNAME_KEY, data.username)
      isAuthenticated.value = true
      username.value = data.username
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || '登录失败'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USERNAME_KEY)
    isAuthenticated.value = false
    username.value = ''
  }

  function getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  }

  return {
    isAuthenticated,
    username,
    loading,
    error,
    login,
    logout,
    getToken,
  }
}
