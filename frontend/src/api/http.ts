import axios from 'axios'

const http = axios.create({
  baseURL: '',
  timeout: 30000,
})

// 请求拦截器：自动携带 token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Token 配额耗尽事件总线
export const quotaExceededEvent = new EventTarget()

// 响应拦截器：处理 401 / 429 / 503
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    // Token quota exceeded handling
    if (error.response?.status === 429) {
      const data = error.response.data || {}
      const detail = data.detail

      // TOKEN_QUOTA_EXCEEDED specific handling
      if (detail && typeof detail === 'object' && detail.code === 'TOKEN_QUOTA_EXCEEDED') {
        error.quotaExceededInfo = detail
        quotaExceededEvent.dispatchEvent(new CustomEvent('quota-exceeded', { detail }))
      } else {
        // Generic rate limit handling
        error.rateLimitInfo = {
          detail: detail || '',
          message: data.message || '请求过于频繁',
          retryAfter: data.retry_after || 30,
        }
      }
    }
    // Service unavailable (also rate limit related)
    if (error.response?.status === 503) {
      const data = error.response.data || {}
      error.rateLimitInfo = {
        detail: data.detail || '',
        message: data.message || '请求过于频繁',
        retryAfter: data.retry_after || 30,
      }
    }
    return Promise.reject(error)
  }
)

export default http
